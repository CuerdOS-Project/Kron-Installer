from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
import os


class WelcomePage(QWidget):
    languageChanged = Signal(str)

    def __init__(self, sys_data, images_dir=None):
        super().__init__()
        self._images_dir = images_dir
        self.setup_ui(sys_data)
        self.translate_ui()

    def setup_ui(self, sys_data):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 12)
        main_layout.setSpacing(16)

        # --- Selector idioma (esquina superior derecha) ---
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        language_icon = QLabel()
        i18n_path = os.path.join(self._images_dir, "i18n.png") if self._images_dir else "images/i18n.png"
        icon = QPixmap(i18n_path)
        if not icon.isNull():
            language_icon.setPixmap(
                icon.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        self.lang_combo = QComboBox()
        self.lang_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lang_combo.setMinimumWidth(120)

        self.lang_combo.addItem("Espanol", "es_ES")
        self.lang_combo.addItem("English", "en_US")
        self.lang_combo.addItem("Galego", "gl_ES")
        self.lang_combo.addItem("Português", "pt_BR")
        self.lang_combo.addItem("Català", "ca_ES")
        self.lang_combo.addItem("Deutsch", "de_DE")
        self.lang_combo.addItem("Français", "fr_FR")
        self.lang_combo.addItem("日本語", "ja_JP")
        self.lang_combo.addItem("한국어", "ko_KR")
        self.lang_combo.addItem("Italiano", "it_IT")
        self.lang_combo.addItem("Türkçe", "tr_TR")
        self.lang_combo.addItem("Pусский", "ru_RU")

        self.lang_combo.setCurrentIndex(1)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)

        top_bar.addWidget(language_icon)
        top_bar.addWidget(self.lang_combo)

        main_layout.addLayout(top_bar)

        # --- Contenido centrado ---
        center = QVBoxLayout()
        center.addStretch()

        # Logo grande centrado
        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        identity_path = os.path.join(self._images_dir, "identity.png") if self._images_dir else "images/identity.png"
        pixmap = QPixmap(identity_path)
        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(220, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        center.addWidget(logo, alignment=Qt.AlignCenter)

        center.addSpacing(18)

        # Titulo
        self.titl = QLabel()
        self.titl.setObjectName("welcomeTitle")
        self.titl.setAlignment(Qt.AlignCenter)
        center.addWidget(self.titl, alignment=Qt.AlignCenter)

        center.addSpacing(2)

        # Subtitulo
        self.sbtitl = QLabel()
        self.sbtitl.setObjectName("welcomeSubtitle")
        self.sbtitl.setAlignment(Qt.AlignCenter)
        center.addWidget(self.sbtitl, alignment=Qt.AlignCenter)

        center.addSpacing(18)

        # Tarjeta de estado de red
        self.has_net = sys_data["net"]
        self.net_card = QWidget()
        self.net_card.setFixedWidth(380)

        if self.has_net:
            self.net_card.setObjectName("netCardOnline")
        else:
            self.net_card.setObjectName("netCardOffline")

        net_layout = QVBoxLayout(self.net_card)
        net_layout.setContentsMargins(20, 14, 20, 14)
        net_layout.setAlignment(Qt.AlignCenter)

        self.net_label = QLabel()
        self.net_label.setObjectName("netCardLabel")
        self.net_label.setWordWrap(True)
        self.net_label.setAlignment(Qt.AlignCenter)

        net_layout.addWidget(self.net_label)
        center.addWidget(self.net_card, alignment=Qt.AlignCenter)

        center.addStretch()
        main_layout.addLayout(center, 1)

    def translate_ui(self):
        self.titl.setText(self.tr("Bienvenido a CuerdOS!"))
        self.sbtitl.setText(self.tr("“Optimizado hasta el último píxel”"))

        if self.has_net:
            self.net_label.setText(
                self.tr(
                    "Se ha detectado conexion a internet.\n"
                    "Instalador en modo online."
                )
            )
        else:
            self.net_label.setText(
                self.tr(
                    "No se ha detectado conexion a internet.\n"
                    "Instalador en modo offline."
                )
            )

    def on_language_changed(self):
        lang = self.lang_combo.currentData()
        self.languageChanged.emit(lang)