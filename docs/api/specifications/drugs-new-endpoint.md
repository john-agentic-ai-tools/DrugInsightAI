# Drug API - Get New Drugs Endpoint Specification

## Overview

This document provides a comprehensive specification for the **Get New Drugs** endpoint in the DrugInsightAI API. This endpoint retrieves recently added drug entries from the pharmaceutical data platform, providing insights into new drug developments, formulations, approvals, and other significant drug-related events.

## Endpoint Details

### HTTP Method and Path

```
GET /drugs/new
```

### Summary

Retrieves a paginated list of recently added drug entries within a specified time period.

### Tags

- `Drugs`

## Authentication & Authorization

### Authentication Required

✅ **Yes** - This endpoint requires authentication via one of the following methods:

1. **Bearer Token (JWT)** - Primary method

   ```
   Authorization: Bearer <jwt_token>
   ```

2. **API Key** - Alternative method

   ```
   X-API-Key: <api_key>
   ```

3. **AWS Cognito Token** - If AWS authentication is enabled

   ```
   Authorization: Bearer <cognito_token>
   ```

### Authorization

- **Required Role**: `user` (minimum)
- **Permitted Roles**: `user`, `admin`, `researcher`, `analyst`
- No special role restrictions beyond basic user access

## Request Parameters

### Query Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `page` | integer | No | `1` | `>= 1` | Page number for pagination |
| `limit` | integer | No | `20` | `1 <= x <= 100` | Number of items per page |
| `days_back` | integer | No | `30` | `1 <= x <= 365` | Number of days to look back for new entries |

### Example Request URLs

```http
GET /drugs/new
GET /drugs/new?page=2&limit=10
GET /drugs/new?days_back=7
GET /drugs/new?page=1&limit=50&days_back=14
```

## Response Format

### Success Response (200 OK)

```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "drug": {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "name": "Novadrug XR",
        "generic_name": "novamycin extended-release",
        "status": "approved",
        "therapeutic_area": "oncology",
        "indication": "Advanced non-small cell lung cancer",
        "company": {
          "id": "123e4567-e89b-12d3-a456-426614174002",
          "name": "BioPharma Innovations Inc.",
          "ticker": "BPIN"
        }
      },
      "entry_type": "new_formulation",
      "entry_date": "2024-03-15T10:30:00Z",
      "status": "approved",
      "description": "Extended-release formulation of novamycin for improved patient compliance",
      "changes": {
        "formulation_type": "extended_release",
        "dosing_frequency": "once_daily",
        "bioavailability": "improved"
      },
      "regulatory_info": {
        "fda_approval_date": "2024-03-14",
        "application_number": "NDA-012345",
        "priority_review": false
      },
      "market_impact": {
        "estimated_peak_sales": 500000000,
        "target_launch_date": "2024-06-01",
        "competitive_advantage": "first_extended_release"
      },
      "created_at": "2024-03-15T10:30:00Z",
      "updated_at": "2024-03-15T10:30:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 125,
    "pages": 7,
    "has_next": true,
    "has_previous": false
  },
  "filters_applied": {
    "days_back": 30,
    "entry_date_from": "2024-02-14T00:00:00Z",
    "entry_date_to": "2024-03-15T23:59:59Z"
  },
  "summary": {
    "total_new_entries": 125,
    "by_entry_type": {
      "new_chemical_entity": 45,
      "new_formulation": 32,
      "new_indication": 28,
      "new_generic": 15,
      "new_combination": 5
    },
    "by_status": {
      "approved": 78,
      "pending": 35,
      "investigational": 12
    }
  }
}
```

### Response Schema Details

#### Root Object

| Field | Type | Description |
|-------|------|-------------|
| `data` | Array[NewDrugEntry] | Array of new drug entry objects |
| `meta` | PaginationMeta | Pagination metadata |
| `filters_applied` | FiltersApplied | Summary of filters applied to the query |
| `summary` | Summary | Aggregated statistics for the result set |

#### NewDrugEntry Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier for the new drug entry |
| `drug` | DrugSummary | Yes | Basic drug information |
| `entry_type` | NewDrugEntryTypeEnum | Yes | Type of new drug entry |
| `entry_date` | DateTime (ISO 8601) | Yes | Date when the entry was recorded |
| `status` | string | Yes | Current status of the drug entry |
| `description` | string | No | Human-readable description of the entry |
| `changes` | JSON Object | No | Detailed changes or new features |
| `regulatory_info` | JSON Object | No | Regulatory approval information |
| `market_impact` | JSON Object | No | Market impact assessment |
| `created_at` | DateTime (ISO 8601) | Yes | Record creation timestamp |
| `updated_at` | DateTime (ISO 8601) | Yes | Record last update timestamp |

#### DrugSummary Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Yes | Drug unique identifier |
| `name` | string | Yes | Commercial drug name |
| `generic_name` | string | No | Generic/chemical name |
| `status` | DrugStatusEnum | Yes | Current development status |
| `therapeutic_area` | string | Yes | Primary therapeutic area |
| `indication` | string | No | Primary indication |
| `company` | CompanySummary | Yes | Owning pharmaceutical company |

#### CompanySummary Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Yes | Company unique identifier |
| `name` | string | Yes | Company name |
| `ticker` | string | No | Stock ticker symbol |

#### PaginationMeta Object

| Field | Type | Description |
|-------|------|-------------|
| `page` | integer | Current page number |
| `limit` | integer | Items per page |
| `total` | integer | Total number of items |
| `pages` | integer | Total number of pages |
| `has_next` | boolean | Whether there is a next page |
| `has_previous` | boolean | Whether there is a previous page |

