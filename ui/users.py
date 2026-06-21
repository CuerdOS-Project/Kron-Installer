import os
import re
import unicodedata

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame,
    QPushButton, QSizePolicy, QFormLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon


# Rutas a los iconos de ojo (crearlos en ui/assets/)
_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_ICON_EYE_OFF = os.path.join(_ASSETS, "eye-off.svg")   # contrasena oculta
_ICON_EYE_ON = os.path.join(_ASSETS, "eye-on.svg")     # contrasena visible


class UsersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.translate_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 12)
        main_layout.setSpacing(0)

        # Titulo de pagina
        self.titl = QLabel()
        self.titl.setObjectName("title")
        main_layout.addWidget(self.titl)
        main_layout.addSpacing(14)

        # ===== Unica card con todo el formulario =====
        card = QFrame()
        card.setObjectName("formCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(4)

        # --- FormLayout unico: label izquierda, input derecha ---
        form = QFormLayout()
        form.setVerticalSpacing(10)
        form.setHorizontalSpacing(16)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignLeft)
        self.nombre_label = QLabel()
        self.nombre_equipo = QLineEdit("cuerdos-pc")

        self.username_label = QLabel()
        self.username_name = QLineEdit("CuerdOS User")

        self.user_label = QLabel()
        self.user_name = QLineEdit()

        form.addRow(self.nombre_label, self.nombre_equipo)
        form.addRow(self.username_label, self.username_name)
        form.addRow(self.user_label, self.user_name)

        card_layout.addLayout(form)

        # --- Separador ---
        sep1 = QFrame()
        sep1.setFixedHeight(1)
        sep1.setStyleSheet(
            "border: none; border-top: 1px solid #3a4a42;"
        )
        card_layout.addSpacing(6)
        card_layout.addWidget(sep1)
        card_layout.addSpacing(10)

        # --- Seccion 2: Contrasena de usuario ---
        self.pass_label = QLabel()
        self.pass_label.setObjectName("subtitle")
        card_layout.addWidget(self.pass_label)
        card_layout.addSpacing(4)

        pass_form = QFormLayout()
        pass_form.setVerticalSpacing(10)
        pass_form.setHorizontalSpacing(16)
        pass_form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        pass_form.setFormAlignment(Qt.AlignLeft)

        self.user_pass_label = QLabel()

        self.user_pass = QLineEdit()
        self.user_pass.setEchoMode(QLineEdit.Password)
        self.user_pass.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_show_user_pass = QPushButton()
        self.btn_show_user_pass.setObjectName("togglePassButton")
        self.btn_show_user_pass.setFixedSize(32, 32)
        self.btn_show_user_pass.setCheckable(True)
        self.btn_show_user_pass.setIconSize(QSize(16, 16))
        self._set_eye_icon(self.btn_show_user_pass, visible=False)
        self.btn_show_user_pass.clicked.connect(self._toggle_user_pass_visibility)

        user_pass_row = QHBoxLayout()
        user_pass_row.setSpacing(8)
        user_pass_row.addWidget(self.user_pass)
        user_pass_row.addWidget(self.btn_show_user_pass)

        self.user_pass_confirm_label = QLabel()
        self.user_pass_confirm = QLineEdit()
        self.user_pass_confirm.setEchoMode(QLineEdit.Password)
        self.user_pass_confirm.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        pass_form.addRow(self.user_pass_label, user_pass_row)
        pass_form.addRow(self.user_pass_confirm_label, self.user_pass_confirm)

        self.user_pass_error = QLabel()
        self.user_pass_error.setObjectName("errorLabel")
        self.user_pass_error.hide()
        pass_form.addRow("", self.user_pass_error)

        card_layout.addLayout(pass_form)

        # --- Separador ---
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(
            "border: none; border-top: 1px solid #3a4a42;"
        )
        card_layout.addSpacing(6)
        card_layout.addWidget(sep2)
        card_layout.addSpacing(10)

        # --- Seccion 3: Contrasena de root ---
        self.root_label = QLabel()
        self.root_label.setObjectName("subtitle")
        card_layout.addWidget(self.root_label)
        card_layout.addSpacing(4)

        root_form = QFormLayout()
        root_form.setVerticalSpacing(10)
        root_form.setHorizontalSpacing(16)
        root_form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        root_form.setFormAlignment(Qt.AlignLeft)

        self.root_pass_label = QLabel()

        self.root_pass = QLineEdit()
        self.root_pass.setEchoMode(QLineEdit.Password)
        self.root_pass.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_show_root_pass = QPushButton()
        self.btn_show_root_pass.setObjectName("togglePassButton")
        self.btn_show_root_pass.setFixedSize(32, 32)
        self.btn_show_root_pass.setCheckable(True)
        self.btn_show_root_pass.setIconSize(QSize(16, 16))
        self._set_eye_icon(self.btn_show_root_pass, visible=False)
        self.btn_show_root_pass.clicked.connect(self._toggle_root_pass_visibility)

        root_pass_row = QHBoxLayout()
        root_pass_row.setSpacing(8)
        root_pass_row.addWidget(self.root_pass)
        root_pass_row.addWidget(self.btn_show_root_pass)

        self.root_pass_confirm_label = QLabel()
        self.root_pass_confirm = QLineEdit()
        self.root_pass_confirm.setEchoMode(QLineEdit.Password)
        self.root_pass_confirm.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        root_form.addRow(self.root_pass_label, root_pass_row)
        root_form.addRow(self.root_pass_confirm_label, self.root_pass_confirm)

        self.root_pass_error = QLabel()
        self.root_pass_error.setObjectName("errorLabel")
        self.root_pass_error.hide()
        root_form.addRow("", self.root_pass_error)

        card_layout.addLayout(root_form)

        main_layout.addWidget(card)
        main_layout.addStretch()

        # Conexiones
        self.username_name.textChanged.connect(self._update_login)
        self._update_login(self.username_name.text())

        self.user_pass.textChanged.connect(self._validate_user_password)
        self.user_pass_confirm.textChanged.connect(self._validate_user_password)
        self.root_pass.textChanged.connect(self._validate_root_password)
        self.root_pass_confirm.textChanged.connect(self._validate_root_password)

    def translate_ui(self):
        self.titl.setText(self.tr("Nombre de equipo y usuarios"))
        self.nombre_label.setText(self.tr("Nombre del equipo:"))
        self.username_label.setText(self.tr("Nombre completo:"))
        self.user_label.setText(self.tr("Usuario (login):"))
        self.pass_label.setText(self.tr("Contrasena del usuario"))
        self.root_label.setText(self.tr("Contrasena de root"))

        self.user_pass_label.setText(self.tr("Contrasena:"))
        self.user_pass_confirm_label.setText(self.tr("Confirmar:"))
        self.root_pass_label.setText(self.tr("Contrasena:"))
        self.root_pass_confirm_label.setText(self.tr("Confirmar:"))

        self.user_pass.setPlaceholderText(self.tr("Contrasena"))
        self.root_pass.setPlaceholderText(self.tr("Contrasena"))
        self.user_pass_confirm.setPlaceholderText(self.tr("Repetir contrasena"))
        self.root_pass_confirm.setPlaceholderText(self.tr("Repetir contrasena"))

        self.user_pass_error.setText(
            self.tr("Las contrasenas de usuario no coinciden")
        )
        self.root_pass_error.setText(
            self.tr("Las contrasenas de root no coinciden")
        )

    def _update_login(self, text):
        normalized = unicodedata.normalize("NFKD", text)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

        login = ascii_text.lower()
        login = re.sub(r"[^a-z0-9]+", "-", login)
        login = login.strip("-")

        self.user_name.setText(login)

    @staticmethod
    def _set_eye_icon(button, visible):
        path = _ICON_EYE_ON if visible else _ICON_EYE_OFF
        if os.path.isfile(path):
            button.setIcon(QIcon(path))

    def _toggle_user_pass_visibility(self, checked):
        self.user_pass.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self._set_eye_icon(self.btn_show_user_pass, visible=checked)

    def _toggle_root_pass_visibility(self, checked):
        self.root_pass.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self._set_eye_icon(self.btn_show_root_pass, visible=checked)

    def _check_match(self, pass1, pass2, error_label, ctx_user):
        """Valida que dos campos de contrasena coincidan.

        Returns True si son validos (coinciden o estan vacios),
        False si hay error y muestra el mensaje en *error_label*.
        """
        if pass1:
            if not pass2:
                error_label.setText(
                    self.tr("Debe repetir la contrasena")
                )
                error_label.show()
                return False
            elif pass1 != pass2:
                error_label.setText(
                    self.tr(f"Las contrasenas de {ctx_user} no coinciden")
                )
                error_label.show()
                return False
        error_label.hide()
        return True

    def _validate_user_password(self):
        return self._check_match(
            self.user_pass.text(),
            self.user_pass_confirm.text(),
            self.user_pass_error,
            "usuario",
        )

    def _validate_root_password(self):
        return self._check_match(
            self.root_pass.text(),
            self.root_pass_confirm.text(),
            self.root_pass_error,
            "root",
        )

    def validate_passwords(self):
        user_valid = self._validate_user_password()
        root_valid = self._validate_root_password()

        if not self.user_pass.text():
            self.user_pass_error.setText(
                self.tr("La contrasena de usuario es obligatoria")
            )
            self.user_pass_error.show()
            user_valid = False

        if not self.root_pass.text():
            self.root_pass_error.setText(
                self.tr("La contrasena de root es obligatoria")
            )
            self.root_pass_error.show()
            root_valid = False

        return user_valid and root_valid

