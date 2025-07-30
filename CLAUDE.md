# MCP Code Conventions Server

## Overview
This is an MCP (Model Context Protocol) server that provides tools for AI code agents to access and manage project conventions. The server helps maintain consistency across projects by providing structured access to:

- **Dynamic Tool Configuration**: Tools are defined in `/app/tools.json` for easy customization
- **Project Overview**: Business context, target users, and main features  
- **Technology Stack**: Frontend, backend, database, infrastructure, and development tools
- **Project Structure**: Folder organization, naming conventions, and architecture patterns
- **Automatic Fallback**: If a project doesn't have specific files, it automatically falls back to the default project

## Technology Stack
- **Backend**: Python 3.12+, FastAPI
- **Storage**: File-based markdown storage in `/app/data/`
- **MCP Protocol**: Python MCP SDK
- **Deployment**: Docker, Docker Compose
- **Package Manager**: uv (instead of pip)
- **ASGI Server**: uvicorn

## Setup and Development

### Prerequisites
- Python 3.12 or higher
- Docker and Docker Compose (optional)
- uv package manager

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd mcp_code_conventions

# Install dependencies using uv
uv pip install -r requirements.txt

# Start the services with Docker Compose
docker-compose up -d
```

### Running the MCP Server
```bash
# Run the MCP server directly
python run_mcp_server.py

# Or run the FastAPI server for HTTP access
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### File Storage Setup
The application uses file-based markdown storage. Default project data is included in the Docker image at `/app/data/default/`. Data files are organized by project in `/app/data/{project_id}/` directories. No database setup is required.

## Project Structure
```
mcp_code_conventions/
├── app/
│   ├── data/              # Markdown data storage (in-container)
│   │   └── default/       # Default project data
│   │       ├── PROJECT_OVERVIEW.md
│   │       ├── TECHNOLOGY_STACK.md
│   │       └── PROJECT_STRUCTURE.md
│   ├── models/            # Data models (if needed)
│   ├── schemas/           # Pydantic schemas for API validation
│   ├── tools/             # API endpoints for each tool
│   ├── auth.py            # Authentication logic
│   ├── config.py          # Configuration settings
│   ├── main.py            # FastAPI application
│   ├── mcp_server.py      # MCP protocol implementation
│   └── storage.py         # Markdown file storage operations
├── docker-compose.yml     # Multi-service setup
├── Dockerfile            # Application container
├── requirements.txt      # Python dependencies
├── run_mcp_server.py     # MCP server entry point
└── CLAUDE.md             # This documentation
```

## Dynamic Tool Configuration

Tools are now configured via `/app/tools.json`, making it easy to customize available tools. The configuration includes:

```json
{
    "project_overview": {
        "name": "get_project_overview",
        "description": "Call this tool when you need to understand the business context...",
        "file": "PROJECT_OVERVIEW.md"
    },
    "technology_stack": {
        "name": "get_technology_stack", 
        "description": "Call this tool to get an overview of the technologies...",
        "file": "TECHNOLOGY_STACK.md"
    },
    "project_structure": {
        "name": "get_project_structure",
        "description": "Use this tool to retrieve the overall structure...",
        "file": "PROJECT_STRUCTURE.md"
    }
}
```

## Available Tools

Tools are dynamically loaded from the configuration:

### Configured Tools (from tools.json)
- **get_project_overview**: Retrieves business description, target users, and main features
- **update_project_overview**: Updates project overview information
- **get_technology_stack**: Retrieves technology stack information
- **update_technology_stack**: Updates technology stack details
- **get_project_structure**: Retrieves folder structure, naming conventions, and architecture approach
- **update_project_structure**: Updates project structure guidelines

### Generic Tool Support
- Additional tools can be accessed via `/tool/{tool-name}` endpoints
- Custom tools automatically get fallback support

## Multi-Project Support with Automatic Fallback
Each tool supports a `project_id` parameter that allows managing conventions for multiple projects. **Key feature**: If a project doesn't have a specific file, the system automatically falls back to the default project's file, ensuring all projects have access to baseline conventions.

## API Endpoints
The FastAPI server provides HTTP endpoints for each tool with API key authentication:

### Authentication
All endpoints require Bearer token authentication. Include your API key in the Authorization header:
```
Authorization: Bearer your-secret-api-key
```

### Project Overview
- GET `/{project_id}/project-overview` - Returns markdown-formatted project overview
- GET `/default/project-overview` - Returns default project overview
- POST `/{project_id}/project-overview` - Updates project overview
- POST `/default/project-overview` - Updates default project overview

### Technology Stack
- GET `/{project_id}/technology-stack` - Returns markdown-formatted technology stack
- GET `/default/technology-stack` - Returns default project technology stack
- POST `/{project_id}/technology-stack` - Updates technology stack
- POST `/default/technology-stack` - Updates default project technology stack

### Project Structure
- GET `/{project_id}/project-structure` - Returns markdown-formatted project structure
- GET `/default/project-structure` - Returns default project structure
- POST `/{project_id}/project-structure` - Updates project structure
- POST `/default/project-structure` - Updates default project structure

