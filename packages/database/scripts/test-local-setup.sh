#!/bin/bash

# Test script for local Docker Compose + Liquibase setup
# This script demonstrates the complete workflow for local development

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATABASE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$DATABASE_DIR")")"
INFRA_DIR="$PROJECT_ROOT/infra/database"

echo "=================================="
echo "DrugInsightAI Local Setup Test"
echo "=================================="
echo ""

print_step "1. Checking Docker setup..."
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker daemon is not running"
    exit 1
fi

print_info "✅ Docker is available and running"
echo ""

print_step "2. Checking Docker Compose..."
# Check if docker compose (plugin) or docker-compose (standalone) is available
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
    print_info "✅ Using Docker Compose plugin (docker compose)"
elif command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
    print_info "✅ Using standalone Docker Compose (docker-compose)"
else
    echo "❌ Neither 'docker compose' nor 'docker-compose' is available"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

print_step "3. Starting database services..."
echo "Changing to infra directory: $INFRA_DIR"
cd "$INFRA_DIR"

print_info "Starting PostgreSQL and Redis..."
$DOCKER_COMPOSE_CMD up -d postgres redis

print_info "Waiting for services to be healthy..."
sleep 10

# Verify Docker network was created
if docker network ls --format "table {{.Name}}" | grep -q "druginsightai-network"; then
    print_info "✅ Docker network 'druginsightai-network' is available"
    print_info "Migration script will use host networking for maximum compatibility"
else
    print_info "ℹ️  Docker network 'druginsightai-network' not found (this is normal)"
    print_info "Migration script will use host networking"
fi

# Check if containers are running
if ! docker ps --format "table {{.Names}}" | grep -q "druginsightai-postgres"; then
    echo "❌ PostgreSQL container is not running"
    exit 1
fi

if ! docker ps --format "table {{.Names}}" | grep -q "druginsightai-redis"; then
    echo "❌ Redis container is not running"
    exit 1
fi

print_info "✅ Database services are running"
echo ""

print_step "4. Verifying migration files..."
cd "$DATABASE_DIR"

print_info "Checking migration file structure..."
./scripts/verify-migrations.sh
echo ""

print_step "5. Running database migrations..."
print_info "Running Liquibase migrations using Docker..."
./scripts/migrate.sh status
echo ""
./scripts/migrate.sh update
echo ""

print_step "6. Verifying database setup..."
./scripts/migrate.sh status
echo ""

print_step "7. Testing database connection..."
print_info "Connecting to PostgreSQL to verify tables were created..."

# Test connection using Docker exec
docker exec druginsightai-postgres psql -U druginsightai -d druginsightai -c "
SELECT schemaname, tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
" || {
    echo "❌ Failed to connect to database"
    exit 1
}

echo ""
print_info "✅ Database tables created successfully"
echo ""

print_step "8. Testing sample queries..."
print_info "Querying therapeutic areas..."
docker exec druginsightai-postgres psql -U druginsightai -d druginsightai -c "
SELECT name, code, market_size
FROM therapeutic_areas
LIMIT 5;
"

echo ""
print_info "Querying companies..."
docker exec druginsightai-postgres psql -U druginsightai -d druginsightai -c "
SELECT name, country, market_cap
FROM companies
LIMIT 5;
"

echo ""
print_step "9. Optional: Starting PgAdmin (development profile)..."
print_warning "To start PgAdmin for database management, run:"
print_warning "  cd $INFRA_DIR"
print_warning "  $DOCKER_COMPOSE_CMD --profile dev up -d pgadmin"
print_warning "  Then access: http://localhost:5050"
print_warning "  Email: admin@druginsightai.com"
print_warning "  Password: admin123 (or your PGADMIN_PASSWORD)"

echo ""
echo "=================================="
print_info "✅ Local setup test completed successfully!"
echo "=================================="
echo ""

print_info "Database services are running and ready for development."
print_info "Connection details:"
print_info "  Host: localhost"
print_info "  Port: 5432"
print_info "  Database: druginsightai"
print_info "  Username: druginsightai"
print_info "  Password: changeme"
echo ""

print_info "To stop services:"
print_info "  cd $INFRA_DIR"
print_info "  $DOCKER_COMPOSE_CMD down"
echo ""

print_info "To run migrations in the future:"
print_info "  cd $DATABASE_DIR"
print_info "  ./scripts/migrate.sh update"
