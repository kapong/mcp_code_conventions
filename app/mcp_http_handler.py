import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from mcp.server import Server
from mcp.types import Tool, TextContent
from app.storage import storage
from app.config import settings


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
                    name="update_project_overview",
                    description="Update project overview information when project requirements, target users, or business objectives change. Use this to keep the project context current and aligned with stakeholder expectations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project identifier (defaults to 'default')",
                                "default": "default"
                            },
                            "business_description": {
                                "type": "string",
                                "description": "Clear description of what the business/project does, its value proposition, and core objectives"
                            },
                            "target_users": {
                                "type": "string",
                                "description": "Detailed description of the intended users, their needs, technical level, and use cases"
                            },
                            "main_features": {
                                "type": "string",
                                "description": "List of primary features and functionality that define the project's core capabilities"
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
                    name="update_technology_stack",
                    description="Update technology stack information when new tools, frameworks, or services are added to the project. Keep this current to help future development decisions and maintain team alignment on approved technologies.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project identifier (defaults to 'default')",
                                "default": "default"
                            },
                            "frontend": {
                                "type": "string",
                                "description": "Frontend frameworks, libraries, and tools (e.g., React 18, Next.js, Tailwind CSS, TypeScript)"
                            },
                            "backend": {
                                "type": "string",
                                "description": "Backend technologies, frameworks, and runtime environments (e.g., Node.js, Express.js, Python FastAPI, .NET Core)"
                            },
                            "database": {
                                "type": "string",
                                "description": "Database systems, ORMs, migration tools (e.g., PostgreSQL, MongoDB, Prisma, Alembic)"
                            },
                            "infrastructure": {
                                "type": "string",
                                "description": "Deployment, hosting, containers, cloud services (e.g., Docker, Kubernetes, AWS, Vercel)"
                            },
                            "tools": {
                                "type": "string",
                                "description": "Development tools, testing frameworks, CI/CD, linting (e.g., Jest, ESLint, GitHub Actions, Webpack)"
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
                ),
                Tool(
                    name="update_project_structure",
                    description="Update project structure guidelines when file organization, naming conventions, or architectural patterns change. Use this to document new standards and ensure consistency across the codebase as the project evolves.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project identifier (defaults to 'default')",
                                "default": "default"
                            },
                            "folder_structure": {
                                "type": "string",
                                "description": "Detailed folder organization with explanations of what goes where (e.g., /src/components for React components, /lib for utilities, /pages for Next.js routes)"
                            },
                            "naming_conventions": {
                                "type": "string",
                                "description": "File naming patterns, variable naming styles, class naming conventions (e.g., PascalCase for components, camelCase for functions, kebab-case for files)"
                            },
                            "architecture_approach": {
                                "type": "string",
                                "description": "Architectural patterns, design principles, code organization strategies (e.g., MVC, clean architecture, microservices, monorepo structure)"
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
            
            elif name == "update_project_overview":
                data_dict = {
                    'business_description': arguments.get("business_description"),
                    'target_users': arguments.get("target_users"),
                    'main_features': arguments.get("main_features")
                }
                
                storage.save_project_overview(project_id, data_dict)
                return [TextContent(type="text", text=f"Project overview for '{project_id}' updated successfully")]
                
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
            
            elif name == "update_technology_stack":
                data_dict = {
                    'frontend': arguments.get("frontend"),
                    'backend': arguments.get("backend"),
                    'database': arguments.get("database"),
                    'infrastructure': arguments.get("infrastructure"),
                    'tools': arguments.get("tools")
                }
                
                storage.save_technology_stack(project_id, data_dict)
                return [TextContent(type="text", text=f"Technology stack for '{project_id}' updated successfully")]
                
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
            
            elif name == "update_project_structure":
                data_dict = {
                    'folder_structure': arguments.get("folder_structure"),
                    'naming_conventions': arguments.get("naming_conventions"),
                    'architecture_approach': arguments.get("architecture_approach")
                }
                
                storage.save_project_structure(project_id, data_dict)
                return [TextContent(type="text", text=f"Project structure for '{project_id}' updated successfully")
        
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