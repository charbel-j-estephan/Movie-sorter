import sys
import json
import asyncio
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QMessageBox,
    QFileDialog,
)
from PySide6.QtCore import QThread, Signal
from movie_organizer_core import MovieOrganizer
from setup_dialog import SetupDialog
from movie_browser import MovieBrowser
from loading_screen import LoadingScreen


class MovieOrganizerThread(QThread):
    progress_updated = Signal(str, float)
    finished = Signal()
    error = Signal(str)

    def __init__(self, directory, api_key):
        super().__init__()
        self.directory = directory
        self.api_key = api_key

    def run(self):
        try:

            async def organize():
                async with MovieOrganizer(
                    self.api_key, self.progress_callback
                ) as organizer:
                    await organizer.process_movies(Path(self.directory))

            asyncio.run(organize())
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def progress_callback(self, operation, progress):
        self.progress_updated.emit(operation, progress)


class FileOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movie Organizer")
        self.setMinimumSize(1200, 800)

        # Initialize variables first
        self.current_directory = None
        self.api_key = None
        self.organizer_thread = None

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)

        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Create movie browser with mainwindow reference
        self.movie_browser = MovieBrowser(mainwindow=self)
        self.stacked_widget.addWidget(self.movie_browser)

        # Create loading screen
        self.loading_screen = LoadingScreen(self)
        self.loading_screen.hide()

        # Set application style
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f5f5;
            }
        """
        )

        # Check for first-time setup
        self.check_first_time_setup()

    def check_first_time_setup(self):
        """Check if this is first time running the app"""
        if not Path("settings.json").exists():
            setup_dialog = SetupDialog(self)
            if setup_dialog.exec():
                self.load_settings()
                self.select_directory()
            else:
                sys.exit()
        else:
            if self.load_settings() and self.current_directory:
                # If we have a saved directory, use it
                self.process_and_show_movies(self.current_directory)
            else:
                # If no saved directory or it doesn't exist anymore, ask for a new one
                self.select_directory()

    def load_settings(self):
        """Load settings from file"""
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.api_key = settings.get("api_key")
                saved_directory = settings.get("directory")
                if saved_directory and Path(saved_directory).exists():
                    self.current_directory = saved_directory
                    return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading settings: {str(e)}")
        return False

    def select_directory(self):
        """Select and set up movie directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Movie Directory")
        if directory:
            self.current_directory = directory
            # Save the directory to settings
            try:
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                settings["directory"] = directory
                with open("settings.json", "w") as f:
                    json.dump(settings, f)
            except Exception as e:
                QMessageBox.warning(
                    self, "Warning", f"Could not save directory to settings: {str(e)}"
                )

            self.process_and_show_movies(directory)

    def process_and_show_movies(self, directory):
        """Process movies and show in browser"""
        # Show loading screen
        self.loading_screen.center_on_parent()
        self.loading_screen.show()

        # Create and start worker thread
        self.organizer_thread = MovieOrganizerThread(directory, self.api_key)
        self.organizer_thread.progress_updated.connect(
            self.loading_screen.update_status
        )
        self.organizer_thread.finished.connect(self.processing_finished)
        self.organizer_thread.error.connect(self.processing_error)
        self.organizer_thread.start()

    def processing_finished(self):
        """Handle completion of movie processing"""
        self.loading_screen.hide()
        self.movie_browser.load_movies(self.current_directory)
        QMessageBox.information(self, "Success", "Movies organized successfully!")

    def processing_error(self, error_message):
        """Handle errors in movie processing"""
        self.loading_screen.hide()
        QMessageBox.critical(self, "Error", f"Error processing movies: {error_message}")

    def closeEvent(self, event):
        """Handle application closing"""
        # Stop the organizer thread if it's running
        if self.organizer_thread and self.organizer_thread.isRunning():
            self.organizer_thread.terminate()
            self.organizer_thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    window = FileOrganizerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
