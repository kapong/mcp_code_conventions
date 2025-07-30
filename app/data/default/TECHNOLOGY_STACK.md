# Technology Stack - default

## Frontend
- **Web Interface**: None (API-only service)
- **Documentation**: Markdown files for project documentation

## Backend
- **Framework**: FastAPI (Python 3.12+)
- **ASGI Server**: uvicorn
- **Package Manager**: uv (preferred over pip)
- **Protocol Support**: HTTP REST API, Model Context Protocol (MCP)
- **Authentication**: Bearer token API key authentication

## Database
- **Storage**: File-based markdown storage in `/app/data/` directory
- **Format**: Structured markdown files with YAML frontmatter (when needed)
- **Organization**: Project-based directory structure (`/app/data/{project_id}/`)

## Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for development
- **Data Persistence**: In-container storage (no external volumes)
- **Port Configuration**: Port 8000 for HTTP API access

## Tools
- **Development**: Python 3.12+, FastAPI development server
- **Dependency Management**: uv package manager
- **Container Runtime**: Docker and Docker Compose
- **API Testing**: Built-in FastAPI documentation (Swagger/OpenAPI)
- **Protocol Testing**: MCP client tools for testing protocol integration