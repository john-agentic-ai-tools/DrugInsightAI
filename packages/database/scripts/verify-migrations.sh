#!/bin/bash

# Migration Files Verification Script
# Verifies that all migration files exist and are readable

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATABASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "Migration Files Verification"
echo "==========================="
echo ""

print_header "Directory Structure"
echo "Database directory: $DATABASE_DIR"
echo "Migrations directory: $DATABASE_DIR/migrations"
echo ""

# Check if migrations directory exists
if [[ -d "$DATABASE_DIR/migrations" ]]; then
    print_success "Migrations directory exists"
else
    print_error "Migrations directory not found"
    exit 1
fi

print_header "Master Changelog"
master_file="$DATABASE_DIR/migrations/db.changelog-master.xml"
if [[ -f "$master_file" ]]; then
    print_success "Master changelog found: db.changelog-master.xml"
else
    print_error "Master changelog not found: db.changelog-master.xml"
    exit 1
fi

print_header "Individual Migration Files"
migration_files=(
    "001-initial-schema.xml"
    "002-users-and-auth.xml"
    "003-companies.xml"
    "004-drugs.xml"
    "005-clinical-trials.xml"
    "006-adverse-events.xml"
    "007-reference-data.xml"
    "008-indexes.xml"
    "009-seed-data.xml"
)

all_found=true
for file in "${migration_files[@]}"; do
    filepath="$DATABASE_DIR/migrations/$file"
    if [[ -f "$filepath" ]]; then
        print_success "$file"
    else
        print_error "$file (not found)"
        all_found=false
    fi
done

if [[ "$all_found" != "true" ]]; then
    echo ""
    print_error "Some migration files are missing!"
    exit 1
fi

print_header "File Permissions"
for file in "${migration_files[@]}"; do
    filepath="$DATABASE_DIR/migrations/$file"
    if [[ -r "$filepath" ]]; then
        print_success "$file (readable)"
    else
        print_error "$file (not readable)"
        all_found=false
    fi
done

print_header "Master Changelog Content Verification"
echo "Checking include statements in master changelog..."

# Check if include statements use correct paths
if grep -q 'file="001-initial-schema.xml"' "$master_file"; then
    print_success "Include paths are using relative format"
else
    if grep -q 'file="migrations/001-initial-schema.xml"' "$master_file"; then
        print_error "Include paths are using full path format (should be relative)"
        echo "  Found: migrations/001-initial-schema.xml"
        echo "  Should be: 001-initial-schema.xml"
    else
        print_error "Include statements not found or malformed"
    fi
fi

print_header "Docker Volume Test"
echo "Testing Docker volume mapping..."

# Test if files are accessible via Docker volume
docker run --rm \
    -v "${DATABASE_DIR}/migrations:/test/changelog" \
    -v "${DATABASE_DIR}/config:/test/config" \
    alpine:latest \
    sh -c "
    echo 'Files in /test/changelog:'
    ls -la /test/changelog/
    echo ''
    echo 'Master changelog content:'
    head -20 /test/changelog/db.changelog-master.xml
    echo ''
    echo 'Testing file access:'
    for file in 001-initial-schema.xml 002-users-and-auth.xml; do
        if [ -f /test/changelog/\$file ]; then
            echo '✅ \$file is accessible'
        else
            echo '❌ \$file is not accessible'
        fi
    done
    "

echo ""
if [[ "$all_found" == "true" ]]; then
    print_success "All migration files verified successfully!"
    echo ""
    echo "You can now run migrations with:"
    echo "  cd $DATABASE_DIR"
    echo "  ./scripts/migrate.sh update"
else
    print_error "Migration verification failed!"
    exit 1
fi
