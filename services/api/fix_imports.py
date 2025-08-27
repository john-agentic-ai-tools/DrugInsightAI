#!/usr/bin/env python3
"""
Fix relative imports to absolute imports for proper pytest execution.
"""

import os
import re
from pathlib import Path


def fix_imports_in_file(file_path: Path):
    """Fix relative imports in a single file."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        original_content = content

        # Fix relative imports - convert from .module to module
        # Pattern 1: from .module import something
        content = re.sub(r"from \.([a-zA-Z_][a-zA-Z0-9_]*)", r"from \1", content)

        # Pattern 2: from ..module import something (parent directory)
        content = re.sub(r"from \.\.([a-zA-Z_][a-zA-Z0-9_]*)", r"from \1", content)

        # Pattern 3: from .subpackage.module import something
        content = re.sub(
            r"from \.([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)",
            r"from \1",
            content,
        )

        # Pattern 4: from ..subpackage.module import something
        content = re.sub(
            r"from \.\.([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)",
            r"from \1",
            content,
        )

        # Pattern 5: import .module
        content = re.sub(r"import \.([a-zA-Z_][a-zA-Z0-9_]*)", r"import \1", content)

        if content != original_content:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"✅ Fixed imports in {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed in {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Fix imports in all Python files in src directory."""
    src_dir = Path("src")

    if not src_dir.exists():
        print("❌ src directory not found")
        return

    print("🔧 Fixing relative imports in source files...")

    files_fixed = 0
    files_checked = 0

    # Find all Python files in src directory
    for py_file in src_dir.rglob("*.py"):
        files_checked += 1
        if fix_imports_in_file(py_file):
            files_fixed += 1

    print(f"\n📊 Summary:")
    print(f"   Files checked: {files_checked}")
    print(f"   Files fixed: {files_fixed}")

    if files_fixed > 0:
        print("\n✨ Import fixes complete!")
    else:
        print("\n✅ All imports were already correct!")


if __name__ == "__main__":
    main()
