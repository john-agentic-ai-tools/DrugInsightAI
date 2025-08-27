# DrugInsightAI Database Package

This package contains database schema definitions, migrations, and utilities for the DrugInsightAI pharmaceutical data analysis platform.

## Overview

The database is designed to support comprehensive pharmaceutical data analysis including:

- **Drug Information**: Complete drug profiles, regulatory status, patents
- **Clinical Trials**: Trial data, investigators, results, and outcomes
- **Adverse Events**: FAERS data, MedDRA terminology, safety signals
- **Companies**: Pharmaceutical company profiles and partnerships
- **Market Analysis**: Therapeutic areas, trends, and emerging technologies
- **User Management**: Authentication, API keys, and user profiles

## Architecture

- **Database**: PostgreSQL 15+ with extensions for full-text search and JSON operations
- **Migrations**: Liquibase for schema versioning and deployment
- **Local Development**: Docker Compose for easy setup
- **Production**: AWS RDS PostgreSQL with automated backups

## Quick Start

### Local Development Setup

**Automated Test Script (Recommended):**
```bash
cd packages/database
./scripts/test-local-setup.sh
```

**Manual Setup:**

1. **Start the database services:**
   ```bash
   cd infra/database

   # Option 1: Use helper script (handles both docker compose versions)
   ./docker-helper.sh up

   # Option 2: Direct docker compose command
   docker compose up -d  # or docker-compose up -d
   ```

2. **Run database migrations using containerized Liquibase:**
   ```bash
   cd packages/database
   ./scripts/migrate.sh update
   ```

3. **Verify the setup:**
   ```bash
   ./scripts/migrate.sh status
   ```

### Access Database

- **PostgreSQL**: `localhost:5432`
  - Database: `druginsightai`
  - Username: `druginsightai`
  - Password: `changeme` (configurable via `DB_PASSWORD` env var)

- **PgAdmin** (optional, dev profile): `http://localhost:5050`
  - Email: `admin@druginsightai.com`
  - Password: `admin123` (configurable via `PGADMIN_PASSWORD` env var)

## Migration Management

The migration script (`scripts/migrate.sh`) runs Liquibase in Docker containers for consistent, local-machine-independent execution:

### Key Features:
- **Containerized Liquibase**: No need to install Java or Liquibase locally
- **Automatic Network Detection**: Detects Docker Compose setup automatically
- **Smart Connection Handling**: Uses container networks when available
- **Comprehensive Logging**: All output saved to logs for debugging

### Commands:
```bash
# Run all pending migrations
./scripts/migrate.sh update

# Check migration status
./scripts/migrate.sh status

# Validate changelog
./scripts/migrate.sh validate

# Rollback last migration
./scripts/migrate.sh rollback 1

# Rollback to specific date
./scripts/migrate.sh rollback-date 2024-01-01

# Generate database documentation
./scripts/migrate.sh generate-docs

# Show help
./scripts/migrate.sh help
```

### How it Works:
1. **Docker Detection**: Checks if Docker is available and running
2. **Host Network Default**: Uses host networking by default for maximum compatibility
3. **Container Network Option**: Set `USE_CONTAINER_NETWORK=true` to use Docker networks
4. **Container Execution**: Runs `liquibase/liquibase:4.24` with proper volume mounts

### Network Modes:
- **Host Network** (default): `docker run --network host` - most reliable
- **Container Network** (optional): `USE_CONTAINER_NETWORK=true` - requires Docker Compose setup

## Schema Structure

### Core Entities

- **users** - User accounts and profiles
- **companies** - Pharmaceutical companies
- **drugs** - Drug information and metadata
- **clinical_trials** - Clinical trial data
- **adverse_events** - Adverse event reports
- **therapeutic_areas** - Reference data for therapeutic classifications

### Supporting Tables

- **drug_regulatory_status** - Regulatory approval information
- **drug_patents** - Patent data and expiration dates
- **new_drug_entries** - Tracking recent drug additions
- **meddra_terms** - MedDRA terminology reference
- **adverse_event_summaries** - Pre-calculated statistics

