#!/bin/bash

# DrugInsightAI Database Migration Script
# This script runs Liquibase migrations for the DrugInsightAI database

set -e

# Default values
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-druginsightai}
DB_USERNAME=${DB_USERNAME:-druginsightai}
DB_PASSWORD=${DB_PASSWORD:-changeme}
LIQUIBASE_CONTEXTS=${LIQUIBASE_CONTEXTS:-local}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATABASE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$(dirname "$DATABASE_DIR")")"

# Liquibase settings
LIQUIBASE_JAR_PATH="${DATABASE_DIR}/lib/liquibase.jar"
POSTGRES_DRIVER_PATH="${DATABASE_DIR}/lib/postgresql.jar"
CHANGELOG_FILE="${DATABASE_DIR}/migrations/db.changelog-master.xml"
LIQUIBASE_PROPERTIES="${DATABASE_DIR}/config/liquibase.properties"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if PostgreSQL is running
check_postgres() {
    print_status "Checking PostgreSQL connection..."

    # First check if we have a local Docker Compose setup
    if [[ "$DB_HOST" == "localhost" || "$DB_HOST" == "127.0.0.1" ]]; then
        if docker ps --format "table {{.Names}}" | grep -q "druginsightai-postgres"; then
            print_status "Found PostgreSQL running in Docker Compose"
            # Use Docker to check connection
            if docker exec druginsightai-postgres pg_isready -U "$DB_USERNAME" -d "$DB_NAME" > /dev/null 2>&1; then
                print_status "PostgreSQL is running and accessible in Docker"
                return 0
            else
                print_error "PostgreSQL container is running but not ready"
                return 1
            fi
        fi
    fi

    # Fallback to direct connection check (requires pg_isready on host)
    if command -v pg_isready >/dev/null 2>&1; then
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USERNAME" > /dev/null 2>&1; then
            print_status "PostgreSQL is running and accessible"
            return 0
        else
            print_error "Cannot connect to PostgreSQL at $DB_HOST:$DB_PORT"
            print_error "Make sure PostgreSQL is running and accessible"
            return 1
        fi
    else
        print_warning "pg_isready not found, skipping connection check"
        print_warning "Will attempt to connect during migration"
        return 0
    fi
}

