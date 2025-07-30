import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from app.storage import storage
from app.config import settings
from app.tool_loader import get_tool_loader

server = Server("mcp-code-conventions")

@server.list_tools()
async def list_tools() -> list[Tool]:
    tool_loader = get_tool_loader()
    tool_schemas = tool_loader.get_mcp_tools_schema()
    
    return [Tool(**schema) for schema in tool_schemas]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    project_id = arguments.get("project_id", settings.default_project_id)
    tool_loader = get_tool_loader()
    
    # Handle get tools
    for tool_key, tool_config in tool_loader.tools_config.items():
        if name == tool_config.name:
            content = storage.get_tool_content(tool_key, project_id)
            
            if not content:
                content = f"""# {tool_key.replace('_', ' ').title()} - {project_id}

*No content available for this tool*

*Note: Use update_{tool_key} tool to set this information*"""
            
            return [TextContent(type="text", text=content)]
    
    # Handle update tools
    for tool_key, tool_config in tool_loader.tools_config.items():
        update_tool_name = f"update_{tool_key}"
        if name == update_tool_name:
            # Generate content based on tool type
            content = _generate_content_from_arguments(tool_key, project_id, arguments)
            
            storage.save_tool_content(tool_key, project_id, content)
            return [TextContent(type="text", text=f"{tool_key.replace('_', ' ').title()} for '{project_id}' updated successfully")]
    
    # Tool not found
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

def _generate_content_from_arguments(tool_key: str, project_id: str, arguments: dict) -> str:
    """Generate markdown content from tool arguments"""
    title = tool_key.replace('_', ' ').title()
    content = f"# {title} - {project_id}\n\n"
    
    if tool_key == "project_overview":
        content += f"""## Business Description
{arguments.get('business_description', '')}

## Target Users
{arguments.get('target_users', '')}

## Main Features
{arguments.get('main_features', '')}"""
    elif tool_key == "technology_stack":
        content += f"""## Frontend
{arguments.get('frontend', '')}

## Backend
{arguments.get('backend', '')}

## Database
{arguments.get('database', '')}

## Infrastructure
{arguments.get('infrastructure', '')}

## Tools
{arguments.get('tools', '')}"""
    elif tool_key == "project_structure":
        content += f"""## Folder Structure
{arguments.get('folder_structure', '')}

## Naming Conventions
{arguments.get('naming_conventions', '')}

## Architecture Approach
{arguments.get('architecture_approach', '')}"""
    else:
        # Generic content handling
        content += arguments.get('content', '*No content provided*')
    
    return content

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())