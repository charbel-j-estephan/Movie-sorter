from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QFrame
from PySide6.QtCore import Qt


class LoadingScreen(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setup_ui()

    def setup_ui(self):
        # Set background color and border
        self.setStyleSheet(
            """
            LoadingScreen {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 10px;
            }
        """
        )

        # Main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Title label
        self.title_label = QLabel("Organizing Movies")
        self.title_label.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                color: #333;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """
        )
        self.title_label.setAlignment(Qt.AlignCenter)

        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                color: #666;
                margin-bottom: 20px;
            }
        """
        )
        self.status_label.setAlignment(Qt.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """
        )
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)

        # Add widgets to layout
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch()

        # Set fixed size for the loading screen
        self.setFixedSize(400, 200)

    def update_status(self, operation, progress):
        """Update the loading screen with current status"""
        operations = {
            "renaming": "Renaming movie folders...",
            "scanning": "Scanning files...",
            "fetching": "Fetching movie information...",
            "organizing": "Organizing files...",
            "cleaning": "Cleaning up...",
        }

        self.status_label.setText(operations.get(operation, operation))
        self.progress_bar.setValue(int(progress))

    def center_on_parent(self):
        """Center the loading screen on its parent widget"""
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2,
            )
