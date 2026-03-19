from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

class WelcomePage(QWidget):
    languageChanged = Signal(str)

    def __init__(self, sys_data):
        super().__init__()
        self.setup_ui(sys_data)
        self.translate_ui()

    def setup_ui(self, sys_data):       
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # Selector idioma
        form_layout = QHBoxLayout()
        self.lang_combo = QComboBox()

        language_icon = QLabel()
        icon = QPixmap("images/i18n.png")

        language_icon.setPixmap(icon.scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Español", "es")
        self.lang_combo.addItem("Asturianu", "ast")
        self.lang_combo.addItem("Català", "ca")
        self.lang_combo.addItem("Galego", "gl")
        self.lang_combo.addItem("Basque", "eu")
        self.lang_combo.addItem("Deutsch", "de")
        self.lang_combo.addItem("Français", "fr")
        self.lang_combo.addItem("Italiano", "it")
        self.lang_combo.addItem("Português", "pt_BR")
        self.lang_combo.setFixedWidth(100)

        # Inglés por defecto
        self.lang_combo.setCurrentIndex(0)

        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)

        form_layout.addWidget(language_icon)
        form_layout.addWidget(self.lang_combo)
        form_layout.setAlignment(Qt.AlignLeft)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("images/olivos-logo.png")

        logo.setPixmap(
            pixmap.scaled(
                200, 200,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        
        logo.setAlignment(Qt.AlignCenter)

        # Mensaje bienvenida
        self.titl = QLabel()
        self.titl.setWordWrap(True)
        self.titl.setAlignment(Qt.AlignCenter)
        self.titl.setStyleSheet("font-size: 34px; font-weight: 500")

        self.sbtitl = QLabel()
        self.sbtitl.setWordWrap(True)
        self.sbtitl.setAlignment(Qt.AlignCenter)
        self.sbtitl.setStyleSheet("font-size: 16px; font-weight: 500")

        # Tarjeta de estado
        self.has_net = sys_data["net"]

        self.net_card = QWidget()
        self.net_card.setFixedWidth(400)

        net_layout = QVBoxLayout(self.net_card)
        net_layout.setContentsMargins(15, 10, 15, 10)
        net_layout.setAlignment(Qt.AlignCenter)

        self.net_label = QLabel()
        self.net_label.setWordWrap(True)
        self.net_label.setAlignment(Qt.AlignCenter)

        net_layout.addWidget(self.net_label)

        if self.has_net:
            bg = "#27ae60"
        else:
            bg = "#e78c3c"

        self.net_card.setStyleSheet(f"""
        QWidget {{
            background-color: {bg};
            border-radius: 8px;
        }}
        QLabel {{
            color: white;
            font-size: 14px;
            font-weight: bold;
        }}
        """)

        # Añadir widgets AL LAYOUT PRINCIPAL
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addWidget(logo)
        main_layout.addWidget(self.titl)
        main_layout.addWidget(self.sbtitl)
        main_layout.addWidget(self.net_card, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    def translate_ui(self):
        self.titl.setText(self.tr("¡Bienvenido a OlivOS!"))
        self.sbtitl.setText(self.tr('"Raíz que sostiene, ramas que responden"'))
        
        if self.has_net:
            self.net_label.setText(
                self.tr("Se ha detectado conexión a internet.\nInstalador en modo online.")
            )
        else:
            self.net_label.setText(
                self.tr("No se ha detectado conexión a internet.\nInstalador en modo offline.")
            )

    def on_language_changed(self):
        lang = self.lang_combo.currentData()
        self.languageChanged.emit(lang)