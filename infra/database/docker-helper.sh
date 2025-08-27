#!/bin/bash

# Docker Compose Helper Script
# Automatically detects and uses the correct Docker Compose command

set -e

# Determine Docker Compose command
get_docker_compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        echo "docker-compose"
    else
        echo "❌ Neither 'docker compose' nor 'docker-compose' is available"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  up [services...]        Start services (default: all)"
    echo "  down                    Stop and remove containers"
    echo "  restart [services...]   Restart services"
    echo "  logs [service]          Show logs"
    echo "  ps                      Show running containers"
    echo "  exec <service> <cmd>    Execute command in service"
    echo "  dev                     Start with development profile (includes PgAdmin)"
    echo ""
    echo "Examples:"
    echo "  $0 up                   # Start all services"
    echo "  $0 up postgres redis    # Start only database services"
    echo "  $0 dev                  # Start with PgAdmin"
    echo "  $0 logs postgres        # Show PostgreSQL logs"
    echo "  $0 exec postgres psql -U druginsightai -d druginsightai"
}

# Parse command
case "${1:-}" in
    "up")
        shift
        if [[ $# -eq 0 ]]; then
            echo "Starting all services..."
            $DOCKER_COMPOSE_CMD up -d
        else
            echo "Starting services: $*"
            $DOCKER_COMPOSE_CMD up -d "$@"
        fi
        ;;
    "down")
        echo "Stopping and removing containers..."
        $DOCKER_COMPOSE_CMD down
        ;;
    "restart")
        shift
        if [[ $# -eq 0 ]]; then
            echo "Restarting all services..."
            $DOCKER_COMPOSE_CMD restart
        else
            echo "Restarting services: $*"
            $DOCKER_COMPOSE_CMD restart "$@"
        fi
        ;;
    "logs")
        shift
        if [[ $# -eq 0 ]]; then
            $DOCKER_COMPOSE_CMD logs -f
        else
            $DOCKER_COMPOSE_CMD logs -f "$@"
        fi
        ;;
    "ps")
        $DOCKER_COMPOSE_CMD ps
        ;;
    "exec")
        shift
        if [[ $# -lt 2 ]]; then
            echo "Usage: $0 exec <service> <command>"
            exit 1
        fi
        $DOCKER_COMPOSE_CMD exec "$@"
        ;;
    "dev")
        echo "Starting services with development profile (includes PgAdmin)..."
        $DOCKER_COMPOSE_CMD --profile dev up -d
        echo ""
        echo "Services started:"
        echo "- PostgreSQL: localhost:5432"
        echo "- Redis: localhost:6379"
        echo "- PgAdmin: http://localhost:5050"
        echo "  Email: admin@druginsightai.com"
        echo "  Password: admin123 (or your PGADMIN_PASSWORD)"
        ;;
    "help"|"--help"|"-h"|"")
        show_usage
        ;;
    *)
        echo "Unknown command: ${1:-}"
        echo ""
        show_usage
        exit 1
        ;;
esac
