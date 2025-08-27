#!/usr/bin/env python3
"""
Smart script to update requirements-dev.txt from pyproject.toml
This ensures consistency between Poetry dependencies and pip requirements
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path


def check_poetry_available():
    """Check if poetry is available in PATH."""
    return shutil.which("poetry") is not None


def run_poetry_export():
    """Run poetry export using secure subprocess execution."""
    import subprocess

    # Use shutil.which to get full path to poetry for security
    poetry_path = shutil.which("poetry")
    if not poetry_path:
        return False, "", "Poetry not found in PATH"

    try:
        # Use full path and explicit arguments for security
        cmd = [
            poetry_path,
            "export",
            "--with",
            "dev",
            "--format",
            "requirements.txt",
            "--without-hashes",
        ]

        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
            # Additional security: don't inherit environment
            env={"PATH": str(Path(poetry_path).parent)},
        )
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Poetry export timed out"


def main():
    print("🔄 Updating requirements-dev.txt from pyproject.toml...")

    # Check if poetry is installed
    if not check_poetry_available():
        print("❌ Poetry is not installed. Please install Poetry first.")
        sys.exit(1)

    # Check if we're in the right directory (has pyproject.toml)
    if not Path("pyproject.toml").exists():
        print(
            "❌ pyproject.toml not found. Please run this script from the API service directory."
        )
        sys.exit(1)

    print("📦 Exporting dependencies from pyproject.toml...")

    # Export dependencies using poetry
    success, stdout, stderr = run_poetry_export()

    if not success:
        print(f"❌ Failed to export dependencies: {stderr}")
        sys.exit(1)

    # Create the requirements-dev.txt content
    header = f"""# Development and Testing Dependencies for DrugInsightAI API
# Auto-generated from pyproject.toml - run scripts/update_requirements_dev.py to update
# Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""

    content = header + stdout

    # Write to requirements-dev.txt
    with open("requirements-dev.txt", "w") as f:
        f.write(content)

    print("✅ requirements-dev.txt has been updated successfully!")
    print(f"📄 File location: {Path.cwd() / 'requirements-dev.txt'}")
    print("📋 Use 'git status' and 'git diff' to see changes if needed")


if __name__ == "__main__":
    main()
