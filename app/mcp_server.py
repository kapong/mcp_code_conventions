import asyncio
import logging
from typing import Optional, Dict, Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from app.storage import get_global_storage
from app.config import settings
from app.tool_loader import get_tool_loader
from app.exceptions import (
    MCPServerError, ToolExecutionError, ToolNotFoundError,
    StorageError, ValidationError, ProjectIdError
)

logger = logging.getLogger(__name__)

server = Server("mcp-code-conventions")

def _sanitize_project_id(project_id: Optional[str]) -> str:
    """Sanitize and validate project ID"""
    if not project_id:
        return settings.default_project_id
    
    # Basic sanitization
    sanitized = project_id.strip().lower()
    
    # Validate format
    if not sanitized.replace("-", "").replace("_", "").isalnum():
        logger.warning(f"Invalid project ID format: {project_id}, using default")
        return settings.default_project_id
    
    return sanitized

def _handle_tool_error(tool_name: str, error: Exception, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tool execution errors and return appropriate response"""
    error_msg = f"Error executing tool '{tool_name}': {str(error)}"
    logger.error(error_msg, exc_info=True)
    
    # Create user-friendly error messages
    if isinstance(error, ToolNotFoundError):
        user_msg = f"Tool '{tool_name}' is not available. Available tools: {', '.join(error.available_tools or [])}"
    elif isinstance(error, ProjectIdError):
        user_msg = f"Invalid project ID: {error.reason}"
    elif isinstance(error, StorageError):
        user_msg = f"Storage error for tool '{tool_name}': Unable to access project data"
    elif isinstance(error, ValidationError):
        user_msg = f"Validation error: {error.message}"
    else:
        user_msg = f"An error occurred while executing tool '{tool_name}'. Please check the tool configuration and try again."
    
    return [TextContent(type="text", text=user_msg)]

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools with error handling"""
    try:
        tool_loader = get_tool_loader()
        tool_schemas = tool_loader.get_mcp_tools_schema()
        
        tools = [Tool(**schema) for schema in tool_schemas]
        logger.info(f"Listed {len(tools)} available tools")
        return tools
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}", exc_info=True)
        # Return an empty list rather than crashing
        return []

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool with comprehensive error handling"""
    try:
        # Validate inputs
        if not name:
            raise ToolExecutionError("", "Tool name cannot be empty", arguments)
        
        if not isinstance(arguments, dict):
            raise ToolExecutionError(name, "Arguments must be a dictionary", arguments)
        
        # Sanitize project ID
        project_id = _sanitize_project_id(arguments.get("project_id"))
        arguments["project_id"] = project_id
        
        logger.debug(f"Executing tool '{name}' for project '{project_id}' with arguments: {arguments}")
        
        # Get tool loader and storage
        tool_loader = get_tool_loader()
        storage = get_global_storage()
        
        # Handle get tools
        for tool_key, tool_config in tool_loader.tools_config.items():
            if name == tool_config.name:
                try:
                    content = storage.get_tool_content(tool_key, project_id)
                    
                    if not content:
                        # Generate default content if none found
                        content = tool_loader.generate_default_content(tool_key, project_id)
                        logger.info(f"Generated default content for tool '{tool_key}' in project '{project_id}'")
                    
                    logger.debug(f"Successfully retrieved content for tool '{name}' in project '{project_id}'")
                    return [TextContent(type="text", text=content)]
                    
                except Exception as e:
                    return _handle_tool_error(name, e, arguments)
        
        # Handle update tools (if they exist in the future)
        # This is a placeholder for potential update functionality
        if name.startswith("update_"):
            base_tool_key = name.replace("update_", "")
            if base_tool_key in tool_loader.tools_config:
                error_msg = f"Update functionality for tool '{name}' is not yet implemented via MCP. Use the HTTP API endpoints instead."
                logger.warning(error_msg)
                return [TextContent(type="text", text=error_msg)]
        
        # Tool not found
        available_tools = [config.name for config in tool_loader.tools_config.values()]
        raise ToolNotFoundError(name, available_tools)
        
    except Exception as e:
        return _handle_tool_error(name, e, arguments)

@server.ping()
async def ping() -> str:
    """Health check endpoint"""
    try:
        # Test basic functionality
        tool_loader = get_tool_loader()
        storage = get_global_storage()
        
        # Basic health checks
        available_tools = len(tool_loader.get_available_tools())
        projects = len(storage.list_projects())
        
        health_msg = f"MCP Code Conventions Server is healthy. {available_tools} tools available, {projects} projects configured."
        logger.debug(health_msg)
        return health_msg
        
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg

async def main():
    """Main server entry point with error handling"""
    try:
        logger.info("Starting MCP Code Conventions Server...")
        
        # Initialize and validate configuration
        tool_loader = get_tool_loader()
        storage = get_global_storage()
        
        # Log startup information
        available_tools = tool_loader.get_available_tools()
        projects = storage.list_projects()
        
        logger.info(f"Server initialized with {len(available_tools)} tools: {', '.join(available_tools)}")
        logger.info(f"Found {len(projects)} projects: {', '.join(projects)}")
        logger.info(f"Data directory: {storage.data_dir}")
        
        # Start the server
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP server started successfully")
            await server.run(read_stream, write_stream, server.create_initialization_options())
            
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        raise MCPServerError(f"Server startup failed: {str(e)}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        exit(1)