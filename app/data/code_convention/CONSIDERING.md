# AI Agent Considerations for MCP Code Conventions Server

## Best Practices

### MCP Server Development
- **Follow MCP protocol specifications**: Ensure all tool implementations conform to Model Context Protocol standards
- **Implement proper error handling**: Return appropriate MCP error responses with clear messages
- **Use structured tool definitions**: Define tools in `tools.json` with clear descriptions and file mappings
- **Maintain backwards compatibility**: When updating tools, ensure existing integrations continue to work
- **Document tool usage patterns**: Provide clear examples of when and how to use each tool

### File-Based Storage Management
- **Validate markdown integrity**: Ensure markdown files are well-formed and properly structured
- **Implement atomic file operations**: Use proper file locking and atomic writes to prevent corruption
- **Handle concurrent access**: Multiple AI agents may access the same files simultaneously
- **Maintain file structure consistency**: Keep directory organization predictable and documented
- **Use UTF-8 encoding consistently**: Ensure all text files use UTF-8 to support international characters

### API Design & Authentication
- **Implement proper authentication**: Use Bearer tokens with appropriate validation and error handling
- **Follow RESTful principles**: Use appropriate HTTP methods and status codes
- **Provide consistent response formats**: Standardize JSON responses across all endpoints
- **Implement request validation**: Validate all input parameters and provide clear error messages
- **Support CORS appropriately**: Configure CORS headers for browser-based integrations

### Dynamic Tool Configuration
- **Validate tool definitions**: Ensure `tools.json` has proper schema validation
- **Handle missing files gracefully**: Implement fallback mechanisms when referenced files don't exist
- **Provide tool discovery**: Allow clients to enumerate available tools dynamically
- **Cache tool configurations**: Optimize performance by caching parsed tool definitions
- **Support hot reloading**: Allow tool configuration updates without server restart

## Anti-Patterns to Avoid

### MCP Protocol Anti-Patterns
- **Hardcoded tool definitions**: Don't embed tool definitions in code; use configuration files
- **Inconsistent error responses**: Always use standard MCP error formats and codes
- **Blocking operations**: Avoid synchronous file I/O in request handlers; use async operations
- **Missing tool metadata**: Always provide comprehensive tool descriptions and usage guidance
- **Protocol version conflicts**: Ensure compatibility with target MCP client versions

### Storage Anti-Patterns
- **Direct file manipulation**: Don't bypass the storage abstraction layer for file operations
- **Ignoring file permissions**: Ensure proper read/write permissions for the data directory
- **Unstructured data storage**: Maintain consistent markdown structure across all files
- **Missing backup strategies**: Don't ignore data persistence and backup requirements  
- **Case-sensitive file handling**: Be consistent with file naming across different operating systems

### Security Anti-Patterns
- **Storing secrets in markdown**: Never include API keys or sensitive data in convention files
- **Path traversal vulnerabilities**: Validate all file paths to prevent directory traversal attacks
- **Insufficient access control**: Don't allow unauthenticated access to sensitive project information
- **Logging sensitive data**: Avoid logging authentication tokens or private project details
- **Weak authentication**: Don't use predictable or default API keys in production

## Important Concerns

### Multi-Project Data Integrity
- **Project isolation**: Ensure project data doesn't leak between different project contexts
- **Fallback chain validation**: Verify the default project fallback system works correctly
- **Data consistency**: Maintain referential integrity between related convention files
- **Version control integration**: Consider how convention changes integrate with git workflows
- **Migration strategies**: Plan for schema changes in convention file formats

### Performance & Scalability
- **File system limitations**: Consider performance impact of file-based storage at scale
- **Caching strategies**: Implement appropriate caching for frequently accessed conventions
- **Concurrent request handling**: Ensure the server handles multiple simultaneous requests efficiently
- **Memory usage**: Monitor memory consumption when loading large convention files
- **Response time optimization**: Keep API response times under acceptable thresholds

### Integration & Compatibility
- **MCP client compatibility**: Test with various MCP clients (Claude, other AI systems)
- **HTTP client support**: Ensure REST API works with common HTTP clients and tools
- **Container deployment**: Verify proper operation in Docker/Kubernetes environments
- **Network configuration**: Handle various network setups and proxy configurations
- **Cross-platform compatibility**: Ensure operation across Linux, macOS, and Windows

## Technology-Specific Considerations

### FastAPI Implementation
- **Use async/await consistently**: Leverage FastAPI's async capabilities for I/O operations
- **Implement proper middleware**: Request logging, error handling, and CORS middleware
- **Use Pydantic models**: Define clear request/response models for API validation
- **Handle startup/shutdown events**: Properly initialize and cleanup resources
- **Configure appropriate timeouts**: Set reasonable request timeout values

### Docker & Deployment
- **Use multi-stage builds**: Optimize Docker image size and build times
- **Handle file permissions**: Ensure proper permissions for data directory in containers
- **Environment variable configuration**: Use env vars for all configurable settings
- **Health check implementation**: Provide proper health check endpoints for orchestration
- **Resource limits**: Set appropriate memory and CPU limits for containers

### Python Development
- **Use type hints**: Leverage Python type hints for better code documentation
- **Handle file encoding**: Always specify UTF-8 encoding for file operations
- **Implement proper logging**: Use structured logging with appropriate levels
- **Error handling**: Use specific exception types and provide meaningful error messages
- **Code organization**: Maintain clean separation between MCP, HTTP, and storage layers

## AI Agent Integration Considerations

### Tool Usage Patterns
- **Query conventions before code generation**: Always check project conventions before writing code
- **Use fallback gracefully**: Handle cases where specific project conventions aren't available
- **Cache convention data**: Avoid repeated API calls for the same project information
- **Handle API failures**: Implement proper error handling for network and authentication issues
- **Respect rate limits**: Implement appropriate request throttling if needed

### Context Management
- **Project context switching**: Handle multiple projects in the same session appropriately
- **Convention freshness**: Consider when to refresh cached convention data
- **Tool discovery**: Use available tool enumeration to understand capabilities
- **Error interpretation**: Properly handle and interpret MCP error responses
- **State management**: Maintain appropriate state between tool calls

### Best Practices for AI Agents
- **Read before write**: Always query existing conventions before updating them
- **Validate updates**: Ensure convention updates are well-formed and consistent
- **Use appropriate tools**: Select the right tool for the specific information needed
- **Handle partial information**: Gracefully handle cases where some convention data is missing
- **Provide context**: Include relevant project context when making tool calls