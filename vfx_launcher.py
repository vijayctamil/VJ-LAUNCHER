import sys
import os
import configparser
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QLineEdit, QMessageBox

CONFIG_FILE = "settings.ini"

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def save_config(paths):
    config = configparser.ConfigParser()
    config['Paths'] = paths
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

class VFXLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_settings()

    def initUI(self):
        self.setWindowTitle("VFX Pipeline Launcher")
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()
        
        self.houdini_path = QLineEdit(self)
        self.nuke_path = QLineEdit(self)
        
        self.houdini_btn = QPushButton("Launch Houdini", self)
        self.nuke_btn = QPushButton("Launch Nuke X", self)
        self.save_btn = QPushButton("Save Paths", self)
        self.browse_houdini = QPushButton("Browse Houdini", self)
        self.browse_nuke = QPushButton("Browse Nuke X", self)
        
        layout.addWidget(QLabel("Houdini Path:"))
        layout.addWidget(self.houdini_path)
        layout.addWidget(self.browse_houdini)
        layout.addWidget(QLabel("Nuke X Path:"))
        layout.addWidget(self.nuke_path)
        layout.addWidget(self.browse_nuke)
        layout.addWidget(self.houdini_btn)
        layout.addWidget(self.nuke_btn)
        layout.addWidget(self.save_btn)
        
        self.setLayout(layout)
        
        self.houdini_btn.clicked.connect(self.launch_houdini)
        self.nuke_btn.clicked.connect(self.launch_nuke)
        self.save_btn.clicked.connect(self.save_settings)
        self.browse_houdini.clicked.connect(self.browse_houdini_path)
        self.browse_nuke.clicked.connect(self.browse_nuke_path)

    def load_settings(self):
        config = load_config()
        if 'Paths' in config:
            self.houdini_path.setText(config['Paths'].get('houdini', ''))
            self.nuke_path.setText(config['Paths'].get('nuke', ''))

    def save_settings(self):
        paths = {
            'houdini': self.houdini_path.text(),
            'nuke': self.nuke_path.text()
        }
        save_config(paths)
        QMessageBox.information(self, "Settings Saved", "Paths have been saved successfully!")

    def launch_houdini(self):
        path = self.houdini_path.text()
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self, "Error", "Invalid Houdini path")

    def launch_nuke(self):
        path = self.nuke_path.text()
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self, "Error", "Invalid Nuke X path")

    def browse_houdini_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Houdini Executable")
        if path:
            self.houdini_path.setText(path)

    def browse_nuke_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Nuke X Executable")
        if path:
            self.nuke_path.setText(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = VFXLauncher()
    launcher.show()
    sys.exit(app.exec())
