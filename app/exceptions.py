"""Custom exception classes for MCP Code Conventions Server"""

from typing import Optional, Dict, Any


class MCPConventionsError(Exception):
    """Base exception for MCP Code Conventions Server"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class StorageError(MCPConventionsError):
    """Base exception for storage-related errors"""
    pass


class FileNotFoundError(StorageError):
    """Raised when a requested file is not found"""
    
    def __init__(self, file_path: str, project_id: Optional[str] = None):
        self.file_path = file_path
        self.project_id = project_id
        message = f"File not found: {file_path}"
        if project_id:
            message += f" for project '{project_id}'"
        super().__init__(message, "FILE_NOT_FOUND", {"file_path": file_path, "project_id": project_id})


class FileReadError(StorageError):
    """Raised when file reading fails"""
    
    def __init__(self, file_path: str, reason: str, project_id: Optional[str] = None):
        self.file_path = file_path
        self.project_id = project_id
        self.reason = reason
        message = f"Failed to read file: {file_path} - {reason}"
        if project_id:
            message += f" for project '{project_id}'"
        super().__init__(message, "FILE_READ_ERROR", {
            "file_path": file_path,
            "project_id": project_id,
            "reason": reason
        })


class FileWriteError(StorageError):
    """Raised when file writing fails"""
    
    def __init__(self, file_path: str, reason: str, project_id: Optional[str] = None):
        self.file_path = file_path
        self.project_id = project_id
        self.reason = reason
        message = f"Failed to write file: {file_path} - {reason}"
        if project_id:
            message += f" for project '{project_id}'"
        super().__init__(message, "FILE_WRITE_ERROR", {
            "file_path": file_path,
            "project_id": project_id,
            "reason": reason
        })


class DirectoryCreationError(StorageError):
    """Raised when directory creation fails"""
    
    def __init__(self, directory_path: str, reason: str):
        self.directory_path = directory_path
        self.reason = reason
        message = f"Failed to create directory: {directory_path} - {reason}"
        super().__init__(message, "DIRECTORY_CREATION_ERROR", {
            "directory_path": directory_path,
            "reason": reason
        })


class ValidationError(MCPConventionsError):
    """Base exception for validation errors"""
    pass


class ToolConfigurationError(ValidationError):
    """Raised when tool configuration is invalid"""
    
    def __init__(self, tool_key: str, reason: str, config_path: Optional[str] = None):
        self.tool_key = tool_key
        self.reason = reason
        self.config_path = config_path
        message = f"Invalid tool configuration for '{tool_key}': {reason}"
        if config_path:
            message += f" in {config_path}"
        super().__init__(message, "TOOL_CONFIG_ERROR", {
            "tool_key": tool_key,
            "reason": reason,
            "config_path": config_path
        })


class ProjectIdError(ValidationError):
    """Raised when project ID is invalid"""
    
    def __init__(self, project_id: str, reason: str):
        self.project_id = project_id
        self.reason = reason
        message = f"Invalid project ID '{project_id}': {reason}"
        super().__init__(message, "PROJECT_ID_ERROR", {
            "project_id": project_id,
            "reason": reason
        })


class ToolNotFoundError(MCPConventionsError):
    """Raised when a requested tool is not found"""
    
    def __init__(self, tool_key: str, available_tools: Optional[list] = None):
        self.tool_key = tool_key
        self.available_tools = available_tools or []
        message = f"Tool '{tool_key}' not found"
        if available_tools:
            message += f". Available tools: {', '.join(available_tools)}"
        super().__init__(message, "TOOL_NOT_FOUND", {
            "tool_key": tool_key,
            "available_tools": available_tools
        })


class MCPServerError(MCPConventionsError):
    """Raised for MCP server-specific errors"""
    pass


class ToolExecutionError(MCPServerError):
    """Raised when tool execution fails"""
    
    def __init__(self, tool_name: str, reason: str, arguments: Optional[Dict[str, Any]] = None):
        self.tool_name = tool_name
        self.reason = reason
        self.arguments = arguments or {}
        message = f"Tool execution failed for '{tool_name}': {reason}"
        super().__init__(message, "TOOL_EXECUTION_ERROR", {
            "tool_name": tool_name,
            "reason": reason,
            "arguments": arguments
        })


class AuthenticationError(MCPConventionsError):
    """Raised for authentication-related errors"""
    
    def __init__(self, reason: str = "Authentication failed"):
        super().__init__(reason, "AUTHENTICATION_ERROR")


class AuthorizationError(MCPConventionsError):
    """Raised for authorization-related errors"""
    
    def __init__(self, reason: str = "Access denied"):
        super().__init__(reason, "AUTHORIZATION_ERROR")


class ContentValidationError(ValidationError):
    """Raised when content validation fails"""
    
    def __init__(self, field_name: str, reason: str, value: Optional[str] = None):
        self.field_name = field_name
        self.reason = reason
        self.value = value
        message = f"Content validation failed for '{field_name}': {reason}"
        super().__init__(message, "CONTENT_VALIDATION_ERROR", {
            "field_name": field_name,
            "reason": reason,
            "value": value[:100] + "..." if value and len(value) > 100 else value
        })


class PermissionError(StorageError):
    """Raised when file system permissions are insufficient"""
    
    def __init__(self, operation: str, path: str, reason: str):
        self.operation = operation
        self.path = path
        self.reason = reason
        message = f"Permission denied for {operation} operation on '{path}': {reason}"
        super().__init__(message, "PERMISSION_ERROR", {
            "operation": operation,
            "path": path,
            "reason": reason
        })


class DiskSpaceError(StorageError):
    """Raised when disk space is insufficient"""
    
    def __init__(self, path: str, required_space: Optional[str] = None):
        self.path = path
        self.required_space = required_space
        message = f"Insufficient disk space for operation on '{path}'"
        if required_space:
            message += f" (required: {required_space})"
        super().__init__(message, "DISK_SPACE_ERROR", {
            "path": path,
            "required_space": required_space
        })


def handle_file_operation_error(operation: str, file_path: str, error: Exception, project_id: Optional[str] = None) -> MCPConventionsError:
    """Convert generic file operation errors to specific exception types"""
    error_msg = str(error)
    
    if isinstance(error, FileNotFoundError):
        return FileNotFoundError(file_path, project_id)
    elif isinstance(error, PermissionError):
        return PermissionError(operation, file_path, error_msg)
    elif isinstance(error, OSError):
        if "No space left on device" in error_msg:
            return DiskSpaceError(file_path)
        elif "Permission denied" in error_msg:
            return PermissionError(operation, file_path, error_msg)
        elif operation == "read":
            return FileReadError(file_path, error_msg, project_id)
        elif operation in ["write", "create"]:
            return FileWriteError(file_path, error_msg, project_id)
    elif isinstance(error, UnicodeDecodeError):
        return FileReadError(file_path, f"Invalid file encoding: {error}", project_id)
    elif isinstance(error, UnicodeEncodeError):
        return FileWriteError(file_path, f"Encoding error: {error}", project_id)
    
    # Generic fallback
    if operation == "read":
        return FileReadError(file_path, error_msg, project_id)
    elif operation in ["write", "create"]:
        return FileWriteError(file_path, error_msg, project_id)
    else:
        return StorageError(f"File operation '{operation}' failed on '{file_path}': {error_msg}")