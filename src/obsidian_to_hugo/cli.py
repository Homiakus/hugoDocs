"""Command-line interface for Obsidian to Hugo converter."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .core.models import ConversionConfig
from .converters.hugo_converter import HugoConverter
from .watchers.file_watcher import FileWatcher


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Obsidian to Hugo converter with PaperMod theme support."""
    pass


@cli.command()
@click.option(
    '--obsidian-vault',
    '-i',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help='Path to Obsidian vault directory'
)
@click.option(
    '--hugo-content',
    '-c',
    type=click.Path(path_type=Path),
    default='./content',
    help='Path to Hugo content directory'
)
@click.option(
    '--hugo-static',
    '-s',
    type=click.Path(path_type=Path),
    default='./static',
    help='Path to Hugo static directory'
)
@click.option(
    '--hugo-archetypes',
    '-a',
    type=click.Path(path_type=Path),
    default='./archetypes',
    help='Path to Hugo archetypes directory'
)
@click.option(
    '--theme',
    '-t',
    default='hugo-papermod',
    help='Hugo theme name'
)
@click.option(
    '--include-patterns',
    multiple=True,
    default=['*.md'],
    help='File patterns to include (can be specified multiple times)'
)
@click.option(
    '--exclude-patterns',
    multiple=True,
    default=[],
    help='File patterns to exclude (can be specified multiple times)'
)
@click.option(
    '--attachment-extensions',
    multiple=True,
    default=['png', 'jpg', 'jpeg', 'gif', 'svg', 'pdf', 'mp4', 'mp3', 'zip', 'gltf', 'glb'],
    help='File extensions to copy as attachments'
)
@click.option(
    '--no-wikilinks',
    is_flag=True,
    help='Disable wikilinks conversion'
)
@click.option(
    '--no-tags',
    is_flag=True,
    help='Disable tags conversion'
)
@click.option(
    '--no-attachments',
    is_flag=True,
    help='Disable attachments copying'
)
@click.option(
    '--no-toc',
    is_flag=True,
    help='Disable table of contents generation'
)
@click.option(
    '--toc-max-depth',
    type=int,
    default=3,
    help='Maximum depth for table of contents'
)
@click.option(
    '--no-front-matter',
    is_flag=True,
    help='Do not preserve original front matter'
)
def convert(
    obsidian_vault: Path,
    hugo_content: Path,
    hugo_static: Path,
    hugo_archetypes: Path,
    theme: str,
    include_patterns: tuple,
    exclude_patterns: tuple,
    attachment_extensions: tuple,
    no_wikilinks: bool,
    no_tags: bool,
    no_attachments: bool,
    no_toc: bool,
    toc_max_depth: int,
    no_front_matter: bool,
):
    """Convert Obsidian vault to Hugo format."""
    console = Console()
    
    # Create configuration
    config = ConversionConfig(
        obsidian_vault_path=obsidian_vault,
        hugo_content_path=hugo_content,
        hugo_static_path=hugo_static,
        hugo_archetypes_path=hugo_archetypes,
        theme_name=theme,
        preserve_front_matter=not no_front_matter,
        convert_wikilinks=not no_wikilinks,
        convert_tags=not no_tags,
        convert_attachments=not no_attachments,
        attachment_extensions=set(attachment_extensions),
        include_patterns=list(include_patterns),
        exclude_patterns=list(exclude_patterns),
        create_toc=not no_toc,
        toc_max_depth=toc_max_depth,
    )
    
    # Display configuration
    _display_config(console, config)
    
    # Perform conversion
    try:
        converter = HugoConverter(config)
        stats = converter.convert()
        
        # Display results
        _display_results(console, stats)
        
    except Exception as e:
        console.print(f"[red]Conversion failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    '--obsidian-vault',
    '-i',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help='Path to Obsidian vault directory'
)
@click.option(
    '--hugo-content',
    '-c',
    type=click.Path(path_type=Path),
    default='./content',
    help='Path to Hugo content directory'
)
@click.option(
    '--hugo-static',
    '-s',
    type=click.Path(path_type=Path),
    default='./static',
    help='Path to Hugo static directory'
)
@click.option(
    '--hugo-archetypes',
    '-a',
    type=click.Path(path_type=Path),
    default='./archetypes',
    help='Path to Hugo archetypes directory'
)
@click.option(
    '--theme',
    '-t',
    default='hugo-papermod',
    help='Hugo theme name'
)
@click.option(
    '--include-patterns',
    multiple=True,
    default=['*.md'],
    help='File patterns to include (can be specified multiple times)'
)
@click.option(
    '--exclude-patterns',
    multiple=True,
    default=[],
    help='File patterns to exclude (can be specified multiple times)'
)
def watch(
    obsidian_vault: Path,
    hugo_content: Path,
    hugo_static: Path,
    hugo_archetypes: Path,
    theme: str,
    include_patterns: tuple,
    exclude_patterns: tuple,
):
    """Watch Obsidian vault for changes and automatically convert to Hugo."""
    console = Console()
    
    # Create configuration
    config = ConversionConfig(
        obsidian_vault_path=obsidian_vault,
        hugo_content_path=hugo_content,
        hugo_static_path=hugo_static,
        hugo_archetypes_path=hugo_archetypes,
        theme_name=theme,
        include_patterns=list(include_patterns),
        exclude_patterns=list(exclude_patterns),
    )
    
    # Start file watcher
    try:
        watcher = FileWatcher(config)
        watcher.start()
    except KeyboardInterrupt:
        console.print("\n[yellow]Watch mode stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Watch mode failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    '--obsidian-vault',
    '-i',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help='Path to Obsidian vault directory'
)
def analyze(
    obsidian_vault: Path,
):
    """Analyze Obsidian vault structure and content."""
    console = Console()
    
    try:
        from .utils.obsidian_parser import ObsidianParser
        
        parser = ObsidianParser()
        
        # Find all markdown files
        md_files = list(obsidian_vault.rglob('*.md'))
        
        if not md_files:
            console.print("[yellow]No markdown files found in the vault[/yellow]")
            return
        
        # Analyze files
        total_tags = set()
        total_links = set()
        total_files = len(md_files)
        
        for file_path in md_files:
            try:
                note = parser.parse_file(file_path)
                total_tags.update(note.tags)
                total_links.update(note.links)
            except Exception as e:
                console.print(f"[red]Error analyzing {file_path}: {e}[/red]")
        
        # Display analysis results
        analysis_table = Table(title="Obsidian Vault Analysis")
        analysis_table.add_column("Metric", style="cyan")
        analysis_table.add_column("Value", style="green")
        
        analysis_table.add_row("Total Files", str(total_files))
        analysis_table.add_row("Unique Tags", str(len(total_tags)))
        analysis_table.add_row("Unique Links", str(len(total_links)))
        analysis_table.add_row("Vault Path", str(obsidian_vault))
        
        console.print(analysis_table)
        
        if total_tags:
            console.print(f"\n[cyan]Tags found:[/cyan] {', '.join(sorted(total_tags))}")
        
        if total_links:
            console.print(f"\n[cyan]Links found:[/cyan] {', '.join(sorted(total_links))}")
        
    except Exception as e:
        console.print(f"[red]Analysis failed: {e}[/red]")
        sys.exit(1)


