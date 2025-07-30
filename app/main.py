from fastapi import FastAPI, Request, Depends
from app.mcp_http_handler import mcp_handler, router as dynamic_http_router
from app.auth import verify_api_key

app = FastAPI(
    title="MCP Code Conventions Server",
    description="MCP server that provides tools for AI code agents to follow project conventions",
    version="1.0.0"
)

app.include_router(dynamic_http_router, tags=["Dynamic HTTP Tools"])

@app.get("/")
async def root():
    return {"message": "MCP Code Conventions Server"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# MCP-over-HTTP endpoints
@app.post("/mcp")
async def mcp_default(request: Request, _: str = Depends(verify_api_key)):
    """MCP protocol endpoint for default project"""
    result = await mcp_handler.handle_mcp_request(request, "default")
    return result

@app.post("/mcp/{project_id}")
async def mcp_project(request: Request, project_id: str, _: str = Depends(verify_api_key)):
    """MCP protocol endpoint for specific project"""
    result = await mcp_handler.handle_mcp_request(request, project_id)
    return result