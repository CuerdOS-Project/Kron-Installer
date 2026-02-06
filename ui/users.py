from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import unicodedata, re

class UsersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.translate_ui()

    def setup_ui(self):
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
        pixmap = QPixmap("images/userpc.png")
        imagen.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        left_layout.addWidget(imagen, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # --- Lado derecho: formulario ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignTop)

        # Título
        self.titl = QLabel()
        self.titl.setWordWrap(True)
        self.titl.setAlignment(Qt.AlignLeft)
        self.titl.setStyleSheet("font-size: 24px; font-weight: 500; padding-bottom: 10px;")
        self.titl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.titl.adjustSize()
        right_layout.addWidget(self.titl)

        # --- Nombre de equipo ---
        self.nombre_label = QLabel()
        self.nombre_equipo = QLineEdit("olivos-pc")
        self.nombre_equipo.setFixedWidth(250)

        right_layout.addWidget(self.nombre_label)
        right_layout.addWidget(self.nombre_equipo)

        right_layout.addSpacing(15)

        # --- Usuario principal ---
        self.username_label = QLabel()
        self.username_name = QLineEdit("OlivOS User")
        self.username_name.setFixedWidth(250)

        self.user_label = QLabel()
        self.user_name = QLineEdit()
        self.user_name.setFixedWidth(250)

        self.pass_label = QLabel()
        self.user_pass = QLineEdit()
        self.user_pass.setEchoMode(QLineEdit.Password)
        self.user_pass.setFixedWidth(250)

        right_layout.addWidget(self.username_label)
        right_layout.addWidget(self.username_name)
        right_layout.addWidget(self.user_label)
        right_layout.addWidget(self.user_name)
        right_layout.addWidget(self.pass_label)
        right_layout.addWidget(self.user_pass)

        right_layout.addSpacing(15)

        # --- Root ---
        self.root_label = QLabel()
        self.root_pass = QLineEdit()
        self.root_pass.setEchoMode(QLineEdit.Password)
        self.root_pass.setFixedWidth(250)

        right_layout.addWidget(self.root_label)
        right_layout.addWidget(self.root_pass)

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

        # Variables actualizar label username
        self.username_name.textChanged.connect(self._update_login)
        self._update_login(self.username_name.text())
    
    def translate_ui(self):
        self.titl.setText(self.tr("Nombre de equipo y usuarios"))
        self.nombre_label.setText(self.tr("Nombre del equipo (hostname):"))
        self.username_label.setText(self.tr("Nombre completo:"))
        self.user_label.setText(self.tr("Usuario (login):"))
        self.pass_label.setText(self.tr("Contraseña del usuario:"))
        self.root_label.setText(self.tr("Contraseña de root:"))

    # Función actualizar label username
    def _update_login(self, text):
        normalized = unicodedata.normalize("NFKD", text)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

        login = ascii_text.lower()
        login = re.sub(r"[^a-z0-9]+", "-", login)
        login = login.strip("-")

        self.user_name.setText(login)