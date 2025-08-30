"""Unit tests for Hugo converter."""

import pytest
import tempfile
import shutil
from pathlib import Path

from obsidian_to_hugo.core.models import ConversionConfig, ObsidianNote
from obsidian_to_hugo.converters.hugo_converter import HugoConverter


class TestHugoConverter:
    """Test cases for HugoConverter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.obsidian_vault = Path(self.temp_dir) / "obsidian"
        self.hugo_content = Path(self.temp_dir) / "hugo" / "content"
        self.hugo_static = Path(self.temp_dir) / "hugo" / "static"
        self.hugo_archetypes = Path(self.temp_dir) / "hugo" / "archetypes"
        
        # Create test directory structure
        self.obsidian_vault.mkdir(parents=True, exist_ok=True)
        self.hugo_content.mkdir(parents=True, exist_ok=True)
        self.hugo_static.mkdir(parents=True, exist_ok=True)
        self.hugo_archetypes.mkdir(parents=True, exist_ok=True)
        
        # Create test configuration
        self.config = ConversionConfig(
            obsidian_vault_path=self.obsidian_vault,
            hugo_content_path=self.hugo_content,
            hugo_static_path=self.hugo_static,
            hugo_archetypes_path=self.hugo_archetypes,
            theme_name="hugo-papermod",
            preserve_front_matter=True,
            convert_wikilinks=True,
            convert_tags=True,
            convert_attachments=True,
            create_toc=True,
            toc_max_depth=3
        )
        
        self.converter = HugoConverter(self.config)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_find_markdown_files(self):
        """Test finding markdown files in vault."""
        # Create test files
        (self.obsidian_vault / "note1.md").write_text("# Note 1")
        (self.obsidian_vault / "note2.md").write_text("# Note 2")
        (self.obsidian_vault / "image.png").write_text("fake image")
        (self.obsidian_vault / "subdir" / "note3.md").write_text("# Note 3")
        
        files = self.converter._find_markdown_files()
        
        assert len(files) == 3
        file_names = [f.name for f in files]
        assert "note1.md" in file_names
        assert "note2.md" in file_names
        assert "note3.md" in file_names
    
    def test_find_markdown_files_with_exclusions(self):
        """Test finding markdown files with exclusion patterns."""
        # Update config with exclusions
        self.config.exclude_patterns = ["**/draft/*"]
        
        # Create test files
        (self.obsidian_vault / "note1.md").write_text("# Note 1")
        (self.obsidian_vault / "draft" / "note2.md").write_text("# Note 2")
        (self.obsidian_vault / "published" / "note3.md").write_text("# Note 3")
        
        files = self.converter._find_markdown_files()
        
        assert len(files) == 2
        file_names = [f.name for f in files]
        assert "note1.md" in file_names
        assert "note3.md" in file_names
        assert "note2.md" not in file_names
    
    def test_convert_to_hugo_path(self):
        """Test converting Obsidian paths to Hugo paths."""
        # Test basic conversion
        relative_path = Path("note.md")
        hugo_path = self.converter._convert_to_hugo_path(relative_path)
        assert hugo_path == Path("note")
        
        # Test nested path
        relative_path = Path("folder/subfolder/note.md")
        hugo_path = self.converter._convert_to_hugo_path(relative_path)
        assert hugo_path == Path("folder/subfolder/note")
        
        # Test index file
        relative_path = Path("index.md")
        hugo_path = self.converter._convert_to_hugo_path(relative_path)
        assert hugo_path == Path("_index")
    
    def test_create_hugo_front_matter(self):
        """Test creating Hugo front matter from Obsidian note."""
        obsidian_note = ObsidianNote(
            file_path=Path("test.md"),
            title="Test Note",
            content="# Test Content",
            front_matter={"custom_field": "value"},
            tags={"tag1", "tag2"},
            links=["link1", "link2"],
            created_date="2024-01-01",
            modified_date="2024-01-02"
        )
        
        front_matter = self.converter._create_hugo_front_matter(obsidian_note)
        
        assert front_matter["title"] == "Test Note"
        assert front_matter["date"] == "2024-01-01"
        assert front_matter["lastmod"] == "2024-01-02"
        assert front_matter["tags"] == ["tag1", "tag2"]
        assert front_matter["custom_field"] == "value"
        assert front_matter["showToc"] is True
        assert front_matter["showWordCount"] is True
        assert front_matter["showReadingTime"] is True
    
    def test_process_tags(self):
        """Test processing tags in content."""
        content = "This has #tag1 and #tag2 in the content."
        tags = {"tag1", "tag2"}
        
        result = self.converter._process_tags(content, tags)
        
        # Tags should be removed from content
        assert "#tag1" not in result
        assert "#tag2" not in result
        assert "This has" in result
        assert "in the content." in result
    
    def test_add_table_of_contents(self):
        """Test adding table of contents."""
        content = "# Heading 1\n\n## Heading 2\n\nContent here."
        
        result = self.converter._add_table_of_contents(content)
        
        assert "{{< toc maxdepth=\"3\" >}}" in result
        assert content in result
    
    def test_copy_attachments(self):
        """Test copying attachments."""
        # Create test attachments
        (self.obsidian_vault / "image1.png").write_text("fake image 1")
        (self.obsidian_vault / "subdir" / "image2.jpg").write_text("fake image 2")
        (self.obsidian_vault / "document.pdf").write_text("fake pdf")
        (self.obsidian_vault / "note.md").write_text("# Note")  # Should not be copied
        
        copied_count = self.converter._copy_attachments()
        
        assert copied_count == 3
        assert (self.hugo_static / "image1.png").exists()
        assert (self.hugo_static / "subdir" / "image2.jpg").exists()
        assert (self.hugo_static / "document.pdf").exists()
        assert not (self.hugo_static / "note.md").exists()
    
    def test_build_link_mapping(self):
        """Test building link mapping."""
        # Create test files
        (self.obsidian_vault / "note1.md").write_text("# Note 1")
        (self.obsidian_vault / "folder" / "note2.md").write_text("# Note 2")
        
        files = [self.obsidian_vault / "note1.md", self.obsidian_vault / "folder" / "note2.md"]
        self.converter._build_link_mapping(files)
        
        assert "note1" in self.converter.link_mapping
        assert "note2" in self.converter.link_mapping
        assert self.converter.link_mapping["note1"] == "note1"
        assert self.converter.link_mapping["note2"] == "folder/note2"
    
    def test_convert_empty_vault(self):
        """Test converting empty vault."""
        stats = self.converter.convert()
        
        assert stats.total_files == 0
        assert stats.converted_files == 0
        assert stats.skipped_files == 0
        assert stats.error_files == 0
    
    def test_convert_single_file(self):
        """Test converting a single file."""
        # Create test file
        test_content = """---
title: Test Note
tags: [test, example]
---

# Test Content

This is a test note with [[wikilinks]] and #tags.

> [!note] Callout
> This is a callout block.
"""
        (self.obsidian_vault / "test.md").write_text(test_content)
        
        # Convert
        stats = self.converter.convert()
        
        assert stats.total_files == 1
        assert stats.converted_files == 1
        assert stats.error_files == 0
        
        # Check output file
        output_file = self.hugo_content / "test.md"
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "title: Test Note" in content
        assert "tags: [test, example]" in content
        assert "{{< toc maxdepth=\"3\" >}}" in content
        assert "{{< admonition type=\"note\"" in content