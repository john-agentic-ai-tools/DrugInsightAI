# DrugInsightAI API Service

A comprehensive REST API service for pharmaceutical data analysis, providing endpoints for drug information, clinical trials, company insights, and market analysis.

## Features

- **🔐 Multi-Auth Support**: AWS Cognito integration with local authentication fallback
- **💊 Comprehensive Drug Data**: Detailed drug information, analytics, and adverse events
- **🧪 Clinical Trial Integration**: Complete clinical trial data and results
- **🏢 Company Intelligence**: Pharmaceutical company insights and pipeline analysis
- **📊 Market Analytics**: Therapeutic area trends and market intelligence
- **🚀 Production Ready**: Docker containerization, health checks, and monitoring
- **🧪 100% Test Coverage**: Comprehensive test suite with pytest

## Quick Start

### Using Docker Compose (Recommended)

1. **Start the services:**
   ```bash
   cd services/api
   docker-compose up -d
   ```

2. **Run database migrations:**
   ```bash
   # The database migrations are handled automatically by the database component
   cd ../../packages/database
   ./scripts/migrate.sh update
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Local Development

1. **Install dependencies:**
   ```bash
   cd services/api
   poetry install
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start PostgreSQL and Redis:**
   ```bash
   cd ../../infra/database
   docker-compose up -d postgres redis
   ```

4. **Run migrations:**
   ```bash
   cd ../../packages/database
   ./scripts/migrate.sh update
   ```

5. **Start the API:**
   ```bash
   cd ../../services/api
   poetry run uvicorn src.main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /auth/login` - User authentication
- `POST /auth/refresh` - Token refresh

### Users
- `GET /users/profile` - Get current user profile
- `PATCH /users/profile` - Update user profile

### Drugs
- `GET /drugs/` - List drugs with filtering and pagination
- `GET /drugs/{drug_id}` - Get detailed drug information
- `GET /drugs/{drug_id}/analytics` - Get drug performance analytics
- `GET /drugs/{drug_id}/adverse-events` - Get adverse event data
- `GET /drugs/new` - Get recently added drugs

### Clinical Trials
- `GET /clinical-trials/` - List clinical trials
- `GET /clinical-trials/{trial_id}` - Get trial details

### Companies
- `GET /companies/` - List pharmaceutical companies
- `GET /companies/{company_id}` - Get company details
- `GET /companies/{company_id}/pipeline` - Get company drug pipeline

### Market Analysis
- `GET /market/therapeutic-areas` - Get therapeutic area market data
- `GET /market/trends` - Get current market trends

### Health & Monitoring
- `GET /health` - Health check endpoint
- `GET /metrics` - API performance metrics

## Authentication

The API supports two authentication methods:

### 1. Local Authentication (Development/Testing)

```bash
# Login with email/password
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "your-password"
     }'

# Use the returned access_token in subsequent requests
curl -H "Authorization: Bearer <access_token>" \
     "http://localhost:8000/drugs/"
```

### 2. AWS Cognito (Production)

Set the following environment variables:
```bash
DRUGINSIGHTAI_ENABLE_AWS_AUTH=true
DRUGINSIGHTAI_AWS_COGNITO_USER_POOL_ID=your-pool-id
DRUGINSIGHTAI_AWS_COGNITO_CLIENT_ID=your-client-id
```

### 3. API Key Authentication

```bash
# Use API key in header
curl -H "X-API-Key: your-api-key" \
     "http://localhost:8000/drugs/"
```

## Configuration

Configuration is handled through environment variables with the `DRUGINSIGHTAI_` prefix. Key settings include:

### Database
```bash
DRUGINSIGHTAI_DATABASE_URL=postgresql://user:pass@host:port/db
DRUGINSIGHTAI_REDIS_URL=redis://host:port/db
```

### Security
```bash
DRUGINSIGHTAI_SECRET_KEY=your-secret-key
DRUGINSIGHTAI_ENABLE_LOCAL_AUTH=true
DRUGINSIGHTAI_ENABLE_AWS_AUTH=false
```

### Rate Limiting
```bash
DRUGINSIGHTAI_RATE_LIMIT_REQUESTS=100
DRUGINSIGHTAI_RATE_LIMIT_WINDOW=60
```

See `.env.example` for a complete list of configuration options.

## Database Models

The API includes comprehensive database models for:

- **Users & Authentication**: User accounts, API keys, sessions, refresh tokens
- **Drugs**: Drug information, regulatory status, patents, new entries, analytics
- **Clinical Trials**: Trial data, investigators, results
- **Companies**: Company information, partnerships
- **Adverse Events**: FAERS data integration with MedDRA terminology
- **Reference Data**: Therapeutic areas, countries, market trends

## Testing

### Run Tests
```bash
# Run all tests with coverage
poetry run pytest

# Run specific test file
poetry run pytest tests/test_health.py

# Run with coverage report
poetry run pytest --cov=src --cov-report=html
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Database and authentication integration
- **API Tests**: End-to-end endpoint testing

### Test Data
The test suite uses factory-boy and faker for generating realistic test data and includes fixtures for:
- Test users with various roles
- Sample drug and company data
- Clinical trial information
- Adverse event data

## Deployment

### Docker Production Build
```bash
docker build -t druginsightai-api .
docker run -p 8000:8000 druginsightai-api
```

### Environment-Specific Configurations

#### Development
- Debug logging enabled
- Auto-reload on code changes
- Local authentication enabled
- Detailed error responses

#### Production
- Structured JSON logging
- AWS Cognito authentication
- Rate limiting enabled
- Security headers
- Health check endpoints

## API Documentation

- **Interactive Docs**: Visit `/docs` for Swagger UI
- **ReDoc**: Visit `/redoc` for ReDoc documentation
- **OpenAPI Spec**: Available at `/openapi.json`

## Monitoring & Health Checks

### Health Endpoint
```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "0.1.0",
  "uptime": 3600,
  "dependencies": {
    "database": "healthy",
    "redis": "healthy",
    "external_apis": "unknown"
  }
}
```

### Metrics Endpoint
```bash
curl http://localhost:8000/metrics
```

Returns performance metrics including request counts, response times, and error rates.

## Security Features

- **JWT Token Authentication**: Secure access token and refresh token flow
- **Password Hashing**: bcrypt with configurable rounds
- **Rate Limiting**: Request throttling per user/IP
- **Input Validation**: Comprehensive Pydantic model validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **CORS Configuration**: Configurable cross-origin request handling
- **Security Headers**: Standard security headers in responses

## Integration with Database Component

The API integrates seamlessly with the database component:

1. **Shared Models**: Uses the same database schema defined in the database package
2. **Migration Management**: Database migrations handled by Liquibase in the database component
3. **Connection Pooling**: Optimized connection management for high performance
4. **Health Monitoring**: Database health checks integrated into API health endpoint

## Performance Considerations

- **Async/Await**: Fully asynchronous request handling
- **Connection Pooling**: Database connection reuse
- **Redis Caching**: Response and session caching
- **Pagination**: Efficient large dataset handling
- **Indexes**: Optimized database queries with proper indexing
- **Background Tasks**: Celery integration for long-running operations

## Contributing

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation for API changes
4. Use type hints throughout
5. Follow the project's coding standards

## Support

For issues and questions:
- Check the health endpoint for system status
- Review logs for detailed error information
- Refer to the OpenAPI documentation for endpoint specifications
