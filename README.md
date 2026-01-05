# OlivInstall

Graphical installer for **OlivOS GNU/Linux**, inspired by the official Void Linux installer, but rewritten in **Python + GTK**.  
It allows you to configure partitions, user, system language, keyboard layout, and timezone in a simple and safe way.

---

## Features

- Graphical interface using **GTK3**.
- Support for **UEFI and Legacy BIOS**.
- Partition selection:
  - Root (`/`) → only `ext4`, `btrfs`, `xfs`.
  - Home (`/home`) → only `ext4`, `btrfs`, `xfs`.
  - Swap → only `swap` partitions.
  - EFI → only FAT/VFAT.
- Configuration options:
  - Hostname
  - User account and password
  - System language (locale)
  - Keyboard layout (keymap)
  - Timezone
- **GParted button** with a warning about irreversible changes.
- Installation summary before formatting.
- Real-time installation progress log.
- Automates copying the base system, generating `fstab`, creating users and passwords, setting locales, regenerating initramfs, and installing the bootloader.

---

## Requirements

- Python 3
- PyGObject (GTK3)
- Void Linux base tools:
  - `tar`, `chroot`, `mkfs`, `grub-install`, `xbps-reconfigure`
- Must be run as **root**.
