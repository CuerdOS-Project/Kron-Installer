from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt


class MirrorsPage(QWidget):
    def __init__(self, sys_data):
        super().__init__()
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
        main_layout.addSpacing(20)

        # --- Card: Mirror ---
        mirror_card = QFrame()
        mirror_card.setObjectName("formCard")
        mirror_card_layout = QVBoxLayout(mirror_card)
        mirror_card_layout.setContentsMargins(24, 20, 24, 20)
        mirror_card_layout.setSpacing(12)

        self.mirror_label = QLabel()
        self.mirror_label.setObjectName("subtitle")
        self.mirror_combo = QComboBox()
        self.mirror_combo.setMinimumWidth(200)
        self.mirror_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        mirror_card_layout.addWidget(self.mirror_label)
        mirror_card_layout.addWidget(self.mirror_combo)

        main_layout.addWidget(mirror_card)

        main_layout.addSpacing(12)

        # --- Card: Software adicional ---
        software_card = QFrame()
        software_card.setObjectName("formCard")
        software_card_layout = QVBoxLayout(software_card)
        software_card_layout.setContentsMargins(24, 20, 24, 20)
        software_card_layout.setSpacing(12)

        self.software_title = QLabel()
        self.software_title.setObjectName("subtitle")
        software_card_layout.addWidget(self.software_title)

        self.chk_nonfree = QCheckBox()
        self.chk_nvidia = QCheckBox()
        self.chk_intel = QCheckBox()

        self.chk_nvidia.setEnabled(False)
        self.chk_intel.setEnabled(False)

        self.chk_nonfree.toggled.connect(self.actualizar_nonfree)

        software_card_layout.addWidget(self.chk_nonfree)
        software_card_layout.addSpacing(4)
        software_card_layout.addWidget(self.chk_nvidia)
        software_card_layout.addSpacing(4)
        software_card_layout.addWidget(self.chk_intel)
        software_card_layout.addStretch()

        main_layout.addWidget(software_card, 1)

    def translate_ui(self):
        self.titl.setText(self.tr("Repositorios y software"))
        self.mirror_label.setText(self.tr("Servidor de descarga (mirror)"))
        self.software_title.setText(self.tr("Software adicional"))

        self.mirror_combo.blockSignals(True)
        self.mirror_combo.clear()
        self.mirror_combo.addItem(self.tr("Predeterminado"), "Default")
        self.mirror_combo.addItem(self.tr("Europa, Finlandia"), "Finland")
        self.mirror_combo.addItem(self.tr("Europa, Alemania"), "Germany")
        self.mirror_combo.addItem(self.tr("Global, CDN"), "Global")
        self.mirror_combo.addItem(self.tr("Norteamérica, EE. UU."), "USA")

        self.chk_nonfree.setText(self.tr("Activar repositorios no libres"))
        self.chk_nvidia.setText(self.tr("Instalar drivers NVIDIA"))
        self.chk_nvidia.setToolTip(self.tr(
            "Instala los drivers propietarios de NVIDIA, optimizando el rendimiento "
            "gráfico y la compatibilidad con juegos y aplicaciones 3D."
        ))
        self.chk_intel.setText(self.tr("Instalar microcódigos Intel"))
        self.chk_intel.setToolTip(self.tr(
            "Instala microcódigos recientes de Intel para mejorar seguridad, "
            "estabilidad y compatibilidad con CPUs Intel modernas."
        ))

    def actualizar_nonfree(self, activo):
        self.chk_nvidia.setEnabled(activo)
        self.chk_intel.setEnabled(activo)

        if not activo:
            self.chk_nvidia.setChecked(False)
            self.chk_intel.setChecked(False)