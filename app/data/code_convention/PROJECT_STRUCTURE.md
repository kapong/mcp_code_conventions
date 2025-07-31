# Project Structure

## Root Directory Layout
```
mcp_code_conventions/
├── app/                    # Main application code
├── docker-compose.yml      # Multi-service container orchestration
├── Dockerfile             # Application container definition
├── requirements.txt       # Python dependencies (no version pinning)
├── run_mcp_server.py      # MCP server entry point
├── .env.example           # Environment variable templates
├── .gitignore             # Git ignore patterns
└── CLAUDE.md              # Project documentation and instructions
```

## Application Structure (`/app/`)
```
app/
├── data/                  # Project convention storage
│   ├── default/           # Default project templates
│   │   ├── PROJECT_OVERVIEW.md
│   │   ├── TECHNOLOGY_STACK.md
│   │   └── PROJECT_STRUCTURE.md
│   └── {project_id}/      # Project-specific conventions
├── tools/                 # API endpoint implementations
│   ├── __init__.py
│   ├── project_overview.py
│   ├── technology_stack.py
│   └── project_structure.py
├── schemas/               # Pydantic data models
│   ├── __init__.py
│   └── request_models.py
├── auth.py               # Authentication middleware
├── config.py             # Configuration management
├── main.py               # FastAPI application setup
├── mcp_server.py         # MCP protocol implementation
├── storage.py            # File system operations
└── tools.json            # Dynamic tool configuration
```

## Naming Conventions

### Files and Directories
- **Snake Case**: All Python files use snake_case (e.g., `project_overview.py`)
- **Uppercase**: Configuration and documentation files use UPPERCASE (e.g., `PROJECT_OVERVIEW.md`)
- **Descriptive Names**: File names clearly indicate their purpose and content

### Python Code
- **Classes**: PascalCase (e.g., `ProjectOverview`, `TechnologyStack`)
- **Functions**: snake_case (e.g., `get_project_overview`, `update_technology_stack`)
- **Variables**: snake_case (e.g., `project_id`, `file_path`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `DEFAULT_PROJECT_ID`, `DATA_DIR`)

### API Endpoints
- **URL Pattern**: `/{project_id}/{resource-name}` (kebab-case)
- **HTTP Methods**: Standard REST conventions (GET for read, POST for write)
- **Response Format**: JSON for API, markdown content for tool responses

## Architecture Patterns

### Layered Architecture
1. **API Layer** (`main.py`): FastAPI route definitions and HTTP handling
2. **Service Layer** (`tools/`): Business logic and data processing
3. **Storage Layer** (`storage.py`): File system operations and data persistence
4. **Configuration Layer** (`config.py`, `tools.json`): Settings and tool definitions

### Dependency Injection
- Configuration injected through environment variables
- Tool definitions loaded from external JSON configuration
- Storage layer abstracted for potential future database integration

### Plugin Architecture
- **Dynamic Tool Loading**: Tools defined in `tools.json` are automatically loaded
- **Fallback System**: Projects without specific files inherit from default project
- **Extensible Design**: New tools can be added without code changes

## Data Organization

### Project Data Structure
```
/app/data/
├── default/               # Template project (always present)
│   ├── PROJECT_OVERVIEW.md
│   ├── TECHNOLOGY_STACK.md
│   └── PROJECT_STRUCTURE.md
├── project_a/             # Specific project conventions
│   ├── PROJECT_OVERVIEW.md
│   └── TECHNOLOGY_STACK.md    # PROJECT_STRUCTURE.md falls back to default
└── project_b/             # Another project
    └── PROJECT_OVERVIEW.md    # Other files fall back to default
```

### File Format Standards
- **Markdown Format**: All convention files use standard markdown syntax
- **Structured Headers**: Consistent heading hierarchy (H1 for title, H2 for main sections)
- **Code Blocks**: Use fenced code blocks with language specification
- **Lists**: Use bullet points for features, numbered lists for procedures

## Development Patterns

### Error Handling
- **HTTP Status Codes**: Standard codes (200, 404, 401, 500)
- **Exception Handling**: Try-catch blocks around file operations
- **Graceful Fallback**: Default project data when specific files missing

### Testing Strategy
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints end-to-end
- **Docker Testing**: Validate container behavior

### Configuration Management
- **Environment Variables**: Sensitive data (API keys, paths)
- **JSON Configuration**: Tool definitions and metadata
- **Default Values**: Sensible defaults for all configuration options

## Deployment Structure

### Container Organization
- **Single Container**: All application code in one Docker image
- **Data Inclusion**: Default project data embedded in container
- **Port Exposure**: Standard port 8000 for external access
- **Health Checks**: Built-in endpoint monitoring

### Environment Configuration
- **Development**: Local Python execution with hot reload
- **Production**: Docker container with uvicorn server
- **Testing**: Docker Compose with isolated environment

## Extension Guidelines

### Adding New Tools
1. Define tool in `/app/tools.json`
2. Create corresponding markdown template in `/app/data/default/`
3. Implement API endpoint in `/app/tools/` (if custom logic needed)
4. Update documentation

### Adding New Projects
1. Create directory `/app/data/{project_id}/`
2. Add project-specific markdown files
3. Missing files automatically fall back to default project

### Modifying Existing Tools
1. Update tool description in `/app/tools.json`
2. Modify corresponding markdown templates
3. Test fallback behavior with existing projects