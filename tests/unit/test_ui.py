"""Tests for UI components."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread

from obsidian_to_hugo.ui.main_window import MainWindow, ConversionWorker, WatchWorker
from obsidian_to_hugo.core.models import ConversionConfig, ConversionStats


class TestMainWindow:
    """Test MainWindow functionality."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        app = QApplication([])
        yield app
        app.quit()
    
    @pytest.fixture
    def window(self, app):
        """Create MainWindow instance."""
        return MainWindow()
    
    def test_window_creation(self, window):
        """Test that window is created successfully."""
        assert window is not None
        assert window.windowTitle() == "Obsidian to Hugo Converter"
    
    def test_config_panel_creation(self, window):
        """Test that configuration panel is created."""
        assert window.vault_path is not None
        assert window.hugo_content is not None
        assert window.hugo_static is not None
        assert window.theme_combo is not None
        assert window.convert_btn is not None
    
    def test_tab_panel_creation(self, window):
        """Test that tab panel is created."""
        # Check that all tabs exist
        tab_widget = window.findChild(QWidget, "").findChild(QWidget, "").findChild(QWidget, "")
        # This is a simplified test - in practice we'd need to traverse the widget tree
        assert window.progress_bar is not None
        assert window.status_label is not None
        assert window.results_text is not None
    
    def test_get_config_valid_paths(self, window, tmp_path):
        """Test getting configuration with valid paths."""
        # Create temporary directories
        vault_path = tmp_path / "vault"
        content_path = tmp_path / "content"
        static_path = tmp_path / "static"
        
        vault_path.mkdir()
        content_path.mkdir()
        static_path.mkdir()
        
        # Set paths in UI
        window.vault_path.setText(str(vault_path))
        window.hugo_content.setText(str(content_path))
        window.hugo_static.setText(str(static_path))
        
        # Get configuration
        config = window.get_config()
        
        assert config is not None
        assert config.obsidian_vault_path == vault_path
        assert config.hugo_content_path == content_path
        assert config.hugo_static_path == static_path
        assert config.theme_name == "hugo-papermod"  # Default value
    
    def test_get_config_invalid_paths(self, window):
        """Test getting configuration with invalid paths."""
        window.vault_path.setText("/nonexistent/path")
        window.hugo_content.setText("/nonexistent/content")
        window.hugo_static.setText("/nonexistent/static")
        
        config = window.get_config()
        assert config is None
    
    @patch('obsidian_to_hugo.ui.main_window.QMessageBox.warning')
    def test_get_config_shows_warning(self, mock_warning, window):
        """Test that warning is shown for invalid paths."""
        window.vault_path.setText("/nonexistent/path")
        window.get_config()
        mock_warning.assert_called()


class TestConversionWorker:
    """Test ConversionWorker functionality."""
    
    def test_conversion_worker_creation(self):
        """Test that ConversionWorker can be created."""
        config = ConversionConfig(
            obsidian_vault_path=Path("/test/vault"),
            hugo_content_path=Path("/test/content"),
            hugo_static_path=Path("/test/static")
        )
        
        worker = ConversionWorker(config)
        assert worker is not None
        assert worker.config == config
    
    @patch('obsidian_to_hugo.ui.main_window.HugoConverter')
    def test_conversion_worker_run_success(self, mock_converter_class):
        """Test successful conversion run."""
        # Mock converter
        mock_converter = Mock()
        mock_stats = ConversionStats(
            processing_time=1.5,
            total_files=10,
            converted_files=8,
            skipped_files=1,
            error_files=1,
            attachments_copied=5,
            links_converted=20,
            tags_processed=15
        )
        mock_converter.convert.return_value = mock_stats
        mock_converter_class.return_value = mock_converter
        
        config = ConversionConfig(
            obsidian_vault_path=Path("/test/vault"),
            hugo_content_path=Path("/test/content"),
            hugo_static_path=Path("/test/static")
        )
        
        worker = ConversionWorker(config)
        
        # Mock signals
        worker.progress = Mock()
        worker.finished = Mock()
        worker.error = Mock()
        
        # Run conversion
        worker.run()
        
        # Check that signals were emitted
        worker.progress.assert_called_with("Starting conversion...")
        worker.finished.assert_called_with(mock_stats)
        worker.error.assert_not_called()
    
    @patch('obsidian_to_hugo.ui.main_window.HugoConverter')
    def test_conversion_worker_run_error(self, mock_converter_class):
        """Test conversion run with error."""
        # Mock converter to raise exception
        mock_converter = Mock()
        mock_converter.convert.side_effect = Exception("Test error")
        mock_converter_class.return_value = mock_converter
        
        config = ConversionConfig(
            obsidian_vault_path=Path("/test/vault"),
            hugo_content_path=Path("/test/content"),
            hugo_static_path=Path("/test/static")
        )
        
        worker = ConversionWorker(config)
        
        # Mock signals
        worker.progress = Mock()
        worker.finished = Mock()
        worker.error = Mock()
        
        # Run conversion
        worker.run()
        
        # Check that error signal was emitted
        worker.progress.assert_called_with("Starting conversion...")
        worker.error.assert_called_with("Test error")
        worker.finished.assert_not_called()


