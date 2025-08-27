#!/usr/bin/env python3
"""
Smart script to update requirements-dev.txt from pyproject.toml
This ensures consistency between Poetry dependencies and pip requirements

SECURITY: This script eliminates subprocess usage to avoid security risks.
It reads pyproject.toml directly and generates requirements-dev.txt safely.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import tomllib
except ImportError:
    # Python < 3.11 fallback
    try:
        import tomli as tomllib
    except ImportError:
        print(
            "❌ Neither tomllib nor tomli available. Please install tomli: pip install tomli"
        )
        sys.exit(1)


def read_pyproject_toml() -> Optional[Dict]:
    """Read and parse pyproject.toml file securely."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return None

    try:
        with open(pyproject_path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        print(f"❌ Failed to parse pyproject.toml: {e}")
        return None


def format_dependency(name: str, version_spec: Union[str, Dict]) -> Optional[str]:
    """Format a dependency for requirements.txt format."""
    if name == "python":
        return None  # Skip Python version requirement

    if isinstance(version_spec, str):
        # Simple version string like "^1.0.0" -> ">=1.0.0,<2.0.0"
        if version_spec.startswith("^"):
            # Handle caret requirements
            base_version = version_spec[1:]
            parts = base_version.split(".")
            if len(parts) >= 2:
                major, minor = parts[0], parts[1]
                next_major = str(int(major) + 1)
                return f"{name}>={base_version},<{next_major}.0.0"
            else:
                return f"{name}>={base_version}"
        elif version_spec.startswith("~"):
            # Handle tilde requirements
            base_version = version_spec[1:]
            return f"{name}>={base_version}"
        elif (
            version_spec.startswith(">=")
            or version_spec.startswith("<=")
            or version_spec.startswith("==")
            or version_spec.startswith(">")
            or version_spec.startswith("<")
        ):
            # Already formatted version
            return f"{name}{version_spec}"
        else:
            # Assume it's a version without operator, default to >=
            return f"{name}>={version_spec}"

    elif isinstance(version_spec, dict):
        # Complex dependency specification
        version = version_spec.get("version", "")
        if version:
            return format_dependency(name, version)

        # Handle git, path, or URL dependencies
        git_url = version_spec.get("git")
        if git_url:
            return f"# {name} from git: {git_url}"

        path = version_spec.get("path")
        if path:
            return f"# {name} from path: {path}"

        # Fallback for other sources
        return f"# {name} (complex dependency)"

    else:
        # Fallback for other formats
        return f"{name}"


def extract_dependencies(pyproject_data: Dict) -> List[str]:
    """Extract and format dependencies from pyproject.toml data."""
    dependencies = []

    # Get tool.poetry section
    poetry_config = pyproject_data.get("tool", {}).get("poetry", {})

    # Main dependencies
    main_deps = poetry_config.get("dependencies", {})

    # Development dependencies (group format)
    dev_deps = {}
    groups = poetry_config.get("group", {})
    for group_name, group_data in groups.items():
        if "dependencies" in group_data:
            dev_deps.update(group_data["dependencies"])

    # Legacy dev-dependencies format (for older poetry versions)
    legacy_dev_deps = poetry_config.get("dev-dependencies", {})
    dev_deps.update(legacy_dev_deps)

    # Process main dependencies
    for name, version_spec in main_deps.items():
        formatted = format_dependency(name, version_spec)
        if formatted:
            dependencies.append(formatted)

    # Add separator comment
    if main_deps and dev_deps:
        dependencies.append("")
        dependencies.append("# Development dependencies")

    # Process development dependencies
    for name, version_spec in dev_deps.items():
        formatted = format_dependency(name, version_spec)
        if formatted:
            dependencies.append(formatted)

    # Filter out None values and sort (keeping comments in place)
    result: List[str] = []
    regular_deps: List[str] = []

    for dep in dependencies:
        if dep == "" or dep.startswith("#"):
            # Add accumulated regular deps, then the comment
            if regular_deps:
                result.extend(sorted(regular_deps))
                regular_deps = []
            result.append(dep)
        else:
            regular_deps.append(dep)

    # Add any remaining regular deps
    if regular_deps:
        result.extend(sorted(regular_deps))

    return result


def main():
    """Main function to update requirements-dev.txt from pyproject.toml."""
    print("🔄 Updating requirements-dev.txt from pyproject.toml...")

    # Check if we're in the right directory (has pyproject.toml)
    if not Path("pyproject.toml").exists():
        print(
            "❌ pyproject.toml not found. Please run this script from the API service directory."
        )
        sys.exit(1)

    print("📦 Reading dependencies from pyproject.toml...")

    # Read pyproject.toml
    pyproject_data = read_pyproject_toml()
    if not pyproject_data:
        print("❌ Failed to read pyproject.toml")
        sys.exit(1)

    # Extract dependencies
    dependencies = extract_dependencies(pyproject_data)

    if not dependencies:
        print("❌ No dependencies found in pyproject.toml")
        sys.exit(1)

    # Create the requirements-dev.txt content
    header = f"""# Development and Testing Dependencies for DrugInsightAI API
# Auto-generated from pyproject.toml - run scripts/update_requirements_dev.py to update
# Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#
# This file is generated without subprocess usage for security compliance
# Dependencies are parsed directly from pyproject.toml

"""

    content = header + "\n".join(dependencies) + "\n"

    # Write to requirements-dev.txt
    with open("requirements-dev.txt", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ requirements-dev.txt has been updated successfully!")
    print(f"📄 File location: {Path.cwd() / 'requirements-dev.txt'}")
    print(
        f"📊 Generated {len([d for d in dependencies if d and not d.startswith('#')])} dependency entries"
    )
    print("📋 Use 'git status' and 'git diff' to see changes if needed")


if __name__ == "__main__":
    main()
