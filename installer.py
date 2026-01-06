#!/usr/bin/env python3
import gi
import os
import sys
import subprocess
import threading
import json
import shutil

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# Helpers del sistema

def get_locales():
    locales = []
    locales_dir = "/usr/share/i18n/locales"
    try:
        for f in os.listdir(locales_dir):
            if "_" in f:
                locales.append(f"{f}.UTF-8")
    except Exception:
        pass
    return sorted(locales)


def get_keymaps():
    keymaps = []
    base = "/usr/share/kbd/keymaps"
    for root, _, files in os.walk(base):
        for f in files:
            if f.endswith(".map.gz"):
                name = f.replace(".map.gz", "")
                keymaps.append((name, name))
    return sorted(set(keymaps))


def get_timezones():
    zones = []
    base = "/usr/share/zoneinfo"
    for root, _, files in os.walk(base):
        for f in files:
            path = os.path.join(root, f)
            if os.path.isfile(path):
                tz = path.replace(base + "/", "")
                if not tz.startswith(("Etc/", "posix/", "right/")):
                    zones.append(tz)
    return sorted(zones)

# --- Configuración Global ---
INSTALL_CONFIG = {
    "HOSTNAME": "olivos",
    "ROOT_PASSWORD": "",
    "USER_LOGIN": "",
    "USER_NAME": "",
    "USER_PASSWORD": "",
    "PARTITION_ROOT": None,
    "PARTITION_EFI": None,
    "PARTITION_SWAP": None,
    "PARTITION_HOME": None,
    "ROOT_FSTYPE": "ext4",
    "HOME_FSTYPE": "ext4",
    "TARGET_DISK": None,
    "LOCALE": "en_US.UTF-8",
    "KEYMAP": "us",
    "TIMEZONE": "UTC"
}

LOCALES = get_locales()
KEYMAPS = get_keymaps()
TIMEZONES = get_timezones()

MOUNT_POINT = "/mnt/target"