# Function to run Liquibase command
run_liquibase() {
    local command="$1"
    local additional_args="${2:-}"

    print_status "Running Liquibase $command using Docker..."

    # Check if Docker is available
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed or not in PATH"
        print_error "Please install Docker to run database migrations"
        exit 1
    fi

    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running"
        print_error "Please start Docker and try again"
        exit 1
    fi

    # Determine network mode and host based on setup
    local network_mode="host"
    local db_host="$DB_HOST"

    # Always use host network by default for maximum compatibility
    # This avoids Docker network issues while still allowing container-to-container communication
    network_mode="host"

    # Only try to use container network if explicitly requested and everything is properly set up
    if [[ "${USE_CONTAINER_NETWORK:-}" == "true" ]]; then
        # Check if we're connecting to Docker Compose services
        if [[ "$DB_HOST" == "localhost" || "$DB_HOST" == "127.0.0.1" ]]; then
            # Check if druginsightai-postgres container is running
            if docker ps --format "table {{.Names}}" | grep -q "druginsightai-postgres"; then
                # Check if the network exists
                if docker network ls --format "table {{.Name}}" | grep -q "druginsightai-network"; then
                    print_status "Using container network (explicitly requested)"
                    network_mode="druginsightai-network"
                    db_host="druginsightai-postgres"
                else
                    print_warning "Container network requested but not available, using host network"
                    network_mode="host"
                    db_host="localhost"
                fi
            else
                print_warning "Container network requested but postgres container not running, using host network"
                network_mode="host"
            fi
        else
            # For remote databases
            network_mode="bridge"
        fi
    fi

    # Set final db_host if not already set
    if [[ -z "${db_host:-}" ]]; then
        db_host="$DB_HOST"
    fi

    # Create logs directory if it doesn't exist
    mkdir -p "${DATABASE_DIR}/../logs"

    print_status "Using Docker network mode: $network_mode"
    print_status "Connecting to database: ${db_host}:${DB_PORT}/${DB_NAME}"

    # Debug: Show what we're about to mount
    print_status "Volume mappings:"
    print_status "  Host migrations: ${DATABASE_DIR}/migrations"
    print_status "  Container migrations: /liquibase/changelog"

    # Verify the master changelog file exists on the host
    if [[ ! -f "${DATABASE_DIR}/migrations/db.changelog-master.xml" ]]; then
        print_error "Master changelog not found: ${DATABASE_DIR}/migrations/db.changelog-master.xml"
        exit 1
    fi

    print_status "Master changelog found on host: ${DATABASE_DIR}/migrations/db.changelog-master.xml"

    # Test Docker volume mapping first
    print_status "Testing Docker volume mapping..."
    docker run --rm \
        -v "${DATABASE_DIR}/migrations:/liquibase/changelog" \
        alpine:latest \
        sh -c "echo 'Files in /liquibase/changelog:'; ls -la /liquibase/changelog/; echo 'Master file exists:'; ls -la /liquibase/changelog/db.changelog-master.xml"

    # Run Liquibase in Docker container
    print_status "Running Liquibase command: $command"
    docker run --rm \
        --network "$network_mode" \
        -v "${DATABASE_DIR}/migrations:/liquibase/changelog" \
        -v "${DATABASE_DIR}/config:/liquibase/config" \
        -v "${DATABASE_DIR}/../logs:/liquibase/logs" \
        -w /liquibase/changelog \
        -e LIQUIBASE_COMMAND_URL="jdbc:postgresql://${db_host}:${DB_PORT}/${DB_NAME}" \
        -e LIQUIBASE_COMMAND_USERNAME="$DB_USERNAME" \
        -e LIQUIBASE_COMMAND_PASSWORD="$DB_PASSWORD" \
        -e LIQUIBASE_COMMAND_CHANGELOG_FILE="db.changelog-master.xml" \
        -e LIQUIBASE_LOG_LEVEL=INFO \
        liquibase/liquibase:4.24 \
        --contexts="$LIQUIBASE_CONTEXTS" \
        $command $additional_args

    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        print_status "Liquibase $command completed successfully"
    else
        print_error "Liquibase $command failed with exit code $exit_code"
        print_error "Check the logs in ${DATABASE_DIR}/../logs/ for more details"
        exit $exit_code
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  update              Run all pending migrations"
    echo "  status              Show migration status"
    echo "  validate            Validate changelog"
    echo "  rollback COUNT      Rollback COUNT number of changesets"
    echo "  rollback-date DATE  Rollback to specific date (YYYY-MM-DD)"
    echo "  generate-docs       Generate database documentation"
    echo "  drop-all           Drop all database objects (DANGEROUS!)"
    echo ""
    echo "Environment Variables:"
    echo "  DB_HOST               Database host (default: localhost)"
    echo "  DB_PORT               Database port (default: 5432)"
    echo "  DB_NAME               Database name (default: druginsightai)"
    echo "  DB_USERNAME           Database username (default: druginsightai)"
    echo "  DB_PASSWORD           Database password (default: changeme)"
    echo "  LIQUIBASE_CONTEXTS    Liquibase contexts (default: local)"
    echo "  USE_CONTAINER_NETWORK Use Docker container network (default: false)"
    echo ""
    echo "Examples:"
    echo "  $0 update                              # Run all pending migrations"
    echo "  $0 status                              # Show migration status"
    echo "  $0 rollback 1                          # Rollback last migration"
    echo "  LIQUIBASE_CONTEXTS=dev $0 update       # Run with dev context"
    echo "  USE_CONTAINER_NETWORK=true $0 update   # Use Docker container network"
}

# Main script logic
main() {
    local command="${1:-}"

    case "$command" in
        "update")
            check_postgres || exit 1
            run_liquibase "update"
            print_status "Migration completed successfully!"
            ;;
        "status")
            check_postgres || exit 1
            run_liquibase "status" "--verbose"
            ;;
        "validate")
            run_liquibase "validate"
            print_status "Changelog validation completed!"
            ;;
        "rollback")
            local count="${2:-}"
            if [[ -z "$count" ]]; then
                print_error "Please specify the number of changesets to rollback"
                show_usage
                exit 1
            fi
            check_postgres || exit 1
            run_liquibase "rollbackCount" "$count"
            print_status "Rollback completed!"
            ;;
        "rollback-date")
            local date="${2:-}"
            if [[ -z "$date" ]]; then
                print_error "Please specify the date (YYYY-MM-DD) to rollback to"
                show_usage
                exit 1
            fi
            check_postgres || exit 1
            run_liquibase "rollbackToDate" "$date"
            print_status "Rollback to date completed!"
            ;;
        "generate-docs")
            run_liquibase "dbDoc" "${DATABASE_DIR}/docs"
            print_status "Database documentation generated!"
            ;;
        "drop-all")
            print_warning "This will drop ALL database objects!"
            read -p "Are you sure? (type 'yes' to confirm): " confirm
            if [[ "$confirm" == "yes" ]]; then
                check_postgres || exit 1
                run_liquibase "dropAll"
                print_status "All database objects dropped!"
            else
                print_status "Operation cancelled"
            fi
            ;;
        "help" | "--help" | "-h" | "")
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
