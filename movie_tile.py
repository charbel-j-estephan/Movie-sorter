# movie_tile.py
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QObject, Signal, QTimer
from PySide6.QtGui import QPixmap, QCursor
from pathlib import Path
import json
import aiohttp
import asyncio
import sys
import threading
from functools import partial


class PosterLoader(QObject):
    poster_loaded = Signal(QPixmap)

    def __init__(self, url):
        super().__init__()
        self.url = url

    async def load_poster(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    if response.status == 200:
                        data = await response.read()
                        pixmap = QPixmap()
                        if pixmap.loadFromData(data):
                            scaled_pixmap = pixmap.scaled(
                                180, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation
                            )
                            self.poster_loaded.emit(scaled_pixmap)
                            return
        except Exception as e:
            print(f"Error loading poster: {e}")


class MovieTile(QFrame):
    def __init__(self, movie_path, parent=None):
        super().__init__(parent)
        self.movie_path = Path(movie_path)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setFixedSize(200, 300)

        self.setup_ui()
        QTimer.singleShot(0, self.load_movie_info)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Movie poster
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(180, 240)
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet(
            "QLabel { background-color: #f0f0f0; border-radius: 5px; }"
        )

        # Set initial placeholder
        placeholder = QPixmap(180, 240)
        placeholder.fill(Qt.lightGray)
        self.poster_label.setPixmap(placeholder)

        # Movie title
        title = self.movie_path.name
        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #333;
                margin-top: 5px;
            }
        """
        )

        layout.addWidget(self.poster_label)
        layout.addWidget(self.title_label)

        self.setStyleSheet(
            """
            MovieTile {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            MovieTile:hover {
                border: 2px solid #4CAF50;
                background-color: #f0f0f0;
            }
        """
        )
        self.setCursor(Qt.PointingHandCursor)

    def load_movie_info(self):
        try:
            root_dir = self.movie_path.parent.parent
            info_path = root_dir / "movies info" / f"{self.movie_path.name}_about.json"

            if info_path.exists():
                with open(info_path, encoding="utf-8") as f:
                    movie_data = json.load(f)

                    # Check for local poster first
                    local_poster = movie_data.get("LocalPoster")
                    if local_poster and Path(local_poster).exists():
                        pixmap = QPixmap(local_poster)
                        scaled_pixmap = pixmap.scaled(
                            180, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                        self.poster_label.setPixmap(scaled_pixmap)
                    else:
                        # Fall back to online poster if local doesn't exist
                        poster_url = movie_data.get("Poster")
                        if poster_url and poster_url != "N/A":
                            loader = PosterLoader(poster_url)
                            loader.poster_loaded.connect(self.poster_label.setPixmap)

                            def run_async():
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                loop.run_until_complete(loader.load_poster())
                                loop.close()

                            thread = threading.Thread(target=run_async)
                            thread.start()

        except Exception as e:
            print(f"Error loading info for {self.movie_path.name}: {e}")

    def mousePressEvent(self, event):
        from movie_details_dialog import MovieDetailsDialog

        dialog = MovieDetailsDialog(str(self.movie_path), self.window())
        dialog.exec()
