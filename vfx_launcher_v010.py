import sys
import os
import configparser
import csv
import subprocess
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QSystemTrayIcon, QMenu, QLabel, QListWidget, QComboBox
from PySide6.QtGui import QIcon, QAction
import tempfile

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


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 150)
        
        layout = QVBoxLayout()
        
        self.houdini_path = QLineEdit(self)
        self.nuke_path = QLineEdit(self)
        
        self.browse_houdini = QPushButton("Browse Houdini")
        self.browse_nuke = QPushButton("Browse Nuke X")
        self.save_btn = QPushButton("Save")
        
        self.browse_houdini.clicked.connect(self.browse_houdini_path)
        self.browse_nuke.clicked.connect(self.browse_nuke_path)
        self.save_btn.clicked.connect(self.save_settings)
        
        layout.addWidget(self.houdini_path)
        layout.addWidget(self.browse_houdini)
        layout.addWidget(self.nuke_path)
        layout.addWidget(self.browse_nuke)
        layout.addWidget(self.save_btn)
        
        self.setLayout(layout)
        self.load_settings()
    
    def browse_houdini_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Houdini Executable")
        if path:
            self.houdini_path.setText(path)
    
    def browse_nuke_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Nuke X Executable")
        if path:
            self.nuke_path.setText(path)
    
    def closeEvent(self, event):
        self.hide()
        event.ignore()

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


