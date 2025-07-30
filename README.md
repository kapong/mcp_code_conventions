# MCP Code Conventions Server

A Model Context Protocol (MCP) server that provides AI agents with structured access to project conventions, technology stacks, and architectural patterns. Ensures consistency across development teams by maintaining project standards in easily accessible markdown files.

## 💡 Inspiration

This project was inspired by the blog post ["โค้ดจาก AI จะไม่หลุด style อีกต่อไป ถ้าทีมมี conventions จาก MCP Server"](https://medium.com/tech-at-tdg/%E0%B9%82%E0%B8%84%E0%B9%89%E0%B8%94%E0%B8%88%E0%B8%B2%E0%B8%81-ai-%E0%B8%88%E0%B8%B0%E0%B9%84%E0%B8%A1%E0%B9%88%E0%B8%AB%E0%B8%A5%E0%B8%B8%E0%B8%94-style-%E0%B8%AD%E0%B8%B5%E0%B8%81%E0%B8%95%E0%B9%88%E0%B8%AD%E0%B9%84%E0%B8%9B-%E0%B8%96%E0%B9%89%E0%B8%B2%E0%B8%97%E0%B8%B5%E0%B8%A1%E0%B8%A1%E0%B8%B5-conventions-%E0%B8%88%E0%B8%B2%E0%B8%81-mcp-server-3a10974eec33) by **Jassadakorn.ket** (Jul 18, 2025) on **tech @TDG**.

### The Problem
AI-generated code often doesn't follow team conventions, coding standards, or project-specific patterns, leading to:
- **Inconsistent Code Style**: AI doesn't know your team's preferred patterns
- **Architecture Mismatches**: Generated code may not align with project structure  
- **Technology Conflicts**: AI might suggest libraries or approaches that don't fit your stack
- **Manual Corrections**: Developers spend time fixing AI-generated code to match standards

### The Solution
This MCP server provides AI agents with direct access to your team's:
- **Project Context**: Business goals, target users, and feature requirements
- **Technology Standards**: Approved frameworks, libraries, and tools
- **Code Organization**: File structure, naming conventions, and architectural patterns

**Result**: AI agents generate code that follows your team's conventions from the start! 🎯

## ⚡ Quick Start

```bash
# Using Docker (Recommended)
docker-compose up -d

# Or run locally
uv pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Access the API at `http://localhost:8000` and docs at `http://localhost:8000/docs`

## 🌟 Features

- **🔧 Dynamic Tool Configuration**: Define tools in `/app/tools.json` for easy customization
- **📄 Markdown Storage**: Human-readable project conventions stored as markdown files
- **🔄 Automatic Fallback**: Projects inherit from default when specific files don't exist
- **🔒 API Key Authentication**: Secure access with Bearer token authentication
- **🐳 Docker Ready**: Self-contained deployment with embedded default data
- **🤖 MCP Protocol**: Direct integration with AI agents via Model Context Protocol
- **🌐 HTTP API**: RESTful endpoints for programmatic access

## 📊 Available Tools

### Project Context Tools
- **Project Overview**: Business description, target users, and main features
- **Technology Stack**: Frontend, backend, database, infrastructure, and development tools  
- **Project Structure**: Folder organization, naming conventions, and architecture patterns

### API Endpoints
```
GET  /{project_id}/project-overview     # Get project overview
POST /{project_id}/project-overview     # Update project overview
GET  /{project_id}/technology-stack     # Get technology stack
POST /{project_id}/technology-stack     # Update technology stack
GET  /{project_id}/project-structure    # Get project structure
POST /{project_id}/project-structure    # Update project structure
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.12+
- Docker & Docker Compose (optional)
- `uv` package manager

### Environment Setup
```bash
# Clone repository
git clone <your-repository-url>
cd mcp_code_conventions

# Copy environment file
cp .env.example .env
# Edit .env with your API key

# Install dependencies
uv pip install -r requirements.txt
```

### Docker Deployment (Recommended)
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Local Development
```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run MCP server directly
python run_mcp_server.py
```

## 🔧 Configuration

### Environment Variables
```bash
API_KEY=your-secret-api-key          # Bearer token for authentication
DATA_DIR=/app/data                   # Directory for markdown files
DEFAULT_PROJECT_ID=default           # Default project identifier
```

### Tool Configuration (`/app/tools.json`)
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
    }
}
```

## 📡 API Usage

### Authentication
All endpoints require Bearer token authentication:
```bash
curl -H "Authorization: Bearer your-secret-api-key" \
     http://localhost:8000/myproject/project-overview
```

### Example API Calls
```bash
# Get project overview
curl -H "Authorization: Bearer your-secret-api-key" \
     http://localhost:8000/myproject/project-overview

# Update technology stack
curl -X POST \
     -H "Authorization: Bearer your-secret-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "data": {
         "frontend": "React 18, TypeScript",
         "backend": "Python FastAPI",
         "database": "PostgreSQL"
       }
     }' \
     http://localhost:8000/myproject/technology-stack
```

## 🤖 AI Agent Integration

### Claude Desktop Configuration
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "code-conventions": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"],
      "env": {
        "MCP_SERVER_URL": "http://localhost:8000/myproject",
        "MCP_API_KEY": "your-secret-api-key"
      }
    }
  }
}
```

### Available MCP Tools
- `get_project_overview` - Understand business context and user needs
- `update_project_overview` - Update project requirements and objectives
- `get_technology_stack` - Check existing technologies and frameworks
- `update_technology_stack` - Add new tools and technologies
- `get_project_structure` - Align with file organization and naming conventions  
- `update_project_structure` - Update architectural patterns

## 📁 Project Structure

```
mcp_code_conventions/
├── app/
│   ├── data/                    # Markdown data storage
│   │   └── default/            # Default project templates
│   │       ├── PROJECT_OVERVIEW.md
│   │       ├── TECHNOLOGY_STACK.md
│   │       └── PROJECT_STRUCTURE.md
│   ├── schemas/                # Pydantic validation schemas
│   ├── tools/                  # API endpoint implementations
│   ├── auth.py                 # Authentication logic
│   ├── config.py               # Configuration settings
│   ├── main.py                 # FastAPI application
│   ├── mcp_server.py           # MCP protocol server
│   ├── storage.py              # File storage operations
│   ├── tool_loader.py          # Dynamic tool configuration
│   └── tools.json              # Tool definitions
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Container configuration
├── requirements.txt            # Python dependencies
└── run_mcp_server.py           # MCP server entry point
```

## 🔄 Multi-Project Support

### Project Inheritance
Projects automatically inherit from the default project when specific files don't exist:

1. **Project-specific file** (`/app/data/myproject/PROJECT_OVERVIEW.md`) - Used if exists
2. **Default fallback** (`/app/data/default/PROJECT_OVERVIEW.md`) - Used as fallback
3. **Generated default** - Created if neither exists

### Managing Multiple Projects
```bash
# Project-specific endpoints
GET /myproject/project-overview    # Uses myproject data or falls back to default
GET /webapp/technology-stack       # Uses webapp data or falls back to default
GET /api/project-structure         # Uses api data or falls back to default