### Example Usage
```bash
# Get project overview for "myproject"
curl -H "Authorization: Bearer your-secret-api-key" \
     http://localhost:8000/myproject/project-overview

# Update default project overview
curl -X POST \
     -H "Authorization: Bearer your-secret-api-key" \
     -H "Content-Type: application/json" \
     -d '{"business_description": "E-commerce platform", "target_users": "Online shoppers"}' \
     http://localhost:8000/default/project-overview
```

## Configuration
Environment variables:
- `DATA_DIR`: Directory for storing markdown files (default: "/app/data")
- `API_KEY`: Secret API key for authentication (default: "your-secret-api-key")
- `DEFAULT_PROJECT_ID`: Default project identifier (default: "default")

Copy `.env.example` to `.env` and update with your values:
```bash
cp .env.example .env
# Edit .env with your actual values
```

## Development Commands
```bash
# Start FastAPI development server (HTTP API)
uvicorn app.main:app --reload

# Run with Docker Compose
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

## Server Ports
- **Port 8000**: FastAPI HTTP API server (supports both direct HTTP requests and MCP connections)

## Important Notes
- Uses `uv` instead of `pip` for package management
- No version pinning in requirements.txt - uses latest versions
- Docker setup with data included in image (no external volumes)
- Default project markdown files are embedded in the Docker image
- All responses from GET endpoints return markdown-formatted strings
- **API Key Authentication**: All endpoints require Bearer token authentication
- **URL Structure**: Project ID is now a prefix in the URL path (e.g., `/myproject/project-overview`)
- **Easy Project Copying**: Markdown files can be easily copied between projects
- **Dynamic Tool Configuration**: Tools are defined in `/app/tools.json` for easy customization
- **Automatic Fallback**: Projects inherit from default when specific files don't exist
- **Extensible**: Add new tools by updating tools.json and creating corresponding markdown files

## For AI Agents

### HTTP API Integration
When integrating with AI agents via HTTP API, use these URLs with your API key:

**Base URL**: `http://your-server:8000`
**Authentication**: `Authorization: Bearer your-secret-api-key`

**Endpoint Examples for AI Agents**:
- Get project overview: `GET /{project_id}/project-overview`
- Update project overview: `POST /{project_id}/project-overview`
- Get tech stack: `GET /{project_id}/technology-stack`
- Update tech stack: `POST /{project_id}/technology-stack`
- Get project structure: `GET /{project_id}/project-structure`
- Update project structure: `POST /{project_id}/project-structure`

### MCP Server Configuration
For AI agents that support MCP (Model Context Protocol), configure the server to use the HTTP API endpoints:

**Base URL**: `http://your-server:8000`
**Project-specific endpoints**: `/{project_id}/[tool-name]`

**Configuration Examples**:

#### Claude Desktop Configuration
Add to your `claude_desktop_config.json` file at `~/Library/Application Support/Claude/claude_desktop_config.json`:

**Option 1: Using Claude Code CLI (Recommended)**:
```bash
# Add server for specific project
claude mcp add --transport http code-conventions-myproject \
  http://localhost:8000/myproject \
  --header "Authorization: Bearer your-secret-api-key"

# Add server for default project  
claude mcp add --transport http code-conventions-default \
  http://localhost:8000/default \
  --header "Authorization: Bearer your-secret-api-key"
```

**Option 2: Direct JSON Configuration**:
Add to your `claude_desktop_config.json` file:
```json
{
  "mcpServers": {
    "code-conventions-myproject": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-fetch"
      ],
      "env": {
        "MCP_SERVER_URL": "http://localhost:8000/myproject",
        "MCP_API_KEY": "your-secret-api-key"
      }
    }
  }
}
```

**Option 3: Using HTTP Fetch with URL Parameters**:
```json
{
  "mcpServers": {
    "code-conventions-myproject": {
      "command": "curl",
      "args": [
        "-H", "Authorization: Bearer your-secret-api-key",
        "http://localhost:8000/myproject/project-overview"
      ]
    }
  }
}
```

#### Available MCP Tools (per project):
When connected via MCP, these tools are automatically available with detailed usage guidance:

**Project Context Tools:**
- `get_project_overview` - **When to use**: Call when you need to understand the business context, target audience, or core functionality. Essential for ensuring your code serves the intended business purpose and user needs.
- `update_project_overview` - **When to use**: Update when project requirements, target users, or business objectives change.

**Technology Stack Tools:**
- `get_technology_stack` - **When to use**: Call before writing code to understand which frameworks, libraries, and technologies are already in use. Essential for maintaining consistency, avoiding conflicts, and ensuring compatibility.
- `update_technology_stack` - **When to use**: Update when new tools, frameworks, or services are added to the project.

**Code Organization Tools:**
- `get_project_structure` - **When to use**: Call whenever you are generating code and need to align with the project's file organization, naming conventions, or architecture guidelines. Ensures generated code fits cleanly into existing structure.
- `update_project_structure` - **When to use**: Update when file organization, naming conventions, or architectural patterns change.

**Note**: Each MCP connection is automatically scoped to the specified project_id, so all tools operate within that project context. AI agents should proactively use these tools to maintain project consistency and follow established conventions.