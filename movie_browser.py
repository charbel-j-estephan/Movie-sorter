from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QComboBox,
    QSpacerItem,
    QSizePolicy,
    QGridLayout,
)
from PySide6.QtCore import Qt, QTimer
from pathlib import Path
from movie_tile import MovieTile


class MovieBrowser(QScrollArea):
    def __init__(self, mainwindow=None):
        super().__init__()
        self.mainwindow = mainwindow
        self.setup_ui()
        self.movies = []
        self.tiles_to_load = []
        self.current_load_index = 0
        self.load_timer = QTimer(self)
        self.load_timer.timeout.connect(self.load_next_batch)

    def setup_ui(self):
        # Make the scroll area look clean
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("QScrollArea { border: none; background-color: #f5f5f5; }")

        # Create main container widget
        container = QWidget()
        self.setWidget(container)

        # Main layout
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header section
        header_layout = QHBoxLayout()

        # Title with movie count
        self.title_label = QLabel("My Movies")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self.title_label)

        # Spacer
        header_layout.addStretch()

        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Genre", "Year"])
        self.sort_combo.setStyleSheet(
            """
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-width: 100px;
            }
        """
        )
        self.sort_combo.currentTextChanged.connect(self.sort_movies)
        header_layout.addWidget(QLabel("Sort by:"))
        header_layout.addWidget(self.sort_combo)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                padding: 5px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        refresh_btn.clicked.connect(self.refresh_movies)
        header_layout.addWidget(refresh_btn)

        main_layout.addLayout(header_layout)

        # Grid for movie tiles
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        main_layout.addLayout(self.grid_layout)

        # Add stretch at the bottom
        main_layout.addStretch()

    def is_duplicate_movie(self, movie_path, existing_movies):
        """
        Check if a movie is a duplicate based on name and quality
        Returns True if it's a duplicate, False otherwise
        """
        movie_name = movie_path.name.lower()

        # Remove quality indicators from name for comparison
        quality_indicators = ["2160p", "1080p", "720p", "480p", "576p"]
        base_name = movie_name
        for quality in quality_indicators:
            base_name = base_name.replace(quality, "").strip()

        # Check against existing movies
        for existing_movie in existing_movies:
            existing_name = existing_movie.name.lower()
            # Remove quality from existing name
            existing_base = existing_name
            for quality in quality_indicators:
                existing_base = existing_base.replace(quality, "").strip()

            if base_name == existing_base:
                # If it's the same movie, keep the higher quality version
                current_quality = self.get_quality_level(movie_path.name)
                existing_quality = self.get_quality_level(existing_movie.name)

                if current_quality > existing_quality:
                    # Remove the lower quality version
                    existing_movies.remove(existing_movie)
                    return False
                return True

        return False

    def get_quality_level(self, filename):
        """Get numerical quality level for comparison"""
        if "2160p" in filename:
            return 4
        elif "1080p" in filename:
            return 3
        elif "720p" in filename:
            return 2
        elif "576p" in filename:
            return 1
        elif "480p" in filename:
            return 0
        return -1  # No quality specified

    def load_movies(self, directory):
        """Load movies from the specified directory"""
        print(f"Loading movies from directory: {directory}")
        self.clear_movies()

        directory_path = Path(directory)
        unique_movies = []

        # Load movies from each folder
        for folder in directory_path.iterdir():
            if folder.is_dir() and folder.name not in [
                "movies info",
                "Manual Checking",
            ]:
                print(f"Scanning folder: {folder.name}")

                # Scan this folder for movie folders
                for movie_folder in folder.iterdir():
                    if movie_folder.is_dir():
                        if not self.is_duplicate_movie(movie_folder, unique_movies):
                            print(f"Found movie: {movie_folder.name}")
                            unique_movies.append(movie_folder)
                        else:
                            print(f"Skipping duplicate: {movie_folder.name}")

        self.movies = unique_movies
        print(f"Total unique movies found: {len(self.movies)}")

        # Update title with movie count
        self.title_label.setText(f"My Movies ({len(self.movies)})")

        # Sort movies initially by name
        self.sort_movies("Name")

        # Start loading movies in batches
        self.current_load_index = 0
        self.display_movies()

    def clear_movies(self):
        """Clear all movies from the grid"""
        print("Clearing existing movies")
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.movies.clear()
        self.load_timer.stop()

    def load_next_batch(self):
        """Load next batch of movies"""
        BATCH_SIZE = 10
        end_index = min(self.current_load_index + BATCH_SIZE, len(self.tiles_to_load))

        for i in range(self.current_load_index, end_index):
            movie_path, row, col = self.tiles_to_load[i]
            movie_tile = MovieTile(str(movie_path))
            self.grid_layout.addWidget(movie_tile, row, col)

        self.current_load_index = end_index
        if self.current_load_index >= len(self.tiles_to_load):
            self.load_timer.stop()

    def display_movies(self):
        """Display movies in the grid"""
        print(f"Displaying {len(self.movies)} movies")

        # Calculate number of columns based on window width
        columns = max(1, self.width() // 250)  # 250px per tile including spacing
        print(f"Grid columns: {columns}")

        # Prepare tiles to load
        self.tiles_to_load = []
        for i, movie_path in enumerate(self.movies):
            print(f"Creating tile for movie {i+1}: {movie_path.name}")
            row = i // columns
            col = i % columns
            self.tiles_to_load.append((movie_path, row, col))

        # Start loading timer
        self.current_load_index = 0
        self.load_timer.start(50)  # Load batch every 50ms

    def sort_movies(self, criteria):
        """Sort movies based on selected criteria"""
        print(f"Sorting by: {criteria}")
        if criteria == "Name":
            self.movies.sort(key=lambda x: x.name.lower())
        elif criteria == "Genre":
            self.movies.sort(key=lambda x: x.parent.name.lower())
        elif criteria == "Year":

            def get_year(path):
                name = path.name
                import re

                year_match = re.search(r"\((\d{4})\)", name)
                return year_match.group(1) if year_match else name.lower()

            self.movies.sort(key=get_year)

        self.display_movies()

    def refresh_movies(self):
        """Refresh the movie list"""
        if self.mainwindow and self.mainwindow.current_directory:
            self.load_movies(self.mainwindow.current_directory)

    def resizeEvent(self, event):
        """Handle resize events to adjust the grid layout"""
        super().resizeEvent(event)
        if self.movies:  # Only redisplay if there are movies
            self.display_movies()
