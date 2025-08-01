# Project Structure

## Folder Structure

```
fullstack-demo/
├── frontend/                    # Vue.js frontend application
│   ├── public/                 # Static assets served directly
│   │   ├── favicon.ico
│   │   └── manifest.json      # PWA manifest
│   ├── src/
│   │   ├── assets/            # Build-time assets (images, fonts)
│   │   ├── components/        # Reusable Vue components
│   │   │   ├── ui/           # Base UI components (buttons, inputs)
│   │   │   ├── forms/        # Form-specific components
│   │   │   └── layout/       # Layout components (header, sidebar)
│   │   ├── composables/       # Vue composition functions
│   │   ├── layouts/           # Page layout templates
│   │   ├── pages/             # Route pages (auto-imported by unplugin-vue-router)
│   │   │   ├── auth/         # Authentication pages
│   │   │   ├── dashboard/    # Dashboard pages
│   │   │   └── profile/      # User profile pages
│   │   ├── plugins/           # Vue plugins and configurations
│   │   ├── services/          # API service layer
│   │   ├── stores/            # Pinia state management
│   │   ├── types/             # TypeScript type definitions
│   │   ├── utils/             # Utility functions
│   │   ├── App.vue           # Root application component
│   │   └── main.ts           # Application entry point
│   ├── tests/
│   │   ├── unit/             # Vitest unit tests
│   │   └── e2e/              # Cypress end-to-end tests
│   ├── index.html            # HTML entry point
│   ├── package.json          # Node.js dependencies
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   ├── tsconfig.json         # TypeScript configuration
│   └── vite.config.ts        # Vite build configuration
│
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   ├── v1/          # API version 1 endpoints
│   │   │   │   ├── auth.py  # Authentication endpoints
│   │   │   │   ├── users.py # User management endpoints
│   │   │   │   └── items.py # Business entity endpoints
│   │   │   └── dependencies.py # FastAPI dependencies
│   │   ├── core/             # Core application logic
│   │   │   ├── config.py    # Application configuration
│   │   │   ├── security.py  # Security utilities (JWT, hashing)
│   │   │   └── database.py  # Database connection setup
│   │   ├── crud/             # Database CRUD operations
│   │   │   ├── base.py      # Base CRUD class
│   │   │   ├── user.py      # User CRUD operations
│   │   │   └── item.py      # Item CRUD operations
│   │   ├── db/               # Database related code
│   │   │   ├── base.py      # SQLAlchemy base class
│   │   │   ├── session.py   # Database session handling
│   │   │   └── init_db.py   # Database initialization
│   │   ├── models/           # SQLAlchemy database models
│   │   │   ├── user.py      # User model
│   │   │   └── item.py      # Item model
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   │   ├── user.py      # User schemas
│   │   │   ├── item.py      # Item schemas
│   │   │   └── token.py     # Authentication token schemas
│   │   ├── services/         # Business logic layer
│   │   │   ├── auth_service.py    # Authentication business logic
│   │   │   ├── user_service.py    # User business logic
│   │   │   └── notification_service.py # Notification handling
│   │   ├── utils/            # Utility functions
│   │   │   ├── deps.py      # Dependency injection utilities
│   │   │   └── security.py  # Security helper functions
│   │   └── main.py          # FastAPI application factory
│   ├── alembic/             # Database migration files
│   │   ├── versions/        # Migration version files
│   │   └── alembic.ini     # Alembic configuration
│   ├── tests/
│   │   ├── api/            # API endpoint tests
│   │   ├── crud/           # CRUD operation tests
│   │   ├── services/       # Service layer tests
│   │   └── conftest.py     # Pytest configuration and fixtures
│   ├── requirements.txt     # Python dependencies
│   └── pyproject.toml      # Python project configuration
│
├── docker/                    # Docker configuration files
│   ├── frontend.Dockerfile   # Frontend container configuration
│   ├── backend.Dockerfile    # Backend container configuration
│   └── nginx.conf           # Nginx configuration
│
├── docker-compose.yml        # Development orchestration
├── docker-compose.prod.yml   # Production orchestration
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore patterns
└── README.md                # Project documentation
```

## Naming Conventions

### Frontend (Vue.js)
- **Components**: Use PascalCase for Vue components (`UserProfile.vue`, `DataTable.vue`)
- **Composables**: Use camelCase with "use" prefix (`useAuth.ts`, `useLocalStorage.ts`)
- **Pages**: Use kebab-case for page files (`user-profile.vue`, `order-history.vue`)
- **Stores**: Use camelCase for store names (`userStore.ts`, `cartStore.ts`)
- **Types**: Use PascalCase for interfaces and types (`User`, `ApiResponse`)
- **Functions**: Use camelCase (`getUserData`, `formatCurrency`)
- **Constants**: Use UPPER_SNAKE_CASE (`API_BASE_URL`, `DEFAULT_LOCALE`)

### Backend (FastAPI)
- **Files**: Use lowercase with underscores (`user_service.py`, `auth_router.py`)
- **Classes**: Use PascalCase (`UserService`, `DatabaseSession`)
- **Functions**: Use snake_case (`get_current_user`, `create_access_token`)
- **Variables**: Use snake_case (`user_data`, `access_token`)
- **Constants**: Use UPPER_SNAKE_CASE (`SECRET_KEY`, `TOKEN_EXPIRE_MINUTES`)
- **Database Models**: Use PascalCase (`User`, `Item`, `UserRole`)
- **API Endpoints**: Use kebab-case (`/api/v1/users`, `/api/v1/auth/login`)

## Architecture Approach

### Clean Architecture Principles
- **Separation of Concerns**: Clear boundaries between presentation, business logic, and data layers
- **Dependency Inversion**: Core business logic doesn't depend on external frameworks
- **Single Responsibility**: Each module has one reason to change
- **Interface Segregation**: Small, focused interfaces rather than large monolithic ones

### Frontend Architecture
- **Component-Based**: Reusable Vue components with clear props and emits
- **Composition API**: Prefer Composition API over Options API for better TypeScript support
- **State Management**: Centralized state with Pinia, local component state for UI-only data
- **Service Layer**: API calls abstracted into service classes with error handling
- **Auto-routing**: File-based routing with unplugin-vue-router for automatic route generation
- **Type Safety**: Full TypeScript integration with strict mode enabled

### Backend Architecture
- **Layered Architecture**: API → Services → CRUD → Models → Database
- **Dependency Injection**: FastAPI's dependency system for loose coupling
- **Repository Pattern**: CRUD operations abstracted from business logic
- **Schema Validation**: Pydantic schemas for request/response validation
- **Async/Await**: Asynchronous operations throughout the application
- **Clean API Design**: RESTful endpoints with consistent naming and status codes

### Database Design
- **Relational Model**: PostgreSQL with proper foreign key relationships
- **Migration Strategy**: Alembic for version-controlled schema changes
- **Connection Pooling**: Async SQLAlchemy engine with optimized connection management
- **Query Optimization**: Proper indexing and query patterns

### Docker Architecture
- **Multi-stage Builds**: Optimized container images with build and runtime stages
- **Service Separation**: Separate containers for frontend, backend, database, and cache
- **Environment-based Configuration**: Different compose files for development and production
- **Health Checks**: Container health monitoring and dependency management
- **Volume Management**: Persistent data storage for database and file uploads