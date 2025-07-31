import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.types import Tool, TextContent
from app.storage import get_global_storage
from app.config import settings
from app.tool_loader import get_tool_loader
from app.auth import verify_api_key


class MCPOverHTTPHandler:
    def __init__(self):
        self.server = Server("mcp-code-conventions")
        self.tools = []
        self.tool_handler = None
        self.tool_loader = get_tool_loader()
        self._setup_tools()
    
    def _setup_tools(self):
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            # Generate tools dynamically from tools.json configuration
            tool_schemas = self.tool_loader.get_mcp_tools_schema()
            tools = []
            
            for schema in tool_schemas:
                tools.append(Tool(
                    name=schema["name"],
                    description=schema["description"],
                    inputSchema=schema["inputSchema"]
                ))
            
            self.tools = tools
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            # Extract project_id from URL context or arguments
            project_id = arguments.get("project_id", settings.default_project_id)
            
            # Find tool configuration by name
            tool_key = None
            for key, config in self.tool_loader.tools_config.items():
                if config.name == name:
                    tool_key = key
                    break
            
            if not tool_key:
                raise Exception(f"Tool '{name}' not found in configuration")
            
            # Get content using the tool loader with fallback
            content = self.tool_loader.get_file_content(tool_key, project_id)
            
            if not content:
                # Generate default content using tool loader
                content = self.tool_loader.generate_default_content(tool_key, project_id)
            
            return [TextContent(type="text", text=content)]
        
        # Store handlers for direct access
        self.list_tools_handler = list_tools
        self.call_tool_handler = call_tool
    
    def _generate_default_content(self, tool_key: str, project_id: str) -> str:
        """Generate default content when no file exists for a tool"""
        title = tool_key.replace('_', ' ').title()
        
        return f"""# {title} - {project_id}

*No content available for this tool*

*Note: Configure this tool in tools.json and add corresponding markdown file*"""

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
    
    content = get_global_storage().get_tool_content(tool_key, project_id)
    
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
    
    # Generate content using tool loader
    content = tool_loader.generate_content_from_data(tool_key, project_id, request_data.data)
    
    # Save the content
    success = get_global_storage().save_tool_content(tool_key, project_id, content)
    
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

