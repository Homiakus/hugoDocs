"""GUI entry point for Obsidian to Hugo converter."""

import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from obsidian_to_hugo.ui import main

if __name__ == "__main__":
    main()