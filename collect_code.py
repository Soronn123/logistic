#!/usr/bin/env python3
"""
Script to collect Django project code files and write them to Kod.txt
with a 200MB file size limit.
"""

import os
import sys
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent
OUTPUT_FILE = PROJECT_ROOT / "Kod.txt"
MAX_FILE_SIZE = 500 * 1024 * 1024  # 200MB in bytes

# Directories to exclude
EXCLUDE_DIRS = {
    '.venv',
    'venv',
    'media',
    'staticfiles',
    '__pycache__',
    '.git',
    'node_modules',
    '.pytest_cache',
    'dist',
    'build',
}

# File extensions to include
INCLUDE_EXTENSIONS = {
    '.py',          # Python files
    '.html',        # Templates
    '.css',         # Stylesheets
    '.js',          # JavaScript
}


def should_include_file(file_path: Path) -> bool:
    """Check if a file should be included in the output."""
    # Check if any parent directory is in EXCLUDE_DIRS
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False

    # Exclude __init__.py files
    if file_path.name == '__init__.py':
        return False

    # Include files with specific extensions
    if file_path.suffix in INCLUDE_EXTENSIONS:
        return True

    return False


def collect_files(project_root: Path) -> list[Path]:
    """Collect all relevant files from the project."""
    files = []

    for root, dirs, filenames in os.walk(project_root):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for filename in filenames:
            file_path = Path(root) / filename
            if should_include_file(file_path):
                files.append(file_path)

    # Sort files for consistent output
    files.sort()
    return files


def main():
    """Main function to collect code and write to Kod.txt."""
    print(f"Collecting Django project code files...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Max file size: {MAX_FILE_SIZE / 1024 / 1024:.0f}MB")
    print("-" * 60)

    # Collect files
    files = collect_files(PROJECT_ROOT)
    print(f"Found {len(files)} files to process")

    # Write to output file
    current_size = 0
    files_written = 0

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outf:
        for file_path in files:
            # Check if adding this file would exceed the limit
            try:
                file_size = file_path.stat().st_size
            except OSError:
                continue

            if current_size + file_size > MAX_FILE_SIZE:
                print(f"\nReached file size limit ({MAX_FILE_SIZE / 1024 / 1024:.0f}MB)")
                print(f"Skipping remaining files...")
                break

            # Write file header
            relative_path = file_path.relative_to(PROJECT_ROOT)
            header = f"\n{'='*80}\n"
            header += f"FILE: {relative_path}\n"
            header += f"{'='*80}\n\n"

            outf.write(header)
            current_size += len(header.encode('utf-8'))

            # Write file content
            try:
                with open(file_path, 'r', encoding='utf-8') as inf:
                    content = inf.read()
                    outf.write(content)
                    outf.write('\n')
                    current_size += len(content.encode('utf-8')) + 1

                files_written += 1

                # Progress indicator
                if files_written % 10 == 0:
                    print(f"Processed {files_written}/{len(files)} files... "
                          f"({current_size / 1024 / 1024:.1f}MB)")

            except (UnicodeDecodeError, OSError) as e:
                # Skip binary files or files that can't be read
                error_msg = f"[ERROR: Could not read file: {e}]\n"
                outf.write(error_msg)
                current_size += len(error_msg.encode('utf-8'))

    print("-" * 60)
    print(f"Done! Written {files_written} files to {OUTPUT_FILE}")
    print(f"Total file size: {current_size / 1024 / 1024:.1f}MB")


if __name__ == '__main__':
    main()
