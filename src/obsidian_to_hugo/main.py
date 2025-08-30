"""Main entry point for Obsidian to Hugo converter."""

import sys
from pathlib import Path

from .cli import cli


def main():
    """Main entry point."""
    # Add src to Python path for development
    src_path = Path(__file__).parent.parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    cli()


if __name__ == '__main__':
    main()