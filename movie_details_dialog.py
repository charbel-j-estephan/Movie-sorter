from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QWidget,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os
import subprocess
import json
import aiohttp
import asyncio
from pathlib import Path
import webbrowser


class MovieDetailsDialog(QDialog):
    def __init__(self, movie_path, parent=None):
        super().__init__(parent)
        self.movie_path = Path(movie_path)
        print(f"Movie path: {self.movie_path}")  # Debug print
        self.setWindowTitle(self.movie_path.name)
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_movie_info()

    def setup_ui(self):
        # [Previous UI setup code remains the same...]
        layout = QHBoxLayout(self)

        # Left side - Poster and buttons
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Poster
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(300, 450)
        self.poster_label.setStyleSheet("border: 2px solid #ccc; border-radius: 5px;")
        left_layout.addWidget(self.poster_label)

        # Play button
        play_button = QPushButton("Play Movie")
        play_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        play_button.clicked.connect(self.play_movie)
        left_layout.addWidget(play_button)

        # Watch Trailer button
        trailer_button = QPushButton("Watch Trailer")
        trailer_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
        """
        )
        trailer_button.clicked.connect(self.watch_trailer)
        left_layout.addWidget(trailer_button)

        left_layout.addStretch()
        layout.addWidget(left_panel)

        # Right side - Movie details
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_panel.setStyleSheet("QScrollArea { border: none; }")

        details_widget = QWidget()
        self.details_layout = QVBoxLayout(details_widget)

        # Title
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.title_label.setWordWrap(True)
        self.details_layout.addWidget(self.title_label)

        # Year and Runtime
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 16px; color: #666;")
        self.details_layout.addWidget(self.info_label)

        # Genre
        self.genre_label = QLabel()
        self.genre_label.setStyleSheet("font-size: 16px; color: #666;")
        self.details_layout.addWidget(self.genre_label)

        # Rating
        self.rating_label = QLabel()
        self.rating_label.setStyleSheet("font-size: 16px; color: #666;")
        self.details_layout.addWidget(self.rating_label)

        # Plot
        plot_heading = QLabel("Plot")
        plot_heading.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-top: 20px;"
        )
        self.details_layout.addWidget(plot_heading)

        self.plot_label = QLabel()
        self.plot_label.setWordWrap(True)
        self.plot_label.setStyleSheet("font-size: 16px;")
        self.details_layout.addWidget(self.plot_label)

        # Cast
        cast_heading = QLabel("Cast")
        cast_heading.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-top: 20px;"
        )
        self.details_layout.addWidget(cast_heading)

        self.cast_label = QLabel()
        self.cast_label.setWordWrap(True)
        self.cast_label.setStyleSheet("font-size: 16px;")
        self.details_layout.addWidget(self.cast_label)

        self.details_layout.addStretch()
        right_panel.setWidget(details_widget)
        layout.addWidget(right_panel)

    def load_movie_info(self):
        try:
            # Get the root movies directory (two levels up from movie folder)
            root_dir = self.movie_path.parent.parent
            info_path = root_dir / "movies info" / f"{self.movie_path.name}_about.json"
            print(f"Looking for info file at: {info_path}")  # Debug print

            if info_path.exists():
                print("Info file found!")  # Debug print
                with open(info_path, encoding="utf-8") as f:
                    movie_data = json.load(f)
                    print(f"Loaded movie data: {movie_data}")  # Debug print
                    self.update_ui_with_movie_data(movie_data)
            else:
                print(f"Movie info file not found at {info_path}")
                QMessageBox.warning(
                    self, "Warning", f"Movie information file not found at {info_path}"
                )
        except Exception as e:
            print(f"Error in load_movie_info: {str(e)}")  # Debug print
            QMessageBox.warning(self, "Warning", f"Error loading movie info: {str(e)}")

    def update_ui_with_movie_data(self, movie_data):
        try:
            # Update title
            title = movie_data.get("Title", self.movie_path.name)
            print(f"Setting title: {title}")  # Debug print
            self.title_label.setText(title)

            # Year and Runtime
            year = movie_data.get("Year", "N/A")
            runtime = movie_data.get("Runtime", "N/A")
            info_text = f"{year} • {runtime}"
            print(f"Setting info: {info_text}")  # Debug print
            self.info_label.setText(info_text)

            # Genre
            genre_text = f"Genre: {movie_data.get('Genre', 'N/A')}"
            print(f"Setting genre: {genre_text}")  # Debug print
            self.genre_label.setText(genre_text)

            # Rating
            rating = movie_data.get("imdbRating", "N/A")
            votes = movie_data.get("imdbVotes", "N/A")
            rating_text = f"IMDb Rating: {rating}/10 ({votes} votes)"
            print(f"Setting rating: {rating_text}")  # Debug print
            self.rating_label.setText(rating_text)

            # Plot
            plot = movie_data.get("Plot", "No plot available.")
            print(f"Setting plot: {plot}")  # Debug print
            self.plot_label.setText(plot)

            # Cast
            cast = movie_data.get("Actors", "N/A")
            director = movie_data.get("Director", "N/A")
            cast_text = f"Director: {director}\nStarring: {cast}"
            print(f"Setting cast: {cast_text}")  # Debug print
            self.cast_label.setText(cast_text)

            # Load poster
            poster_url = movie_data.get("Poster")
            print(f"Poster URL: {poster_url}")  # Debug print
            if poster_url and poster_url != "N/A":
                asyncio.run(self.load_poster(poster_url))
            else:
                print("No valid poster URL found")  # Debug print
                placeholder = QPixmap(300, 450)
                placeholder.fill(Qt.gray)
                self.poster_label.setPixmap(placeholder)
        except Exception as e:
            print(f"Error in update_ui_with_movie_data: {str(e)}")  # Debug print
            QMessageBox.warning(
                self, "Warning", f"Error updating UI with movie data: {str(e)}"
            )

    async def load_poster(self, url):
        try:
            print(f"Attempting to load poster from: {url}")  # Debug print
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    print(f"Poster response status: {response.status}")  # Debug print
                    if response.status == 200:
                        data = await response.read()
                        pixmap = QPixmap()
                        success = pixmap.loadFromData(data)
                        print(f"Pixmap load success: {success}")  # Debug print
                        if success:
                            scaled_pixmap = pixmap.scaled(
                                300, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation
                            )
                            self.poster_label.setPixmap(scaled_pixmap)
                        else:
                            print("Failed to create pixmap from data")
        except Exception as e:
            print(f"Error loading poster: {str(e)}")  # Debug print
            placeholder = QPixmap(300, 450)
            placeholder.fill(Qt.gray)
            self.poster_label.setPixmap(placeholder)

    def watch_trailer(self):
        try:
            title = self.title_label.text()
            year = self.info_label.text().split("•")[0].strip()
            print(f"Searching trailer for: {title} ({year})")  # Debug print
            search_query = f"{title} {year} official trailer"
            url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            print(f"Opening URL: {url}")  # Debug print
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening trailer: {str(e)}")  # Debug print
            QMessageBox.warning(
                self, "Error", f"Could not open trailer search: {str(e)}"
            )

    def find_video_file(self):
        video_extensions = [".mp4", ".mkv", ".avi", ".mov", ".wmv"]
        try:
            for item in self.movie_path.iterdir():
                if item.suffix.lower() in video_extensions:
                    print(f"Found video file: {item}")  # Debug print
                    return item
        except Exception as e:
            print(f"Error finding video file: {e}")  # Debug print
        return None

    def play_movie(self):
        video_file = self.find_video_file()
        if video_file:
            try:
                if os.name == "nt":  # Windows
                    os.startfile(str(video_file))
                else:  # macOS and Linux
                    subprocess.run(
                        ["xdg-open" if os.name == "posix" else "open", str(video_file)]
                    )
            except Exception as e:
                print(f"Error playing video: {str(e)}")  # Debug print
                QMessageBox.critical(self, "Error", f"Could not play video: {str(e)}")
        else:
            print("No video file found")  # Debug print
            QMessageBox.warning(
                self, "Error", "No video file found in the movie directory."
            )