class Shell:
    """Ejecutor de comandos seguro (sin shell=True para evitar inyecciones)"""
    @staticmethod
    def run(cmd_list, input_text=None, check=True):
        """
        Ejecuta un comando pasando una LISTA de argumentos.
        Ejemplo: run(["useradd", "-m", "usuario con espacio"])
        """
        try:
            cmd_str = " ".join(cmd_list)
            print(f"[CMD] {cmd_str}")
            
            result = subprocess.run(
                cmd_list,
                shell=False, # CRÍTICO: False para evitar errores con espacios
                check=check,
                input=input_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stdout
        except FileNotFoundError:
            return False, f"Command not found: {cmd_list[0]}"

    @staticmethod
    def get_partitions():
        # lsblk devuelve JSON, es seguro parsearlo
        cmd = ["lsblk", "-J", "-p", "-o", "NAME,SIZE,TYPE,FSTYPE,LABEL"]
        success, output = Shell.run(cmd, check=False)
        partitions = []
        if success:
            try:
                data = json.loads(output)
                for device in data.get('blockdevices', []):
                    if device['type'] == 'disk':
                        partitions.append({
                            'path': device['name'], 
                            'desc': f"DISK: {device['name']} ({device['size']})",
                            'type': 'disk'
                        })
                    if 'children' in device:
                        for child in device['children']:
                            if child['type'] == 'part':
                                fstype = child.get('fstype', 'Raw')
                                label = f" [{child['label']}]" if child.get('label') else ""
                                partitions.append({
                                    'path': child['name'],
                                    'desc': f"PART: {child['name']} ({child['size']}) - {fstype}{label}",
                                    'type': 'part',
                                    'fstype': fstype
                                })
            except json.JSONDecodeError:
                pass
        return partitions

    @staticmethod
    def get_uuid(partition):
        success, output = Shell.run(["blkid", "-s", "UUID", "-o", "value", partition])
        return output.strip() if success else None

    @staticmethod
    def get_fstype(partition):
        success, output = Shell.run(["blkid", "-s", "TYPE", "-o", "value", partition])
        return output.strip().lower() if success else "unknown"

    @staticmethod
    def is_uefi():
        return os.path.exists("/sys/firmware/efi")

class VoidInstaller(Gtk.Window):
    def __init__(self):
        super().__init__(title="OlivOS Installer")
        self.set_default_size(900, 650)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        if os.geteuid() != 0:
            self.show_error("This installer MUST be run as root.", exit_app=True)
            return

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.main_box)

        # UI Setup
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("OlivOS Installer")
        self.set_titlebar(header)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.main_box.pack_start(self.stack, True, True, 0)

        # Navigation Area
        action_area = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_area.set_margin_top(10)
        action_area.set_margin_bottom(10)
        action_area.set_margin_end(10)
        action_area.set_margin_start(10)
        self.main_box.pack_end(action_area, False, False, 0)

        self.btn_back = Gtk.Button(label="Back")
        self.btn_back.connect("clicked", self.on_back)
        action_area.pack_start(self.btn_back, False, False, 0)

        self.btn_next = Gtk.Button(label="Next")
        self.btn_next.get_style_context().add_class("suggested-action")
        self.btn_next.connect("clicked", self.on_next)
        action_area.pack_end(self.btn_next, False, False, 0)

        self.pages = ["welcome", "regional", "user_config", "partitioning", "install"]
        self.current_page_idx = 0
        
        self.install_messages = [
            "OlivOS: fast, simple and clean",
            "Based on Void Linux",
            "Designed for real hardware",
            "No systemd. No bloat.",
            "Terminal-friendly by design"
        ]
        self._install_msg_idx = 0
        
        self.init_ui()
        self.update_nav()

    def init_ui(self):
        self.stack.add_named(self.create_welcome_page(), "welcome")
        self.stack.add_named(self.create_regional_page(), "regional")
        self.stack.add_named(self.create_user_page(), "user_config")
        self.stack.add_named(self.create_partition_page(), "partitioning")
        self.stack.add_named(self.create_install_page(), "install")

    def create_welcome_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)
        
        # Logo
        logo_path = "/usr/share/olivinstall/olivos-logo.png"
        if os.path.exists(logo_path):
            logo = Gtk.Image.new_from_file(logo_path)
            box.pack_start(logo, False, False, 0)

        # Texto
        lbl = Gtk.Label()
        lbl.set_markup("<span size='30000' weight='bold'>OlivOS GNU/Linux</span>")
        
        mode = "UEFI mode detected" if Shell.is_uefi() else "Legacy BIOS mode detected"
        msg = Gtk.Label(label=f"Welcome to OlivOS.\n{mode}\n\nWARNING: The data on the selected partitions will be deleted.")
        msg.set_justify(Gtk.Justification.CENTER)
        
        box.pack_start(lbl, False, False, 0)
        box.pack_start(msg, False, False, 0)
        return box

    def create_regional_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)
        box.set_margin_start(50)
        box.set_margin_end(50)
        
        title = Gtk.Label()
        title.set_markup("<span size='16000' weight='bold'>Regional Settings</span>")
        box.pack_start(title, False, False, 0)
        
        grid = Gtk.Grid(column_spacing=15, row_spacing=15)
        grid.set_halign(Gtk.Align.CENTER)
        
        # Idioma del sistema (Locale)
        lbl_locale = Gtk.Label(label="System Language:")
        lbl_locale.set_halign(Gtk.Align.END)
        self.combo_locale = Gtk.ComboBoxText()
        for locale in LOCALES:
            self.combo_locale.append(locale, locale)
        self.combo_locale.set_active_id(INSTALL_CONFIG["LOCALE"])
        
        grid.attach(lbl_locale, 0, 0, 1, 1)
        grid.attach(self.combo_locale, 1, 0, 1, 1)
        
        # Distribución de teclado
        lbl_keymap = Gtk.Label(label="Keyboard Layout:")
        lbl_keymap.set_halign(Gtk.Align.END)
        self.combo_keymap = Gtk.ComboBoxText()
        for keymap_id, keymap_name in KEYMAPS:
           self.combo_keymap.append(keymap_id, keymap_name)
        self.combo_keymap.set_active_id(INSTALL_CONFIG["KEYMAP"])
        
        grid.attach(lbl_keymap, 0, 1, 1, 1)
        grid.attach(self.combo_keymap, 1, 1, 1, 1)
        
        # Zona horaria
        lbl_timezone = Gtk.Label(label="Time Zone:")
        lbl_timezone.set_halign(Gtk.Align.END)
        self.combo_timezone = Gtk.ComboBoxText()
        for tz in TIMEZONES:
            self.combo_timezone.append(tz, tz)
        self.combo_timezone.set_active_id(INSTALL_CONFIG["TIMEZONE"])
        
        grid.attach(lbl_timezone, 0, 2, 1, 1)
        grid.attach(self.combo_timezone, 1, 2, 1, 1)
        
        box.pack_start(grid, False, False, 0)
    
        return box

    def create_user_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_valign(Gtk.Align.CENTER)
        box.set_margin_start(50)
        box.set_margin_end(50)

        title = Gtk.Label()
        title.set_markup("<span size='16000' weight='bold'>User Setup</span>")
        box.pack_start(title, False, False, 0)

        grid = Gtk.Grid(column_spacing=15, row_spacing=15)
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_valign(Gtk.Align.CENTER)
        grid.set_margin_top(20)
        box.pack_start(grid, False, False, 0)

        self.ent_host = Gtk.Entry(text=INSTALL_CONFIG["HOSTNAME"])
        grid.attach(Gtk.Label(label="Hostname:"), 0, 0, 1, 1)
        grid.attach(self.ent_host, 1, 0, 1, 1)

        grid.attach(Gtk.Separator(), 0, 1, 2, 1)

        self.ent_root_pass = Gtk.Entry(visibility=False)
        grid.attach(Gtk.Label(label="Password ROOT:"), 0, 2, 1, 1)
        grid.attach(self.ent_root_pass, 1, 2, 1, 1)

        grid.attach(Gtk.Separator(), 0, 3, 2, 1)

        self.ent_user = Gtk.Entry(text=INSTALL_CONFIG["USER_LOGIN"])
        self.ent_name = Gtk.Entry(text=INSTALL_CONFIG["USER_NAME"])
        self.ent_user_pass = Gtk.Entry(visibility=False)
        
        grid.attach(Gtk.Label(label="User (login):"), 0, 4, 1, 1)
        grid.attach(self.ent_user, 1, 4, 1, 1)
        grid.attach(Gtk.Label(label="Full Name:"), 0, 5, 1, 1)
        grid.attach(self.ent_name, 1, 5, 1, 1)
        grid.attach(Gtk.Label(label="User Password:"), 0, 6, 1, 1)
        grid.attach(self.ent_user_pass, 1, 6, 1, 1)
        
        lbl_hint = Gtk.Label(label="* The user will have superuser privileges with sudo")
        lbl_hint.get_style_context().add_class("dim-label")
        grid.attach(lbl_hint, 0, 7, 2, 1)
        
        return box

    def create_partition_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_valign(Gtk.Align.CENTER)
        box.set_margin_start(50)
        box.set_margin_end(50)

        title = Gtk.Label()
        title.set_markup("<span size='16000' weight='bold'>Disk Setup</span>")
        box.pack_start(title, False, False, 0)
        
        btn_gparted = Gtk.Button(label="Open GParted")
        btn_gparted.connect("clicked", self.launch_gparted)
        box.pack_start(btn_gparted, False, False, 10)

        grid = Gtk.Grid(row_spacing=10, column_spacing=10)
        
        # Selectores
        self.combo_root = Gtk.ComboBoxText()
        grid.attach(Gtk.Label(label="Root (/, ext4/btrfs/xfs):"), 0, 0, 1, 1)
        grid.attach(self.combo_root, 1, 0, 1, 1)

        self.combo_efi = Gtk.ComboBoxText()
        lbl_efi = Gtk.Label(label="EFI (/boot/efi):")
        if not Shell.is_uefi(): lbl_efi.set_sensitive(False)
        grid.attach(lbl_efi, 0, 1, 1, 1)
        grid.attach(self.combo_efi, 1, 1, 1, 1)

        self.combo_swap = Gtk.ComboBoxText()
        grid.attach(Gtk.Label(label="Swap:"), 0, 2, 1, 1)
        grid.attach(self.combo_swap, 1, 2, 1, 1)

        self.combo_home = Gtk.ComboBoxText()
        grid.attach(Gtk.Label(label="Home (/home):"), 0, 3, 1, 1)
        grid.attach(self.combo_home, 1, 3, 1, 1)

        self.combo_grub_disk = Gtk.ComboBoxText()
        lbl_grub = Gtk.Label(label="GRUB disk (Legacy):")
        if Shell.is_uefi(): lbl_grub.set_sensitive(False)
        grid.attach(lbl_grub, 0, 4, 1, 1)
        grid.attach(self.combo_grub_disk, 1, 4, 1, 1)

        box.pack_start(grid, False, False, 10)
        
        btn_refresh = Gtk.Button(label="Refresh List")
        btn_refresh.connect("clicked", lambda x: self.refresh_partitions())
        box.pack_start(btn_refresh, False, False, 0)
        return box

    def create_install_page(self):
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)

        # ZONA SUPERIOR (IMAGEN + TEXTO)
        overlay = Gtk.Overlay()
        overlay.set_hexpand(True)
        overlay.set_vexpand(True)

        image_path = "/usr/share/olivinstall/install-bg.png"
        if os.path.exists(image_path):
            image = Gtk.Image.new_from_file(image_path)
            image.set_hexpand(True)
            image.set_vexpand(True)
            image.set_halign(Gtk.Align.CENTER)
            image.set_valign(Gtk.Align.CENTER)
            overlay.add(image)
        else:
            overlay.add(Gtk.Label(label="Installing OlivOS..."))

        # --- Texto rotativo (overlay inferior) ---
        self.install_label = Gtk.Label()
        self.install_label.set_xalign(0.5)
        self.install_label.set_yalign(1.0)
        self.install_label.set_margin_bottom(12)

        self.install_label.set_markup(
            "<span size='24000' weight='bold' foreground='#4d551f'>Installing OlivOS…</span>"
        )

        overlay.add_overlay(self.install_label)

        paned.add1(overlay)

        # ZONA INFERIOR (STATUS + LOG)
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        bottom_box.set_margin_start(8)
        bottom_box.set_margin_end(8)
        bottom_box.set_margin_bottom(8)
        bottom_box.set_margin_top(6)

        self.lbl_status = Gtk.Label(label="Preparing installation...")
        self.lbl_status.set_xalign(0)
        bottom_box.pack_start(self.lbl_status, False, False, 0)

        self.progress = Gtk.ProgressBar()
        bottom_box.pack_start(self.progress, False, False, 0)

        self.log_view = Gtk.TextView(editable=False, monospace=True)
        self.log_view.set_wrap_mode(Gtk.WrapMode.NONE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.add(self.log_view)

        bottom_box.pack_start(scroll, True, True, 0)

        paned.add2(bottom_box)

        # Proporción
        GLib.idle_add(
            lambda: paned.set_position(int(self.get_allocated_height() * 0.6))
        )

        return paned

    def rotate_install_message(self):
        msg = self.install_messages[self._install_msg_idx]
        self.install_label.set_markup(
            f"<span size='24000' weight='bold' foreground='#4d551f'>{msg}</span>"
        )

        self._install_msg_idx = (self._install_msg_idx + 1) % len(self.install_messages)
        return True  # mantiene el timeout activo

    # --- Lógica ---

    def launch_gparted(self, widget):
        # Ventana de advertencia
        dlg = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Warning"
        )
        dlg.format_secondary_text(
            "GParted will open.\n"
            "Any changes you make will be permanent and may delete data.\n"
            "Do you want to continue?"
        )
        response = dlg.run()
        dlg.destroy()
    
        if response != Gtk.ResponseType.OK:
            return  # Usuario canceló

        # Lanzar GParted
        self.set_sensitive(False)
        subprocess.run(["gparted"])
        self.set_sensitive(True)
        self.refresh_partitions()

    def refresh_partitions(self):
        parts = Shell.get_partitions()
        self.combo_root.remove_all()
        self.combo_efi.remove_all()
        self.combo_swap.remove_all()
        self.combo_home.remove_all()
        self.combo_grub_disk.remove_all()
        
        self.combo_efi.append("none", "Ignore (Only Legacy)")
        self.combo_swap.append("none", "No Swap")
        self.combo_home.append("none", "No Home")
        self.combo_grub_disk.append("none", "Ignore (Only UEFI)")
        
        self.combo_efi.set_active_id("none")
        self.combo_swap.set_active_id("none")
        self.combo_home.set_active_id("none")

        for p in parts:
            fstype = p.get('fstype', '').lower()
            
            # Definición sistemas de archivos
            if p['type'] == 'part':
                if fstype in ["ext4", "btrfs", "xfs"]:
                     self.combo_root.append(p['path'], p['desc'])
                     self.combo_home.append(p['path'], p['desc'])
                     
                if fstype in ["swap", "linux-swap"]:
                     self.combo_swap.append(p['path'], p['desc'])
                     
                if 'vfat' in fstype or 'fat' in fstype:
                     self.combo_efi.append(p['path'], p['desc'])
                     
            # Asignación de disco/partición por defecto
            if p['type'] == 'disk' and not p['path'].startswith("/dev/zram"):
                  self.combo_grub_disk.append(p['path'], p['desc'])

            if self.combo_root.get_model() and len(self.combo_root.get_model()) > 0:
                self.combo_root.set_active(0)

            if self.combo_swap.get_model() and len(self.combo_swap.get_model()) > 1:
                self.combo_swap.set_active(1)

            if Shell.is_uefi():
                efi_model = self.combo_efi.get_model()
                if efi_model and len(efi_model) > 1:
                    self.combo_efi.set_active(1)
                grub_model = self.combo_grub_disk.get_model()
                if grub_model and len(grub_model) > 0:
                    self.combo_grub_disk.set_active(0)
            else:
                efi_model = self.combo_efi.get_model()
                if efi_model and len(efi_model) > 0:
                    self.combo_efi.set_active(0)
                grub_model = self.combo_grub_disk.get_model()
                if grub_model and len(grub_model) > 1:
                    self.combo_grub_disk.set_active(1)
                elif grub_model and len(grub_model) == 1:
                    self.combo_grub_disk.set_active(0)

    def update_nav(self):
        page = self.pages[self.current_page_idx]
        self.btn_back.set_sensitive(self.current_page_idx > 0)
        self.btn_back.set_visible(page != "install")
        if page == "partitioning": self.refresh_partitions()
        if page == "install":
            self.btn_next.set_visible(False)
            GLib.timeout_add_seconds(5, self.rotate_install_message) # Texto rotativo cada 5 segundos
            self.start_installation()
            
        elif self.current_page_idx == len(self.pages) - 2:
            self.btn_next.set_label("INSTALL")
            self.btn_next.get_style_context().add_class("destructive-action")
        else:
            self.btn_next.set_label("Next")
            self.btn_next.get_style_context().remove_class("destructive-action")

    def on_back(self, w):
        if self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.stack.set_visible_child_name(self.pages[self.current_page_idx])
            self.update_nav()

    def on_next(self, w):
        if self.validate_page():
            # Antes de instalar, mostrar resumen
            if self.pages[self.current_page_idx] == "partitioning":
                summary = (
                    f"Installation summary:\n\n"
                    f"Hostname: {INSTALL_CONFIG['HOSTNAME']}\n"
                    f"User: {INSTALL_CONFIG['USER_LOGIN']} ({INSTALL_CONFIG['USER_NAME']})\n"
                    f"Root: {INSTALL_CONFIG['PARTITION_ROOT']} ({INSTALL_CONFIG['ROOT_FSTYPE']})\n"
                    f"Home: {INSTALL_CONFIG['PARTITION_HOME']} ({INSTALL_CONFIG.get('HOME_FSTYPE', '')})\n"
                    f"Swap: {INSTALL_CONFIG['PARTITION_SWAP']}\n"
                    f"EFI: {INSTALL_CONFIG['PARTITION_EFI']}\n"
                    f"GRUB Disk: {INSTALL_CONFIG['TARGET_DISK']}\n"
                    f"Locale: {INSTALL_CONFIG['LOCALE']}\n"
                    f"Keymap: {INSTALL_CONFIG['KEYMAP']}\n"
                    f"Timezone: {INSTALL_CONFIG['TIMEZONE']}\n\n"
                    "Do you want to continue with the installation?"
                )
                dlg = Gtk.MessageDialog(
                    parent=self,
                    flags=0,
                    message_type=Gtk.MessageType.QUESTION,
                    buttons=Gtk.ButtonsType.YES_NO,
                    text="Installation confirmation"
                )
                dlg.format_secondary_text(summary)
                response = dlg.run()
                dlg.destroy()
                if response != Gtk.ResponseType.YES:
                    return  # Usuario canceló

            # Continuar al siguiente paso
            self.current_page_idx += 1
            self.stack.set_visible_child_name(self.pages[self.current_page_idx])
            self.update_nav()

    def validate_page(self):
        page = self.pages[self.current_page_idx]
        if page == "regional":
             INSTALL_CONFIG["LOCALE"] = self.combo_locale.get_active_id()
             INSTALL_CONFIG["KEYMAP"] = self.combo_keymap.get_active_id()
             INSTALL_CONFIG["TIMEZONE"] = self.combo_timezone.get_active_id()
        
             if not all([INSTALL_CONFIG["LOCALE"], INSTALL_CONFIG["KEYMAP"], INSTALL_CONFIG["TIMEZONE"]]):
                 self.show_error("You must select all regional settings.")
                 return False
        if page == "user_config":
            INSTALL_CONFIG["HOSTNAME"] = self.ent_host.get_text().strip()
            INSTALL_CONFIG["ROOT_PASSWORD"] = self.ent_root_pass.get_text()
            INSTALL_CONFIG["USER_LOGIN"] = self.ent_user.get_text().strip()
            INSTALL_CONFIG["USER_PASSWORD"] = self.ent_user_pass.get_text()
            INSTALL_CONFIG["USER_NAME"] = self.ent_name.get_text().strip()
            
            # Validaciones básicas
            if " " in INSTALL_CONFIG["USER_LOGIN"]:
                self.show_error("The user login cannot contain spaces.")
                return False
            
            if not all([INSTALL_CONFIG["HOSTNAME"], INSTALL_CONFIG["ROOT_PASSWORD"], 
                        INSTALL_CONFIG["USER_LOGIN"], INSTALL_CONFIG["USER_PASSWORD"]]):
                self.show_error("All fields are required.")
                return False
                
        if page == "partitioning":
            INSTALL_CONFIG["PARTITION_ROOT"] = self.combo_root.get_active_id()
            INSTALL_CONFIG["PARTITION_SWAP"] = self.combo_swap.get_active_id()
            INSTALL_CONFIG["PARTITION_HOME"] = self.combo_home.get_active_id()
            INSTALL_CONFIG["PARTITION_EFI"] = self.combo_efi.get_active_id()
            INSTALL_CONFIG["TARGET_DISK"] = self.combo_grub_disk.get_active_id()
            
            if not INSTALL_CONFIG["PARTITION_ROOT"]:
                self.show_error("You must select a root partition.")
                return False
            
            if Shell.is_uefi() and INSTALL_CONFIG["PARTITION_EFI"] == "none":
                self.show_error("You are in UEFI mode but did not select the EFI partition.\nThe system will NOT start.")
                return False

            INSTALL_CONFIG["ROOT_FSTYPE"] = Shell.get_fstype(INSTALL_CONFIG["PARTITION_ROOT"])

            home = INSTALL_CONFIG["PARTITION_HOME"]
            if home != "none":
                INSTALL_CONFIG["HOME_FSTYPE"] = Shell.get_fstype(home)

        return True

    def log(self, text):
        GLib.idle_add(self._log_gui, text)

    def _log_gui(self, text):
        buf = self.log_view.get_buffer()
        buf.insert(buf.get_end_iter(), f"{text}\n")
        self.log_view.scroll_to_mark(buf.create_mark(None, buf.get_end_iter(), False), 0.0, True, 0.0, 1.0)

    def update_progress(self, fraction, status):
        GLib.idle_add(self._update_progress_gui, fraction, status)
    
    def _update_progress_gui(self, f, s):
        self.progress.set_fraction(f)
        self.lbl_status.set_text(s)

    def start_installation(self):
        thread = threading.Thread(target=self.run_install_process)
        thread.daemon = True
        thread.start()

    def run_cmd_chk(self, cmd_list, desc):
        """Wrapper para comandos tipo lista"""
        self.log(f"> {desc}...")
        success, out = Shell.run(cmd_list)
        if not success:
            self.log(f"ERROR OUTPUT: {out}")
            raise Exception(f"Failure in: {desc}")

    def run_install_process(self):
        try:
            root = INSTALL_CONFIG["PARTITION_ROOT"]
            swap = INSTALL_CONFIG["PARTITION_SWAP"]
            efi = INSTALL_CONFIG["PARTITION_EFI"]
            is_uefi = Shell.is_uefi()
            
            # 1. Formateo
            self.update_progress(0.1, "Preparing partitions...")
            Shell.run(["umount", "-R", MOUNT_POINT], check=False)
            if swap != "none": Shell.run(["swapoff", swap], check=False)
            
            root_fs = INSTALL_CONFIG["ROOT_FSTYPE"]

            if root_fs == "ext4":
                self.run_cmd_chk(["mkfs.ext4", "-F", root], "Formatting Root (ext4)")
            elif root_fs == "btrfs":
                self.run_cmd_chk(["mkfs.btrfs", "-f", root], "Formatting Root (btrfs)")
            elif root_fs == "xfs":
                self.run_cmd_chk(["mkfs.xfs", "-f", root], "Formatting Root (xfs)")
            else:
                raise Exception(f"Filesystem {root_fs} not supported")
                
            if swap != "none": 
                self.run_cmd_chk(["mkswap", swap], "Formatting Swap")

            # 2. Montaje
            self.update_progress(0.2, "Mounting file system...")
            self.run_cmd_chk(["mkdir", "-p", MOUNT_POINT], "Creating root dir")
            self.run_cmd_chk(["mount", root, MOUNT_POINT], "Mounting Root")
            
            home = INSTALL_CONFIG["PARTITION_HOME"]

            if home != "none":
                self.run_cmd_chk(["mkdir", "-p", f"{MOUNT_POINT}/home"], "Creating /home")
                self.run_cmd_chk(["mount", home, f"{MOUNT_POINT}/home"], "Mounting /home")
            
            if is_uefi and efi != "none":
                self.run_cmd_chk(["mkdir", "-p", f"{MOUNT_POINT}/boot/efi"], "Creating dir EFI")
                self.run_cmd_chk(["mount", efi, f"{MOUNT_POINT}/boot/efi"], "Mounting EFI")
                
            if swap != "none": 
                self.run_cmd_chk(["swapon", swap], "Activating Swap")

            # 3. COPIA LOCAL
            self.update_progress(0.3, "Cloning system (This may take a while)...")
            # Excluimos directorios virtuales y basura temporal
            tar_cmd = [
                "tar", "-c",
                "--one-file-system",
                "--exclude=" + MOUNT_POINT, # No copiarse a sí mismo
                "--exclude=/sys/*",
                "--exclude=/proc/*",
                "--exclude=/tmp/*",
                "--exclude=/run/*",
                "--exclude=/mnt/*",
                "-C", "/", "." 
            ]
            
            # Pipe a extract
            extract_cmd = ["tar", "-x", "-p", "--xattrs", "-C", MOUNT_POINT]
            
            # Python subprocess pipe
            self.log("Starting TAR pipe...")
            p1 = subprocess.Popen(tar_cmd, stdout=subprocess.PIPE)
            p2 = subprocess.run(extract_cmd, stdin=p1.stdout, check=True)
            p1.wait()

            # 4. Configuración Post-Copia
            self.update_progress(0.6, "Configuring chroot...")
            
            # Montar pseudo-filesystems
            for fs in ["dev", "proc", "sys"]:
                self.run_cmd_chk(["mount", "--rbind", f"/{fs}", f"{MOUNT_POINT}/{fs}"], f"Bind /{fs}")
                self.run_cmd_chk(["mount", "--make-rslave", f"{MOUNT_POINT}/{fs}"], f"Slave /{fs}")

            def in_chroot(cmd_list, input_text=None):
                # Ejecuta directamente el binario dentro del chroot
                full_cmd = ["chroot", MOUNT_POINT] + cmd_list
                # AHORA SÍ pasamos el input_text a Shell.run
                s, o = Shell.run(full_cmd, input_text=input_text)
                if not s: raise Exception(f"Error Chroot {cmd_list[0]}: {o}")
                self.log(f"[CHROOT] {' '.join(cmd_list)}")

            # Limpieza
            Shell.run(["rm", "-f", f"{MOUNT_POINT}/etc/sudoers.d/99-void-live"], check=False)
            
            # Generar fstab
            self.log("Generating fstab...")
            uuid_root = Shell.get_uuid(root)
            fstab_content = f"UUID={uuid_root} / {root_fs} defaults 0 1\n"
            
            if is_uefi and efi != "none":
                uuid_efi = Shell.get_uuid(efi)
                fstab_content += f"UUID={uuid_efi} /boot/efi vfat defaults 0 2\n"
                
            if swap != "none":
                uuid_swap = Shell.get_uuid(swap)
                fstab_content += f"UUID={uuid_swap} none swap defaults 0 0\n"
                
            if home != "none":
                uuid_home = Shell.get_uuid(home)
                home_fs = INSTALL_CONFIG.get("HOME_FSTYPE", "ext4")
                fstab_content += f"UUID={uuid_home} /home {home_fs} defaults 0 2\n"

            with open(f"{MOUNT_POINT}/etc/fstab", "w") as f: f.write(fstab_content)

            # Fix Sudoers (Tu fallo #2 corregido programáticamente)
            sudoers_path = f"{MOUNT_POINT}/etc/sudoers"
            if os.path.exists(sudoers_path):
                with open(sudoers_path, 'r') as f: s_data = f.read()
                # Descomentar el grupo wheel
                s_data = s_data.replace("# %wheel ALL=(ALL:ALL) ALL", "%wheel ALL=(ALL:ALL) ALL")
                with open(sudoers_path, 'w') as f: f.write(s_data)

            # Configuración Regional
            self.update_progress(0.65, "Applying regional settings...")

            # Hostname
            with open(f"{MOUNT_POINT}/etc/hostname", "w") as f: 
                f.write(INSTALL_CONFIG["HOSTNAME"])

            # Locale
            self.log(f"Configuring locale: {INSTALL_CONFIG['LOCALE']}")
            locale_conf = f"LANG={INSTALL_CONFIG['LOCALE']}\nLC_COLLATE=C\n"
            with open(f"{MOUNT_POINT}/etc/locale.conf", "w") as f: 
                f.write(locale_conf)

            # Descomenta el locale en /etc/default/libc-locales
            locale_base = INSTALL_CONFIG['LOCALE'].split('.')[0]
            locales_file = f"{MOUNT_POINT}/etc/default/libc-locales"
            if os.path.exists(locales_file):
                with open(locales_file, 'r') as f:
                    locales_data = f.read()
                locales_data = locales_data.replace(f"#{locale_base}", locale_base)
                with open(locales_file, 'w') as f:
                    f.write(locales_data)

            # Keymap y Timezone en rc.conf
            with open(f"{MOUNT_POINT}/etc/rc.conf", "a") as f:
                f.write(f"\nKEYMAP={INSTALL_CONFIG['KEYMAP']}\nTIMEZONE={INSTALL_CONFIG['TIMEZONE']}\n")
            
            # Consola (explícito)
            with open(f"{MOUNT_POINT}/etc/vconsole.conf", "w") as f:
                f.write(f"KEYMAP={INSTALL_CONFIG['KEYMAP']}\n")
            
            # Keymap X11 (soluciona el bug histórico de Void)
            keymap = INSTALL_CONFIG["KEYMAP"]

            content = f"""Section "InputClass"
                Identifier "system-keyboard"
                MatchIsKeyboard "on"
                Option "XkbLayout" "{keymap}"
                Option "XkbModel" "pc105"
            EndSection
            """

            path = os.path.join(MOUNT_POINT, "etc/X11/xorg.conf.d")
            os.makedirs(path, exist_ok=True)

            with open(os.path.join(path, "00-keyboard.conf"), "w") as f:
                f.write(content)
            
            # Crear symlink para timezone
            tz_source = f"/usr/share/zoneinfo/{INSTALL_CONFIG['TIMEZONE']}"
            tz_dest = f"{MOUNT_POINT}/etc/localtime"
            Shell.run(["rm", "-f", tz_dest], check=False)
            Shell.run(["ln", "-sf", tz_source, tz_dest], check=False)
            
            # Root pass
            in_chroot(["chpasswd", "-c", "SHA512"], input_text=f"root:{INSTALL_CONFIG['ROOT_PASSWORD']}")

            # Crear usuario (Tu fallo #1 corregido usando listas)
            u, n, p = INSTALL_CONFIG['USER_LOGIN'], INSTALL_CONFIG['USER_NAME'], INSTALL_CONFIG['USER_PASSWORD']
            # Borrar usuario live si existe conflicto (opcional)
            in_chroot(["userdel", "-r", "anon"]) # Ignorar error
            
            # useradd recibe lista pura. Los espacios en 'n' son manejados por subprocess.
            in_chroot(["useradd", "-m", "-c", n, "-G", "wheel,users,audio,video,cdrom,input", u])
            in_chroot(["chpasswd", "-c", "SHA512"], input_text=f"{u}:{p}")

            # Regenerar Initramfs
            self.update_progress(0.8, "Regenerating Initramfs...")
            # Usar regenerate-all para evitar discrepancias de versión de kernel
            in_chroot(["dracut", "--regenerate-all", "--force"])

            # Regenerar locales
            self.log("Regenerating locales...")
            in_chroot(["xbps-reconfigure", "-f", "glibc-locales"])

            # Bootloader
            self.update_progress(0.9, "Installing Bootloader...")
            if is_uefi:
                self.log("Installing GRUB for UEFI...")
                in_chroot(["grub-install", "--target=x86_64-efi", "--efi-directory=/boot/efi", "--bootloader-id=OlivOS"])
            else:
                self.log("Installing GRUB Legacy (MBR)...")
                in_chroot(["grub-install", INSTALL_CONFIG['TARGET_DISK']])
                
            in_chroot(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])
            in_chroot(["xbps-reconfigure", "-fa"])

            # --- Limpieza final de montajes ---
            self.update_progress(0.98, "Final cleanup...")

            # Desactivar swap
            swap = INSTALL_CONFIG.get("PARTITION_SWAP")
            if swap and swap != "none":
                Shell.run(["swapoff", swap], check=False)

            # Desmontar pseudo-filesystems primero
            for fs in ["dev", "proc", "sys"]:
                Shell.run(["umount", "-R", f"{MOUNT_POINT}/{fs}"], check=False)

            # Desmontaje recursivo final
            Shell.run(["umount", "-R", MOUNT_POINT], check=False)

            self.update_progress(1.0, "Installation complete.")
            GLib.idle_add(self.show_success)

        except Exception as e:
            self.log(f"CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            GLib.idle_add(self.show_error, str(e))

    def show_error(self, msg, exit_app=False):
        dlg = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dlg.format_secondary_text(msg)
        dlg.run(); dlg.destroy()
        if exit_app: sys.exit(1)

    def show_success(self):
        dlg = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Success"
        )
        dlg.format_secondary_text("Installation completed successfully.\nRestart now?")
        if dlg.run() == Gtk.ResponseType.YES: 
            subprocess.run(["reboot"])
        else: 
            sys.exit(0)
        dlg.destroy()

if __name__ == "__main__":
    win = VoidInstaller()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
