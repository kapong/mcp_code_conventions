from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, Dict, Any
import re

class ProjectOverviewCreate(BaseModel):
    """Schema for creating/updating project overview information"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    business_description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Clear description of what the business/project does",
        examples=["A modern e-commerce platform for selling handmade crafts"]
    )
    target_users: str = Field(
        ...,
        min_length=10,
        max_length=3000,
        description="Detailed description of intended users and their needs",
        examples=["Small business owners looking to sell products online"]
    )
    main_features: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="List of primary features and functionality",
        examples=["User authentication, product catalog, shopping cart, payment processing"]
    )

    @validator('business_description', 'target_users', 'main_features')
    def validate_not_empty_or_placeholder(cls, v, field):
        if not v or v.strip() == '':
            raise ValueError(f'{field.name} cannot be empty')
        
        # Check for common placeholder text
        placeholders = ['TODO', 'TBD', 'PLACEHOLDER', 'FIXME', 'XXX', '*No ', '*Not defined*']
        v_upper = v.upper()
        if any(placeholder in v_upper for placeholder in placeholders):
            raise ValueError(f'{field.name} appears to contain placeholder text')
        
        return v.strip()

class TechnologyStackCreate(BaseModel):
    """Schema for creating/updating technology stack information"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    frontend: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Frontend technologies, frameworks, and libraries",
        examples=["React 18, TypeScript, Tailwind CSS, Vite"]
    )
    backend: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Backend technologies, frameworks, and services",
        examples=["Node.js, Express, TypeScript, Prisma ORM"]
    )
    database: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Database systems, ORMs, and data storage",
        examples=["PostgreSQL, Redis for caching, Prisma migrations"]
    )
    infrastructure: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Deployment, hosting, containers, and cloud services",
        examples=["Docker, AWS ECS, CloudFront CDN, Route53 DNS"]
    )
    tools: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Development tools, testing frameworks, CI/CD",
        examples=["Jest, ESLint, Prettier, GitHub Actions, Sentry"]
    )

    @validator('frontend', 'backend', 'database', 'infrastructure', 'tools')
    def validate_tech_field(cls, v, field):
        if not v or v.strip() == '':
            raise ValueError(f'{field.name} cannot be empty')
        
        # Check for placeholder text
        placeholders = ['TODO', 'TBD', 'PLACEHOLDER', 'FIXME', '*No ', '*Not specified*']
        v_upper = v.upper()
        if any(placeholder in v_upper for placeholder in placeholders):
            raise ValueError(f'{field.name} appears to contain placeholder text')
        
        return v.strip()

class ProjectStructureCreate(BaseModel):
    """Schema for creating/updating project structure information"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    folder_structure: str = Field(
        ...,
        min_length=20,
        max_length=10000,
        description="Detailed folder organization with explanations",
        examples=["src/\n├── components/\n├── pages/\n├── utils/\n└── types/"]
    )
    naming_conventions: str = Field(
        ...,
        min_length=10,
        max_length=3000,
        description="File naming patterns, variable naming styles",
        examples=["PascalCase for components, camelCase for functions, kebab-case for files"]
    )
    architecture_approach: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Architectural patterns and design principles",
        examples=["Clean Architecture, SOLID principles, dependency injection"]
    )

    @validator('folder_structure', 'naming_conventions', 'architecture_approach')
    def validate_structure_field(cls, v, field):
        if not v or v.strip() == '':
            raise ValueError(f'{field.name} cannot be empty')
        
        # Check for placeholder text
        placeholders = ['TODO', 'TBD', 'PLACEHOLDER', 'FIXME', '*No ', '*Not defined*']
        v_upper = v.upper()
        if any(placeholder in v_upper for placeholder in placeholders):
            raise ValueError(f'{field.name} appears to contain placeholder text')
        
        return v.strip()

class ConsideringCreate(BaseModel):
    """Schema for creating/updating project considerations and guidelines"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    content: str = Field(
        ...,
        min_length=50,
        max_length=20000,
        description="Important considerations, best practices, and guidance",
        examples=["## Security\n- Always validate input\n- Use HTTPS in production"]
    )

    @validator('content')
    def validate_content(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Content cannot be empty')
        
        # Check for placeholder text
        placeholders = ['TODO', 'TBD', 'PLACEHOLDER', 'FIXME', '*No ', '*Not defined*']
        v_upper = v.upper()
        if any(placeholder in v_upper for placeholder in placeholders):
            raise ValueError('Content appears to contain placeholder text')
        
        return v.strip()

class GenericToolCreate(BaseModel):
    """Generic schema for tools not covered by specific schemas"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    content: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Content for the tool"
    )

    @validator('content')
    def validate_content(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Content cannot be empty')
        return v.strip()

class ProjectIdValidation(BaseModel):
    """Schema for validating project IDs"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    project_id: str = Field(
        default="default",
        min_length=1,
        max_length=100,
        description="Project identifier",
        pattern=r'^[a-zA-Z0-9_-]+$'
    )

    @validator('project_id')
    def validate_project_id(cls, v):
        if not v or v.strip() == '':
            return "default"
        
        # Sanitize project ID
        v = v.strip().lower()
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Project ID can only contain letters, numbers, hyphens, and underscores')
        
        # Prevent reserved names
        reserved = ['admin', 'api', 'root', 'system', 'test', 'null', 'undefined']
        if v in reserved:
            raise ValueError(f'Project ID "{v}" is reserved and cannot be used')
        
        return v