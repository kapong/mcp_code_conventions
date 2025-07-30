from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.storage import storage
from app.config import settings
from app.auth import verify_api_key
from app.tool_loader import get_tool_loader

router = APIRouter()

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

# Specific endpoints for configured tools
@router.get("/{project_id}/project-overview", response_model=str)
async def get_project_overview(
    project_id: str,
    api_key: str = Depends(verify_api_key)
):
    content = storage.get_tool_content("project_overview", project_id)
    
    if not content:
        content = _generate_default_content("project_overview", project_id)
    
    return content

@router.post("/{project_id}/project-overview", response_model=str)
async def update_project_overview(
    project_id: str,
    request_data: ToolUpdateRequest,
    api_key: str = Depends(verify_api_key)
):
    content = _generate_content_from_data("project_overview", project_id, request_data.data)
    return storage.save_tool_content("project_overview", project_id, content)

@router.get("/default/project-overview", response_model=str)
async def get_default_project_overview(
    api_key: str = Depends(verify_api_key)
):
    return await get_project_overview(settings.default_project_id, api_key)

@router.post("/default/project-overview", response_model=str)
async def update_default_project_overview(
    request_data: ToolUpdateRequest,
    api_key: str = Depends(verify_api_key)
):
    return await update_project_overview(settings.default_project_id, request_data, api_key)

@router.get("/{project_id}/technology-stack", response_model=str)
async def get_technology_stack(
    project_id: str,
    api_key: str = Depends(verify_api_key)
):
    content = storage.get_tool_content("technology_stack", project_id)
    
    if not content:
        content = _generate_default_content("technology_stack", project_id)
    
    return content

@router.post("/{project_id}/technology-stack", response_model=str)
async def update_technology_stack(
    project_id: str,
    request_data: ToolUpdateRequest,
    api_key: str = Depends(verify_api_key)
):
    content = _generate_content_from_data("technology_stack", project_id, request_data.data)
    return storage.save_tool_content("technology_stack", project_id, content)

@router.get("/default/technology-stack", response_model=str)
async def get_default_technology_stack(
    api_key: str = Depends(verify_api_key)
):
    return await get_technology_stack(settings.default_project_id, api_key)

@router.post("/default/technology-stack", response_model=str)
async def update_default_technology_stack(
    request_data: ToolUpdateRequest,
    api_key: str = Depends(verify_api_key)
):
    return await update_technology_stack(settings.default_project_id, request_data, api_key)

@router.get("/{project_id}/project-structure", response_model=str)
async def get_project_structure(
    project_id: str,
    api_key: str = Depends(verify_api_key)
):
    content = storage.get_tool_content("project_structure", project_id)
    
    if not content:
        content = _generate_default_content("project_structure", project_id)
    
    return content

@router.post("/{project_id}/project-structure", response_model=str)
async def update_project_structure(
    project_id: str,
    request_data: ToolUpdateRequest,
    api_key: str = Depends(verify_api_key)
):
    content = _generate_content_from_data("project_structure", project_id, request_data.data)
    return storage.save_tool_content("project_structure", project_id, content)

@router.get("/default/project-structure", response_model=str)
async def get_default_project_structure(
    api_key: str = Depends(verify_api_key)
):
    return await get_project_structure(settings.default_project_id, api_key)

@router.post("/default/project-structure", response_model=str)
async def update_default_project_structure(
    request_data: ToolUpdateRequest,
    api_key: str = Depends(verify_api_key)
):
    return await update_project_structure(settings.default_project_id, request_data, api_key)

# Generic endpoints for additional tools
@router.get("/{project_id}/tool/{tool_name}", response_model=str)
async def get_generic_content(
    project_id: str,
    tool_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Generic endpoint for tools not explicitly defined"""
    tool_key = tool_name.replace('-', '_')
    content = storage.get_tool_content(tool_key, project_id)
    
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
    return storage.save_tool_content(tool_key, project_id, request_data.content)