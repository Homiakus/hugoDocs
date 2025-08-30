"""Core data models for Obsidian to Hugo converter."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field


class ObsidianNote(BaseModel):
    """Represents an Obsidian note with metadata."""
    
    file_path: Path
    title: str
    content: str
    front_matter: Dict = Field(default_factory=dict)
    tags: Set[str] = Field(default_factory=set)
    links: List[str] = Field(default_factory=list)
    backlinks: List[str] = Field(default_factory=list)
    created_date: Optional[str] = None
    modified_date: Optional[str] = None


class HugoPost(BaseModel):
    """Represents a Hugo post/page."""
    
    file_path: Path
    title: str
    content: str
    front_matter: Dict = Field(default_factory=dict)
    url: str
    weight: int = 0
    draft: bool = False


class ConversionConfig(BaseModel):
    """Configuration for Obsidian to Hugo conversion."""
    
    obsidian_vault_path: Path
    hugo_content_path: Path
    hugo_static_path: Path
    hugo_archetypes_path: Path
    theme_name: str = "hugo-papermod"
    preserve_front_matter: bool = True
    convert_wikilinks: bool = True
    convert_tags: bool = True
    convert_attachments: bool = True
    attachment_extensions: Set[str] = Field(default_factory=lambda: {
        "png", "jpg", "jpeg", "gif", "svg", "pdf", "mp4", "mp3", "zip", "gltf", "glb"
    })
    exclude_patterns: List[str] = Field(default_factory=list)
    include_patterns: List[str] = Field(default_factory=lambda: ["*.md"])
    create_toc: bool = True
    toc_max_depth: int = 3


@dataclass
class ConversionStats:
    """Statistics about the conversion process."""
    
    total_files: int = 0
    converted_files: int = 0
    skipped_files: int = 0
    error_files: int = 0
    attachments_copied: int = 0
    links_converted: int = 0
    tags_processed: int = 0
    processing_time: float = 0.0
    
    def __str__(self) -> str:
        return (
            f"Conversion completed in {self.processing_time:.2f}s\n"
            f"Files: {self.converted_files}/{self.total_files} converted, "
            f"{self.skipped_files} skipped, {self.error_files} errors\n"
            f"Attachments: {self.attachments_copied} copied\n"
            f"Links: {self.links_converted} converted\n"
            f"Tags: {self.tags_processed} processed"
        )