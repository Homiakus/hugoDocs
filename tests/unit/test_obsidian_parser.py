"""Unit tests for Obsidian parser."""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from obsidian_to_hugo.utils.obsidian_parser import ObsidianParser
from obsidian_to_hugo.core.models import ObsidianNote


class TestObsidianParser:
    """Test cases for ObsidianParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ObsidianParser()
    
    def test_parse_file_with_front_matter(self):
        """Test parsing file with front matter."""
        content = """---
title: Test Note
tags: [test, example]
created: 2024-01-01
---

# Test Content

This is a test note with [[wikilinks]] and #tags.

> [!note] Callout
> This is a callout block.
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            file_path = Path(f.name)
        
        try:
            note = self.parser.parse_file(file_path)
            
            assert isinstance(note, ObsidianNote)
            assert note.title == "Test Note"
            assert note.file_path == file_path
            assert "Test Content" in note.content
            assert "test" in note.tags
            assert "example" in note.tags
            assert note.created_date == "2024-01-01"
            assert "wikilinks" in note.links
            
        finally:
            file_path.unlink()
    
    def test_parse_file_without_front_matter(self):
        """Test parsing file without front matter."""
        content = """# Test Note

This is a test note without front matter.

- [[Link 1]]
- [[Link 2|Display Text]]
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            file_path = Path(f.name)
        
        try:
            note = self.parser.parse_file(file_path)
            
            assert note.title == file_path.stem
            assert "Test Note" in note.content
            assert "Link 1" in note.links
            assert "Link 2" in note.links
            
        finally:
            file_path.unlink()
    
    def test_extract_tags_from_content(self):
        """Test extracting tags from content."""
        content = """# Test Note

This note has #tag1 and #tag2 in the content.

Also has #another-tag and #tag_with_underscore.
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            file_path = Path(f.name)
        
        try:
            note = self.parser.parse_file(file_path)
            
            expected_tags = {"tag1", "tag2", "another-tag", "tag_with_underscore"}
            assert note.tags == expected_tags
            
        finally:
            file_path.unlink()
    
    def test_extract_tags_from_front_matter(self):
        """Test extracting tags from front matter."""
        content = """---
title: Test Note
tags: [front-matter-tag, another-tag]
---

# Content

This has #content-tag.
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            file_path = Path(f.name)
        
        try:
            note = self.parser.parse_file(file_path)
            
            expected_tags = {"front-matter-tag", "another-tag", "content-tag"}
            assert note.tags == expected_tags
            
        finally:
            file_path.unlink()
    
    def test_extract_links(self):
        """Test extracting wikilinks from content."""
        content = """# Test Note

Here are some links:
- [[Simple Link]]
- [[Link with display|Display Text]]
- [[Nested/Link/Path]]
- [[Link with spaces]]

External links should not be extracted:
- [External Link](https://example.com)
"""
        
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            file_path = Path(f.name)
        
        try:
            note = self.parser.parse_file(file_path)
            
            expected_links = ["Simple Link", "Link with display", "Nested/Link/Path", "Link with spaces"]
            assert set(note.links) == set(expected_links)
            
        finally:
            file_path.unlink()
    
    def test_convert_wikilinks(self):
        """Test converting wikilinks to markdown links."""
        content = "This has [[Link 1]] and [[Link 2|Display Text]]."
        link_mapping = {
            "Link 1": "/link-1",
            "Link 2": "/link-2"
        }
        
        result = self.parser.convert_wikilinks(content, link_mapping)
        
        expected = "This has [Link 1](/link-1) and [Display Text](/link-2)."
        assert result == expected
    
    def test_convert_callouts(self):
        """Test converting Obsidian callouts to Hugo format."""
        content = """# Test Note

> [!note] Note Title
> This is a note callout.

> [!warning] Warning Title
> This is a warning callout.

> [!error] Error Title
> This is an error callout.
"""
        
        result = self.parser.convert_callouts(content)
        
        assert "{{< admonition type=\"note\" title=\"Note Title\" >}}" in result
        assert "{{< admonition type=\"warning\" title=\"Warning Title\" >}}" in result
        assert "{{< admonition type=\"danger\" title=\"Error Title\" >}}" in result
    
    def test_convert_code_blocks(self):
        """Test converting code blocks."""
        content = """# Test Note

```python
def hello():
    print("Hello, World!")
```

```bash
echo "Hello"
```
"""
        
        result = self.parser.convert_code_blocks(content)
        
        # Should preserve code blocks as they are
        assert "```python" in result
        assert "```bash" in result
        assert "def hello():" in result
        assert "echo \"Hello\"" in result
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        non_existent_path = Path("/non/existent/file.md")
        
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file(non_existent_path)