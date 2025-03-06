import sys
import os
import configparser
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QMessageBox, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction

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

class VFXTrayApp(QSystemTrayIcon):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setIcon(QIcon("img\\V_icon.png"))  # Ensure you have an icon.png file
        self.setToolTip("VFX Pipeline Launcher")
        self.menu = QMenu()
        
        self.launch_houdini_action = QAction("Launch Houdini", self)
        self.launch_nuke_action = QAction("Launch Nuke X", self)
        self.settings_action = QAction("Settings", self)
        self.quit_action = QAction("Quit", self)
        
        self.menu.addAction(self.launch_houdini_action)
        self.menu.addAction(self.launch_nuke_action)
        self.menu.addSeparator()
        self.menu.addAction(self.settings_action)
        self.menu.addAction(self.quit_action)
        
        self.setContextMenu(self.menu)
        
        self.launch_houdini_action.triggered.connect(self.launch_houdini)
        self.launch_nuke_action.triggered.connect(self.launch_nuke)
        self.settings_action.triggered.connect(self.show_settings)
        self.quit_action.triggered.connect(self.quit_app)
        
        self.load_settings()
        self.show()
    
    def load_settings(self):
        config = load_config()
        self.houdini_path = config['Paths'].get('houdini', '')
        self.nuke_path = config['Paths'].get('nuke', '')

    def launch_houdini(self):
        if os.path.exists(self.houdini_path):
            os.startfile(self.houdini_path)
        else:
            QMessageBox.warning(None, "Error", "Invalid Houdini path")
    
    def launch_nuke(self):
        if os.path.exists(self.nuke_path):
            os.startfile(self.nuke_path)
        else:
            QMessageBox.warning(None, "Error", "Invalid Nuke X path")

    def show_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()
    
    def quit_app(self):
        self.app.quit()

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 150)
        
        self.houdini_path = QLineEdit(self)
        self.nuke_path = QLineEdit(self)
        
        self.browse_houdini = QAction("Browse Houdini")
        self.browse_nuke = QAction("Browse Nuke X")
        self.save_btn = QAction("Save")
        
        self.browse_houdini.triggered.connect(self.browse_houdini_path)
        self.browse_nuke.triggered.connect(self.browse_nuke_path)
        self.save_btn.triggered.connect(self.save_settings)
        
        layout = QMenu()
        layout.addAction(self.browse_houdini)
        layout.addAction(self.browse_nuke)
        layout.addSeparator()
        layout.addAction(self.save_btn)
        
        self.setContextMenuPolicy(layout)
        self.load_settings()

    def load_settings(self):
        config = load_config()
        self.houdini_path.setText(config['Paths'].get('houdini', ''))
        self.nuke_path.setText(config['Paths'].get('nuke', ''))

    def save_settings(self):
        paths = {
            'houdini': self.houdini_path.text(),
            'nuke': self.nuke_path.text()
        }
        save_config(paths)
        QMessageBox.information(self, "Settings Saved", "Paths have been saved successfully!")

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
    tray = VFXTrayApp(app)
    sys.exit(app.exec())
