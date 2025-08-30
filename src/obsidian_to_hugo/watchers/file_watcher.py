"""File watcher for automatic Obsidian to Hugo conversion."""

import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from ..core.models import ConversionConfig, ConversionStats
from ..converters.hugo_converter import HugoConverter


class ObsidianFileHandler(FileSystemEventHandler):
    """Handles file system events for Obsidian files."""
    
    def __init__(self, config: ConversionConfig, converter: HugoConverter):
        self.config = config
        self.converter = converter
        self.console = Console()
        self.last_modified: dict[str, float] = {}
        self.debounce_time = 2.0  # seconds
        
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if not event.is_directory and self._is_obsidian_file(event.src_path):
            self._schedule_conversion("created", event.src_path)
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if not event.is_directory and self._is_obsidian_file(event.src_path):
            self._schedule_conversion("modified", event.src_path)
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events."""
        if not event.is_directory and self._is_obsidian_file(event.src_path):
            self._schedule_conversion("deleted", event.src_path)
    
    def on_moved(self, event: FileSystemEvent):
        """Handle file move/rename events."""
        if not event.is_directory and self._is_obsidian_file(event.src_path):
            self._schedule_conversion("moved", event.src_path)
    
    def _is_obsidian_file(self, file_path: str) -> bool:
        """Check if file is an Obsidian file that should be watched."""
        path = Path(file_path)
        
        # Check if file is in Obsidian vault
        try:
            path.relative_to(self.config.obsidian_vault_path)
        except ValueError:
            return False
        
        # Check if file matches include patterns
        for pattern in self.config.include_patterns:
            if path.match(pattern):
                return True
        
        # Check if file matches exclude patterns
        for pattern in self.config.exclude_patterns:
            if path.match(pattern):
                return False
        
        return False
    
    def _schedule_conversion(self, event_type: str, file_path: str):
        """Schedule conversion with debouncing."""
        current_time = time.time()
        
        # Debounce rapid changes
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < self.debounce_time:
                return
        
        self.last_modified[file_path] = current_time
        
        self.console.print(f"[blue]File {event_type}: {file_path}[/blue]")
        
        # Perform conversion
        try:
            stats = self.converter.convert()
            self.console.print(f"[green]Conversion completed: {stats}[/green]")
        except Exception as e:
            self.console.print(f"[red]Conversion error: {e}[/red]")


class FileWatcher:
    """Watches Obsidian vault for changes and automatically converts to Hugo."""
    
    def __init__(self, config: ConversionConfig):
        self.config = config
        self.converter = HugoConverter(config)
        self.console = Console()
        self.observer: Optional[Observer] = None
        self.handler: Optional[ObsidianFileHandler] = None
        
    def start(self):
        """Start watching the Obsidian vault."""
        if not self.config.obsidian_vault_path.exists():
            self.console.print(f"[red]Obsidian vault not found: {self.config.obsidian_vault_path}[/red]")
            return
        
        self.console.print(f"[green]Starting file watcher for: {self.config.obsidian_vault_path}[/green]")
        
        # Create handler and observer
        self.handler = ObsidianFileHandler(self.config, self.converter)
        self.observer = Observer()
        self.observer.schedule(
            self.handler,
            str(self.config.obsidian_vault_path),
            recursive=True
        )
        
        # Start observer
        self.observer.start()
        
        # Display status
        self._display_status()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop watching the Obsidian vault."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.console.print("[yellow]File watcher stopped[/yellow]")
    
    def _display_status(self):
        """Display current status."""
        status_table = Table(title="File Watcher Status")
        status_table.add_column("Property", style="cyan")
        status_table.add_column("Value", style="green")
        
        status_table.add_row("Obsidian Vault", str(self.config.obsidian_vault_path))
        status_table.add_row("Hugo Content", str(self.config.hugo_content_path))
        status_table.add_row("Hugo Static", str(self.config.hugo_static_path))
        status_table.add_row("Theme", self.config.theme_name)
        status_table.add_row("Watch Patterns", ", ".join(self.config.include_patterns))
        status_table.add_row("Exclude Patterns", ", ".join(self.config.exclude_patterns) or "None")
        
        self.console.print(status_table)
        self.console.print("\n[green]Watching for changes... Press Ctrl+C to stop[/green]")