from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class MirrorsPage(QWidget):
    def __init__(self, sys_data):
        super().__init__()
        self.setup_ui(sys_data)
        self.translate_ui()

    def setup_ui(self, sys_data):
        # --- Layout vertical principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # --- Layout horizontal: izquierda/derecha ---
        h_layout = QHBoxLayout()

        # --- Lado izquierdo: imagen centrada ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addStretch()
        imagen = QLabel()
        pixmap = QPixmap("images/repos.png")
        imagen.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        left_layout.addWidget(imagen, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # --- Lado derecho: formulario y checkboxes ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        right_layout.setAlignment(Qt.AlignTop)

        # Título
        self.titl = QLabel()
        self.titl.setWordWrap(True)
        self.titl.setAlignment(Qt.AlignLeft)
        self.titl.setStyleSheet("font-size: 24px; font-weight: 500; padding-bottom: 10px;")
        right_layout.addWidget(self.titl)

        # Mirror
        self.mirror_label = QLabel()
        self.mirror_combo = QComboBox()
        self.mirror_combo.setFixedWidth(200)

        right_layout.addWidget(self.mirror_label)
        right_layout.addWidget(self.mirror_combo)

        # Espaciado
        right_layout.addSpacing(15)

        # Software no libre
        self.chk_nonfree = QCheckBox()
        self.chk_nvidia = QCheckBox()
        self.chk_intel = QCheckBox()

        # Inicialmente deshabilitados
        self.chk_nvidia.setEnabled(False)
        self.chk_intel.setEnabled(False)

        # Conectar toggle
        self.chk_nonfree.toggled.connect(self.actualizar_nonfree)

        right_layout.addWidget(self.chk_nonfree, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.chk_nvidia, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.chk_intel, alignment=Qt.AlignLeft)

        right_layout.addStretch()

        # --- Añadir widgets izquierdo/derecho al layout horizontal ---
        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        h_layout.setStretch(0, 1)
        h_layout.setStretch(1, 1)

        # --- Añadir layout horizontal al layout principal ---
        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

    def translate_ui(self):
        self.titl.setText(self.tr("Repositorios y software"))
        self.mirror_label.setText(self.tr("Servidor de descarga (mirror)"))
        
        self.mirror_combo.blockSignals(True)      
        self.mirror_combo.clear()
        self.mirror_combo.addItem(self.tr("Predeterminado"), "Default")
        self.mirror_combo.addItem(self.tr("Europa, Finlandia"), "Finland")
        self.mirror_combo.addItem(self.tr("Europa, Alemania"), "Germany")
        self.mirror_combo.addItem(self.tr("Global, CDN"), "Global")
        self.mirror_combo.addItem(self.tr("Norte América, EEUU"), "USA")

        self.chk_nonfree.setText(self.tr("Activar repositorios no libres"))
        self.chk_nvidia.setText(self.tr("Instalar drivers NVIDIA"))
        self.chk_nvidia.setToolTip(self.tr(
            "Instala los drivers propietarios de NVIDIA, optimizando el rendimiento gráfico y la compatibilidad con juegos y aplicaciones 3D."
        ))
        self.chk_intel.setText(self.tr("Instalar microcódigos Intel"))
        self.chk_intel.setToolTip(
            "Instala microcódigos recientes de Intel para mejorar seguridad, estabilidad y compatibilidad con CPUs Intel modernas."
        )

    def actualizar_nonfree(self, activo):
        self.chk_nvidia.setEnabled(activo)
        self.chk_intel.setEnabled(activo)

        if not activo:
            self.chk_nvidia.setChecked(False)
            self.chk_intel.setChecked(False)