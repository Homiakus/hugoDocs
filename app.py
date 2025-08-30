#!/usr/bin/env python3
"""Entry point for Obsidian to Hugo converter CLI."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from obsidian_to_hugo.cli import cli

if __name__ == '__main__':
    cli()