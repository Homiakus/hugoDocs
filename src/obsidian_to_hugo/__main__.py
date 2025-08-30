"""Main entry point for obsidian_to_hugo package."""

import sys
from .cli import cli
from .ui import main as gui_main

if __name__ == '__main__':
    # Check for --gui flag before passing to click
    if '--gui' in sys.argv:
        sys.argv.remove('--gui')  # Remove --gui argument
        gui_main()
    else:
        # Run CLI
        cli()