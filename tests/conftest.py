import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.tool_loader import DynamicToolLoader
from app.storage import MarkdownStorage


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_tools_config():
    """Sample tools configuration for testing"""
    return {
        "test_tool": {
            "name": "get_test_tool",
            "description": "Test tool for unit testing",
            "file": "TEST_TOOL.md",
            "update_fields": {
                "content": {
                    "type": "string",
                    "description": "Test content"
                }
            },
            "content_template": "# {title} - {project_id}\n\n{content}",
            "default_content": "# Test Tool - {project_id}\n\n*No content available*"
        }
    }


@pytest.fixture
def mock_tool_loader(test_tools_config):
    """Mock DynamicToolLoader with test configuration"""
    loader = Mock(spec=DynamicToolLoader)
    loader.tools_config = {
        key: Mock(
            name=config["name"],
            description=config["description"],
            file=config["file"],
            update_fields=config.get("update_fields"),
            content_template=config.get("content_template"),
            default_content=config.get("default_content")
        )
        for key, config in test_tools_config.items()
    }
    return loader


@pytest.fixture
def test_client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Valid authentication headers"""
    return {"Authorization": f"Bearer {settings.api_key}"}


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing"""
    return """# Test Project Overview - test_project

## Business Description
A test project for unit testing

## Target Users
Test users and developers

## Main Features
- Feature 1
- Feature 2
- Feature 3"""


@pytest.fixture
def setup_test_data(temp_data_dir, sample_markdown_content):
    """Set up test data directory with sample files"""
    # Create default project data
    default_dir = Path(temp_data_dir) / "default"
    default_dir.mkdir(parents=True, exist_ok=True)
    
    (default_dir / "PROJECT_OVERVIEW.md").write_text(sample_markdown_content)
    (default_dir / "TECHNOLOGY_STACK.md").write_text("# Technology Stack\n\nTest content")
    (default_dir / "PROJECT_STRUCTURE.md").write_text("# Project Structure\n\nTest content")
    
    # Create test project data
    test_dir = Path(temp_data_dir) / "test_project"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    (test_dir / "PROJECT_OVERVIEW.md").write_text(sample_markdown_content)
    
    return temp_data_dir


@pytest.fixture(autouse=True)
def mock_settings(temp_data_dir):
    """Mock settings for tests"""
    with patch.object(settings, 'data_dir', temp_data_dir), \
         patch.object(settings, 'api_key', 'test-api-key'), \
         patch.object(settings, 'default_project_id', 'default'):
        yield settings


@pytest.fixture
def sample_technology_stack_content():
    """Sample technology stack content for testing"""
    return """# Technology Stack - test_project

## Frontend
React 18, TypeScript, Tailwind CSS

## Backend
Python 3.12, FastAPI, Pydantic

## Database
PostgreSQL 15, Redis

## Infrastructure
Docker, AWS ECS, CloudWatch

## Tools
pytest, ESLint, Docker Compose"""


@pytest.fixture
def sample_project_structure_content():
    """Sample project structure content for testing"""
    return """# Project Structure - test_project

## Folder Structure
```
src/
  components/
    ui/
    layout/
  pages/
  hooks/
  utils/
tests/
  unit/
  integration/
docs/
```

## Naming Conventions
- Components: PascalCase (UserProfile.tsx)
- Files: camelCase (userService.ts)
- Directories: kebab-case (user-management/)

## Architecture Approach
Clean Architecture with separation of concerns:
- Presentation Layer (React components)
- Business Logic Layer (custom hooks)
- Data Access Layer (API services)"""


@pytest.fixture
def sample_considering_content():
    """Sample considering content for testing"""
    return """# Important Considerations - test_project

## Security Best Practices
- Always validate input data
- Use environment variables for secrets
- Implement proper authentication

## Performance Considerations
- Lazy load components when possible
- Optimize database queries
- Use caching for frequently accessed data

## Code Quality
- Write comprehensive tests
- Follow established coding standards
- Use TypeScript for type safety

## Deployment
- Use CI/CD pipelines
- Monitor application performance
- Maintain proper logging"""


