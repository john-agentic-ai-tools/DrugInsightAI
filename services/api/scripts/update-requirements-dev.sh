#!/bin/bash
# Smart script to update requirements-dev.txt from pyproject.toml
# This ensures consistency between Poetry dependencies and pip requirements

set -e

echo "🔄 Updating requirements-dev.txt from pyproject.toml..."

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first."
    exit 1
fi

# Export production and dev dependencies
echo "📦 Exporting dependencies..."
poetry export --with dev --format requirements.txt --output requirements-dev.txt --without-hashes

# Add header comment
sed -i '1i# Development and Testing Dependencies for DrugInsightAI API' requirements-dev.txt
sed -i '2i# Auto-generated from pyproject.toml - run scripts/update-requirements-dev.sh to update' requirements-dev.txt
sed -i '3i# Last updated: '"$(date)"'' requirements-dev.txt
sed -i '4i' requirements-dev.txt

echo "✅ requirements-dev.txt has been updated successfully!"
echo "📄 File location: $(pwd)/requirements-dev.txt"

# Optional: Show diff if git is available
if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
    if git diff --quiet requirements-dev.txt; then
        echo "📋 No changes detected in requirements-dev.txt"
    else
        echo "📋 Changes detected in requirements-dev.txt:"
        git diff requirements-dev.txt || true
    fi
fi
