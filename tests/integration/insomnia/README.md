# DrugInsightAI API Integration Tests - Insomnia Setup

This directory contains Insomnia REST client configurations for integration testing of the DrugInsightAI API.

## 📁 Structure

```
tests/integration/insomnia/
├── README.md                     # This file
├── DrugInsightAI_v1.json         # Main workspace and collection setup
├── environments.json             # Environment configurations
├── auth/
│   └── login_requests.json       # Authentication endpoints
├── health/
│   └── monitoring_requests.json  # Health & monitoring endpoints
├── drugs/
│   └── drug_requests.json        # Drug-related endpoints
├── users/
│   └── user_requests.json        # User management endpoints
├── companies/                    # (Future) Company endpoints
└── test-suites/
    └── smoke_tests.json          # Automated test suites
```

## 🚀 Quick Setup

### 1. Import Workspace
1. Open Insomnia
2. Go to `Application` → `Preferences` → `Data` → `Import Data`
3. Select `DrugInsightAI_v1.json` to create the main workspace

### 2. Import Environments
1. In your workspace, go to environment dropdown (top-left)
2. Click `Manage Environments`
3. Import `environments.json`
4. Select appropriate environment (Development/Staging/Production)

### 3. Import Request Collections
Import each endpoint collection as needed:
- `auth/login_requests.json` - Authentication flows
- `health/monitoring_requests.json` - Health checks
- `drugs/drug_requests.json` - Drug data endpoints
- `users/user_requests.json` - User management
- `test-suites/smoke_tests.json` - Automated tests

## 🌍 Environments

### Development
- **Base URL**: `http://localhost:8000`
- **Purpose**: Local development testing
- **Auth**: Local test credentials

### Staging
- **Base URL**: `https://api-staging.druginsightai.com`
- **Purpose**: Pre-production testing
- **Auth**: Environment variables for security

### Production
- **Base URL**: `https://api.druginsightai.com`
- **Purpose**: Production smoke tests only
- **Auth**: Restricted test account

## 🔐 Authentication Flow

1. **Login**: Use `auth/Login - Success` request
2. **Token Storage**: Response automatically sets `auth_token` and `refresh_token` environment variables
3. **Authenticated Requests**: All protected endpoints use `Bearer {{ _.auth_token }}` header
4. **Token Refresh**: Use `auth/Refresh Token` when access token expires

## 🧪 Test Suites

### Smoke Tests
Basic functionality verification:
- Health check response
- Authentication flow
- Core API endpoints
- Response structure validation

### Running Tests
1. Import `test-suites/smoke_tests.json`
2. Each request includes test assertions in the `Tests` tab
3. Run individual tests or create test sequences
4. View results in the test output panel

## 📊 Request Organization

### Folder Structure
- **🔐 Authentication** - Login, logout, token refresh
- **🏥 Health & Monitoring** - System status, metrics
- **💊 Drugs** - Drug listings, details, analytics
- **👤 Users** - Profile management
- **🏢 Companies** - Pharmaceutical companies
- **🧪 Test Suites** - Automated test workflows

### Naming Convention
- `{Action} - {Scenario}` (e.g., "Login - Success", "Login - Invalid Credentials")
- Emojis for visual organization
- Descriptive names for easy identification

## 🔧 Environment Variables

Common variables available in all environments:

| Variable | Description | Example |
|----------|-------------|---------|
| `base_url` | API base URL | `http://localhost:8000` |
| `api_version` | API version | `v1` |
| `auth_token` | Access token (auto-set) | `eyJ0eXAiOiJKV1Q...` |
| `refresh_token` | Refresh token (auto-set) | `eyJ0eXAiOiJKV1Q...` |
| `user_id` | Current user ID (auto-set) | `123e4567-e89b...` |
| `test_email` | Test user email | `test@druginsightai.com` |
| `test_password` | Test user password | `testpass123` |

## 💡 Tips

### Development Workflow
1. Start with health check to verify API is running
2. Authenticate to get tokens
3. Test core functionality with drug/user endpoints
4. Run smoke tests for comprehensive verification

### Adding New Tests
1. Create requests in appropriate folder
2. Use consistent naming and organization
3. Add test assertions where applicable
4. Update this README with new endpoints

### Security Notes
- Never commit real passwords or tokens
- Use environment variables for sensitive data
- Rotate test credentials regularly
- Limit production testing to non-destructive operations

## 🐛 Troubleshooting

### Common Issues
- **401 Unauthorized**: Check if `auth_token` is set and valid
- **Connection Failed**: Verify `base_url` and API server is running
- **404 Not Found**: Check endpoint URLs match API specification
- **Environment Variables**: Ensure correct environment is selected

### Debug Steps
1. Check environment selection (top-left dropdown)
2. Verify base_url in current environment
3. Test health endpoint first
4. Check authentication token validity
5. Review request headers and body format

---

For API documentation, see: [API Documentation](../../../services/api/README.md)
