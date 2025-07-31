# MCP Code Conventions Server

## Business Description
The MCP Code Conventions Server is a specialized Model Context Protocol (MCP) server designed to help AI code agents maintain consistency and follow established conventions across software projects. It provides structured access to project documentation, coding standards, and architectural guidelines through a standardized API.

## Target Users
- **AI Code Agents**: Primary users that integrate with the MCP server to access project conventions
- **Development Teams**: Teams that want to maintain consistent coding practices across projects
- **DevOps Engineers**: Those managing multiple projects and need centralized convention management
- **Code Review Automation**: Systems that need to validate code against established conventions
- **Documentation Systems**: Tools that generate or maintain project documentation

## Main Features
- **Dynamic Tool Configuration**: Tools are defined in `/app/tools.json` for easy customization without code changes
- **Multi-Project Support**: Manage conventions for multiple projects with automatic fallback to default conventions
- **Structured Convention Access**: Organized access to project overview, technology stack, and project structure guidelines
- **Automatic Fallback System**: Projects without specific conventions automatically inherit from default project
- **HTTP API & MCP Protocol**: Dual interface supporting both direct HTTP access and MCP protocol integration
- **Authentication**: Bearer token authentication for secure access
- **File-Based Storage**: Simple markdown-based storage system for easy maintenance and version control
- **Convention Templates**: Pre-built templates for common project types and structures
- **Real-Time Updates**: Update project conventions through API endpoints with immediate effect

## Core Value Proposition
Enables AI agents to write code that naturally fits into existing projects by providing instant access to:
- Project business context and requirements
- Technology stack and framework choices
- File organization and naming conventions
- Architecture patterns and coding standards
- Best practices and project-specific guidelines

## Use Cases
1. **Code Generation**: AI agents query conventions before generating code to ensure alignment
2. **Code Review**: Automated systems validate code against established project conventions
3. **Project Onboarding**: New team members (human or AI) quickly understand project standards
4. **Cross-Project Consistency**: Maintain similar patterns across multiple related projects
5. **Convention Evolution**: Update and propagate convention changes across projects
6. **Documentation Maintenance**: Keep project documentation current and accessible