import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from app.exceptions import (
    ToolConfigurationError, FileNotFoundError, ValidationError,
    handle_file_operation_error
)

logger = logging.getLogger(__name__)

@dataclass
class ToolConfig:
    name: str
    description: str
    file: str
    update_fields: Optional[Dict[str, Dict[str, str]]] = None
    content_template: Optional[str] = None
    default_content: Optional[str] = None

class DynamicToolLoader:
    """Loads tool configuration from tools.json with comprehensive validation"""
    
    def __init__(self, tools_config_path: str = "app/tools.json"):
        self.tools_config_path = Path(tools_config_path)
        self.tools_config = self._load_tools_config()
        logger.info(f"Loaded {len(self.tools_config)} tools from {self.tools_config_path}")
    
    def _validate_tool_name(self, tool_name: str, tool_key: str) -> None:
        """Validate tool name format and requirements"""
        if not tool_name or not isinstance(tool_name, str):
            raise ToolConfigurationError(
                tool_key, 
                "Tool name must be a non-empty string", 
                str(self.tools_config_path)
            )
        
        tool_name = tool_name.strip()
        if not tool_name:
            raise ToolConfigurationError(
                tool_key, 
                "Tool name cannot be empty or whitespace only", 
                str(self.tools_config_path)
            )
        
        # Validate naming pattern (should be valid function name)
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', tool_name):
            raise ToolConfigurationError(
                tool_key, 
                f"Tool name '{tool_name}' must start with a letter and contain only letters, numbers, and underscores", 
                str(self.tools_config_path)
            )
        
        # Check for reserved names
        reserved_names = {
            'list_tools', 'call_tool', 'ping', 'init', 'main', 'help',
            'admin', 'root', 'system', 'config', 'settings'
        }
        if tool_name.lower() in reserved_names:
            raise ToolConfigurationError(
                tool_key, 
                f"Tool name '{tool_name}' is reserved and cannot be used", 
                str(self.tools_config_path)
            )
    
    def _validate_description(self, description: str, tool_key: str) -> None:
        """Validate tool description"""
        if not description or not isinstance(description, str):
            raise ToolConfigurationError(
                tool_key, 
                "Tool description must be a non-empty string", 
                str(self.tools_config_path)
            )
        
        description = description.strip()
        if not description:
            raise ToolConfigurationError(
                tool_key, 
                "Tool description cannot be empty or whitespace only", 
                str(self.tools_config_path)
            )
        
        # Minimum length check for meaningful descriptions
        if len(description) < 10:
            raise ToolConfigurationError(
                tool_key, 
                f"Tool description too short (minimum 10 characters): '{description}'", 
                str(self.tools_config_path)
            )
        
        # Maximum length check to prevent extremely long descriptions
        if len(description) > 1000:
            raise ToolConfigurationError(
                tool_key, 
                f"Tool description too long (maximum 1000 characters): {len(description)} characters", 
                str(self.tools_config_path)
            )
    
    def _validate_file_path(self, file_path: str, tool_key: str) -> None:
        """Validate file path format"""
        if not file_path or not isinstance(file_path, str):
            raise ToolConfigurationError(
                tool_key, 
                "File path must be a non-empty string", 
                str(self.tools_config_path)
            )
        
        file_path = file_path.strip()
        if not file_path:
            raise ToolConfigurationError(
                tool_key, 
                "File path cannot be empty or whitespace only", 
                str(self.tools_config_path)
            )
        
        # Validate file extension
        if not file_path.endswith('.md'):
            raise ToolConfigurationError(
                tool_key, 
                f"File path must end with .md extension: '{file_path}'", 
                str(self.tools_config_path)
            )
        
        # Validate path format (no absolute paths, no parent directory references)
        if file_path.startswith('/') or file_path.startswith('\\'):
            raise ToolConfigurationError(
                tool_key, 
                f"File path cannot be absolute: '{file_path}'", 
                str(self.tools_config_path)
            )
        
        if '..' in file_path:
            raise ToolConfigurationError(
                tool_key, 
                f"File path cannot contain parent directory references: '{file_path}'", 
                str(self.tools_config_path)
            )
        
        # Validate filename format
        path_obj = Path(file_path)
        filename = path_obj.name
        if not re.match(r'^[A-Z_][A-Z0-9_]*\.md$', filename):
            raise ToolConfigurationError(
                tool_key, 
                f"Filename must be uppercase with underscores (e.g., PROJECT_OVERVIEW.md): '{filename}'", 
                str(self.tools_config_path)
            )
    
    def _validate_update_fields(self, update_fields: Optional[Dict[str, Dict[str, str]]], tool_key: str) -> None:
        """Validate update fields configuration"""
        if update_fields is None:
            return
        
        if not isinstance(update_fields, dict):
            raise ToolConfigurationError(
                tool_key, 
                "Update fields must be a dictionary", 
                str(self.tools_config_path)
            )
        
        for field_name, field_config in update_fields.items():
            if not isinstance(field_name, str) or not field_name.strip():
                raise ToolConfigurationError(
                    tool_key, 
                    f"Update field name must be a non-empty string: '{field_name}'", 
                    str(self.tools_config_path)
                )
            
            if not isinstance(field_config, dict):
                raise ToolConfigurationError(
                    tool_key, 
                    f"Update field configuration must be a dictionary for field '{field_name}'", 
                    str(self.tools_config_path)
                )
            
            # Validate required field properties
            if 'type' not in field_config:
                raise ToolConfigurationError(
                    tool_key, 
                    f"Update field '{field_name}' must have a 'type' property", 
                    str(self.tools_config_path)
                )
            
            if 'description' not in field_config:
                raise ToolConfigurationError(
                    tool_key, 
                    f"Update field '{field_name}' must have a 'description' property", 
                    str(self.tools_config_path)
                )
            
            # Validate field type
            valid_types = {'string', 'integer', 'number', 'boolean', 'array', 'object'}
            if field_config['type'] not in valid_types:
                raise ToolConfigurationError(
                    tool_key, 
                    f"Invalid field type '{field_config['type']}' for field '{field_name}'. Valid types: {valid_types}", 
                    str(self.tools_config_path)
                )
    
    def _validate_template(self, template: Optional[str], tool_key: str, template_type: str) -> None:
        """Validate content templates"""
        if template is None:
            return
        
        if not isinstance(template, str):
            raise ToolConfigurationError(
                tool_key, 
                f"{template_type} must be a string", 
                str(self.tools_config_path)
            )
        
        template = template.strip()
        if not template:
            raise ToolConfigurationError(
                tool_key, 
                f"{template_type} cannot be empty", 
                str(self.tools_config_path)
            )
        
        # Basic template variable validation
        # Check for balanced braces
        open_braces = template.count('{')
        close_braces = template.count('}')
        if open_braces != close_braces:
            raise ToolConfigurationError(
                tool_key, 
                f"{template_type} has unbalanced template braces", 
                str(self.tools_config_path)
            )
    
    def _load_tools_config(self) -> Dict[str, ToolConfig]:
        """Load and validate tool configuration from tools.json"""
        try:
            if not self.tools_config_path.exists():
                raise FileNotFoundError(
                    str(self.tools_config_path), 
                    "default"  # Using default project_id for this error
                )
            
            # Read and parse JSON
            try:
                with open(self.tools_config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ToolConfigurationError(
                    "config_file", 
                    f"Invalid JSON in tools configuration: {e}", 
                    str(self.tools_config_path)
                )
            except Exception as e:
                raise handle_file_operation_error("read", str(self.tools_config_path), e)
            
            if not isinstance(config_data, dict):
                raise ToolConfigurationError(
                    "config_file", 
                    "Tools configuration must be a JSON object", 
                    str(self.tools_config_path)
                )
            
            if not config_data:
                raise ToolConfigurationError(
                    "config_file", 
                    "Tools configuration cannot be empty", 
                    str(self.tools_config_path)
                )
            
            # Validate and load tools
            tools = {}
            tool_names: Set[str] = set()
            file_paths: Set[str] = set()
            
            for tool_key, tool_data in config_data.items():
                if not isinstance(tool_key, str) or not tool_key.strip():
                    raise ToolConfigurationError(
                        str(tool_key), 
                        "Tool key must be a non-empty string", 
                        str(self.tools_config_path)
                    )
                
                tool_key = tool_key.strip()
                
                # Validate tool key format
                if not re.match(r'^[a-z][a-z0-9_]*$', tool_key):
                    raise ToolConfigurationError(
                        tool_key, 
                        "Tool key must be lowercase with underscores (e.g., project_overview)", 
                        str(self.tools_config_path)
                    )
                
                if not isinstance(tool_data, dict):
                    raise ToolConfigurationError(
                        tool_key, 
                        "Tool configuration must be a dictionary", 
                        str(self.tools_config_path)
                    )
                
                # Validate required fields
                required_fields = ['name', 'description', 'file']
                for field in required_fields:
                    if field not in tool_data:
                        raise ToolConfigurationError(
                            tool_key, 
                            f"Missing required field: '{field}'", 
                            str(self.tools_config_path)
                        )
                
                # Validate individual fields
                self._validate_tool_name(tool_data['name'], tool_key)
                self._validate_description(tool_data['description'], tool_key)
                self._validate_file_path(tool_data['file'], tool_key)
                self._validate_update_fields(tool_data.get('update_fields'), tool_key)
                self._validate_template(tool_data.get('content_template'), tool_key, "Content template")
                self._validate_template(tool_data.get('default_content'), tool_key, "Default content")
                
                # Check for duplicates
                tool_name = tool_data['name']
                if tool_name in tool_names:
                    raise ToolConfigurationError(
                        tool_key, 
                        f"Duplicate tool name: '{tool_name}'", 
                        str(self.tools_config_path)
                    )
                tool_names.add(tool_name)
                
                file_path = tool_data['file']
                if file_path in file_paths:
                    raise ToolConfigurationError(
                        tool_key, 
                        f"Duplicate file path: '{file_path}'", 
                        str(self.tools_config_path)
                    )
                file_paths.add(file_path)
                
                # Create tool config
                tools[tool_key] = ToolConfig(
                    name=tool_data['name'],
                    description=tool_data['description'],
                    file=tool_data['file'],
                    update_fields=tool_data.get('update_fields'),
                    content_template=tool_data.get('content_template'),
                    default_content=tool_data.get('default_content')
                )
            
            logger.info(f"Successfully validated and loaded {len(tools)} tool configurations")
            return tools
            
        except (ToolConfigurationError, FileNotFoundError, ValidationError):
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading tool configuration: {e}", exc_info=True)
            raise ToolConfigurationError(
                "config_file", 
                f"Failed to load tool configuration: {str(e)}", 
                str(self.tools_config_path)
            )
    
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