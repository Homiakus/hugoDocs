"""Main window for Obsidian to Hugo converter GUI."""

import sys
import threading
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QFileDialog, QCheckBox, QSpinBox, QGroupBox, QFormLayout, QMessageBox,
    QSplitter, QListWidget, QListWidgetItem, QComboBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap

from qt_material import apply_stylesheet

from ..core.models import ConversionConfig, ConversionStats
from ..converters.hugo_converter import HugoConverter
from ..watchers.file_watcher import FileWatcher
from ..utils.obsidian_parser import ObsidianParser


class ConversionWorker(QThread):
    """Worker thread for conversion operations."""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(ConversionStats)
    error = pyqtSignal(str)
    
    def __init__(self, config: ConversionConfig):
        super().__init__()
        self.config = config
        
    def run(self):
        """Run the conversion."""
        try:
            self.progress.emit("Starting conversion...")
            converter = HugoConverter(self.config)
            stats = converter.convert()
            self.finished.emit(stats)
        except Exception as e:
            self.error.emit(str(e))


class WatchWorker(QThread):
    """Worker thread for file watching."""
    
    file_changed = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, obsidian_vault: Path):
        super().__init__()
        self.obsidian_vault = obsidian_vault
        self.watcher = None
        self.running = False
        
    def run(self):
        """Start file watching."""
        try:
            self.running = True
            self.watcher = FileWatcher(self.obsidian_vault)
            self.watcher.start()
            
            # Keep the thread alive
            while self.running:
                self.msleep(100)
                
        except Exception as e:
            self.error.emit(str(e))
            
    def stop(self):
        """Stop file watching."""
        self.running = False
        if self.watcher:
            self.watcher.stop()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.conversion_worker = None
        self.watch_worker = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Obsidian to Hugo Converter")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply Material Design theme
        apply_stylesheet(self, theme='light_blue.xml')
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Configuration
        left_panel = self.create_config_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Tabs for different functions
        right_panel = self.create_tab_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
    def create_config_panel(self) -> QWidget:
        """Create the configuration panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Configuration")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Obsidian Vault
        vault_group = QGroupBox("Obsidian Vault")
        vault_layout = QFormLayout(vault_group)
        
        self.vault_path = QLineEdit()
        self.vault_path.setPlaceholderText("Select Obsidian vault directory...")
        vault_browse = QPushButton("Browse")
        vault_browse.clicked.connect(self.browse_vault)
        
        vault_path_layout = QHBoxLayout()
        vault_path_layout.addWidget(self.vault_path)
        vault_path_layout.addWidget(vault_browse)
        vault_layout.addRow("Vault Path:", vault_path_layout)
        
        layout.addWidget(vault_group)
        
        # Hugo Output
        hugo_group = QGroupBox("Hugo Output")
        hugo_layout = QFormLayout(hugo_group)
        
        self.hugo_content = QLineEdit()
        self.hugo_content.setPlaceholderText("Select Hugo content directory...")
        content_browse = QPushButton("Browse")
        content_browse.clicked.connect(self.browse_content)
        
        content_layout = QHBoxLayout()
        content_layout.addWidget(self.hugo_content)
        content_layout.addWidget(content_browse)
        hugo_layout.addRow("Content Path:", content_layout)
        
        self.hugo_static = QLineEdit()
        self.hugo_static.setPlaceholderText("Select Hugo static directory...")
        static_browse = QPushButton("Browse")
        static_browse.clicked.connect(self.browse_static)
        
        static_layout = QHBoxLayout()
        static_layout.addWidget(self.hugo_static)
        static_layout.addWidget(static_browse)
        hugo_layout.addRow("Static Path:", static_layout)
        
        layout.addWidget(hugo_group)
        
        # Conversion Options
        options_group = QGroupBox("Conversion Options")
        options_layout = QFormLayout(options_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["hugo-papermod", "hugo-theme-stack", "hugo-theme-terminal"])
        options_layout.addRow("Theme:", self.theme_combo)
        
        self.toc_depth = QSpinBox()
        self.toc_depth.setRange(1, 6)
        self.toc_depth.setValue(3)
        options_layout.addRow("TOC Depth:", self.toc_depth)
        
        self.convert_wikilinks = QCheckBox("Convert Wikilinks")
        self.convert_wikilinks.setChecked(True)
        options_layout.addRow(self.convert_wikilinks)
        
        self.convert_tags = QCheckBox("Convert Tags")
        self.convert_tags.setChecked(True)
        options_layout.addRow(self.convert_tags)
        
        self.convert_attachments = QCheckBox("Convert Attachments")
        self.convert_attachments.setChecked(True)
        options_layout.addRow(self.convert_attachments)
        
        self.create_toc = QCheckBox("Create Table of Contents")
        self.create_toc.setChecked(True)
        options_layout.addRow(self.create_toc)
        
        layout.addWidget(options_group)
        
        # Action Buttons
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        actions_layout.addWidget(self.convert_btn)
        
        self.watch_btn = QPushButton("Start Watching")
        self.watch_btn.clicked.connect(self.toggle_watching)
        self.watch_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """)
        actions_layout.addWidget(self.watch_btn)
        
        self.analyze_btn = QPushButton("Analyze Vault")
        self.analyze_btn.clicked.connect(self.analyze_vault)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """)
        actions_layout.addWidget(self.analyze_btn)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        return panel
        
    def create_tab_panel(self) -> QWidget:
        """Create the tab panel for different functions."""
        tab_widget = QTabWidget()
        
        # Conversion Tab
        conversion_tab = self.create_conversion_tab()
        tab_widget.addTab(conversion_tab, "Conversion")
        
        # Watch Tab
        watch_tab = self.create_watch_tab()
        tab_widget.addTab(watch_tab, "File Watching")
        
        # Analysis Tab
        analysis_tab = self.create_analysis_tab()
        tab_widget.addTab(analysis_tab, "Vault Analysis")
        
        # Logs Tab
        logs_tab = self.create_logs_tab()
        tab_widget.addTab(logs_tab, "Logs")
        
        return tab_widget
        
    def create_conversion_tab(self) -> QWidget:
        """Create the conversion tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Ready to convert")
        layout.addWidget(self.status_label)
        
        # Results
        results_group = QGroupBox("Conversion Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        return tab
        
    def create_watch_tab(self) -> QWidget:
        """Create the file watching tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Status
        self.watch_status = QLabel("File watching is not active")
        layout.addWidget(self.watch_status)
        
        # File list
        files_group = QGroupBox("Changed Files")
        files_layout = QVBoxLayout(files_group)
        
        self.changed_files = QListWidget()
        files_layout.addWidget(self.changed_files)
        
        layout.addWidget(files_group)
        
        return tab
        
    def create_analysis_tab(self) -> QWidget:
        """Create the vault analysis tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Analysis results
        analysis_group = QGroupBox("Vault Analysis")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        analysis_layout.addWidget(self.analysis_text)
        
        layout.addWidget(analysis_group)
        
        return tab
        
    def create_logs_tab(self) -> QWidget:
        """Create the logs tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Logs
        logs_group = QGroupBox("Application Logs")
        logs_layout = QVBoxLayout(logs_group)
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        logs_layout.addWidget(self.logs_text)
        
        # Clear logs button
        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        logs_layout.addWidget(clear_logs_btn)
        
        layout.addWidget(logs_group)
        
        return tab
        
    def browse_vault(self):
        """Browse for Obsidian vault directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Obsidian Vault")
        if directory:
            self.vault_path.setText(directory)
            
    def browse_content(self):
        """Browse for Hugo content directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Hugo Content Directory")
        if directory:
            self.hugo_content.setText(directory)
            
    def browse_static(self):
        """Browse for Hugo static directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Hugo Static Directory")
        if directory:
            self.hugo_static.setText(directory)
            
    def get_config(self) -> Optional[ConversionConfig]:
        """Get conversion configuration from UI."""
        vault_path = Path(self.vault_path.text())
        content_path = Path(self.hugo_content.text())
        static_path = Path(self.hugo_static.text())
        
        if not vault_path.exists():
            QMessageBox.warning(self, "Error", "Obsidian vault path does not exist")
            return None
            
        if not content_path.exists():
            QMessageBox.warning(self, "Error", "Hugo content path does not exist")
            return None
            
        if not static_path.exists():
            QMessageBox.warning(self, "Error", "Hugo static path does not exist")
            return None
            
        return ConversionConfig(
            obsidian_vault_path=vault_path,
            hugo_content_path=content_path,
            hugo_static_path=static_path,
            theme_name=self.theme_combo.currentText(),
            convert_wikilinks=self.convert_wikilinks.isChecked(),
            convert_tags=self.convert_tags.isChecked(),
            convert_attachments=self.convert_attachments.isChecked(),
            create_toc=self.create_toc.isChecked(),
            toc_max_depth=self.toc_depth.value()
        )
        
    def start_conversion(self):
        """Start the conversion process."""
        config = self.get_config()
        if not config:
            return
            
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Converting...")
        
        self.conversion_worker = ConversionWorker(config)
        self.conversion_worker.progress.connect(self.update_progress)
        self.conversion_worker.finished.connect(self.conversion_finished)
        self.conversion_worker.error.connect(self.conversion_error)
        self.conversion_worker.start()
        
    def update_progress(self, message: str):
        """Update progress message."""
        self.status_label.setText(message)
        self.logs_text.append(f"[INFO] {message}")
        
    def conversion_finished(self, stats: ConversionStats):
        """Handle conversion completion."""
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Conversion completed successfully!")
        
        # Display results
        results = f"""
Conversion Results:
==================
Processing Time: {stats.processing_time:.2f}s
Total Files: {stats.total_files}
Converted Files: {stats.converted_files}
Skipped Files: {stats.skipped_files}
Error Files: {stats.error_files}
Attachments Copied: {stats.attachments_copied}
Links Converted: {stats.links_converted}
Tags Processed: {stats.tags_processed}
"""
        self.results_text.setText(results)
        self.logs_text.append(f"[SUCCESS] Conversion completed in {stats.processing_time:.2f}s")
        
    def conversion_error(self, error: str):
        """Handle conversion error."""
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Conversion failed!")
        QMessageBox.critical(self, "Error", f"Conversion failed: {error}")
        self.logs_text.append(f"[ERROR] {error}")
        
    def toggle_watching(self):
        """Toggle file watching."""
        if self.watch_worker and self.watch_worker.isRunning():
            self.stop_watching()
        else:
            self.start_watching()
            
    def start_watching(self):
        """Start file watching."""
        vault_path = Path(self.vault_path.text())
        if not vault_path.exists():
            QMessageBox.warning(self, "Error", "Please select a valid Obsidian vault first")
            return
            
        self.watch_worker = WatchWorker(vault_path)
        self.watch_worker.file_changed.connect(self.file_changed)
        self.watch_worker.error.connect(self.watch_error)
        self.watch_worker.start()
        
        self.watch_btn.setText("Stop Watching")
        self.watch_status.setText("File watching is active")
        self.logs_text.append("[INFO] File watching started")
        
    def stop_watching(self):
        """Stop file watching."""
        if self.watch_worker:
            self.watch_worker.stop()
            self.watch_worker.wait()
            
        self.watch_btn.setText("Start Watching")
        self.watch_status.setText("File watching is not active")
        self.logs_text.append("[INFO] File watching stopped")
        
    def file_changed(self, file_path: str):
        """Handle file change event."""
        item = QListWidgetItem(f"{file_path} - {QTimer().remainingTime()}")
        self.changed_files.insertItem(0, item)
        self.logs_text.append(f"[INFO] File changed: {file_path}")
        
    def watch_error(self, error: str):
        """Handle watch error."""
        QMessageBox.critical(self, "Watch Error", f"File watching error: {error}")
        self.logs_text.append(f"[ERROR] Watch error: {error}")
        
    def analyze_vault(self):
        """Analyze the Obsidian vault."""
        vault_path = Path(self.vault_path.text())
        if not vault_path.exists():
            QMessageBox.warning(self, "Error", "Please select a valid Obsidian vault first")
            return
            
        try:
            parser = ObsidianParser()
            markdown_files = list(vault_path.rglob("*.md"))
            
            analysis = f"""
Vault Analysis:
===============
Vault Path: {vault_path}
Total Markdown Files: {len(markdown_files)}

Files by Directory:
"""
            
            # Group files by directory
            dir_files = {}
            for file in markdown_files:
                rel_path = file.relative_to(vault_path)
                dir_name = str(rel_path.parent) if rel_path.parent != Path('.') else 'Root'
                if dir_name not in dir_files:
                    dir_files[dir_name] = []
                dir_files[dir_name].append(rel_path.name)
                
            for dir_name, files in dir_files.items():
                analysis += f"\n{dir_name}/ ({len(files)} files):\n"
                for file in files[:5]:  # Show first 5 files
                    analysis += f"  - {file}\n"
                if len(files) > 5:
                    analysis += f"  ... and {len(files) - 5} more\n"
                    
            self.analysis_text.setText(analysis)
            self.logs_text.append(f"[INFO] Vault analysis completed: {len(markdown_files)} files found")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {e}")
            self.logs_text.append(f"[ERROR] Analysis error: {e}")
            
    def clear_logs(self):
        """Clear the logs."""
        self.logs_text.clear()
        self.logs_text.append("[INFO] Logs cleared")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Obsidian to Hugo Converter")
    app.setApplicationVersion("0.2.0")
    app.setOrganizationName("Obsidian to Hugo")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()