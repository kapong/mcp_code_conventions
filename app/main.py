from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
import logging
from typing import Dict, Any
from app.mcp_http_handler import mcp_handler, router as dynamic_http_router
from app.tools.dynamic_tools import router as tools_router
from app.auth import verify_api_key
from app.exceptions import (
    MCPConventionsError, StorageError, ValidationError, 
    AuthenticationError, AuthorizationError, ToolNotFoundError,
    ProjectIdError, FileNotFoundError, PermissionError
)
from app.storage import get_global_storage
from app.tool_loader import get_tool_loader

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Code Conventions Server",
    description="MCP server that provides tools for AI code agents to follow project conventions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(MCPConventionsError)
async def mcp_conventions_exception_handler(request: Request, exc: MCPConventionsError):
    """Handle custom MCP Conventions Server exceptions"""
    logger.error(f"MCP Conventions Error: {exc.message}", exc_info=True)
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Map specific exceptions to HTTP status codes
    if isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, (ToolNotFoundError, FileNotFoundError)):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ProjectIdError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, PermissionError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, StorageError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "type": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors with proper HTTP status"""
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "type": "VALIDATION_ERROR",
                "message": str(exc),
                "details": {}
            }
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please contact support if this persists.",
                "details": {}
            }
        }
    )

# Include routers with error handling
app.include_router(dynamic_http_router, tags=["Dynamic HTTP Tools"])
app.include_router(tools_router, tags=["Tool Endpoints"])

@app.get("/")
async def root():
    """Root endpoint with basic server information"""
    try:
        tool_loader = get_tool_loader()
        storage = get_global_storage()
        
        available_tools = tool_loader.get_available_tools()
        projects = storage.list_projects()
        
        return {
            "message": "MCP Code Conventions Server",
            "version": "1.0.0",
            "status": "operational",
            "tools_available": len(available_tools),
            "projects_configured": len(projects),
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "mcp": "/mcp/{project_id}",
                "tools": "/{project_id}/{tool-name}"
            }
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        return {
            "message": "MCP Code Conventions Server",
            "version": "1.0.0",
            "status": "degraded",
            "error": "Unable to retrieve full status information"
        }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Test tool loader
        tool_loader = get_tool_loader()
        available_tools = tool_loader.get_available_tools()
        
        # Test storage
        storage = get_global_storage()
        projects = storage.list_projects()
        
        # Test basic functionality
        test_content = storage.get_tool_content("project_overview", "default")
        
        health_data = {
            "status": "healthy",
            "timestamp": None,  # FastAPI will handle this
            "components": {
                "tool_loader": {
                    "status": "healthy",
                    "tools_count": len(available_tools),
                    "tools": available_tools
                },
                "storage": {
                    "status": "healthy",
                    "projects_count": len(projects),
                    "data_directory": str(storage.data_dir),
                    "test_read": bool(test_content)
                }
            }
        }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "components": {
                    "tool_loader": {"status": "unknown"},
                    "storage": {"status": "unknown"}
                }
            }
        )

@app.get("/projects")
async def list_projects(_: str = Depends(verify_api_key)):
    """List all available projects"""
    try:
        storage = get_global_storage()
        tool_loader = get_tool_loader()
        
        projects = storage.list_projects()
        project_details = {}
        
        for project_id in projects:
            try:
                tools_status = storage.get_project_tools(project_id)
                project_details[project_id] = {
                    "tools": tools_status,
                    "tools_count": len(tools_status),
                    "configured_tools": sum(1 for exists in tools_status.values() if exists)
                }
            except Exception as e:
                logger.warning(f"Error getting details for project {project_id}: {e}")
                project_details[project_id] = {"error": str(e)}
        
        return {
            "projects": projects,
            "total_count": len(projects),
            "details": project_details,
            "available_tools": tool_loader.get_available_tools()
        }
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list projects"
        )

# MCP-over-HTTP endpoints with enhanced error handling
@app.post("/mcp")
async def mcp_default(request: Request, _: str = Depends(verify_api_key)):
    """MCP protocol endpoint for default project"""
    try:
        result = await mcp_handler.handle_mcp_request(request, "default")
        return result
    except Exception as e:
        logger.error(f"MCP request failed for default project: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MCP request processing failed"
        )

@app.post("/mcp/{project_id}")
async def mcp_project(request: Request, project_id: str, _: str = Depends(verify_api_key)):
    """MCP protocol endpoint for specific project"""
    try:
        # Validate project_id
        if not project_id or not project_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project ID cannot be empty"
            )
        
        # Sanitize project_id
        sanitized_project_id = project_id.strip().lower()
        if not sanitized_project_id.replace("-", "").replace("_", "").isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project ID can only contain letters, numbers, hyphens, and underscores"
            )
        
        result = await mcp_handler.handle_mcp_request(request, sanitized_project_id)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"MCP request failed for project {project_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MCP request processing failed"
        )

# Add startup event for initialization logging
@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    try:
        logger.info("Starting MCP Code Conventions Server...")
        
        tool_loader = get_tool_loader()
        storage = get_global_storage()
        
        available_tools = tool_loader.get_available_tools()
        projects = storage.list_projects()
        
        logger.info(f"Server started with {len(available_tools)} tools: {', '.join(available_tools)}")
        logger.info(f"Found {len(projects)} projects: {', '.join(projects)}")
        logger.info(f"Data directory: {storage.data_dir}")
        logger.info("MCP Code Conventions Server started successfully")
        
    except Exception as e:
        logger.error(f"Startup initialization failed: {e}", exc_info=True)
        # Don't fail startup, but log the error

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info("MCP Code Conventions Server shutting down...")

# Configure logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )