# Technology Stack

## Backend Framework
- **FastAPI**: Modern Python web framework for building APIs with automatic OpenAPI documentation
- **Python 3.12+**: Latest Python version with enhanced performance and type hints
- **Pydantic**: Data validation and serialization using Python type hints
- **uvicorn**: Lightning-fast ASGI server for production deployment

## MCP Protocol
- **Python MCP SDK**: Official Model Context Protocol implementation for Python
- **HTTP Transport**: RESTful API endpoints with Bearer token authentication
- **JSON Communication**: Structured data exchange between AI agents and server

## Package Management
- **uv**: Modern Python package installer and resolver (preferred over pip)
- **requirements.txt**: Dependency specification without version pinning for latest versions

## Storage & Data
- **File-based Storage**: Markdown files organized by project in `/app/data/` directory
- **No Database Required**: Simple file system storage for easy maintenance and version control
- **Markdown Format**: Human-readable project documentation format

## Development Tools
- **Docker**: Containerization for consistent deployment environments
- **Docker Compose**: Multi-service orchestration for development and production
- **Hot Reload**: Development server with automatic code reloading

## Configuration Management
- **Environment Variables**: Configuration through .env files
- **JSON Configuration**: Dynamic tool configuration via `/app/tools.json`
- **Default Fallback**: Automatic fallback to default project conventions

## Authentication & Security
- **Bearer Token Authentication**: API key-based security for all endpoints
- **CORS Support**: Cross-origin resource sharing for web client integration
- **Input Validation**: Pydantic models for request/response validation

## API Design
- **RESTful Endpoints**: Standard HTTP methods (GET, POST) for CRUD operations
- **Project-scoped URLs**: URLs include project ID for multi-tenant support
- **Automatic Documentation**: FastAPI generates interactive API documentation

## Deployment
- **Docker Containers**: Production-ready containerized deployment
- **Port Configuration**: Standard port 8000 for HTTP API server
- **Health Checks**: Built-in endpoint monitoring and status reporting
- **Log Management**: Structured logging with Docker Compose log aggregation

## Development Workflow
- **Local Development**: Direct Python execution with uvicorn
- **Container Development**: Docker Compose for full stack testing
- **Hot Reload**: Automatic server restart on code changes
- **No External Dependencies**: Self-contained with embedded default data

## Integration Patterns
- **Claude Desktop**: MCP server configuration for Claude AI integration
- **HTTP Clients**: Direct API access for any HTTP-capable client
- **Curl Compatible**: Standard REST API accessible via command line tools
- **AI Agent SDKs**: Compatible with various AI framework integrations