### Authentication & Authorization

- **api_keys** - API key management
- **refresh_tokens** - JWT token management
- **user_sessions** - Session tracking

## Environment Configuration

Set environment variables for different deployment contexts:

```bash
# Database connection
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=druginsightai
export DB_USERNAME=druginsightai
export DB_PASSWORD=your-secure-password

# Liquibase contexts
export LIQUIBASE_CONTEXTS=local,dev,staging,prod
```

## Data Types and Enums

The schema uses PostgreSQL enums for standardized values:

- `drug_status`: Drug development stages
- `trial_phase`: Clinical trial phases
- `adverse_event_severity`: Severity classifications
- `approval_authority`: Regulatory authorities (FDA, EMA, etc.)
- `age_group`: Patient age classifications
- `gender`: Gender classifications

## Indexing Strategy

The database includes comprehensive indexing for:

- **Text Search**: Full-text search on drug names and descriptions
- **Filtering**: Common filter columns (status, dates, companies)
- **Analytics**: Performance-optimized queries for reporting
- **Foreign Keys**: All relationship columns indexed

## Security Features

- **Data Encryption**: Passwords and sensitive data hashed
- **Access Control**: Role-based permissions
- **Audit Trails**: Created/updated timestamps on all entities
- **Data Privacy**: De-identified patient data structures

## Production Deployment

For AWS RDS deployment:

1. Create RDS PostgreSQL instance
2. Configure security groups and VPC
3. Set environment variables for RDS endpoint
4. Run migrations with production context:
   ```bash
   LIQUIBASE_CONTEXTS=prod ./scripts/migrate.sh update
   ```

## Monitoring and Maintenance

- **Health Checks**: Built into Docker Compose
- **Performance Monitoring**: Query execution plans and indexes
- **Data Quality**: Constraints and validation rules
- **Backup Strategy**: Automated backups for production

## Contributing

When making schema changes:

1. Create new migration files in `migrations/`
2. Follow naming convention: `XXX-description.xml`
3. Test migrations locally before deployment
4. Update this README with schema changes
5. Run validation: `./scripts/migrate.sh validate`

## Helper Scripts

### Docker Helper (`infra/database/docker-helper.sh`)
Convenient wrapper for Docker Compose operations:

```bash
cd infra/database

# Start all services
./docker-helper.sh up

# Start with PgAdmin (development mode)
./docker-helper.sh dev

# Stop services
./docker-helper.sh down

# Show logs
./docker-helper.sh logs postgres

# Execute commands
./docker-helper.sh exec postgres psql -U druginsightai -d druginsightai
```

## Troubleshooting

### Common Issues

**Docker Compose `distutils` error:**
- Modern Docker Desktop uses `docker compose` (plugin) instead of `docker-compose`
- The scripts automatically detect and use the correct version
- If issues persist, update Docker Desktop or install the Compose plugin

**Connection refused:**
- Ensure PostgreSQL is running: `./docker-helper.sh ps`
- Check port conflicts: `lsof -i :5432`
- Wait for health checks: services have startup delays

**Migration failures:**
- Check Liquibase logs in `infra/database/logs/`
- Validate changelog: `./scripts/migrate.sh validate`
- Check PostgreSQL logs: `./docker-helper.sh logs postgres`

**Permission issues:**
- Ensure database user has required permissions
- Check PostgreSQL user roles and privileges
- Verify container networking if using Docker Compose

**Network issues:**
- **"network druginsightai-network not found"**: The script now uses host networking by default to avoid this issue
- To use container networking, set `USE_CONTAINER_NETWORK=true` and ensure Docker Compose is running
- For custom setups, set `DB_HOST` environment variable
- Check firewall settings for port 5432

**Debug networking issues:**
```bash
# Run network diagnostics
cd packages/database
./scripts/debug-network.sh

# Manual network check
docker network ls | grep druginsightai
docker ps | grep druginsightai
```

For more help, see the project's main documentation or create an issue.
