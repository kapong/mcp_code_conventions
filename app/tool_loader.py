import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class ToolConfig:
    name: str
    description: str
    file: str
    update_fields: Optional[Dict[str, Dict[str, str]]] = None
    content_template: Optional[str] = None
    default_content: Optional[str] = None

class DynamicToolLoader:
    """Loads tool configuration from tools.json and manages file fallback"""
    
    def __init__(self, tools_config_path: str = "app/tools.json"):
        self.tools_config_path = Path(tools_config_path)
        self.tools_config = self._load_tools_config()
    
    def _load_tools_config(self) -> Dict[str, ToolConfig]:
        """Load tool configuration from tools.json"""
        if not self.tools_config_path.exists():
            raise FileNotFoundError(f"Tools configuration file not found: {self.tools_config_path}")
        
        with open(self.tools_config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        tools = {}
        for tool_key, tool_data in config_data.items():
            tools[tool_key] = ToolConfig(
                name=tool_data['name'],
                description=tool_data['description'],
                file=tool_data['file'],
                update_fields=tool_data.get('update_fields'),
                content_template=tool_data.get('content_template'),
                default_content=tool_data.get('default_content')
            )
        
        return tools
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool keys"""
        return list(self.tools_config.keys())
    
    def get_tool_config(self, tool_key: str) -> Optional[ToolConfig]:
        """Get tool configuration for a specific tool"""
        return self.tools_config.get(tool_key)
    
    def get_file_content(self, tool_key: str, project_id: str, data_dir: str = "app/data") -> Optional[str]:
        """
        Get file content for a tool, with fallback to default project
        
        Args:
            tool_key: Tool identifier (e.g., 'project_overview')
            project_id: Project identifier
            data_dir: Base data directory
            
        Returns:
            File content or None if not found
        """
        tool_config = self.get_tool_config(tool_key)
        if not tool_config:
            return None
        
        data_path = Path(data_dir)
        
        # Try project-specific file first
        project_file = data_path / project_id / tool_config.file
        if project_file.exists():
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except IOError:
                pass
        
        # Fallback to default project file
        default_file = data_path / "default" / tool_config.file
        if default_file.exists():
            try:
                with open(default_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except IOError:
                pass
        
        return None
    
    def save_file_content(self, tool_key: str, project_id: str, content: str, data_dir: str = "app/data") -> bool:
        """
        Save file content for a tool
        
        Args:
            tool_key: Tool identifier
            project_id: Project identifier
            content: Content to save
            data_dir: Base data directory
            
        Returns:
            True if saved successfully, False otherwise
        """
        tool_config = self.get_tool_config(tool_key)
        if not tool_config:
            return False
        
        data_path = Path(data_dir)
        project_dir = data_path / project_id
        project_dir.mkdir(exist_ok=True, parents=True)
        
        file_path = project_dir / tool_config.file
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except IOError:
            return False
    
    def get_mcp_tools_schema(self) -> List[Dict[str, Any]]:
        """Generate MCP tool schema from configuration"""
        tools = []
        
        for _, tool_config in self.tools_config.items():
            # Base schema for get operations
            get_tool = {
                "name": tool_config.name,
                "description": tool_config.description,
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier (defaults to 'default')",
                            "default": "default"
                        }
                    }
                }
            }
            tools.append(get_tool)
            
        
        return tools
    
    def _generate_update_schema(self, tool_key: str) -> Dict[str, Any]:
        """Generate update schema for a tool using configuration"""
        tool_config = self.get_tool_config(tool_key)
        
        base_schema = {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Project identifier (defaults to 'default')",
                    "default": "default"
                }
            }
        }
        
        # Add tool-specific fields from configuration
        if tool_config and tool_config.update_fields:
            base_schema["properties"].update(tool_config.update_fields)
        else:
            # Generic content field for tools without specific update fields
            base_schema["properties"]["content"] = {
                "type": "string",
                "description": "Content for this tool"
            }
        
        return base_schema
    
    def generate_content_from_data(self, tool_key: str, project_id: str, data: Dict[str, Any]) -> str:
        """Generate markdown content from tool data using configuration templates"""
        tool_config = self.get_tool_config(tool_key)
        
        if not tool_config:
            return f"# {tool_key.replace('_', ' ').title()} - {project_id}\n\n*Tool configuration not found*"
        
        title = tool_key.replace('_', ' ').title()
        
        # Use content template if available
        if tool_config.content_template:
            template_data = {"title": title, "project_id": project_id}
            template_data.update(data)
            
            try:
                return tool_config.content_template.format(**template_data)
            except KeyError as e:
                return f"# {title} - {project_id}\n\n*Template error: Missing field {e}*"
        
        # Fallback to generic content
        content = f"# {title} - {project_id}\n\n"
        content += data.get('content', '*No content provided*')
        return content
    
    def generate_default_content(self, tool_key: str, project_id: str) -> str:
        """Generate default content when no file exists for a tool"""
        tool_config = self.get_tool_config(tool_key)
        
        if tool_config and tool_config.default_content:
            return tool_config.default_content.format(project_id=project_id)
        
        # Generic fallback
        title = tool_key.replace('_', ' ').title()
        return f"""# {title} - {project_id}

*No content available for this tool*

*Note: Configure this tool in tools.json and add corresponding markdown file*"""

# Global tool loader instance
_tool_loader_instance = None

def get_tool_loader() -> DynamicToolLoader:
    """Get tool loader singleton"""
    global _tool_loader_instance
    if _tool_loader_instance is None:
        _tool_loader_instance = DynamicToolLoader()
    return _tool_loader_instance