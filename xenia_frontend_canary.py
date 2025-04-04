import json
import os
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QListWidget, QHBoxLayout, QGridLayout, QStackedWidget, QLineEdit)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import subprocess
import urllib.request
import zipfile
import shutil

settings_file = "settings.json"
xenia_folder = "xenia"
xenia_url = "https://xenia-project.github.io/downloads/xenia.zip"

settings = {
    "xenia_path": "",
    "ui_type": "Metro",
    "game_library": []
}

def ensure_files():
    if not os.path.exists(settings_file):
        save_settings()
    
    if not os.path.exists(settings["xenia_path"]):
        install_xenia()

def save_settings():
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)

def load_settings():
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as f:
                data = json.load(f)
                data.setdefault("game_library", [])
                return data
        except json.JSONDecodeError:
            print("Settings file is corrupted. A new file will be created.")
    return settings

def install_xenia():
    try:
        if not os.path.exists(xenia_folder):
            print("Xenia not found. Downloading and installing...")
            urllib.request.urlretrieve(xenia_url, "xenia.zip")
            with zipfile.ZipFile("xenia.zip", "r") as zip_ref:
                zip_ref.extractall(xenia_folder)
            os.remove("xenia.zip")
            print("Xenia installed successfully!")
        settings["xenia_path"] = os.path.join(xenia_folder, "xenia.exe")
        save_settings()
    except Exception as e:
        print(f"Error installing Xenia: {str(e)}")

def run_game(game_path):
    if not settings["xenia_path"]:
        print("Xenia path is not set!")
        return
    subprocess.run([settings["xenia_path"], game_path])

class Xbox360MetroUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xbox 360 Metro UI")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("background-color: #1c1c1c; color: white;")
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)
        
        self.home_screen = QWidget()
        self.settings_screen = QWidget()
        self.setup_home_screen()
        self.setup_settings_screen()
        
        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.settings_screen)
        
        self.show_home()
    
    def setup_home_screen(self):
        layout = QVBoxLayout()
        self.home_screen.setLayout(layout)

        self.title_label = QLabel("Xenia Game Launcher", self)
        self.title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.game_grid = QGridLayout()
        layout.addLayout(self.game_grid)
        
        self.update_game_grid()
        
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.settings_button = QPushButton("Settings", self)
        self.settings_button.setStyleSheet("background-color: #0078d7; color: white;")
        self.settings_button.clicked.connect(self.show_settings)
        button_layout.addWidget(self.settings_button)
    
    def setup_settings_screen(self):
        layout = QVBoxLayout()
        self.settings_screen.setLayout(layout)
        
        self.settings_title = QLabel("Settings", self)
        self.settings_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.settings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.settings_title)
        
        self.xenia_path_input = QLineEdit(self)
        self.xenia_path_input.setPlaceholderText("Xenia Emulator Path")
        self.xenia_path_input.setText(settings["xenia_path"])
        layout.addWidget(self.xenia_path_input)
        
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_xenia_path)
        layout.addWidget(self.browse_button)
        
        self.add_game_button = QPushButton("Add Games", self)
        self.add_game_button.clicked.connect(self.add_games_from_folder)
        layout.addWidget(self.add_game_button)
        
        self.back_button = QPushButton("Back", self)
        self.back_button.clicked.connect(self.show_home)
        layout.addWidget(self.back_button)
    
    def show_home(self):
        self.stack.setCurrentWidget(self.home_screen)
    
    def show_settings(self):
        self.stack.setCurrentWidget(self.settings_screen)
    
    def browse_xenia_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Xenia Executable", "", "Executable Files (*.exe)")
        if file_path:
            settings["xenia_path"] = file_path
            self.xenia_path_input.setText(file_path)
            save_settings()
    
    def add_games_from_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Game Folder")
        if folder_path:
            games = [os.path.join(root, file) for root, dirs, files in os.walk(folder_path) for file in files if file.endswith(".iso")]
            if games:
                new_games = []
                for game in games:
                    if game not in [g["path"] for g in settings["game_library"]]:  # Prevent duplicates
                        new_games.append({"path": game, "fps_counter": False, "resolution": "720p"})
                settings["game_library"].extend(new_games)
                save_settings()
                self.update_game_grid()
    
    def update_game_grid(self):
        while self.game_grid.count():
            child = self.game_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not settings["game_library"]:
            self.game_grid.addWidget(QLabel("No games available"))
        else:
            for index, game in enumerate(settings["game_library"]):
                btn = QPushButton(f"{os.path.basename(game['path'])} - {game['resolution']} - FPS: {'Enabled' if game['fps_counter'] else 'Disabled'}")
                btn.setStyleSheet("background-color: #0078d7; color: white; padding: 10px;")
                btn.clicked.connect(lambda _, g=game["path"]: run_game(g))
                self.game_grid.addWidget(btn, index // 3, index % 3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings.update(load_settings())
    ensure_files()
    main_window = Xbox360MetroUI()
    main_window.show()
    sys.exit(app.exec())
