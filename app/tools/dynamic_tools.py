from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.storage import get_global_storage
from app.config import settings
from app.auth import verify_api_key
from app.tool_loader import get_tool_loader

router = APIRouter()

# Initialize tool loader
tool_loader = get_tool_loader()

class GenericContentRequest(BaseModel):
    """Generic content request for any tool"""
    content: str = Field(..., description="Content to save")

class ToolUpdateRequest(BaseModel):
    """Dynamic update request based on tool configuration"""
    data: Dict[str, Any] = Field(..., description="Tool-specific data")

def _generate_default_content(tool_key: str, project_id: str) -> str:
    """Generate default content when no content is found"""
    title = tool_key.replace('_', ' ').title()
    
    if tool_key == "project_overview":
        return f"""# Project Overview - {project_id}

## Business Description
*No business description available*

## Target Users
*No target users defined*

## Main Features
*No main features listed*

*Note: Use POST /{project_id}/project-overview to update this information*"""
    
    elif tool_key == "technology_stack":
        return f"""# Technology Stack - {project_id}

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

*Note: Use POST /{project_id}/technology-stack to update this information*"""
    
    elif tool_key == "project_structure":
        return f"""# Project Structure - {project_id}

## Folder Structure
*No folder structure defined*

## Naming Conventions
*No naming conventions specified*

## Architecture Approach
*No architecture approach defined*

*Note: Use POST /{project_id}/project-structure to update this information*"""
    
    else:
        return f"""# {title} - {project_id}

*No content available for this tool*

*Note: Use POST /{project_id}/{tool_key.replace('_', '-')} to update this information*"""

def _generate_content_from_data(tool_key: str, project_id: str, data: Dict[str, Any]) -> str:
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

# Dynamic endpoint creation functions
def _create_get_endpoint(tool_key: str, url_path: str):
    """Create a GET endpoint for a tool"""
    async def get_tool_content(
        project_id: str,
        api_key: str = Depends(verify_api_key)
    ):
        content = get_global_storage().get_tool_content(tool_key, project_id)
        
        if not content:
            content = _generate_default_content(tool_key, project_id)
        
        return content
    
    return get_tool_content

def _create_post_endpoint(tool_key: str, url_path: str):
    """Create a POST endpoint for a tool"""
    # Determine if this tool uses structured data or generic content
    structured_tools = ["project_overview", "technology_stack", "project_structure"]
    
    if tool_key in structured_tools:
        async def update_structured_tool_content(
            project_id: str,
            request_data: ToolUpdateRequest,
            api_key: str = Depends(verify_api_key)
        ):
            content = _generate_content_from_data(tool_key, project_id, request_data.data)
            return get_global_storage().save_tool_content(tool_key, project_id, content)
        
        return update_structured_tool_content
    else:
        async def update_generic_tool_content(
            project_id: str,
            request_data: GenericContentRequest,
            api_key: str = Depends(verify_api_key)
        ):
            return get_global_storage().save_tool_content(tool_key, project_id, request_data.content)
        
        return update_generic_tool_content

def _create_default_get_endpoint(tool_key: str, url_path: str):
    """Create a default GET endpoint for a tool"""
    get_endpoint = _create_get_endpoint(tool_key, url_path)
    
    async def get_default_tool_content(
        api_key: str = Depends(verify_api_key)
    ):
        return await get_endpoint(settings.default_project_id, api_key)
    
    return get_default_tool_content

def _create_default_post_endpoint(tool_key: str, url_path: str):
    """Create a default POST endpoint for a tool"""
    post_endpoint = _create_post_endpoint(tool_key, url_path)
    structured_tools = ["project_overview", "technology_stack", "project_structure"]
    
    if tool_key in structured_tools:
        async def update_default_structured_tool_content(
            request_data: ToolUpdateRequest,
            api_key: str = Depends(verify_api_key)
        ):
            return await post_endpoint(settings.default_project_id, request_data, api_key)
        
        return update_default_structured_tool_content
    else:
        async def update_default_generic_tool_content(
            request_data: GenericContentRequest,
            api_key: str = Depends(verify_api_key)
        ):
            return await post_endpoint(settings.default_project_id, request_data, api_key)
        
        return update_default_generic_tool_content

# Dynamically register endpoints for all tools from tools.json
for tool_key, tool_config in tool_loader.tools_config.items():
    # Convert tool_key to URL path (e.g., "project_overview" -> "project-overview")
    url_path = tool_key.replace('_', '-')
    
    # Register project-specific endpoints
    router.add_api_route(
        f"/{{project_id}}/{url_path}",
        _create_get_endpoint(tool_key, url_path),
        methods=["GET"],
        response_model=str,
        name=f"get_{tool_key}"
    )
    
    router.add_api_route(
        f"/{{project_id}}/{url_path}",
        _create_post_endpoint(tool_key, url_path),
        methods=["POST"],
        response_model=str,
        name=f"update_{tool_key}"
    )
    
    # Register default project endpoints
    router.add_api_route(
        f"/default/{url_path}",
        _create_default_get_endpoint(tool_key, url_path),
        methods=["GET"],
        response_model=str,
        name=f"get_default_{tool_key}"
    )
    
    router.add_api_route(
        f"/default/{url_path}",
        _create_default_post_endpoint(tool_key, url_path),
        methods=["POST"],
        response_model=str,
        name=f"update_default_{tool_key}"
    )

# Generic endpoints for additional tools
@router.get("/{project_id}/tool/{tool_name}", response_model=str)
async def get_generic_content(
    project_id: str,
    tool_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Generic endpoint for tools not explicitly defined"""
    tool_key = tool_name.replace('-', '_')
    content = get_global_storage().get_tool_content(tool_key, project_id)
    
    if not content:
        content = _generate_default_content(tool_key, project_id)
    
    return content

@router.post("/{project_id}/tool/{tool_name}", response_model=str)
async def update_generic_content(
    project_id: str,
    tool_name: str,
    request_data: GenericContentRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generic endpoint for updating tools not explicitly defined"""
    tool_key = tool_name.replace('-', '_')
    return get_global_storage().save_tool_content(tool_key, project_id, request_data.content)