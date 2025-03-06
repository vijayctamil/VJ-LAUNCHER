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

class VFXTrayApp(QSystemTrayIcon):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setIcon(QIcon("img\\V_icon.png"))
        self.setToolTip("VFX Pipeline Launcher")
        self.menu = QMenu()
        
        self.folder_generator_action = QAction("Folder Generator", self)
        self.get_node_action = QAction("Get Node", self)
        self.launch_houdini_action = QAction("Launch Houdini", self)
        self.launch_nuke_action = QAction("Launch Nuke X", self)
        self.settings_action = QAction("Settings", self)
        self.quit_action = QAction("Quit", self)
        
        self.menu.addAction(self.folder_generator_action)
        self.menu.addAction(self.get_node_action)
        self.menu.addAction(self.launch_houdini_action)
        self.menu.addAction(self.launch_nuke_action)
        self.menu.addSeparator()
        self.menu.addAction(self.settings_action)
        self.menu.addAction(self.quit_action)
        
        self.setContextMenu(self.menu)
        
        self.folder_generator_action.triggered.connect(self.show_folder_generator)
        self.get_node_action.triggered.connect(self.show_get_node)
        self.launch_houdini_action.triggered.connect(self.launch_houdini)
        self.launch_nuke_action.triggered.connect(self.launch_nuke)
        self.settings_action.triggered.connect(self.show_settings)
        self.quit_action.triggered.connect(self.quit_app)
        
        self.settings_window = None
        self.folder_generator_window = None
        self.get_node_window = None
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
