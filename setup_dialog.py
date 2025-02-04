from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt
import json
import os


class SetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Movie Organizer Setup")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # API Key input
        api_label = QLabel("Enter your OMDB API Key:")
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Enter your API key here")

        # Get API key button
        get_api_btn = QPushButton("How to get an API Key?")
        get_api_btn.clicked.connect(self.show_api_instructions)

        # Save button
        save_btn = QPushButton("Save and Continue")
        save_btn.clicked.connect(self.save_settings)

        # Add widgets to layout
        layout.addWidget(api_label)
        layout.addWidget(self.api_input)
        layout.addWidget(get_api_btn)
        layout.addSpacing(20)
        layout.addWidget(save_btn)

        # Load existing settings if any
        self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    self.api_input.setText(settings.get("api_key", ""))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading settings: {str(e)}")

    def save_settings(self):
        api_key = self.api_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Error", "Please enter an API key")
            return

        try:
            # Load existing settings if they exist
            settings = {}
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)

            # Update API key
            settings["api_key"] = api_key

            # Save settings
            with open("settings.json", "w") as f:
                json.dump(settings, f)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")

    def show_api_instructions(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("How to Get an OMDB API Key")
        msg.setText(
            """To get an OMDB API key:
1. Visit http://www.omdbapi.com/apikey.aspx
2. Choose the FREE tier
3. Fill out the form
4. Check your email for the API key
5. Copy and paste the key here"""
        )
        msg.exec()