# Default project (inherited by others)
GET /default/project-overview      # Always uses default data
```

## 🛠️ Development

### Adding New Tools
1. Update `/app/tools.json` with new tool definition
2. Create corresponding markdown template in `/app/data/default/`
3. Restart server to load new configuration

### Testing
```bash
# Run with development server
uvicorn app.main:app --reload

# Test API endpoints
curl -H "Authorization: Bearer your-secret-api-key" \
     http://localhost:8000/health
```

## 🐳 Docker Configuration

### Dockerfile Features
- Python 3.12 slim base image
- Uses `uv` for faster package installation
- Embeds default project data in image
- No external volume dependencies
- Runs on port 8000

### Docker Compose Services
- **app**: Main FastAPI application
- **Environment**: API key and data directory configuration
- **No volumes**: Self-contained with embedded data

## 📋 API Reference

### Health Check
- `GET /` - Server status
- `GET /health` - Health check endpoint

### MCP Protocol
- `POST /mcp` - MCP endpoint for default project
- `POST /mcp/{project_id}` - MCP endpoint for specific project

### Tool Endpoints
- `GET /{project_id}/{tool-name}` - Get tool content
- `POST /{project_id}/{tool-name}` - Update tool content
- `GET /tool/{custom-tool}` - Generic tool access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Special thanks to **Jassadakorn.ket** and **tech @TDG** ([Medium](https://medium.com/tech-at-tdg)) for the inspiring blog post (Jul 18, 2025) that identified the core problem this project solves: ensuring AI-generated code follows team conventions and standards.

## 🤖 AI Use Disclaimer

**This project was developed with assistance from AI tools, specifically Claude (Anthropic).** 

### AI Contributions Include:
- **Code Architecture**: System design and implementation patterns
- **Documentation**: README, API documentation, and inline comments  
- **Configuration**: Docker setup, environment configuration, and deployment scripts
- **Testing**: Test scenarios and validation approaches
- **Best Practices**: Security implementations, error handling, and code organization

### Human Oversight:
- **Requirements Definition**: Project goals and specifications were human-defined
- **Code Review**: All AI-generated code has been reviewed and validated
- **Testing**: Manual testing and validation of functionality
- **Deployment**: Production deployment decisions and configurations
- **Maintenance**: Ongoing updates and improvements

### Transparency:
We believe in transparent development practices. This disclaimer ensures users understand the collaborative nature of this project between human developers and AI assistance. The code quality, security, and functionality remain the responsibility of the human maintainers.

### Quality Assurance:
- All code follows established best practices
- Security measures have been implemented and reviewed
- The system has been tested for reliability and performance
- Documentation accurately reflects the implemented functionality

---

For questions, issues, or contributions, please use the GitHub repository's issue tracker.