### Enums

#### NewDrugEntryTypeEnum

- `new_chemical_entity` - Completely new chemical compound
- `new_formulation` - New formulation of existing drug
- `new_route` - New route of administration
- `new_dosage` - New dosage strength
- `new_generic` - Generic version of branded drug
- `new_combination` - New combination product
- `new_indication` - New therapeutic indication

#### DrugStatusEnum

- `discovery` - In discovery phase
- `preclinical` - Preclinical development
- `phase_1` - Phase I clinical trials
- `phase_2` - Phase II clinical trials
- `phase_3` - Phase III clinical trials
- `approved` - Regulatory approved
- `withdrawn` - Withdrawn from market
- `discontinued` - Development discontinued

## Error Responses

### Authentication Errors

#### 401 Unauthorized - Missing Token

```json
{
  "error": "AUTHENTICATION_ERROR",
  "message": "No authentication token provided",
  "details": {}
}
```

#### 401 Unauthorized - Invalid Token

```json
{
  "error": "AUTHENTICATION_ERROR",
  "message": "Invalid or expired token",
  "details": {}
}
```

### Validation Errors

#### 422 Unprocessable Entity - Invalid Parameters

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid request data",
  "details": {
    "validation_errors": [
      {
        "loc": ["query", "days_back"],
        "msg": "ensure this value is less than or equal to 365",
        "type": "value_error.number.not_le",
        "ctx": {"limit_value": 365}
      }
    ]
  }
}
```

### Server Errors

#### 500 Internal Server Error

```json
{
  "error": "INTERNAL_ERROR",
  "message": "An internal server error occurred",
  "details": {}
}
```

#### 502 Bad Gateway - External Service Error

```json
{
  "error": "EXTERNAL_SERVICE_ERROR",
  "message": "External service error",
  "details": {
    "service": "drug_database"
  }
}
```

## Business Logic Requirements

### Data Retrieval Logic

1. **Time Window Calculation**:
   - Calculate `entry_date_from` as current date minus `days_back` days
   - Calculate `entry_date_to` as current date
   - Filter `NewDrugEntry` records where `entry_date` falls within this window

2. **Sorting**:
   - Primary sort: `entry_date` (descending - most recent first)
   - Secondary sort: `created_at` (descending)

3. **Pagination**:
   - Apply OFFSET/LIMIT based on `page` and `limit` parameters
   - Calculate total count for pagination metadata

4. **Data Enrichment**:
   - Join with `Drug` table for drug details
   - Join with `Companies` table for company information
   - Include relevant regulatory and market impact data

### Performance Requirements

- **Response Time**: < 500ms for typical requests (p95)
- **Throughput**: Handle 100+ concurrent requests
- **Data Freshness**: Data should be updated within 1 hour of source changes

### Caching Strategy

- **Cache Key**: `new_drugs:{days_back}:{page}:{limit}`
- **TTL**: 15 minutes
- **Cache Invalidation**: On new drug entry creation or updates

## Security Considerations

### Input Validation

- All query parameters are validated against defined constraints
- UUID format validation for any ID parameters
- SQL injection prevention through parameterized queries

### Rate Limiting

- **Authenticated Users**: 1000 requests/hour per user
- **API Keys**: 5000 requests/hour per key
- **Burst Limit**: 10 requests/minute

### Data Protection

- No sensitive financial data exposed in public responses
- Patent information filtered based on user permissions
- Internal company data restricted to authorized users

### Audit Logging

- Log all requests with user ID, timestamp, and parameters
- Track data access patterns for security monitoring
- Maintain audit trail for compliance purposes

## Performance Considerations

### Database Optimization

- **Indexes Required**:
  - `new_drug_entries(entry_date)` - For time range queries
  - `new_drug_entries(entry_type, entry_date)` - For filtered queries
  - `new_drug_entries(status, entry_date)` - For status filtering
  - `drugs(company_id)` - For company joins

### Query Optimization

- Use database connection pooling
- Implement query result caching
- Optimize JOIN operations with proper indexes
- Use pagination to limit memory usage

### Monitoring

- Track response times and error rates
- Monitor database query performance
- Alert on unusual traffic patterns
- Track cache hit/miss rates

## Example Usage Scenarios

### Scenario 1: Recent Weekly Updates

```http
GET /drugs/new?days_back=7&limit=50
```

**Use Case**: Weekly review of new drug developments

### Scenario 2: Monthly Report Generation

```http
GET /drugs/new?days_back=30&page=1&limit=100
```

**Use Case**: Generate monthly pharmaceutical industry report

### Scenario 3: Real-time Monitoring Dashboard

```http
GET /drugs/new?days_back=1&limit=10
```

**Use Case**: Display recent activity on monitoring dashboard

## Integration Notes

### API Client Libraries

- Supports standard HTTP clients
- JSON response format for easy parsing
- RESTful design principles
- OpenAPI 3.0 specification available

### Webhook Integration

- Consider implementing webhooks for real-time new drug notifications
- Could trigger on new entries matching specific criteria

### Data Export

- Support for CSV/Excel export of results
- Bulk data access for authorized research partners

## Testing Considerations

### Unit Tests

- Parameter validation
- Authentication/authorization logic
- Business logic correctness
- Error handling scenarios

### Integration Tests

- Database query correctness
- Response format validation
- Performance benchmarks
- Cache behavior verification

### Load Tests

- Concurrent user scenarios
- Database performance under load
- Cache effectiveness testing
- Rate limiting behavior

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-03-15 | Initial specification |

---

**Document Maintainer**: API Development Team
**Last Updated**: March 15, 2024
**Next Review**: April 15, 2024
