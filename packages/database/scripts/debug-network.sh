#!/bin/bash

# Network Debug Script for DrugInsightAI Database Setup
# This script helps diagnose Docker networking issues

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "DrugInsightAI Docker Network Diagnostics"
echo "========================================"
echo ""

print_header "Docker Environment"

# Check Docker
if command -v docker >/dev/null 2>&1; then
    print_info "✅ Docker is installed"
    docker --version
else
    print_error "❌ Docker is not installed"
    exit 1
fi

# Check Docker daemon
if docker info >/dev/null 2>&1; then
    print_info "✅ Docker daemon is running"
else
    print_error "❌ Docker daemon is not running"
    exit 1
fi

echo ""
print_header "Docker Compose"

# Check Docker Compose
if docker compose version >/dev/null 2>&1; then
    print_info "✅ Docker Compose plugin available"
    docker compose version
elif command -v docker-compose >/dev/null 2>&1; then
    print_info "✅ Docker Compose standalone available"
    docker-compose --version
else
    print_error "❌ Docker Compose not found"
fi

echo ""
print_header "Containers Status"

# Check for our containers
containers=("druginsightai-postgres" "druginsightai-redis" "druginsightai-liquibase")
for container in "${containers[@]}"; do
    if docker ps -a --format "table {{.Names}}" | grep -q "$container"; then
        status=$(docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep "$container" | awk '{$1=""; print $0}' | sed 's/^ *//')
        print_info "Container $container: $status"
    else
        print_warning "Container $container: Not found"
    fi
done

echo ""
print_header "Docker Networks"

# List all networks
print_info "Available Docker networks:"
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"

echo ""
# Check our specific network
if docker network ls --format "table {{.Name}}" | grep -q "druginsightai-network"; then
    print_info "✅ Network 'druginsightai-network' exists"

    # Show network details
    echo ""
    print_info "Network details:"
    docker network inspect druginsightai-network --format="{{json .}}" | jq '.Name, .Driver, .IPAM.Config, .Containers' 2>/dev/null || {
        # Fallback if jq is not available
        docker network inspect druginsightai-network
    }
else
    print_warning "❌ Network 'druginsightai-network' not found"
fi

echo ""
print_header "Port Usage"

# Check if ports are in use
ports=(5432 6379 5050)
port_names=("PostgreSQL" "Redis" "PgAdmin")

for i in "${!ports[@]}"; do
    port=${ports[$i]}
    name=${port_names[$i]}

    if command -v lsof >/dev/null 2>&1; then
        if lsof -i :$port >/dev/null 2>&1; then
            process=$(lsof -i :$port -t | head -1)
            print_info "Port $port ($name) is in use by process $process"
        else
            print_warning "Port $port ($name) is not in use"
        fi
    else
        print_warning "lsof not available, cannot check port usage"
    fi
done

echo ""
print_header "Database Connectivity Test"

# Test database connection if container is running
if docker ps --format "table {{.Names}}" | grep -q "druginsightai-postgres"; then
    print_info "Testing PostgreSQL connection..."

    if docker exec druginsightai-postgres pg_isready -U druginsightai -d druginsightai >/dev/null 2>&1; then
        print_info "✅ PostgreSQL is ready and accepting connections"
    else
        print_error "❌ PostgreSQL is not ready"
    fi
else
    print_warning "PostgreSQL container is not running"
fi

echo ""
print_header "Recommendations"

if ! docker network ls --format "table {{.Name}}" | grep -q "druginsightai-network"; then
    echo "Network not found. Try:"
    echo "1. Start services with Docker Compose:"
    echo "   cd infra/database && docker compose up -d"
    echo ""
    echo "2. Or create network manually:"
    echo "   docker network create druginsightai-network"
fi

if ! docker ps --format "table {{.Names}}" | grep -q "druginsightai-postgres"; then
    echo "PostgreSQL container not running. Try:"
    echo "   cd infra/database && docker compose up -d postgres"
fi

echo ""
print_info "For migration issues, the script will automatically fall back to host networking"
print_info "This is safe and will work as long as PostgreSQL is accessible on localhost:5432"
