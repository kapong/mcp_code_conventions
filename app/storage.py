from pathlib import Path
from typing import Optional, Dict, Any
import os
import logging
from app.tool_loader import get_tool_loader
from app.exceptions import (
    StorageError, FileNotFoundError, FileReadError, FileWriteError,
    DirectoryCreationError, ToolNotFoundError, ProjectIdError,
    PermissionError, DiskSpaceError, handle_file_operation_error
)

logger = logging.getLogger(__name__)

class MarkdownStorage:
    """Markdown-based storage system for MCP code conventions with comprehensive error handling"""
    
    def __init__(self, data_dir: str = "/app/data", tool_loader=None):
        self.tool_loader = tool_loader or get_tool_loader()
        
        try:
            self.data_dir = Path(data_dir).resolve()
            self._ensure_data_directory()
            logger.info(f"Initialized MarkdownStorage with data directory: {self.data_dir}")
        except Exception as e:
            raise DirectoryCreationError(data_dir, str(e))
    
    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists and is writable"""
        try:
            # Create directory if it doesn't exist
            self.data_dir.mkdir(exist_ok=True, parents=True)
            
            # Test write permissions
            test_file = self.data_dir / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                raise PermissionError("write", str(self.data_dir), str(e))
                
        except OSError as e:
            if "No space left on device" in str(e):
                raise DiskSpaceError(str(self.data_dir))
            elif "Permission denied" in str(e):
                raise PermissionError("create", str(self.data_dir), str(e))
            else:
                raise DirectoryCreationError(str(self.data_dir), str(e))
    
    def _validate_inputs(self, tool_key: str, project_id: str) -> None:
        """Validate tool_key and project_id inputs"""
        if not tool_key or not isinstance(tool_key, str):
            raise ValueError("tool_key must be a non-empty string")
        
        if not project_id or not isinstance(project_id, str):
            raise ValueError("project_id must be a non-empty string")
        
        # Check if tool exists in configuration
        if not self.tool_loader.get_tool_config(tool_key):
            available_tools = self.tool_loader.get_available_tools()
            raise ToolNotFoundError(tool_key, available_tools)
        
        # Validate project_id format (basic validation)
        if not project_id.replace("-", "").replace("_", "").isalnum():
            raise ProjectIdError(project_id, "Project ID can only contain letters, numbers, hyphens, and underscores")
    
    def _get_file_path(self, tool_key: str, project_id: str) -> Path:
        """Get the file path for a tool and project, with validation"""
        self._validate_inputs(tool_key, project_id)
        
        tool_config = self.tool_loader.get_tool_config(tool_key)
        if not tool_config:
            raise ToolNotFoundError(tool_key)
        
        project_dir = self.data_dir / project_id
        return project_dir / tool_config.file
    
    def _ensure_project_directory(self, project_id: str) -> Path:
        """Ensure project directory exists"""
        try:
            project_dir = self.data_dir / project_id
            project_dir.mkdir(exist_ok=True, parents=True)
            return project_dir
        except OSError as e:
            raise handle_file_operation_error("create", str(project_dir), e)
    
    def get_tool_content(self, tool_key: str, project_id: str) -> Optional[str]:
        """Get content for any tool using dynamic configuration with fallback and error handling"""
        try:
            self._validate_inputs(tool_key, project_id)
            
            # Try to get content using tool loader (includes fallback logic)
            content = self.tool_loader.get_file_content(tool_key, project_id, str(self.data_dir))
            
            if content is not None:
                logger.debug(f"Retrieved content for tool '{tool_key}' in project '{project_id}'")
                return content
            
            # If no content found, generate default content
            logger.info(f"No content found for tool '{tool_key}' in project '{project_id}', generating default")
            return self.tool_loader.generate_default_content(tool_key, project_id)
            
        except (ToolNotFoundError, ProjectIdError):
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            logger.error(f"Error retrieving content for tool '{tool_key}' in project '{project_id}': {e}")
            raise StorageError(f"Failed to retrieve content for tool '{tool_key}' in project '{project_id}': {str(e)}")
    
    def save_tool_content(self, tool_key: str, project_id: str, content: str) -> str:
        """Save content for any tool using dynamic configuration with comprehensive error handling"""
        try:
            self._validate_inputs(tool_key, project_id)
            
            if content is None:
                raise ValueError("Content cannot be None")
            
            if not isinstance(content, str):
                raise ValueError("Content must be a string")
            
            # Ensure project directory exists
            self._ensure_project_directory(project_id)
            
            # Get file path
            file_path = self._get_file_path(tool_key, project_id)
            
            # Check available disk space (basic check)
            content_size = len(content.encode('utf-8'))
            try:
                stat = os.statvfs(str(file_path.parent))
                available_space = stat.f_bavail * stat.f_frsize
                if available_space < content_size * 2:  # Require 2x content size as buffer
                    raise DiskSpaceError(
                        str(file_path.parent), 
                        f"{content_size * 2} bytes"
                    )
            except OSError:
                # If we can't check disk space, proceed anyway
                pass
            
            # Write content to file
            try:
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"Saved content for tool '{tool_key}' in project '{project_id}' to {file_path}")
                return content
                
            except OSError as e:
                raise handle_file_operation_error("write", str(file_path), e, project_id)
            
        except (ToolNotFoundError, ProjectIdError, ValueError, DiskSpaceError):
            # Re-raise specific errors as-is
            raise
        except Exception as e:
            logger.error(f"Error saving content for tool '{tool_key}' in project '{project_id}': {e}")
            raise StorageError(f"Failed to save content for tool '{tool_key}' in project '{project_id}': {str(e)}")
    
    def delete_tool_content(self, tool_key: str, project_id: str) -> bool:
        """Delete content for a tool in a specific project"""
        try:
            self._validate_inputs(tool_key, project_id)
            
            file_path = self._get_file_path(tool_key, project_id)
            
            if not file_path.exists():
                logger.warning(f"File not found for deletion: {file_path}")
                return False
            
            try:
                file_path.unlink()
                logger.info(f"Deleted content for tool '{tool_key}' in project '{project_id}'")
                return True
                
            except OSError as e:
                raise handle_file_operation_error("delete", str(file_path), e, project_id)
                
        except (ToolNotFoundError, ProjectIdError):
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            logger.error(f"Error deleting content for tool '{tool_key}' in project '{project_id}': {e}")
            raise StorageError(f"Failed to delete content for tool '{tool_key}' in project '{project_id}': {str(e)}")
    
    def list_projects(self) -> list[str]:
        """List all available projects"""
        try:
            if not self.data_dir.exists():
                return []
            
            projects = []
            for item in self.data_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    projects.append(item.name)
            
            return sorted(projects)
            
        except OSError as e:
            logger.error(f"Error listing projects: {e}")
            raise StorageError(f"Failed to list projects: {str(e)}")
    
    def get_project_tools(self, project_id: str) -> Dict[str, bool]:
        """Get a mapping of tools and whether they exist for a project"""
        try:
            if not project_id or not isinstance(project_id, str):
                raise ProjectIdError(project_id, "Invalid project ID")
            
            project_dir = self.data_dir / project_id
            available_tools = self.tool_loader.get_available_tools()
            tool_status = {}
            
            for tool_key in available_tools:
                tool_config = self.tool_loader.get_tool_config(tool_key)
                if tool_config:
                    file_path = project_dir / tool_config.file
                    tool_status[tool_key] = file_path.exists()
            
            return tool_status
            
        except ProjectIdError:
            raise
        except Exception as e:
            logger.error(f"Error getting project tools for '{project_id}': {e}")
            raise StorageError(f"Failed to get project tools for '{project_id}': {str(e)}")
    
    def validate_content_safety(self, content: str) -> bool:
        """Basic content safety validation"""
        if not content:
            return False
        
        # Check for potentially dangerous content
        dangerous_patterns = [
            '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            'data:text/html', 'file://', '<?php'
        ]
        
        content_lower = content.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                logger.warning(f"Potentially dangerous content detected: {pattern}")
                return False
        
        return True
    

# Global storage instance with lazy initialization
_storage_instance = None

def get_storage():
    """Get storage instance with configured data directory"""
    global _storage_instance
    if _storage_instance is None:
        from app.config import settings
        _storage_instance = MarkdownStorage(settings.data_dir)
    return _storage_instance

# Global storage instance (lazy initialization)
storage = None

def get_global_storage():
    """Get or create global storage instance"""
    global storage
    if storage is None:
        storage = get_storage()
    return storage