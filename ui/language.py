from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QFormLayout, QComboBox,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from utils.utils_locales import LanguageName, KeymapName


class LanguagePage(QWidget):
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

        # Card contenedora
        card = QFrame()
        card.setObjectName("formCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)

        self.form_layout = QFormLayout()
        self.form_layout.setVerticalSpacing(14)
        self.form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.form_layout.setFormAlignment(Qt.AlignLeft)

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
                self.idioma_combo.addItem(display, l)

            for k in sys_data["keymaps"]:
                display = f"{KeymapName(k)} ({k})"
                self.teclado_combo.addItem(display, k)

        # Tamanos flexibles
        for combo in (self.region_combo, self.ciudad_combo,
                       self.idioma_combo, self.teclado_combo):
            combo.setMinimumWidth(200)
            combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.form_layout.addRow(self.lbl_timezone, self.region_combo)
        self.form_layout.addRow(self.lbl_city, self.ciudad_combo)
        self.form_layout.addRow(self.lbl_language, self.idioma_combo)
        self.form_layout.addRow(self.lbl_keyboard, self.teclado_combo)

        card_layout.addLayout(self.form_layout)

        main_layout.addWidget(card, 1)

    def translate_ui(self):
        self.titl.setText(self.tr("Configuracion regional"))

        self.lbl_timezone.setText(self.tr("Zona horaria:"))
        self.lbl_city.setText(self.tr("Ciudad:"))
        self.lbl_language.setText(self.tr("Idioma:"))
        self.lbl_keyboard.setText(self.tr("Teclado:"))

    def actualizar_ciudades(self, region):
        self.ciudad_combo.clear()
        if hasattr(self, "timezones") and region in self.timezones:
            self.ciudad_combo.addItems(self.timezones[region])