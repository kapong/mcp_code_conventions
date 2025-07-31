# AI Agent Considerations

## Best Practices

### Code Quality & Architecture
- **Follow clean architecture principles**: Maintain clear separation between presentation, business logic, and data layers
- **Implement proper error handling**: Use try-catch blocks with meaningful error messages and appropriate HTTP status codes
- **Write self-documenting code**: Use descriptive variable names, function names, and add comments only when necessary
- **Follow SOLID principles**: Single responsibility, open-closed, Liskov substitution, interface segregation, dependency inversion
- **Implement comprehensive validation**: Validate data on both frontend (Vue) and backend (Pydantic) layers
- **Use TypeScript/Python type hints**: Leverage static typing for better code reliability and IDE support

### Security Considerations
- **Always validate and sanitize input**: Never trust user input, validate everything on both client and server
- **Implement proper authentication/authorization**: Use JWT tokens correctly with appropriate expiration and refresh mechanisms
- **Follow security headers best practices**: Implement CORS, CSP, HSTS, and other security headers
- **Protect against common vulnerabilities**: SQL injection, XSS, CSRF, and other OWASP Top 10 threats
- **Handle sensitive data carefully**: Never log passwords, tokens, or PII; use environment variables for secrets
- **Implement rate limiting**: Protect APIs from abuse with appropriate rate limiting strategies

### Performance & Scalability
- **Optimize database queries**: Use appropriate indexes, avoid N+1 queries, implement pagination
- **Implement caching strategies**: Use Redis for session storage and frequently accessed data
- **Optimize frontend bundle size**: Code splitting, lazy loading, and tree shaking for Vue.js components
- **Use connection pooling**: Efficient database connection management with proper pool sizing
- **Implement proper logging**: Structured logging with appropriate levels (DEBUG, INFO, WARN, ERROR)

## Anti-Patterns to Avoid

### Code Structure Anti-Patterns
- **God objects/functions**: Avoid creating overly complex classes or functions that do too much
- **Copy-paste programming**: Don't duplicate code; extract common functionality into reusable modules
- **Magic numbers/strings**: Use constants or configuration files instead of hardcoded values
- **Tight coupling**: Avoid direct dependencies between unrelated modules; use dependency injection
- **Inconsistent naming conventions**: Stick to established naming patterns throughout the codebase

### Security Anti-Patterns
- **Storing secrets in code**: Never commit API keys, passwords, or tokens to version control
- **Client-side security**: Don't rely solely on frontend validation; always validate on the backend
- **Overprivileged access**: Follow principle of least privilege for database connections and API access
- **Inadequate session management**: Don't use predictable session IDs or inadequate timeout policies
- **Ignoring HTTPS**: Always use secure connections in production environments

### Performance Anti-Patterns
- **Premature optimization**: Don't optimize without measuring; profile first, then optimize bottlenecks
- **Synchronous blocking operations**: Use async/await patterns for I/O operations
- **Memory leaks**: Properly clean up event listeners, timers, and database connections
- **Excessive API calls**: Batch requests where possible and implement proper caching
- **Ignoring database indexing**: Don't forget to add indexes for frequently queried columns

## Important Concerns

### Data Integrity
- **Maintain data consistency**: Use database transactions for multi-step operations
- **Implement proper backup strategies**: Regular automated backups with tested recovery procedures
- **Handle concurrent access**: Use appropriate locking mechanisms to prevent race conditions
- **Validate business rules**: Ensure data modifications follow business logic constraints

### User Experience
- **Provide meaningful feedback**: Clear success/error messages and loading states
- **Implement proper error boundaries**: Graceful degradation when components fail
- **Ensure accessibility**: Follow WCAG guidelines for inclusive user interfaces
- **Optimize for mobile**: Responsive design that works well on all device sizes
- **Implement proper form validation**: Real-time validation with clear error messages

### Maintenance & Operations
- **Write comprehensive tests**: Unit, integration, and end-to-end tests with good coverage
- **Document API changes**: Keep OpenAPI/Swagger documentation up to date
- **Monitor application health**: Implement health checks and monitoring dashboards
- **Plan for deployment**: Use CI/CD pipelines with proper staging environments
- **Version control best practices**: Clear commit messages, feature branches, and code reviews

## Technology-Specific Considerations

### Vue.js Frontend
- **Use composition API**: Prefer composition API over options API for better TypeScript support
- **Implement proper state management**: Use Pinia for complex state management needs
- **Optimize component rendering**: Use v-memo and computed properties appropriately
- **Handle component lifecycle**: Proper cleanup in onUnmounted hook

### FastAPI Backend
- **Use dependency injection**: Leverage FastAPI's dependency system for clean architecture
- **Implement proper middleware**: Request logging, CORS, and error handling middleware
- **Use background tasks**: For operations that don't need immediate response
- **Proper response models**: Use Pydantic models for consistent API responses

### Database (PostgreSQL)
- **Use migrations**: Proper database schema versioning with Alembic
- **Implement connection pooling**: Efficient database connection management
- **Use appropriate data types**: Choose optimal PostgreSQL data types for your use case
- **Plan for scaling**: Consider read replicas and partitioning strategies