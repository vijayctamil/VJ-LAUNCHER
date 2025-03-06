import sys
import os
import configparser
import csv
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QSystemTrayIcon, QMenu , QLabel
from PySide6.QtGui import QIcon, QAction

CONFIG_FILE = "settings.ini"

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if 'Paths' not in config:
        config['Paths'] = {'houdini': '', 'nuke': ''}
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
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
        self.setIcon(QIcon("img\\V_icon.png"))
        self.setToolTip("VFX Pipeline Launcher")
        self.menu = QMenu()
        
        self.folder_generator_action = QAction("Folder Generator", self)
        self.launch_houdini_action = QAction("Launch Houdini", self)
        self.launch_nuke_action = QAction("Launch Nuke X", self)
        self.settings_action = QAction("Settings", self)
        self.quit_action = QAction("Quit", self)
        
        self.menu.addAction(self.folder_generator_action)
        self.menu.addAction(self.launch_houdini_action)
        self.menu.addAction(self.launch_nuke_action)
        self.menu.addSeparator()
        self.menu.addAction(self.settings_action)
        self.menu.addAction(self.quit_action)
        
        self.setContextMenu(self.menu)
        
        self.folder_generator_action.triggered.connect(self.show_folder_generator)
        self.launch_houdini_action.triggered.connect(self.launch_houdini)
        self.launch_nuke_action.triggered.connect(self.launch_nuke)
        self.settings_action.triggered.connect(self.show_settings)
        self.quit_action.triggered.connect(self.quit_app)
        
        self.settings_window = None
        self.folder_generator_window = None
        self.load_settings()
        self.show()
    
    def load_settings(self):
        config = load_config()
        self.houdini_path = config['Paths'].get('houdini', '')
        self.nuke_path = config['Paths'].get('nuke', '')

    def show_folder_generator(self):
        if self.folder_generator_window is None:
            self.folder_generator_window = FolderGeneratorWindow()
        self.folder_generator_window.show()
        self.folder_generator_window.activateWindow()
    
    def show_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow()
        self.settings_window.show()
        self.settings_window.activateWindow()
    
    def launch_houdini(self):
        if self.houdini_path:
            os.startfile(self.houdini_path)
        else:
            QMessageBox.warning(None, "Error", "Houdini path is not set.")
    
    def launch_nuke(self):
        if self.nuke_path:
            os.startfile(self.nuke_path)
        else:
            QMessageBox.warning(None, "Error", "Nuke X path is not set.")
    
    def quit_app(self):
        self.app.quit()

class FolderGeneratorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Folder Generator")
        self.setGeometry(100, 100, 400, 250)
        
        layout = QVBoxLayout()
        
        self.target_path_label = QLabel("Select Target Path:")
        self.target_path_input = QLineEdit(self)
        self.browse_target_btn = QPushButton("Browse")
        self.upload_csv_btn = QPushButton("Upload CSV")
        self.confirm_label = QLabel("No CSV uploaded.")
        self.create_folders_btn = QPushButton("Create Folders")
        self.create_folders_btn.setEnabled(False)
        
        self.browse_target_btn.clicked.connect(self.browse_target_path)
        self.upload_csv_btn.clicked.connect(self.upload_csv)
        self.create_folders_btn.clicked.connect(self.create_folders)
        
        layout.addWidget(self.target_path_label)
        layout.addWidget(self.target_path_input)
        layout.addWidget(self.browse_target_btn)
        layout.addWidget(self.upload_csv_btn)
        layout.addWidget(self.confirm_label)
        layout.addWidget(self.create_folders_btn)
        
        self.setLayout(layout)
        self.folder_paths = []
        self.target_path = ""
    
    def closeEvent(self, event):
        self.hide()
        event.ignore()
    
    def browse_target_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Target Directory")
        if folder:
            self.target_path = folder
            self.target_path_input.setText(folder)
    
    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.folder_paths = []
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row:
                        self.folder_paths.append(row[0])
            
            self.confirm_label.setText("CSV Uploaded: {} folders detected".format(len(self.folder_paths)))
            self.create_folders_btn.setEnabled(True)
    
    def create_folders(self):
        if not self.target_path:
            QMessageBox.warning(self, "Error", "Please select a target path first.")
            return
        
        for path in self.folder_paths:
            full_path = os.path.join(self.target_path, path)
            os.makedirs(full_path, exist_ok=True)
        QMessageBox.information(self, "Folders Created", "All folders have been successfully created!")
        self.create_folders_btn.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tray = VFXTrayApp(app)
    sys.exit(app.exec())
