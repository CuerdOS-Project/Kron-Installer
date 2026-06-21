import re

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject


class InstallerConfigCollector(QObject):
    def __init__(self, parent, paginas, system_data):
        super().__init__(parent)
        self.parent = parent
        self.paginas = paginas
        self.system_data = system_data
        
    def collect_data(self):
        data = {}
        try:
            # --- 1. Idiomas ---
            pag_idiomas = self.paginas["idiomas"]

            data["LOCALE"] = pag_idiomas.idioma_combo.currentData()
            tz_region = pag_idiomas.region_combo.currentText()
            tz_city = pag_idiomas.ciudad_combo.currentText()
            data["TIMEZONE"] = f"{tz_region}/{tz_city}"
            data["KEYMAP"] = pag_idiomas.teclado_combo.currentData()

            # --- 2. Usuarios ---
            pag_usuarios = self.paginas["usuarios"]

            # Validar que las contraseñas coincidan antes de continuar
            if not pag_usuarios.validate_passwords():
                QMessageBox.warning(
                    self.parent,
                    self.tr("Error en contraseñas"),
                    self.tr("Las contraseñas no coinciden o están vacías. Por favor, verifica los campos de contraseña."),
                )
                return None

            data["HOSTNAME"] = pag_usuarios.nombre_equipo.text().strip()
            data["USERLOGIN"] = pag_usuarios.user_name.text().strip()
            data["USERNAME"] = pag_usuarios.username_name.text()
            data["USERPASSWORD"] = pag_usuarios.user_pass.text()
            data["ROOTPASSWORD"] = pag_usuarios.root_pass.text()
            data["USERGROUPS"] = "wheel,audio,video,users,network,optical,cdrom"

            # Validación campos obligatorios
            required_fields = {
                "HOSTNAME" : self.tr("Nombre del equipo (hostname)"),
                "USERLOGIN": self.tr("Usuario (login)"),
                "USERNAME": self.tr("Nombre completo"),
                "USERPASSWORD": self.tr("Contraseña del usuario"),
                "ROOTPASSWORD": self.tr("Contraseña de root"),
            }
            missing = [label for key, label in required_fields.items() if not data[key]]
            if missing:
                QMessageBox.warning(
                    self.parent,
                    self.tr("Faltan datos"),
                    self.tr("Debes completar los siguientes campos:\n\n- ")
                    + "\n- ".join(missing),
                )
                return None

            # Validación de campos mal introducidos
            hostname = data["HOSTNAME"]
            userlogin = data["USERLOGIN"]
            user_pass = data["USERPASSWORD"]
            root_pass = data["ROOTPASSWORD"]

            hostname_re = re.compile(r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$')
            user_re = re.compile(r'^[a-z_][a-z0-9_-]*$')

            if hostname.lower() != hostname or not hostname_re.match(hostname):
                QMessageBox.warning(
                    self.parent,
                    self.tr("Hostname inválido"),
                    self.tr(
                        "El nombre del equipo solo puede contener letras minúsculas,\n"
                        "números y guiones, y no puede empezar ni terminar con un guión."
                    ),
                )
                return None

            if userlogin.lower() != userlogin or not user_re.match(userlogin):
                QMessageBox.warning(
                    self.parent,
                    self.tr("Usuario inválido"),
                    self.tr(
                        "El nombre de usuario solo puede contener letras minúsculas,\n"
                        "números, guiones y guiones bajos, y no puede contener espacios."
                    ),
                )
                return None

            for key, label, pwd in [
                ("USERPASSWORD", self.tr("Contraseña del usuario"), user_pass),
                ("ROOTPASSWORD", self.tr("Contraseña de root"), root_pass),
            ]:
                if pwd.strip() != pwd:
                    QMessageBox.warning(
                        self.parent,
                        self.tr("Contraseña inválida"),
                        self.tr("{label} no puede empezar ni terminar con espacios.").format(label = label),
                    )
                    return None

                if len(pwd) < 4:
                    QMessageBox.warning(
                        self.parent,
                        self.tr("Contraseña demasiado corta"),
                        self.tr("{label} debe tener al menos 4 caracteres.").format(label = label),
                    )
                    return None

            # --- 3. Repo y software ---
            pag_mirrors = self.paginas["mirrors"]

            data["UPDATE"] = "1" if self.system_data.get("net", True) else "0"
            data["MIRROR"] = pag_mirrors.mirror_combo.currentData()
            data["NONFREE"] = "1" if pag_mirrors.chk_nonfree.isChecked() else "0"
            data["NVIDIA"] = "1" if pag_mirrors.chk_nvidia.isChecked() else "0"
            data["INTEL"] = "1" if pag_mirrors.chk_intel.isChecked() else "0"

            # --- 4. Discos ---
            pag_discos = self.paginas["discos"]

            raw_parts = pag_discos.obtener_seleccion()
            partitions = []
            filesys = pag_discos.filesys_combo.currentText().lower()

            def clean(txt):
                return txt.split(" ")[0]

            # Validaciones y creación de particiones
            part_checks = [
                ("root", "/", True, self.tr("Debe seleccionar una partición Raíz (/)."))
            ]
            if self.system_data.get("efi", False):
                part_checks.append(("efi", "/boot/efi", True, self.tr("Debe seleccionar una partición EFI (/boot/efi).")))

            for key, point, must_format, msg in part_checks:
                if raw_parts[key] is None:
                    QMessageBox.warning(self.parent, self.tr("Error"), msg)
                    return None
                partitions.append({
                    "dev": clean(raw_parts[key]),
                    "point": point,
                    "fs": "vfat" if key == "efi" else filesys,
                    "format": "1" if must_format else "0"
                })

            # SWAP
            if raw_parts["swap"] is not None:
                partitions.append({"dev": clean(raw_parts["swap"]), "point": "none", "fs": "swap", "format": "1"})

            # HOME
            if raw_parts["home"] is not None:
                partitions.append({"dev": clean(raw_parts["home"]), "point": "/home", "fs": filesys, "format": "0"})

            data["PARTITIONS"] = partitions

            # --- BOOTLOADER ---
            root_dev = clean(raw_parts["root"])
            disk_dev = re.sub(r'\d+$', '', root_dev)
            if "nvme" in disk_dev and disk_dev.endswith("p"):
                disk_dev = disk_dev[:-1]
            data["BOOTLOADER"] = disk_dev

            return data

        except Exception as e:
            QMessageBox.critical(self.parent, self.tr("Error"), self.tr("Error procesando datos: ") + str(e))
            return None