@pytest.fixture
def mock_storage_with_all_content(sample_markdown_content, sample_technology_stack_content, 
                                  sample_project_structure_content, sample_considering_content):
    """Mock storage that returns appropriate content based on tool key"""
    def get_content_by_tool(tool_key, project_id):
        content_map = {
            "project_overview": sample_markdown_content,
            "technology_stack": sample_technology_stack_content,
            "project_structure": sample_project_structure_content,
            "considering": sample_considering_content
        }
        return content_map.get(tool_key, None)
    
    mock_storage = Mock(spec=MarkdownStorage)
    mock_storage.get_tool_content.side_effect = get_content_by_tool
    mock_storage.save_tool_content.return_value = True
    return mock_storage


@pytest.fixture
def complete_tools_config():
    """Complete tools configuration for testing all standard tools"""
    return {
        "project_overview": {
            "name": "get_project_overview",
            "description": "Get project overview information",
            "file": "PROJECT_OVERVIEW.md",
            "update_fields": {
                "business_description": {"type": "string"},
                "target_users": {"type": "string"},
                "main_features": {"type": "string"}
            }
        },
        "technology_stack": {
            "name": "get_technology_stack",
            "description": "Get technology stack information",
            "file": "TECHNOLOGY_STACK.md",
            "update_fields": {
                "frontend": {"type": "string"},
                "backend": {"type": "string"},
                "database": {"type": "string"},
                "infrastructure": {"type": "string"},
                "tools": {"type": "string"}
            }
        },
        "project_structure": {
            "name": "get_project_structure", 
            "description": "Get project structure information",
            "file": "PROJECT_STRUCTURE.md",
            "update_fields": {
                "folder_structure": {"type": "string"},
                "naming_conventions": {"type": "string"},
                "architecture_approach": {"type": "string"}
            }
        },
        "considering": {
            "name": "get_considering",
            "description": "Get important considerations and best practices",
            "file": "CONSIDERING.md",
            "update_fields": {
                "security": {"type": "string"},
                "performance": {"type": "string"},
                "code_quality": {"type": "string"},
                "deployment": {"type": "string"}
            }
        }
    }


@pytest.fixture
def mock_complete_tool_loader(complete_tools_config):
    """Mock DynamicToolLoader with complete tool configuration"""
    loader = Mock(spec=DynamicToolLoader)
    loader.tools_config = {
        key: Mock(
            name=config["name"],
            description=config["description"], 
            file=config["file"],
            update_fields=config.get("update_fields")
        )
        for key, config in complete_tools_config.items()
    }
    
    # Mock schema generation methods
    loader.get_mcp_tools_schema.return_value = [
        {
            "name": config["name"],
            "description": config["description"],
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project identifier",
                        "default": "default"
                    }
                }
            }
        }
        for config in complete_tools_config.values()
    ]
    
    return loader


@pytest.fixture
def invalid_auth_headers():
    """Invalid authentication headers for testing unauthorized access"""
    return {"Authorization": "Bearer invalid-token"}


@pytest.fixture
def missing_auth_headers():
    """No authentication headers for testing unauthorized access"""
    return {}


def create_update_request_data(tool_key: str, **kwargs):
    """Helper function to create update request data for different tools"""
    if tool_key == "project_overview":
        return {
            "data": {
                "business_description": kwargs.get("business_description", "Test business description"),  
                "target_users": kwargs.get("target_users", "Test target users"),
                "main_features": kwargs.get("main_features", "Test main features")
            }
        }
    elif tool_key == "technology_stack":
        return {
            "data": {
                "frontend": kwargs.get("frontend", "React, TypeScript"),
                "backend": kwargs.get("backend", "Python, FastAPI"),
                "database": kwargs.get("database", "PostgreSQL"),
                "infrastructure": kwargs.get("infrastructure", "Docker, AWS"),
                "tools": kwargs.get("tools", "pytest, ESLint")
            }
        }
    elif tool_key == "project_structure":
        return {
            "data": {
                "folder_structure": kwargs.get("folder_structure", "src/\n  components/\n  pages/"),
                "naming_conventions": kwargs.get("naming_conventions", "camelCase for variables"),
                "architecture_approach": kwargs.get("architecture_approach", "Clean architecture")
            }
        }
    elif tool_key == "considering":
        return {
            "data": {
                "security": kwargs.get("security", "Security best practices"),
                "performance": kwargs.get("performance", "Performance considerations"),
                "code_quality": kwargs.get("code_quality", "Code quality standards"),
                "deployment": kwargs.get("deployment", "Deployment guidelines")
            }
        }
    else:
        return {
            "data": kwargs
        }


@pytest.fixture
def create_update_data():
    """Fixture that provides the helper function for creating update data"""
    return create_update_request_data