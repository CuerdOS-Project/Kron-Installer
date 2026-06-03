from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from utils.utils_locales import LanguageName, KeymapName

class LanguagePage(QWidget):
    def __init__(self, sys_data):
        super().__init__()
        self.setup_ui(sys_data)
        self.translate_ui()

    def setup_ui(self, sys_data):
        # --- Layouts ---
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        h_layout = QHBoxLayout()

        # --- Izquierda ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addStretch()
        imagen = QLabel()
        pixmap = QPixmap("images/idiomas.png")
        imagen.setPixmap(
            pixmap.scaled(150, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        imagen.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(imagen)
        left_layout.addStretch()

        # --- Derecha ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.titl = QLabel("Configuración regional")
        self.titl.setObjectName("title")
        right_layout.addStretch()
        right_layout.addWidget(self.titl)
        right_layout.setSpacing(20)
    
        self.form_layout = QFormLayout()
        
        # Combos regionales
        self.region_combo = QComboBox()
        self.ciudad_combo = QComboBox()
        self.idioma_combo = QComboBox()
        self.teclado_combo = QComboBox()

        self.lbl_timezone = QLabel()
        self.lbl_city = QLabel()
        self.lbl_language = QLabel()
        self.lbl_keyboard = QLabel()

        if sys_data:
            self.timezones = sys_data["timezones"]
            self.region_combo.addItems(sorted(self.timezones.keys()))
            
            self.region_combo.currentTextChanged.connect(self.actualizar_ciudades)
            self.actualizar_ciudades(self.region_combo.currentText())

            for l in sys_data["locales"]:
                display = f"{LanguageName(l[:2])} ({l})"
                self.idioma_combo.addItem(display, l) # 'l' es el código real

            for k in sys_data["keymaps"]:
                display = f"{KeymapName(k)} ({k})"
                self.teclado_combo.addItem(display, k) # 'k' es el código real
        
        # Anchos
        self.region_combo.setFixedWidth(200)
        self.ciudad_combo.setFixedWidth(200)
        self.idioma_combo.setFixedWidth(200)
        self.teclado_combo.setFixedWidth(200)

        self.form_layout.addRow(self.lbl_timezone, self.region_combo)
        self.form_layout.addRow(self.lbl_city, self.ciudad_combo)
        self.form_layout.addRow(self.lbl_language, self.idioma_combo)
        self.form_layout.addRow(self.lbl_keyboard, self.teclado_combo)

        self.form_layout.setLabelAlignment(Qt.AlignLeft)
        self.form_layout.setFormAlignment(Qt.AlignLeft)
        self.form_layout.setVerticalSpacing(10)

        right_layout.addLayout(self.form_layout)
        right_layout.addStretch()

        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        main_layout.addLayout(h_layout)

    def translate_ui(self):
        self.titl.setText(self.tr("Configuración regional"))

        self.lbl_timezone.setText(self.tr("Zona horaria:"))
        self.lbl_city.setText(self.tr("Ciudad:"))
        self.lbl_language.setText(self.tr("Idioma:"))
        self.lbl_keyboard.setText(self.tr("Teclado:"))

    def actualizar_ciudades(self, region):
        self.ciudad_combo.clear()
        if hasattr(self, 'timezones') and region in self.timezones:
            self.ciudad_combo.addItems(self.timezones[region])
