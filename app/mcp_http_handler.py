import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.types import Tool, TextContent
from app.storage import storage
from app.config import settings
from app.tool_loader import get_tool_loader
from app.auth import verify_api_key


class MCPOverHTTPHandler:
    def __init__(self):
        self.server = Server("mcp-code-conventions")
        self.tools = []
        self.tool_handler = None
        self._setup_tools()
    
    def _setup_tools(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            tools = [
                Tool(
                    name="get_project_overview",
                    description="Call this tool when you need to understand the business context, target audience, or core functionality of the project. Use this information to make decisions about feature implementation, user experience, and business logic alignment. Essential for ensuring your code serves the intended business purpose and user needs.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project identifier (defaults to 'default')",
                                "default": "default"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_technology_stack",
                    description="Call this tool before writing code to understand which frameworks, libraries, and technologies are already in use. Essential for maintaining consistency, avoiding conflicts, and ensuring compatibility. Use this information to choose appropriate dependencies, follow established patterns, and integrate properly with existing systems.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project identifier (defaults to 'default')",
                                "default": "default"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_project_structure",
                    description="Call this tool whenever you are generating code and need to align with the project's file organization, naming conventions, or architecture guidelines. Ensures that generated code fits cleanly into the existing structure of the app and services. Essential for maintaining code organization, following team standards, and ensuring files are placed in the correct locations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project identifier (defaults to 'default')",
                                "default": "default"
                            }
                        }
                    }
                )
            ]
            self.tools = tools
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            # Extract project_id from URL context or arguments
            project_id = arguments.get("project_id", settings.default_project_id)
            if name == "get_project_overview":
                overview_data = storage.get_project_overview(project_id)
                
                if not overview_data:
                    content = f"""# Project Overview - {project_id}

## Business Description
*No business description available*

## Target Users
*No target users defined*

## Main Features
*No main features listed*

*Note: Use update_project_overview tool to set this information*"""
                else:
                    content = f"""# Project Overview - {project_id}

## Business Description
{overview_data.get('business_description') or '*No business description available*'}

## Target Users
{overview_data.get('target_users') or '*No target users defined*'}

## Main Features
{overview_data.get('main_features') or '*No main features listed*'}"""
                
                return [TextContent(type="text", text=content)]
            
            elif name == "get_technology_stack":
                tech_stack_data = storage.get_technology_stack(project_id)
                
                if not tech_stack_data:
                    content = f"""# Technology Stack - {project_id}

## Frontend
*No frontend technologies specified*

## Backend
*No backend technologies specified*

## Database
*No database technologies specified*

## Infrastructure
*No infrastructure technologies specified*

## Tools
*No tools specified*

*Note: Use update_technology_stack tool to set this information*"""
                else:
                    content = f"""# Technology Stack - {project_id}

## Frontend
{tech_stack_data.get('frontend') or '*No frontend technologies specified*'}

## Backend
{tech_stack_data.get('backend') or '*No backend technologies specified*'}

## Database
{tech_stack_data.get('database') or '*No database technologies specified*'}

## Infrastructure
{tech_stack_data.get('infrastructure') or '*No infrastructure technologies specified*'}

## Tools
{tech_stack_data.get('tools') or '*No tools specified*'}"""
                
                return [TextContent(type="text", text=content)]
            
            elif name == "get_project_structure":
                structure_data = storage.get_project_structure(project_id)
                
                if not structure_data:
                    content = f"""# Project Structure - {project_id}

## Folder Structure
*No folder structure defined*

## Naming Conventions
*No naming conventions specified*

## Architecture Approach
*No architecture approach defined*

*Note: Use update_project_structure tool to set this information*"""
                else:
                    content = f"""# Project Structure - {project_id}

## Folder Structure
{structure_data.get('folder_structure') or '*No folder structure defined*'}

## Naming Conventions
{structure_data.get('naming_conventions') or '*No naming conventions specified*'}

## Architecture Approach
{structure_data.get('architecture_approach') or '*No architecture approach defined*'}"""
                
                return [TextContent(type="text", text=content)]
        
        # Store handlers for direct access
        self.list_tools_handler = list_tools
        self.call_tool_handler = call_tool

    async def handle_mcp_request(self, request: Request, project_id: str = "default") -> Dict[str, Any]:
        """Handle MCP protocol requests over HTTP"""
        try:
            body = await request.json()
            method = body.get("method")
            params = body.get("params", {})
            request_id = body.get("id")
            
            # Set project_id context for tools
            if method == "tools/call" and "arguments" in params:
                params["arguments"]["project_id"] = project_id
            
            # Handle different MCP methods
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "mcp-code-conventions",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                tools = await self.list_tools_handler()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": tool.name,
                                "description": tool.description,
                                "inputSchema": tool.inputSchema
                            }
                            for tool in tools
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                # Ensure project_id is set
                arguments["project_id"] = project_id
                
                result = await self.call_tool_handler(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": content.type,
                                "text": content.text
                            }
                            for content in result
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": body.get("id") if "body" in locals() and body else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }


