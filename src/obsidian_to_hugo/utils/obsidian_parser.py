"""Parser for Obsidian markdown files."""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

import frontmatter
from pydantic import BaseModel

from ..core.models import ObsidianNote


class ObsidianParser:
    """Parser for Obsidian markdown files."""
    
    def __init__(self):
        # Regex patterns for Obsidian-specific syntax
        self.wikilink_pattern = re.compile(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]')
        self.tag_pattern = re.compile(r'#([a-zA-Z0-9_-]+)')
        self.callout_pattern = re.compile(r'^>\s*\[!(\w+)\](.*)', re.MULTILINE)
        self.code_block_pattern = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)
        
        # Patterns for media files
        self.media_link_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self.pdf_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.pdf)\)')
        self.gltf_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.(?:gltf|glb))\)')
        
    def parse_file(self, file_path: Path) -> ObsidianNote:
        """Parse an Obsidian markdown file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        content = file_path.read_text(encoding='utf-8')
        
        # Parse front matter
        try:
            post = frontmatter.loads(content)
            front_matter = dict(post.metadata) if post.metadata else {}
            post_content = post.content
        except AttributeError:
            # Fallback for different frontmatter versions
            fm = frontmatter.Frontmatter()
            post = fm.read(content)
            front_matter = dict(post.get('attributes', {}))
            post_content = post.get('body', content)
        
        # Extract title from front matter or filename
        title = front_matter.get('title', file_path.stem)
        
        # Extract tags
        tags = self._extract_tags(post_content, front_matter)
        
        # Extract links
        links = self._extract_links(post_content)
        
        # Extract dates
        created_date = str(front_matter.get('created', '')) if front_matter.get('created') else None
        modified_date = str(front_matter.get('modified', '')) if front_matter.get('modified') else None
        
        return ObsidianNote(
            file_path=file_path,
            title=title,
            content=post_content,
            front_matter=front_matter,
            tags=tags,
            links=links,
            created_date=created_date,
            modified_date=modified_date
        )
    
    def _extract_tags(self, content: str, front_matter: Dict) -> Set[str]:
        """Extract tags from content and front matter."""
        tags = set()
        
        # Extract tags from front matter
        if 'tags' in front_matter:
            if isinstance(front_matter['tags'], list):
                tags.update(front_matter['tags'])
            elif isinstance(front_matter['tags'], str):
                tags.add(front_matter['tags'])
        
        # Extract tags from content (#tag syntax)
        content_tags = self.tag_pattern.findall(content)
        tags.update(content_tags)
        
        return tags
    
    def _extract_links(self, content: str) -> List[str]:
        """Extract wikilinks from content."""
        links = []
        matches = self.wikilink_pattern.findall(content)
        
        for match in matches:
            link_target = match[0].strip()
            if link_target and not link_target.startswith('#'):
                links.append(link_target)
        
        return links
    
    def convert_wikilinks(self, content: str, link_mapping: Dict[str, str]) -> str:
        """Convert Obsidian wikilinks to Hugo markdown links."""
        def replace_wikilink(match):
            link_target = match.group(1).strip()
            display_text = match.group(2) if match.group(2) else link_target
            
            # Handle different types of links
            if link_target.startswith('http'):
                return f'[{display_text}]({link_target})'
            elif link_target.startswith('#'):
                return f'[{display_text}]({link_target})'
            elif link_target in link_mapping:
                return f'[{display_text}]({link_mapping[link_target]})'
            else:
                # Fallback to original format
                return f'[{display_text}]({link_target})'
        
        return self.wikilink_pattern.sub(replace_wikilink, content)
    
    def convert_media_links(self, content: str) -> str:
        """Convert media links to Hugo shortcodes."""
        # Convert PDF links to PDF viewer shortcode
        def replace_pdf_link(match):
            display_text = match.group(1)
            pdf_path = match.group(2)
            return f'{{{{< pdf-viewer url="{pdf_path}" title="{display_text}" >}}}}'
        
        # Convert GLTF links to 3D viewer shortcode
        def replace_gltf_link(match):
            display_text = match.group(1)
            gltf_path = match.group(2)
            return f'{{{{< gltf-viewer url="{gltf_path}" title="{display_text}" >}}}}'
        
        # Convert image links to enhanced image shortcode
        def replace_image_link(match):
            alt_text = match.group(1)
            image_path = match.group(2)
            return f'{{{{< image src="{image_path}" alt="{alt_text}" >}}}}'
        
        # Apply conversions in order
        content = self.pdf_link_pattern.sub(replace_pdf_link, content)
        content = self.gltf_link_pattern.sub(replace_gltf_link, content)
        content = self.media_link_pattern.sub(replace_image_link, content)
        
        return content
    
    def convert_callouts(self, content: str) -> str:
        """Convert Obsidian callouts to Hugo-compatible format."""
        def replace_callout(match):
            callout_type = match.group(1).lower()
            callout_content = match.group(2).strip()
            
            # Map Obsidian callout types to Hugo admonition types
            callout_mapping = {
                'note': 'note',
                'warning': 'warning',
                'error': 'danger',
                'info': 'info',
                'tip': 'tip',
                'success': 'success',
                'question': 'question',
                'example': 'example',
                'quote': 'quote',
                'abstract': 'abstract',
                'bug': 'bug',
                'danger': 'danger',
                'failure': 'failure',
                'important': 'important',
                'missing': 'missing',
                'caution': 'caution',
                'faq': 'faq',
            }
            
            hugo_type = callout_mapping.get(callout_type, 'note')
            return f'{{{{< admonition type="{hugo_type}" title="{callout_type.title()}" >}}}}\n{callout_content}\n{{{{< /admonition >}}}}'
        
        return self.callout_pattern.sub(replace_callout, content)
    
    def convert_code_blocks(self, content: str) -> str:
        """Convert Obsidian code blocks to Hugo format."""
        def replace_code_block(match):
            language = match.group(1) if match.group(1) else ''
            code_content = match.group(2)
            
            if language:
                return f'```{language}\n{code_content}\n```'
            else:
                return f'```\n{code_content}\n```'
        
        return self.code_block_pattern.sub(replace_code_block, content)