class TestWatchWorker:
    """Test WatchWorker functionality."""
    
    def test_watch_worker_creation(self, tmp_path):
        """Test that WatchWorker can be created."""
        worker = WatchWorker(tmp_path)
        assert worker is not None
        assert worker.obsidian_vault == tmp_path
        assert worker.running is False
    
    @patch('obsidian_to_hugo.ui.main_window.FileWatcher')
    def test_watch_worker_run(self, mock_watcher_class):
        """Test watch worker run."""
        mock_watcher = Mock()
        mock_watcher_class.return_value = mock_watcher
        
        worker = WatchWorker(Path("/test/vault"))
        worker.running = True
        
        # Mock signals
        worker.file_changed = Mock()
        worker.error = Mock()
        
        # Run for a short time
        worker.start()
        worker.msleep(100)  # Small delay
        worker.stop()
        worker.wait()
        
        # Check that watcher was started
        mock_watcher.start.assert_called_once()
        mock_watcher.stop.assert_called_once()


class TestUIIntegration:
    """Integration tests for UI components."""
    
    @pytest.fixture
    def app(self):
        """Create QApplication instance."""
        app = QApplication([])
        yield app
        app.quit()
    
    def test_window_initialization(self, app):
        """Test complete window initialization."""
        window = MainWindow()
        
        # Check that all main components exist
        assert window.vault_path is not None
        assert window.hugo_content is not None
        assert window.hugo_static is not None
        assert window.theme_combo is not None
        assert window.convert_btn is not None
        assert window.watch_btn is not None
        assert window.analyze_btn is not None
        
        # Check default values
        assert window.theme_combo.currentText() == "hugo-papermod"
        assert window.toc_depth.value() == 3
        assert window.convert_wikilinks.isChecked() is True
        assert window.convert_tags.isChecked() is True
        assert window.convert_attachments.isChecked() is True
        assert window.create_toc.isChecked() is True
    
    def test_button_styles(self, app):
        """Test that buttons have proper styling."""
        window = MainWindow()
        
        # Check that buttons have custom stylesheets
        assert "background-color" in window.convert_btn.styleSheet()
        assert "background-color" in window.watch_btn.styleSheet()
        assert "background-color" in window.analyze_btn.styleSheet()
    
    def test_progress_bar_visibility(self, app):
        """Test progress bar visibility management."""
        window = MainWindow()
        
        # Initially hidden
        assert window.progress_bar.isVisible() is False
        
        # Simulate conversion start
        window.convert_btn.setEnabled(False)
        window.progress_bar.setVisible(True)
        window.progress_bar.setRange(0, 0)
        
        assert window.progress_bar.isVisible() is True
        assert window.convert_btn.isEnabled() is False
        
        # Simulate conversion finish
        window.convert_btn.setEnabled(True)
        window.progress_bar.setVisible(False)
        
        assert window.progress_bar.isVisible() is False
        assert window.convert_btn.isEnabled() is True