# Global handler instance
mcp_handler = MCPOverHTTPHandler()


# Pydantic models for HTTP API
class ToolUpdateRequest(BaseModel):
    """Dynamic update request based on tool configuration"""
    data: Dict[str, Any] = Field(..., description="Tool-specific data")


# HTTP API Router using dynamic tools
router = APIRouter()

@router.get("/{project_id}/tool/{tool_name}", response_model=str)
async def get_tool_content(
    project_id: str,
    tool_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Get tool content for any dynamically configured tool"""
    tool_loader = get_tool_loader()
    
    # Find tool config by name
    tool_key = None
    for key, config in tool_loader.tools_config.items():
        if config.name == tool_name:
            tool_key = key
            break
    
    if not tool_key:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    content = storage.get_tool_content(tool_key, project_id)
    
    if not content:
        # Generate default content
        title = tool_key.replace('_', ' ').title()
        content = f"""# {title} - {project_id}

*No content available for this tool*

*Note: Use the corresponding update endpoint to set this information*"""
    
    return content

@router.post("/{project_id}/tool/{tool_name}", response_model=str)
async def update_tool_content(
    project_id: str,
    tool_name: str,
    request_data: ToolUpdateRequest,
    api_key: str = Depends(verify_api_key)
):
    """Update tool content for any dynamically configured tool"""
    tool_loader = get_tool_loader()
    
    # Find tool config by name
    tool_key = None
    for key, config in tool_loader.tools_config.items():
        if config.name == tool_name:
            tool_key = key
            break
    
    if not tool_key:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    # Generate content based on tool type and provided data
    content = _generate_content_from_data(tool_key, project_id, request_data.data)
    
    # Save the content
    success = storage.save_tool_content(tool_key, project_id, content)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save content")
    
    return content

# Convenience endpoints for default project
@router.get("/default/tool/{tool_name}", response_model=str)
async def get_default_tool_content(
    tool_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Get tool content for default project"""
    return await get_tool_content(settings.default_project_id, tool_name, api_key)

@router.post("/default/tool/{tool_name}", response_model=str)
async def update_default_tool_content(
    tool_name: str,
    request_data: ToolUpdateRequest,
    api_key: str = Depends(verify_api_key)
):
    """Update tool content for default project"""
    return await update_tool_content(settings.default_project_id, tool_name, request_data, api_key)

def _generate_content_from_data(tool_key: str, project_id: str, data: dict) -> str:
    """Generate markdown content from tool data"""
    title = tool_key.replace('_', ' ').title()
    content = f"# {title} - {project_id}\n\n"
    
    if tool_key == "project_overview":
        content += f"""## Business Description
{data.get('business_description', '')}

## Target Users
{data.get('target_users', '')}

## Main Features
{data.get('main_features', '')}"""
    elif tool_key == "technology_stack":
        content += f"""## Frontend
{data.get('frontend', '')}

## Backend
{data.get('backend', '')}

## Database
{data.get('database', '')}

## Infrastructure
{data.get('infrastructure', '')}

## Tools
{data.get('tools', '')}"""
    elif tool_key == "project_structure":
        content += f"""## Folder Structure
{data.get('folder_structure', '')}

## Naming Conventions
{data.get('naming_conventions', '')}

## Architecture Approach
{data.get('architecture_approach', '')}"""
    else:
        # Generic content handling
        content += data.get('content', '*No content provided*')
    
    return content