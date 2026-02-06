from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class DisksPage(QWidget):
    def __init__(self, sys_data):
        super().__init__()
        self.setup_ui(sys_data)
        self.translate_ui()

    def setup_ui(self, sys_data):
        main_layout = QVBoxLayout(self)

        # --- Layout horizontal ---
        h_layout = QHBoxLayout()

        # --- Izquierda: imagen ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addStretch()
        imagen = QLabel()
        pixmap = QPixmap("images/disco.png")
        imagen.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        left_layout.addWidget(imagen, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # --- Derecha: formulario ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # Título
        self.titl = QLabel()
        self.titl.setStyleSheet("font-size: 24px; font-weight: 500; padding-bottom: 15px;")
        right_layout.addWidget(self.titl)

        # --- Auto particionado ---
        self.auto_label = QLabel()

        auto_layout = QHBoxLayout()
        auto_layout.setSpacing(10)

        self.disk_combo = QComboBox()
        self.disk_combo.setFixedWidth(200)

        self.btn_autopart = QPushButton()
        self.btn_autopart.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.btn_autopart.setFixedWidth(90)

        right_layout.addWidget(self.auto_label)
        auto_layout.addWidget(self.disk_combo)
        auto_layout.addWidget(self.btn_autopart)

        right_layout.addLayout(auto_layout)

        self.btn_autopart.clicked.connect(self.autoparticionado)
        self.cargar_discos()

        right_layout.addSpacing(15)

        # Botón abrir KDE Partition Manager
        self.part_label = QLabel()

        self.btn_partman = QPushButton()
        self.btn_partman.setFixedWidth(300)
        self.btn_partman.clicked.connect(self.abrir_partition_manager)
        right_layout.addWidget(self.part_label)
        right_layout.addWidget(self.btn_partman)
        right_layout.addSpacing(15)
        
        # Sistema de archivos
        fs_layout = QHBoxLayout()  # layout horizontal para combo + label

        self.filesys_combo = QComboBox()
        self.filesys_combo.addItems(["BTRFS", "Ext4", "Ext3", "Ext2", "XFS"])
        self.filesys_combo.setFixedWidth(70)

        self.fs_label = QLabel()  # el texto a la derecha

        fs_layout.addWidget(self.filesys_combo)
        fs_layout.addWidget(self.fs_label)

        right_layout.addLayout(fs_layout)
        right_layout.addSpacing(15)

        # Formulario de particiones
        form_layout = QFormLayout()
        self.raiz_combo = QComboBox()
        self.efi_combo = QComboBox()
        self.home_combo = QComboBox()
        self.swap_combo = QComboBox()

        self.lbl_root = QLabel()
        self.lbl_efi = QLabel()
        self.lbl_home = QLabel()
        self.lbl_swap = QLabel()

        form_layout.addRow(self.lbl_root, self.raiz_combo)
        
        # EFI con label y formulario separados para poder ocultarlos
        form_layout.addRow(self.lbl_efi, self.efi_combo)

        form_layout.addRow(self.lbl_home, self.home_combo)
        form_layout.addRow(self.lbl_swap, self.swap_combo)

        # Ocultar EFI si es BIOS Legacy
        if not sys_data["efi"]:
            self.efi_combo.setVisible(False)
            self.lbl_efi.setVisible(False)

        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setVerticalSpacing(10)

        right_layout.addLayout(form_layout)
        right_layout.addStretch()

        # --- Layout horizontal ---
        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        h_layout.setStretch(0, 1)
        h_layout.setStretch(1, 1)

        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

    def translate_ui(self):
        self.titl.setText(self.tr("Discos y particiones"))
        self.auto_label.setText(self.tr("Elegir disco a particionar (automático):"))
        self.btn_autopart.setText(self.tr("Particionar"))
        self.part_label.setText(self.tr("O particionar manualmente:"))
        self.btn_partman.setText(self.tr("Abrir KDE Partition Manager"))
        self.fs_label.setText(self.tr("Seleccionar sistema de archivos"))
        self.titl.setText(self.tr("Discos y particiones"))

        self.lbl_root.setText(self.tr("Raíz (/):"))
        self.lbl_efi.setText(self.tr("EFI (/boot/efi):"))
        self.lbl_home.setText(self.tr("Home (/home):"))
        self.lbl_swap.setText(self.tr("Swap:"))

        # Cargar particiones en combos
        self.cargar_particiones()

    def abrir_partition_manager(self):
        import subprocess
        try:
            subprocess.Popen(["partitionmanager"])
        except Exception as e:
            print("No se pudo abrir KDE Partition Manager:", e)
        
    def cargar_particiones(self):
        from utils.system_utils import SystemDetector

        partitions = SystemDetector.get_flat_partitions()

        combos = {
            self.raiz_combo: self.tr("Seleccionar..."),
            self.efi_combo: self.tr("Seleccionar..."),
            self.home_combo: self.tr("Sin Home"),
            self.swap_combo: self.tr("Sin Swap"),
        }

        for combo, placeholder in combos.items():
            combo.blockSignals(True)
            combo.clear()
            combo.addItem(placeholder, None)

            for part in partitions:
                combo.addItem(part, part)

                combo.setFixedWidth(200)

            combo.blockSignals(False)

    def obtener_seleccion(self):
        return {
            "root": self.raiz_combo.currentData(),
            "efi": self.efi_combo.currentData(),
            "home": self.home_combo.currentData(),
            "swap": self.swap_combo.currentData()
        }

    def cargar_discos(self):
        self.disk_combo.clear()
        from utils.system_utils import SystemDetector

        for disk in SystemDetector.detect_disks():
            label = f"{disk['model']} ({disk['size']})"
            self.disk_combo.addItem(label, disk['name'])

    def autoparticionado(self):
        import os

        disk = self.disk_combo.currentData()
        if not disk:
            return

        # Mensaje de advertencia
        reply = QMessageBox.warning(
            self,
            self.tr("Advertencia: Particionado automático"),
            self.tr(
                "El disco {disk} se formateará y perderá todos sus datos.\n"
                "Esta acción NO se puede deshacer.\n\n"
                "¿Deseas continuar?"
            ).format(disk = disk),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            import subprocess
            try:
                self.part_script = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),  # carpeta ui/
                    "..",  # subimos a la raíz
                    "install",
                    "auto_partition.sh"
                )
                self.part_script = os.path.abspath(self.part_script) 
                subprocess.run(["pkexec", "bash", self.part_script, disk], check=True)
                QMessageBox.information(
                    self,
                    self.tr("Particionado completado"),
                    self.tr("El disco {disk} ha sido particionado correctamente.").format(disk = disk)
                )

                self.cargar_particiones()
                
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(
                    self,
                    self.tr("Error"),
                    self.tr("Fallo al particionar {disk}:\n{e}").format(disk = disk, e = e)
                )
