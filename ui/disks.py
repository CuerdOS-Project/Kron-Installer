import os
import subprocess

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFormLayout, QComboBox, QMessageBox, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt

from utils.system_utils import SystemDetector


class DisksPage(QWidget):
    def __init__(self, sys_data):
        super().__init__()
        self.sys_data = sys_data
        self.setup_ui(sys_data)
        self.translate_ui()

    def setup_ui(self, sys_data):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 12)
        main_layout.setSpacing(0)

        # Titulo de pagina
        self.titl = QLabel()
        self.titl.setObjectName("title")
        main_layout.addWidget(self.titl)
        main_layout.addSpacing(14)

        # Layout horizontal: dos columnas
        cols = QHBoxLayout()
        cols.setSpacing(16)

        # ===== COLUMNA IZQUIERDA: Particionado + tabla =====
        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        # --- Card: Particionado (auto + manual fusionados) ---
        part_card = QFrame()
        part_card.setObjectName("formCard")
        pc_layout = QVBoxLayout(part_card)
        pc_layout.setContentsMargins(20, 16, 20, 16)
        pc_layout.setSpacing(10)

        self.auto_label = QLabel()
        self.auto_label.setObjectName("subtitle")

        auto_row = QHBoxLayout()
        auto_row.setSpacing(8)

        self.disk_combo = QComboBox()
        self.disk_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_autopart = QPushButton()
        self.btn_autopart.setObjectName("warnButton")
        self.btn_autopart.setFixedWidth(110)

        auto_row.addWidget(self.disk_combo)
        auto_row.addWidget(self.btn_autopart)

        pc_layout.addWidget(self.auto_label)
        pc_layout.addLayout(auto_row)

        self.btn_autopart.clicked.connect(self.autoparticionado)
        self.cargar_discos()

        # Separador visual sutil
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #3a4a42; border: none; border-top: 1px solid #3a4a42;")
        sep.setFixedHeight(1)
        pc_layout.addSpacing(4)
        pc_layout.addWidget(sep)
        pc_layout.addSpacing(6)

        self.part_label = QLabel()
        self.part_label.setObjectName("subtitle")
        pc_layout.addWidget(self.part_label)

        self.btn_partman = QPushButton()
        self.btn_partman.setObjectName("actionButton")
        self.btn_partman.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pc_layout.addWidget(self.btn_partman)
        self.btn_partman.clicked.connect(self.abrir_partition_manager)

        left_col.addWidget(part_card)

        # --- Card: Tabla resumen ---
        table_card = QFrame()
        table_card.setObjectName("formCard")
        table_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        tc_layout = QVBoxLayout(table_card)
        tc_layout.setContentsMargins(20, 14, 20, 14)
        tc_layout.setSpacing(8)

        self.table_title = QLabel()
        self.table_title.setObjectName("subtitle")
        tc_layout.addWidget(self.table_title)

        self.part_table = QTableWidget()
        self.part_table.setColumnCount(3)
        self.part_table.setHorizontalHeaderLabels(
            ["Mount", "Particion", "FS"]
        )
        self.part_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.part_table.verticalHeader().setVisible(False)
        self.part_table.setAlternatingRowColors(True)
        self.part_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.part_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.part_table.setFixedHeight(140)
        self.part_table.showGrid = False

        tc_layout.addWidget(self.part_table)

        left_col.addWidget(table_card)
        left_col.addStretch()

        cols.addLayout(left_col, 1)

        # ===== COLUMNA DERECHA: Asignacion de particiones =====
        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        assign_card = QFrame()
        assign_card.setObjectName("formCard")
        ac_layout = QVBoxLayout(assign_card)
        ac_layout.setContentsMargins(20, 16, 20, 16)
        ac_layout.setSpacing(12)

        self.assign_label = QLabel()
        self.assign_label.setObjectName("subtitle")
        ac_layout.addWidget(self.assign_label)

        # Sistema de archivos
        fs_row = QHBoxLayout()
        fs_row.setSpacing(10)

        self.fs_label = QLabel()
        self.filesys_combo = QComboBox()
        self.filesys_combo.addItems(["BTRFS", "Ext4", "Ext3", "Ext2", "XFS"])
        self.filesys_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        fs_row.addWidget(self.fs_label)
        fs_row.addWidget(self.filesys_combo)
        ac_layout.addLayout(fs_row)

        ac_layout.addSpacing(6)

        # Formulario de particiones
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft)

        self.raiz_combo = QComboBox()
        self.efi_combo = QComboBox()
        self.home_combo = QComboBox()
        self.swap_combo = QComboBox()

        self.lbl_root = QLabel()
        self.lbl_efi = QLabel()
        self.lbl_home = QLabel()
        self.lbl_swap = QLabel()

        for combo in (self.raiz_combo, self.efi_combo,
                       self.home_combo, self.swap_combo):
            combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        form_layout.addRow(self.lbl_root, self.raiz_combo)
        form_layout.addRow(self.lbl_efi, self.efi_combo)
        form_layout.addRow(self.lbl_home, self.home_combo)
        form_layout.addRow(self.lbl_swap, self.swap_combo)

        self._is_efi_system = sys_data.get("efi", False)

        if not self._is_efi_system:
            self.efi_combo.setVisible(False)
            self.lbl_efi.setVisible(False)

        ac_layout.addLayout(form_layout)
        ac_layout.addStretch()

        right_col.addWidget(assign_card, 1)

        cols.addLayout(right_col, 1)

        main_layout.addLayout(cols, 1)

        # Conectar cambios para actualizar tabla
        for combo in (self.raiz_combo, self.efi_combo,
                       self.home_combo, self.swap_combo):
            combo.currentIndexChanged.connect(self._update_table)

    def _update_table(self):
        """Actualiza la tabla resumen con las particiones seleccionadas."""
        rows_data = []
        filesys = self.filesys_combo.currentText().upper()

        if self.raiz_combo.currentData():
            rows_data.append(("/", self.raiz_combo.currentText(), filesys))

        if self.efi_combo.currentData() and self._is_efi_system:
            rows_data.append(("/boot/efi", self.efi_combo.currentText(), "VFAT"))

        if self.home_combo.currentData():
            rows_data.append(("/home", self.home_combo.currentText(), filesys))

        if self.swap_combo.currentData():
            rows_data.append(("swap", self.swap_combo.currentText(), "SWAP"))

        self.part_table.setRowCount(len(rows_data))
        for i, (mount, part, fs) in enumerate(rows_data):
            self.part_table.setItem(i, 0, QTableWidgetItem(mount))
            self.part_table.setItem(i, 1, QTableWidgetItem(part))
            self.part_table.setItem(i, 2, QTableWidgetItem(fs))

    def translate_ui(self):
        self.titl.setText(self.tr("Discos y particiones"))
        self.auto_label.setText(self.tr("Disco a particionar (automatico):"))
        self.btn_autopart.setText(self.tr("Particionar"))
        self.part_label.setText(self.tr("O particionar manualmente:"))
        self.btn_partman.setText(self.tr("Abrir KDE Partition Manager"))
        self.fs_label.setText(self.tr("Sistema de archivos:"))
        self.assign_label.setText(self.tr("Asignar particiones"))
        self.table_title.setText(self.tr("Resumen"))

        self.lbl_root.setText(self.tr("Raiz (/):"))
        self.lbl_efi.setText(self.tr("EFI (/boot/efi):"))
        self.lbl_home.setText(self.tr("Home (/home):"))
        self.lbl_swap.setText(self.tr("Swap:"))

        self.part_table.setHorizontalHeaderLabels(
            [self.tr("Pto. de montaje"), self.tr("Particion"), self.tr("Sistema")]
        )

        self.cargar_particiones()

    def abrir_partition_manager(self):
        try:
            subprocess.run(["partitionmanager"])
            # Tras cerrar el partition manager, recargar particiones
            self.cargar_particiones()
        except FileNotFoundError:
            print("partitionmanager no esta instalado.")
        except Exception as e:
            print("No se pudo abrir KDE Partition Manager:", e)

    def cargar_particiones(self):
        partitions = SystemDetector.get_partitions_detailed()
        if not partitions:
            self._update_table()
            return

        # --- Poblar todos los combos (data = nombre, texto = display) ---
        placeholders = {
            self.raiz_combo: self.tr("Seleccionar..."),
            self.efi_combo: self.tr("Seleccionar..."),
            self.home_combo: self.tr("Sin Home"),
            self.swap_combo: self.tr("Sin Swap"),
        }

        for combo, ph in placeholders.items():
            combo.blockSignals(True)
            combo.clear()
            combo.addItem(ph, None)
            for p in partitions:
                combo.addItem(p["display"], p["name"])

        # --- Auto-seleccion ---
        self._auto_select(partitions)

        # Desbloquear señales y actualizar tabla (una sola vez)
        for combo in placeholders:
            combo.blockSignals(False)

        self._update_table()

    def _auto_select(self, partitions):
        """Marca la particion mas probable en cada combo.

        Estrategia conservadora:
          EFI  → particion vfat mas pequena
          Swap → particion con fstype swap
          Root → particion mas grande (no EFI, no swap)
          Home → segunda particion mas grande (si hay >=2)
        """
        is_efi = self.sys_data.get("efi", False)

        efi_parts = [p for p in partitions if "vfat" in p["fstype"] or "fat" in p["fstype"]]
        swap_parts = [p for p in partitions if "swap" in p["fstype"]]
        efi_names = {p["name"] for p in efi_parts}
        swap_names = {p["name"] for p in swap_parts}
        other_parts = [p for p in partitions if p["name"] not in efi_names | swap_names]
        other_sorted = sorted(other_parts, key=lambda p: p["size_bytes"], reverse=True)

        def _set(combo, part):
            idx = combo.findData(part["name"])
            if idx >= 0:
                combo.setCurrentIndex(idx)

        # EFI: vfat mas pequena
        if is_efi and efi_parts:
            _set(self.efi_combo, min(efi_parts, key=lambda p: p["size_bytes"]))

        # Swap
        if swap_parts:
            _set(self.swap_combo, swap_parts[0])

        # Root: particion mas grande
        if other_sorted:
            _set(self.raiz_combo, other_sorted[0])

        # Home: segunda mas grande (si la hay)
        if len(other_sorted) >= 2:
            _set(self.home_combo, other_sorted[1])

    def obtener_seleccion(self):
        """Devuelve {root, efi, home, swap} con el nombre de dispositivo (/dev/sdaN)."""
        return {
            "root": self.raiz_combo.currentData(),
            "efi": self.efi_combo.currentData(),
            "home": self.home_combo.currentData(),
            "swap": self.swap_combo.currentData()
        }

    def cargar_discos(self):
        self.disk_combo.clear()

        for disk in SystemDetector.detect_disks():
            label = f"{disk['model']} ({disk['size']})"
            self.disk_combo.addItem(label, disk['name'])

    def autoparticionado(self):
        disk = self.disk_combo.currentData()
        if not disk:
            return

        reply = QMessageBox.warning(
            self,
            self.tr("Advertencia: Particionado automatico"),
            self.tr(
                "El disco {disk} se formateara y perdera todos sus datos.\n"
                "Esta accion NO se puede deshacer.\n\n"
                "Deseas continuar?"
            ).format(disk=disk),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.part_script = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "install",
                    "auto_partition.sh"
                )
                self.part_script = os.path.abspath(self.part_script)
                subprocess.run(
                    ["pkexec", "bash", self.part_script, disk], check=True
                )
                QMessageBox.information(
                    self,
                    self.tr("Particionado completado"),
                    self.tr(
                        "El disco {disk} ha sido particionado correctamente."
                    ).format(disk=disk)
                )
                self.cargar_particiones()

            except subprocess.CalledProcessError as e:
                QMessageBox.critical(
                    self,
                    self.tr("Error"),
                    self.tr(
                        "Fallo al particionar {disk}:\n{e}"
                    ).format(disk=disk, e=e)
                )