class BatchRenderSetup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Batch Render Setup")
        self.setGeometry(150, 150, 500, 400)
        
        layout = QVBoxLayout()
        
        self.file_list = QListWidget()
        self.select_files_btn = QPushButton("Select Text Files")
        self.save_path_input = QLineEdit()
        self.browse_save_path_btn = QPushButton("Browse Save Location")
        self.generate_bat_btn = QPushButton("Generate Batch File")
        
        self.select_files_btn.clicked.connect(self.select_text_files)
        self.browse_save_path_btn.clicked.connect(self.browse_save_location)
        self.generate_bat_btn.clicked.connect(self.generate_batch_file)
        
        layout.addWidget(QLabel("Selected Text Files:"))
        layout.addWidget(self.file_list)
        layout.addWidget(self.select_files_btn)
        layout.addWidget(QLabel("Save Batch File To:"))
        layout.addWidget(self.save_path_input)
        layout.addWidget(self.browse_save_path_btn)
        layout.addWidget(self.generate_bat_btn)
        
        self.setLayout(layout)
        
        self.file_paths = []
    
    def select_text_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Text Files", "", "Text Files (*.txt)")
        if files:
            self.file_paths.extend(files)
            self.file_list.addItems(files)
    
    def browse_save_location(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Batch File", "", "Batch Files (*.bat)")
        if file_path:
            self.save_path_input.setText(file_path)
    
    def generate_batch_file(self):
        if not self.file_paths:
            QMessageBox.warning(self, "Error", "No text files selected.")
            return
        
        save_path = self.save_path_input.text()
        if not save_path:
            QMessageBox.warning(self, "Error", "No save location specified.")
            return
        
        try:
            with open(save_path, "w", encoding="utf-8") as bat_file:
                for file in self.file_paths:
                    with open(file, "r", encoding="utf-8") as txt_file:
                        command = txt_file.read().strip()
                        bat_file.write(command + "\n")
            QMessageBox.information(self, "Success", "Batch file generated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate batch file: {str(e)}")
    
    def closeEvent(self, event):
        self.hide()
        event.ignore()




class VFXTrayApp(QSystemTrayIcon):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setIcon(QIcon("img\\V_icon.png"))
        self.setToolTip("VJ VFX Pipeline Launcher")
        self.menu = QMenu()
        
        self.folder_generator_action = QAction("Folder Generator", self)
        self.get_node_action = QAction("Get Node", self)
        self.batch_render_action = QAction("Batch Render Setup", self)
        self.launch_houdini_action = QAction("Launch Houdini", self)
        self.launch_nuke_action = QAction("Launch Nuke X", self)
        self.settings_action = QAction("Settings", self)
        self.quit_action = QAction("Quit", self)
        
        self.menu.addAction(self.folder_generator_action)
        self.menu.addAction(self.get_node_action)
        
        self.menu.addAction(self.launch_houdini_action)
        self.menu.addAction(self.launch_nuke_action)
        self.menu.addAction(self.batch_render_action)
        self.menu.addSeparator()
        self.menu.addAction(self.settings_action)
        self.menu.addAction(self.quit_action)
        
        self.setContextMenu(self.menu)
        
        self.folder_generator_action.triggered.connect(self.show_folder_generator)
        self.get_node_action.triggered.connect(self.show_get_node)
        self.batch_render_action.triggered.connect(self.open_batch_render_setup)
        self.launch_houdini_action.triggered.connect(self.launch_houdini)
        self.launch_nuke_action.triggered.connect(self.launch_nuke)
        self.settings_action.triggered.connect(self.show_settings)
        self.quit_action.triggered.connect(self.quit_app)
        
        self.settings_window = None
        self.folder_generator_window = None
        self.get_node_window = None
        self.batch_render_window = None
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
    
    def show_get_node(self):
        if self.get_node_window is None:
            self.get_node_window = GetNodeWindow()
        self.get_node_window.show()
        self.get_node_window.activateWindow()
    
    def show_settings(self):
        if self.settings_window is None:
            self.settings_window = SettingsWindow()
        self.settings_window.show()
        self.settings_window.activateWindow()
    
    def launch_houdini(self):
        if self.houdini_path:
            os.startfile(self.houdini_path)
    
    def launch_nuke(self):
        if self.nuke_path:
            os.startfile(self.nuke_path)
    
    def quit_app(self):
        self.app.quit()

    def open_batch_render_setup(self):
        if self.batch_render_window is None:
            self.batch_render_window = BatchRenderSetup()
        self.batch_render_window.show()
        self.batch_render_window.activateWindow()

class GetNodeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Get Node")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        self.houdini_file_label = QLabel("Select Houdini File:")
        self.houdini_file_input = QLineEdit(self)
        self.browse_houdini_file_btn = QPushButton("Browse")
        self.load_nodes_btn = QPushButton("Load Nodes")
        self.node_list = QListWidget()
        self.parm_label = QLabel("Select Parameter:")
        self.parm_dropdown = QComboBox()
        self.get_parm_value_btn = QPushButton("Get Parameter Value")
        self.parm_value_label = QLabel("Parameter Value: ")
        self.new_value_input = QLineEdit(self)
        self.set_parm_value_btn = QPushButton("Set Parameter Value")
        
        self.browse_houdini_file_btn.clicked.connect(self.browse_houdini_file)
        self.load_nodes_btn.clicked.connect(self.load_nodes)
        self.node_list.itemSelectionChanged.connect(self.load_parameters)
        self.get_parm_value_btn.clicked.connect(self.get_parm_value)
        self.set_parm_value_btn.clicked.connect(self.set_parm_value)
        
        layout.addWidget(self.houdini_file_label)
        layout.addWidget(self.houdini_file_input)
        layout.addWidget(self.browse_houdini_file_btn)
        layout.addWidget(self.load_nodes_btn)
        layout.addWidget(self.node_list)
        layout.addWidget(self.parm_label)
        layout.addWidget(self.parm_dropdown)
        layout.addWidget(self.get_parm_value_btn)
        layout.addWidget(self.parm_value_label)
        layout.addWidget(QLabel("New Parameter Value:"))
        layout.addWidget(self.new_value_input)
        layout.addWidget(self.set_parm_value_btn)
        
        self.setLayout(layout)
        self.node_list.itemSelectionChanged.connect(self.load_parameters)
    
    def set_parm_value(self):
        selected_node = self.node_list.currentItem()
        if not selected_node:
            QMessageBox.warning(self, "Error", "Please select a node.")
            return
        
        node_path = selected_node.text()
        parm_name = self.parm_dropdown.currentText()
        new_value = self.new_value_input.text()
        file_path = self.houdini_file_input.text()
        
        config = load_config()
        houdini_path = config['Paths'].get('houdini', '')
        houdini_bin_dir = os.path.dirname(houdini_path)
        hython_path = os.path.join(houdini_bin_dir, "hython.exe")
        
        temp_script = tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8")
        temp_script.write("import hou\n")
        temp_script.write(f"hou.hipFile.load(r'{file_path}')\n")
        temp_script.write(f"node = hou.node(r'{node_path}')\n")
        temp_script.write(f"if node.parm(r'{parm_name}'):\n")
        temp_script.write(f"    node.parm(r'{parm_name}').set({repr(new_value)})\n")
        temp_script.write("hou.hipFile.save()\n")
        temp_script.close()
        
        command = f'"{hython_path}" "{temp_script.name}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        os.unlink(temp_script.name)
        
        if result.returncode != 0:
            QMessageBox.warning(self, "Error", f"Houdini execution failed:\n{result.stderr}")
            return
        
        QMessageBox.information(self, "Success", "Parameter value updated and file saved.")


    def closeEvent(self, event):
        self.hide()
        event.ignore()
    
    def browse_houdini_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Houdini File", "", "Houdini Files (*.hip *.hipnc)")
        if file_path:
            self.houdini_file_input.setText(file_path)
    
    def load_nodes(self):
        file_path = self.houdini_file_input.text()
        if not file_path:
            QMessageBox.warning(self, "Error", "Please select a Houdini file.")
            return
        
        config = load_config()
        houdini_path = config['Paths'].get('houdini', '')
        houdini_bin_dir = os.path.dirname(houdini_path)
        hython_path = os.path.join(houdini_bin_dir, "hython.exe")
        
        temp_script = tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8")
        temp_script.write("import hou\n")
        temp_script.write(f"hou.hipFile.load(r'{file_path}')\n")
        temp_script.write("nodes = [node.path() for node in hou.node('/') .allSubChildren()]\n")
        temp_script.write("print('NODE_LIST_START')\n")
        temp_script.write("for node in nodes:\n")
        temp_script.write("    print(node)\n")
        temp_script.write("print('NODE_LIST_END')\n")
        temp_script.close()
        
        command = f'"{hython_path}" "{temp_script.name}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        os.unlink(temp_script.name)
        
        output = result.stdout.strip()
        if "NODE_LIST_START" in output and "NODE_LIST_END" in output:
            nodes_section = output.split("NODE_LIST_START")[1].split("NODE_LIST_END")[0].strip()
            nodes = nodes_section.split("\n") if nodes_section else []
        else:
            nodes = []
        
        self.node_list.clear()
        self.node_list.addItems(nodes)
        if nodes:
            self.node_list.setCurrentRow(0)  # Select the first node automatically
            self.load_parameters()  # Manually trigger loading parameters

    
    def load_parameters(self):
        selected_node = self.node_list.currentItem()
        if not selected_node:
            return
        
        node_path = selected_node.text()
        file_path = self.houdini_file_input.text()
        
        config = load_config()
        houdini_path = config['Paths'].get('houdini', '')
        houdini_bin_dir = os.path.dirname(houdini_path)
        hython_path = os.path.join(houdini_bin_dir, "hython.exe")
        
        temp_script = tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8")
        temp_script.write("import hou\n")
        temp_script.write(f"hou.hipFile.load(r'{file_path}')\n")
        temp_script.write(f"node = hou.node(r'{node_path}')\n")
        temp_script.write("params = [parm.name() for parm in node.parms()] if node else []\n")
        temp_script.write("print('PARAM_LIST_START')\n")
        temp_script.write("print('\\n'.join(params))\n")
        temp_script.write("print('PARAM_LIST_END')\n")
        temp_script.close()
        
        command = f'"{hython_path}" "{temp_script.name}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        os.unlink(temp_script.name)
        
        output = result.stdout.strip()
        
        # Remove debug popup
        # QMessageBox.information(self, "Houdini Output", output)  # Removed to prevent duplicate popups

        if "PARAM_LIST_START" in output and "PARAM_LIST_END" in output:
            params_section = output.split("PARAM_LIST_START")[1].split("PARAM_LIST_END")[0].strip()
            params = params_section.split("\n") if params_section else []
        else:
            params = []

        self.parm_dropdown.clear()
        self.parm_dropdown.addItems(params)

        # # Only show error message if no parameters exist
        # if not params:
        #     QMessageBox.warning(self, "Error", f"No parameters found for {node_path}.")

    
    def get_parm_value(self):
        selected_node = self.node_list.currentItem()
        if not selected_node:
            return
        
        node_path = selected_node.text()
        parm_name = self.parm_dropdown.currentText()
        file_path = self.houdini_file_input.text()
        
        config = load_config()
        houdini_path = config['Paths'].get('houdini', '')
        houdini_bin_dir = os.path.dirname(houdini_path)
        hython_path = os.path.join(houdini_bin_dir, "hython.exe")
        
        temp_script = tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8")
        temp_script.write("import hou\n")
        temp_script.write(f"hou.hipFile.load(r'{file_path}')\n")
        temp_script.write(f"node = hou.node(r'{node_path}')\n")
        temp_script.write(f"parm_value = node.parm(r'{parm_name}').eval()\n")
        temp_script.write("print('PARM_VALUE_START')\n")
        temp_script.write("print(parm_value)\n")
        temp_script.write("print('PARM_VALUE_END')\n")
        temp_script.close()
        
        command = f'"{hython_path}" "{temp_script.name}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        os.unlink(temp_script.name)
        
        output = result.stdout.strip()
        if "PARM_VALUE_START" in output and "PARM_VALUE_END" in output:
            parm_value = output.split("PARM_VALUE_START")[1].split("PARM_VALUE_END")[0].strip()
        else:
            parm_value = "N/A"
        
        self.parm_value_label.setText(f"Parameter Value: {parm_value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tray = VFXTrayApp(app)
    sys.exit(app.exec())
