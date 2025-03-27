# 🎬 VFX Pipeline Launcher

A fully-featured desktop tray app built with **PySide6** for managing a local VFX pipeline. It provides artists and technical directors with a centralized launcher for essential tools like **Houdini**, **Nuke**, folder generation, batch render setup, and parameter access via Houdini scripting.

---

## 🛠 Features

- 🚀 One-click launch for **Houdini** and **NukeX** (paths configurable)
- 📁 **Folder Generator**: Create project folder structures from a CSV
- 🎛 **Get Node Tool**: Load Houdini files, explore nodes, and get/set parameter values
- ⚙️ **Batch Render Setup**: Merge multiple `.txt` command files into a `.bat` file for automation
- 💾 Persistent **settings** stored in `settings.ini`
- 🧰 Runs as a **system tray application**

---

## 🧩 Included Tools

### 📁 Folder Generator
- Upload a CSV with folder names
- Choose a target location
- Instantly create entire folder structures

### 🎛 Get Node Tool (Houdini)
- Browse `.hip` or `.hipnc` files
- Load and list all node paths
- See and interact with node parameters
- Set parameter values using Houdini's `hython`

### 🛠 Batch Render Setup
- Load multiple `.txt` files with render commands
- Combine into a `.bat` file for batch processing
- Choose custom output path

---

## 🚀 Getting Started

### 📦 Install requirements:

```bash
pip install PySide6
```

Make sure Houdini and Nuke are installed locally. You'll also need the Houdini Python executable `hython.exe` for the Get Node tool.

---

## ⚙️ Configuration

Paths to Houdini and Nuke executables are saved in `settings.ini` and can be configured through the **Settings** window:

```ini
[Paths]
houdini = C:/Program Files/SideFX/Houdini XX.X.X/bin/houdini.exe
nuke = C:/Program Files/NukeX XX.X/nukeX.exe
```

---

## ▶️ Running the App

```bash
python vfx_launcher_v010.py
```

- The app launches as a **system tray icon** (bottom right of the desktop)
- Right-click the icon to access all tools

---

## 📂 Folder Structure

```
VFX_Launcher_App/
├── vfx_launcher_v010.py
├── settings.ini  # created automatically
├── img/
│   └── V_icon.png
└── README.md
```
