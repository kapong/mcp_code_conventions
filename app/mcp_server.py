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
    
    
    # Tool not found
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())