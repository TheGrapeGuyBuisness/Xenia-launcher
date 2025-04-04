import sys
import subprocess
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel

class ExeBuilder(QWidget):
    def __init__(self):
        super().__init__()

        self.main_script_path = None
        self.helper_script_path = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EXE Builder")
        self.setGeometry(100, 100, 400, 200)

        # Create layout
        layout = QVBoxLayout()

        # Create buttons and labels
        self.main_script_label = QLabel("Select the main script")
        layout.addWidget(self.main_script_label)

        self.main_script_button = QPushButton("Select Main Script")
        self.main_script_button.clicked.connect(self.select_main_script)
        layout.addWidget(self.main_script_button)

        self.helper_script_label = QLabel("Select the helper script")
        layout.addWidget(self.helper_script_label)

        self.helper_script_button = QPushButton("Select Helper Script")
        self.helper_script_button.clicked.connect(self.select_helper_script)
        layout.addWidget(self.helper_script_button)

        self.build_button = QPushButton("Build EXE")
        self.build_button.clicked.connect(self.build_exe)
        layout.addWidget(self.build_button)

        self.setLayout(layout)

    def select_main_script(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Main Script", "", "Python Files (*.py)")
        if file:
            self.main_script_path = file
            self.main_script_label.setText(f"Main script selected: {os.path.basename(file)}")

    def select_helper_script(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Helper Script", "", "Python Files (*.py)")
        if file:
            self.helper_script_path = file
            self.helper_script_label.setText(f"Helper script selected: {os.path.basename(file)}")

    def build_exe(self):
        if not self.main_script_path or not self.helper_script_path:
            self.main_script_label.setText("Please select both scripts!")
            return

        # Combine both scripts into a temporary folder to bundle
        os.makedirs('temp', exist_ok=True)

        # Write the main script
        with open(os.path.join('temp', 'main.py'), 'w') as main_file:
            with open(self.main_script_path, 'r') as f:
                main_file.write(f.read())

        # Write the helper script
        with open(os.path.join('temp', 'helper.py'), 'w') as helper_file:
            with open(self.helper_script_path, 'r') as f:
                helper_file.write(f.read())

        # Now, create the exe with python -m PyInstaller
        try:
            subprocess.run([sys.executable, '-m', 'PyInstaller', '--onefile', 'temp/main.py'], check=True)
            self.main_script_label.setText("EXE built successfully!")
        except subprocess.CalledProcessError as e:
            self.main_script_label.setText(f"Error during build: {e}")

        # Clean up the temp folder
        if os.path.exists('temp'):
            for root, dirs, files in os.walk('temp', topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
            os.rmdir('temp')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExeBuilder()
    window.show()
    sys.exit(app.exec())
