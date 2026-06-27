# Acme Corp Coding Standards

## Version: 2.0
## Last Updated: 2026-04-01
## Status: Active

---

## Overview

This document defines the coding standards and best practices for all software development at Acme Corp. All developers must adhere to these standards to ensure code quality, maintainability, and consistency across projects.

## Language-Specific Standards

### Python Standards

#### Code Style
- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use type hints for all function signatures
- Use docstrings for all public functions and classes

#### Naming Conventions
```python
# Classes: PascalCase
class UserAccount:
    pass

# Functions and variables: snake_case
def calculate_total_cost():
    user_count = 10
    
# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

#### Required Tools
- **Linter**: Ruff or Pylint
- **Formatter**: Black
- **Type Checker**: MyPy
- **Testing**: Pytest (minimum 80% coverage)

### Java Standards

#### Code Style
- Follow Google Java Style Guide
- Use 2 spaces for indentation
- Maximum line length: 100 characters
- Always use braces for control structures
- Use JavaDoc for all public APIs

#### Naming Conventions
```java
// Classes: PascalCase
public class UserAccount {}

// Methods and variables: camelCase
public void calculateTotalCost() {
    int userCount = 10;
}

// Constants: UPPER_SNAKE_CASE
public static final int MAX_RETRY_ATTEMPTS = 3;

// Packages: lowercase
package com.acme.userservice;
```

#### Required Tools
- **Build**: Maven or Gradle
- **Linter**: Checkstyle
- **Testing**: JUnit 5 (minimum 80% coverage)
- **Static Analysis**: SonarQube

### TypeScript/JavaScript Standards

#### Code Style
- Follow Airbnb JavaScript Style Guide
- Use 2 spaces for indentation
- Use semicolons
- Prefer const over let, never use var
- Use arrow functions for callbacks

#### Naming Conventions
```typescript
// Classes and Interfaces: PascalCase
class UserAccount {}
interface IUserService {}

// Functions and variables: camelCase
function calculateTotalCost(): number {
    const userCount = 10;
    return userCount;
}

// Constants: UPPER_SNAKE_CASE
const MAX_RETRY_ATTEMPTS = 3;

// Type aliases: PascalCase
type UserId = string;
```

#### Required Tools
- **Linter**: ESLint
- **Formatter**: Prettier
- **Type Checker**: TypeScript strict mode
- **Testing**: Jest (minimum 80% coverage)

## Architecture Standards

### Microservices Architecture

#### Service Design Principles
1. **Single Responsibility**: Each service should have one clear purpose
2. **Loose Coupling**: Services should be independently deployable
3. **High Cohesion**: Related functionality should be grouped together
4. **API-First**: Design APIs before implementation
5. **Database per Service**: Each service owns its data

#### Communication Patterns
- **Synchronous**: REST APIs with JSON
- **Asynchronous**: Message queues (RabbitMQ or Kafka)
- **Event-Driven**: Publish-subscribe for domain events

#### Service Structure
```
service-name/
├── src/
│   ├── api/          # API endpoints
│   ├── domain/       # Business logic
│   ├── data/         # Data access
│   └── infrastructure/  # External integrations
├── tests/
├── docs/
└── deployment/
```

### RESTful API Standards

#### URL Structure
```
# Resource naming: plural nouns
GET    /api/v1/users
GET    /api/v1/users/{id}
POST   /api/v1/users
PUT    /api/v1/users/{id}
PATCH  /api/v1/users/{id}
DELETE /api/v1/users/{id}

# Nested resources
GET    /api/v1/users/{id}/orders
POST   /api/v1/users/{id}/orders
```

#### HTTP Status Codes
- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server error

#### Response Format
```json
{
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "meta": {
    "timestamp": "2026-04-01T10:00:00Z",
    "version": "1.0"
  }
}
```

#### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  },
  "meta": {
    "timestamp": "2026-04-01T10:00:00Z",
    "request_id": "abc-123"
  }
}
```

## Security Standards

### Authentication & Authorization
- Use OAuth 2.0 with JWT tokens
- Token expiration: 1 hour (access), 7 days (refresh)
- Implement role-based access control (RBAC)
- Use HTTPS for all communications
- Store passwords using bcrypt (cost factor: 12)

