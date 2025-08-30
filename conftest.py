"""Root conftest.py for pytest configuration.

This handles import errors gracefully for VSCode test discovery and ensures
that all service/package source directories are available in the Python path.

To run API tests specifically (which have additional dependencies):
    cd services/api && poetry install && poetry run pytest
"""

import sys
from pathlib import Path


def pytest_configure(config):
    """Configure pytest to handle missing dependencies gracefully."""
    # Add all service/package src directories to Python path
    root_dir = Path(__file__).parent

    # Add service source directories
    for service_dir in (root_dir / "services").glob("*"):
        if service_dir.is_dir():
            src_path = service_dir / "src"
            if src_path.exists():
                sys.path.insert(0, str(src_path))

    # Add package directories
    for package_dir in (root_dir / "packages").glob("*"):
        if package_dir.is_dir():
            src_path = package_dir / "src"
            if src_path.exists():
                sys.path.insert(0, str(src_path))
            # Also add the package directory itself
            sys.path.insert(0, str(package_dir))


def pytest_collection_modifyitems(config, items):
    """Modify collected items to handle import errors."""
    # This can be used to skip tests that have import issues
    pass


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    pass
