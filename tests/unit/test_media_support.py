"""Tests for media file support (GLTF, PDF, images)."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from obsidian_to_hugo.utils.obsidian_parser import ObsidianParser


class TestMediaSupport:
    """Test media file support functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ObsidianParser()
    
    def test_convert_pdf_links(self):
        """Test conversion of PDF links to Hugo shortcodes."""
        content = """
        # Test Document
        
        [User Manual](manual.pdf)
        [Technical Spec](spec.pdf)
        """
        
        result = self.parser.convert_media_links(content)
        
        assert "{{< pdf-viewer url=\"manual.pdf\" title=\"User Manual\" >}}" in result
        assert "{{< pdf-viewer url=\"spec.pdf\" title=\"Technical Spec\" >}}" in result
    
    def test_convert_gltf_links(self):
        """Test conversion of GLTF links to Hugo shortcodes."""
        content = """
        # 3D Models
        
        [Robot Model](robot.gltf)
        [Car Model](car.glb)
        """
        
        result = self.parser.convert_media_links(content)
        
        assert "{{< gltf-viewer url=\"robot.gltf\" title=\"Robot Model\" >}}" in result
        assert "{{< gltf-viewer url=\"car.glb\" title=\"Car Model\" >}}" in result
    
    def test_convert_image_links(self):
        """Test conversion of image links to Hugo shortcodes."""
        content = """
        # Images
        
        ![Screenshot](screenshot.png)
        ![Diagram](diagram.svg)
        """
        
        result = self.parser.convert_media_links(content)
        
        assert "{{< image src=\"screenshot.png\" alt=\"Screenshot\" >}}" in result
        assert "{{< image src=\"diagram.svg\" alt=\"Diagram\" >}}" in result
    
    def test_convert_mixed_media_links(self):
        """Test conversion of mixed media types."""
        content = """
        # Mixed Media
        
        [Document](report.pdf)
        [3D Model](model.gltf)
        ![Photo](photo.jpg)
        """
        
        result = self.parser.convert_media_links(content)
        
        assert "{{< pdf-viewer url=\"report.pdf\" title=\"Document\" >}}" in result
        assert "{{< gltf-viewer url=\"model.gltf\" title=\"3D Model\" >}}" in result
        assert "{{< image src=\"photo.jpg\" alt=\"Photo\" >}}" in result
    
    def test_preserve_regular_links(self):
        """Test that regular links are not converted."""
        content = """
        # Regular Links
        
        [Google](https://google.com)
        [Internal Link](internal-page)
        """
        
        result = self.parser.convert_media_links(content)
        
        # Should not be converted
        assert "[Google](https://google.com)" in result
        assert "[Internal Link](internal-page)" in result
    
    def test_handle_empty_alt_text(self):
        """Test handling of images with empty alt text."""
        content = """
        ![](image.png)
        """
        
        result = self.parser.convert_media_links(content)
        
        assert "{{< image src=\"image.png\" alt=\"\" >}}" in result
    
    def test_handle_special_characters_in_titles(self):
        """Test handling of special characters in link titles."""
        content = """
        [User's Manual (v2.0)](manual.pdf)
        [3D Model - Robot](robot.gltf)
        """
        
        result = self.parser.convert_media_links(content)
        
        assert "{{< pdf-viewer url=\"manual.pdf\" title=\"User's Manual (v2.0)\" >}}" in result
        assert "{{< gltf-viewer url=\"robot.gltf\" title=\"3D Model - Robot\" >}}" in result
    
    def test_attachment_extensions_in_config(self):
        """Test that GLTF and GLB are included in default attachment extensions."""
        from obsidian_to_hugo.core.models import ConversionConfig
        
        config = ConversionConfig()
        
        assert "gltf" in config.attachment_extensions
        assert "glb" in config.attachment_extensions
        assert "pdf" in config.attachment_extensions
    
    def test_media_link_patterns(self):
        """Test that media link patterns are correctly defined."""
        # Test PDF pattern
        pdf_match = self.parser.pdf_link_pattern.search("[Document](file.pdf)")
        assert pdf_match is not None
        assert pdf_match.group(1) == "Document"
        assert pdf_match.group(2) == "file.pdf"
        
        # Test GLTF pattern
        gltf_match = self.parser.gltf_link_pattern.search("[Model](model.gltf)")
        assert gltf_match is not None
        assert gltf_match.group(1) == "Model"
        assert gltf_match.group(2) == "model.gltf"
        
        # Test GLB pattern
        glb_match = self.parser.gltf_link_pattern.search("[Model](model.glb)")
        assert glb_match is not None
        assert glb_match.group(1) == "Model"
        assert glb_match.group(2) == "model.glb"
        
        # Test image pattern
        img_match = self.parser.media_link_pattern.search("![Alt](image.png)")
        assert img_match is not None
        assert img_match.group(1) == "Alt"
        assert img_match.group(2) == "image.png"
    
    def test_no_false_positives(self):
        """Test that non-media links are not incorrectly matched."""
        content = """
        [Regular Link](https://example.com)
        [Internal Page](internal-page)
        ![Image](image.png)
        [PDF](document.pdf)
        [GLTF](model.gltf)
        """
        
        result = self.parser.convert_media_links(content)
        
        # Regular links should not be converted
        assert "[Regular Link](https://example.com)" in result
        assert "[Internal Page](internal-page)" in result
        
        # Media links should be converted
        assert "{{< image src=\"image.png\" alt=\"Image\" >}}" in result
        assert "{{< pdf-viewer url=\"document.pdf\" title=\"PDF\" >}}" in result
        assert "{{< gltf-viewer url=\"model.gltf\" title=\"GLTF\" >}}" in result