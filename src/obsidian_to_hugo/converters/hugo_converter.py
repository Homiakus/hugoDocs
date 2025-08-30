"""Converter for transforming Obsidian notes to Hugo format."""

import shutil
from pathlib import Path
from typing import Dict, List, Optional

import frontmatter
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.models import ConversionConfig, ConversionStats, HugoPost, ObsidianNote
from ..utils.obsidian_parser import ObsidianParser


class HugoConverter:
    """Converts Obsidian notes to Hugo format."""
    
    def __init__(self, config: ConversionConfig):
        self.config = config
        self.parser = ObsidianParser()
        self.console = Console()
        self.link_mapping: Dict[str, str] = {}
        
    def convert(self) -> ConversionStats:
        """Convert all Obsidian files to Hugo format."""
        stats = ConversionStats()
        
        # Find all markdown files in Obsidian vault
        obsidian_files = self._find_markdown_files()
        stats.total_files = len(obsidian_files)
        
        if stats.total_files == 0:
            self.console.print("[yellow]No markdown files found in Obsidian vault[/yellow]")
            return stats
        
        # Create Hugo content directory structure
        self._create_hugo_structure()
        
        # Build link mapping for wikilinks conversion
        self._build_link_mapping(obsidian_files)
        
        # Convert files
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Converting files...", total=stats.total_files)
            
            for file_path in obsidian_files:
                try:
                    self._convert_single_file(file_path, stats)
                    stats.converted_files += 1
                except Exception as e:
                    self.console.print(f"[red]Error converting {file_path}: {e}[/red]")
                    stats.error_files += 1
                
                progress.advance(task)
        
        # Copy attachments
        if self.config.convert_attachments:
            stats.attachments_copied = self._copy_attachments()
        
        return stats
    
    def _find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the Obsidian vault."""
        files = []
        
        for pattern in self.config.include_patterns:
            files.extend(self.config.obsidian_vault_path.rglob(pattern))
        
        # Filter out excluded patterns
        filtered_files = []
        for file_path in files:
            should_include = True
            for pattern in self.config.exclude_patterns:
                if file_path.match(pattern):
                    should_include = False
                    break
            
            if should_include:
                filtered_files.append(file_path)
        
        return filtered_files
    
    def _create_hugo_structure(self):
        """Create Hugo content directory structure."""
        self.config.hugo_content_path.mkdir(parents=True, exist_ok=True)
        self.config.hugo_static_path.mkdir(parents=True, exist_ok=True)
        self.config.hugo_archetypes_path.mkdir(parents=True, exist_ok=True)
    
    def _build_link_mapping(self, obsidian_files: List[Path]):
        """Build mapping from Obsidian filenames to Hugo URLs."""
        for file_path in obsidian_files:
            if file_path.suffix == '.md':
                # Convert filename to URL-friendly format
                relative_path = file_path.relative_to(self.config.obsidian_vault_path)
                hugo_path = self._convert_to_hugo_path(relative_path)
                self.link_mapping[file_path.stem] = str(hugo_path)
    
    def _convert_to_hugo_path(self, relative_path: Path) -> Path:
        """Convert Obsidian path to Hugo path."""
        # Remove .md extension and convert to Hugo content structure
        hugo_path = relative_path.with_suffix('')
        
        # Handle special cases (index files, etc.)
        if hugo_path.name == '_index':
            return hugo_path
        elif hugo_path.name == 'index':
            return hugo_path.parent / '_index'
        else:
            return hugo_path
    
    def _convert_single_file(self, file_path: Path, stats: ConversionStats):
        """Convert a single Obsidian file to Hugo format."""
        # Parse Obsidian file
        obsidian_note = self.parser.parse_file(file_path)
        
        # Convert content
        converted_content = self._convert_content(obsidian_note, stats)
        
        # Create Hugo front matter
        hugo_front_matter = self._create_hugo_front_matter(obsidian_note)
        
        # Determine Hugo file path
        relative_path = file_path.relative_to(self.config.obsidian_vault_path)
        hugo_path = self._convert_to_hugo_path(relative_path)
        hugo_file_path = self.config.hugo_content_path / hugo_path.with_suffix('.md')
        
        # Create Hugo post
        hugo_post = HugoPost(
            file_path=hugo_file_path,
            title=obsidian_note.title,
            content=converted_content,
            front_matter=hugo_front_matter,
            url=str(hugo_path),
            weight=0,
            draft=False
        )
        
        # Write Hugo file
        self._write_hugo_file(hugo_post)
    
    def _convert_content(self, obsidian_note: ObsidianNote, stats: ConversionStats) -> str:
        """Convert Obsidian content to Hugo format."""
        content = obsidian_note.content
        
        # Convert wikilinks
        if self.config.convert_wikilinks:
            content = self.parser.convert_wikilinks(content, self.link_mapping)
            stats.links_converted += len(obsidian_note.links)
        
        # Convert callouts
        content = self.parser.convert_callouts(content)
        
        # Convert code blocks
        content = self.parser.convert_code_blocks(content)
        
        # Convert media links (PDF, GLTF, images)
        content = self.parser.convert_media_links(content)
        
        # Process tags
        if self.config.convert_tags:
            content = self._process_tags(content, obsidian_note.tags)
            stats.tags_processed += len(obsidian_note.tags)
        
        # Create table of contents if requested
        if self.config.create_toc:
            content = self._add_table_of_contents(content)
        
        return content
    
    def _create_hugo_front_matter(self, obsidian_note: ObsidianNote) -> Dict:
        """Create Hugo front matter from Obsidian metadata."""
        front_matter = {}
        
        # Preserve original front matter if requested
        if self.config.preserve_front_matter:
            front_matter.update(obsidian_note.front_matter)
        
        # Set Hugo-specific fields
        front_matter['title'] = obsidian_note.title
        front_matter['date'] = obsidian_note.created_date or '2024-01-01'
        front_matter['lastmod'] = obsidian_note.modified_date or obsidian_note.created_date or '2024-01-01'
        
        # Convert tags
        if obsidian_note.tags:
            front_matter['tags'] = list(obsidian_note.tags)
        
        # Set theme-specific fields for PaperMod
        front_matter['showToc'] = self.config.create_toc
        front_matter['TocOpen'] = False
        front_matter['hideSummary'] = False
        front_matter['showWordCount'] = True
        front_matter['showReadingTime'] = True
        
        return front_matter
    
    def _process_tags(self, content: str, tags: set) -> str:
        """Process tags in content."""
        # Remove #tag syntax from content as tags are now in front matter
        import re
        tag_pattern = re.compile(r'#([a-zA-Z0-9_-]+)')
        return tag_pattern.sub('', content)
    
    def _add_table_of_contents(self, content: str) -> str:
        """Add Hugo table of contents shortcode."""
        toc_shortcode = f'{{{{< toc maxdepth="{self.config.toc_max_depth}" >}}}}'
        return f"{toc_shortcode}\n\n{content}"
    
    def _write_hugo_file(self, hugo_post: HugoPost):
        """Write Hugo post to file."""
        # Create directory if it doesn't exist
        hugo_post.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create front matter string
        try:
            front_matter_str = frontmatter.dumps(
                frontmatter.Post(hugo_post.content, **hugo_post.front_matter)
            )
        except AttributeError:
            # Fallback for different frontmatter versions
            import yaml
            front_matter_str = "---\n"
            front_matter_str += yaml.dump(hugo_post.front_matter, default_flow_style=False, allow_unicode=True)
            front_matter_str += "---\n\n"
            front_matter_str += hugo_post.content
        
        # Write file
        hugo_post.file_path.write_text(front_matter_str, encoding='utf-8')
    
    def _copy_attachments(self) -> int:
        """Copy attachments from Obsidian to Hugo static directory."""
        copied_count = 0
        
        for file_path in self.config.obsidian_vault_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.config.attachment_extensions:
                # Calculate relative path
                relative_path = file_path.relative_to(self.config.obsidian_vault_path)
                target_path = self.config.hugo_static_path / relative_path
                
                # Create target directory
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(file_path, target_path)
                copied_count += 1
        
        return copied_count