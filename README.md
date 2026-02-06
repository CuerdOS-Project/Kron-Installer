# Azamara Intaller

Graphical installer for **OlivOS GNU/Linux**, inspired by the official Void Linux installer, but rewritten in **Python + PySide6 (Qt6)**.  
It allows you to configure partitions, user, system language, keyboard layout, and timezone in a simple and safe way.

---

## Features

- **Modern Graphical Interface**: Built with **PySide6 (Qt6)** for a responsive look and feel.
- **Partition Management**:
  - Root (`/`) → Supports `ext4/3/2`, `btrfs`, `xfs`.
  - Home (`/home`) → Supports `ext4/3/2`, `btrfs`, `xfs`.
  - Swap → Automatic detection and selection.
  - EFI → Supports FAT/VFAT (required for UEFI).
  - Button to open **KDE Partition Manager** for manual setup.
- **System Configuration**:
  - Hostname configuration.
  - User account and password creation.
  - System language (locale) and timezone selection.
  - Keyboard layout (keymap) selection.
  - Software repository (Mirrors) selection.
  - Optional: Non-free drivers (NVIDIA, Intel microcode).
- **Installation Process**:
  - **Non-blocking installation**: Uses a threaded backend (`InstallWorker`) to keep the UI responsive.
  - **Dynamic Progress Bar**: Heuristic progress tracking with smooth animations during long operations (Copy/Update).
  - Real-time log terminal (toggleable).
  - Automates copying the base system, generating `fstab`, creating users, setting locales, regenerating initramfs, and installing the bootloader (GRUB).
- **Internationalization (i18n)**: Full support for translations using Qt Linguist.

---

## Requirements

- Python 3.10+
- **PySide6** (Qt6 for Python)
- Qt6 Core and Widgets libraries
- System tools (Void Linux base):
  - `tar`, `chroot`, `mkfs`, `grub-install`, `xbps-reconfigure`
  - `gptfdisk` (provides sgdisk, required for automatic partition)
  - `partitionmanager` (KDE Partition Manager) for manual disk setup.
  - `pkexec` (for policykit/root privileges)
- Must be run as **root** (handled via `pkexec`).

---

## Project Structure

The project is organized modularly for better maintenance:

- `main.py`: Entry point.
- `ui/`: Contains all UI pages (`disks.py`, `installation.py`, `welcome.py`, etc.).
- `install/`: Contains the backend logic and scripts:
  - `install_thread.py`: `InstallWorker` class (QThread) managing the installation process.
  - `backend_install.sh`: Bash script for low-level system operations.
  - `auto_partition.sh`: Script for automated partitioning.
- `utils/`: Helper functions (system detection, locales).
- `i18n/`: Translation files (`.ts` and compiled `.qm`).
- `images/`: Contains all images used by the graphical interface.

---

## Usage

1.  Ensure you have the necessary Python dependencies:
    Via pip (generic):
    ```bash
    pip install PySide6
    ```
    or via XBPS:
    ```bash
    xbps-install -S python3-pyside6-widgets python3-pyside6-gui
    ```
    
2.  Run the installer (usually via a desktop launcher or policykit):
    ```bash
    python3 main.py
    ```
```