def _display_config(console: Console, config: ConversionConfig):
    """Display conversion configuration."""
    config_table = Table(title="Conversion Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Obsidian Vault", str(config.obsidian_vault_path))
    config_table.add_row("Hugo Content", str(config.hugo_content_path))
    config_table.add_row("Hugo Static", str(config.hugo_static_path))
    config_table.add_row("Hugo Archetypes", str(config.hugo_archetypes_path))
    config_table.add_row("Theme", config.theme_name)
    config_table.add_row("Include Patterns", ", ".join(config.include_patterns))
    config_table.add_row("Exclude Patterns", ", ".join(config.exclude_patterns) or "None")
    config_table.add_row("Convert Wikilinks", str(config.convert_wikilinks))
    config_table.add_row("Convert Tags", str(config.convert_tags))
    config_table.add_row("Convert Attachments", str(config.convert_attachments))
    config_table.add_row("Create TOC", str(config.create_toc))
    config_table.add_row("TOC Max Depth", str(config.toc_max_depth))
    
    console.print(config_table)


def _display_results(console: Console, stats):
    """Display conversion results."""
    results_table = Table(title="Conversion Results")
    results_table.add_column("Metric", style="cyan")
    results_table.add_column("Value", style="green")
    
    results_table.add_row("Processing Time", f"{stats.processing_time:.2f}s")
    results_table.add_row("Total Files", str(stats.total_files))
    results_table.add_row("Converted Files", str(stats.converted_files))
    results_table.add_row("Skipped Files", str(stats.skipped_files))
    results_table.add_row("Error Files", str(stats.error_files))
    results_table.add_row("Attachments Copied", str(stats.attachments_copied))
    results_table.add_row("Links Converted", str(stats.links_converted))
    results_table.add_row("Tags Processed", str(stats.tags_processed))
    
    console.print(results_table)
    
    if stats.error_files > 0:
        console.print("[yellow]Some files had errors during conversion[/yellow]")
    else:
        console.print("[green]Conversion completed successfully![/green]")


if __name__ == '__main__':
    cli()