### Data Protection
- Encrypt sensitive data at rest (AES-256)
- Encrypt data in transit (TLS 1.3)
- Never log sensitive information (passwords, tokens, PII)
- Implement data masking for logs and monitoring
- Follow GDPR and data privacy regulations

### Input Validation
- Validate all user inputs
- Use parameterized queries (prevent SQL injection)
- Sanitize HTML inputs (prevent XSS)
- Implement rate limiting on APIs
- Use CSRF tokens for state-changing operations

## Testing Standards

### Test Coverage Requirements
- **Unit Tests**: Minimum 80% code coverage
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user workflows
- **Performance Tests**: Load and stress testing

### Test Structure
```python
# Arrange-Act-Assert pattern
def test_calculate_total_cost():
    # Arrange
    items = [10, 20, 30]
    
    # Act
    result = calculate_total_cost(items)
    
    # Assert
    assert result == 60
```

### Test Naming
```python
# Pattern: test_<method>_<scenario>_<expected_result>
def test_create_user_with_valid_data_returns_user():
    pass

def test_create_user_with_invalid_email_raises_validation_error():
    pass
```

## Documentation Standards

### Code Documentation
- All public APIs must have documentation
- Use standard documentation formats (JSDoc, JavaDoc, docstrings)
- Include examples for complex functions
- Document assumptions and limitations
- Keep documentation up-to-date with code changes

### API Documentation
- Use OpenAPI/Swagger for REST APIs
- Include request/response examples
- Document all error codes
- Provide authentication instructions
- Include rate limiting information

### README Requirements
Every repository must include:
1. Project description and purpose
2. Prerequisites and dependencies
3. Installation instructions
4. Configuration guide
5. Usage examples
6. Testing instructions
7. Deployment guide
8. Contributing guidelines
9. License information

## Version Control Standards

### Git Workflow
- Use feature branch workflow
- Branch naming: `feature/`, `bugfix/`, `hotfix/`
- Commit message format: `type(scope): description`
- Squash commits before merging
- Require code review before merge

### Commit Message Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting)
- **refactor**: Code refactoring
- **test**: Test additions or changes
- **chore**: Build process or auxiliary tool changes

### Example Commit Messages
```
feat(auth): add OAuth2 authentication
fix(api): resolve null pointer in user service
docs(readme): update installation instructions
refactor(database): optimize query performance
```

## Code Review Standards

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Error handling is appropriate
- [ ] Code is maintainable and readable

### Review Process
1. Developer creates pull request
2. Automated checks run (linting, tests, security scan)
3. At least 2 reviewers approve
4. Address all review comments
5. Merge to main branch

## Performance Standards

### Response Time Targets
- **API Endpoints**: < 200ms (p95)
- **Database Queries**: < 100ms (p95)
- **Page Load**: < 2 seconds
- **Background Jobs**: Complete within SLA

### Scalability Requirements
- Support horizontal scaling
- Stateless application design
- Use caching where appropriate (Redis)
- Implement connection pooling
- Monitor and optimize database queries

## Monitoring & Logging

### Logging Standards
- Use structured logging (JSON format)
- Include correlation IDs for request tracing
- Log levels: DEBUG, INFO, WARN, ERROR, FATAL
- Never log sensitive information
- Implement log rotation and retention

### Monitoring Requirements
- Application metrics (response time, error rate)
- Infrastructure metrics (CPU, memory, disk)
- Business metrics (user activity, transactions)
- Set up alerts for critical issues
- Implement health check endpoints

## Compliance

### Required Compliance
- **GDPR**: Data privacy and protection
- **SOC 2**: Security and availability
- **ISO 27001**: Information security management
- **OWASP Top 10**: Web application security

### Audit Requirements
- Maintain audit logs for all data access
- Implement data retention policies
- Regular security assessments
- Vulnerability scanning and patching
- Incident response procedures

---

## Enforcement

These standards are mandatory for all projects. Non-compliance may result in:
1. Code review rejection
2. Deployment blocking
3. Technical debt tracking
4. Team escalation

## Updates

This document is reviewed quarterly and updated as needed. Suggestions for improvements should be submitted via the standards review process.

## Contact

For questions or clarifications, contact:
- **Standards Committee**: standards@acme.com
- **Security Team**: security@acme.com
- **Architecture Team**: architecture@acme.com