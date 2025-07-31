from pathlib import Path
from typing import Optional
from app.tool_loader import get_tool_loader

class MarkdownStorage:
    """Markdown-based storage system for MCP code conventions"""
    
    def __init__(self, data_dir: str = "/app/data", tool_loader=None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self.tool_loader = tool_loader or get_tool_loader()
    
    def get_tool_content(self, tool_key: str, project_id: str) -> Optional[str]:
        """Get content for any tool using dynamic configuration with fallback"""
        return self.tool_loader.get_file_content(tool_key, project_id, str(self.data_dir))
    
    def save_tool_content(self, tool_key: str, project_id: str, content: str) -> str:
        """Save content for any tool using dynamic configuration"""
        success = self.tool_loader.save_file_content(tool_key, project_id, content, str(self.data_dir))
        if success:
            return content
        else:
            raise IOError(f"Failed to save content for tool '{tool_key}' in project '{project_id}'")
    

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