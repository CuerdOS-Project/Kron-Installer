from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QSizePolicy, QPushButton
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

        # --- Layout horizontal ---
        h_layout = QHBoxLayout()

        # --- Lado izquierdo: imagen centrada ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addStretch()
        imagen = QLabel()
        pixmap = QPixmap("images/userpc.png")
        imagen.setPixmap(
            pixmap.scaled(150, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        left_layout.addWidget(imagen, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # --- Lado derecho: formulario ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(6)
        right_layout.setAlignment(Qt.AlignTop)

        # Título
        self.titl = QLabel()
        self.titl.setObjectName("title")
        self.titl.setWordWrap(True)
        self.titl.setAlignment(Qt.AlignLeft)
        self.titl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        right_layout.addWidget(self.titl)

        # --- Fila 1: Nombre de equipo ---
        self.nombre_label = QLabel()
        self.nombre_equipo = QLineEdit("cuerdos-pc")
        self.nombre_equipo.setFixedWidth(330)
        right_layout.addWidget(self.nombre_label)
        right_layout.addWidget(self.nombre_equipo)

        # --- Fila 2: Nombre completo ---
        self.username_label = QLabel()
        self.username_name = QLineEdit("CuerdOS User")
        self.username_name.setFixedWidth(330)
        right_layout.addWidget(self.username_label)
        right_layout.addWidget(self.username_name)

        # --- Fila 3: Usuario (login) ---
        self.user_label = QLabel()
        self.user_name = QLineEdit()
        self.user_name.setFixedWidth(330)
        right_layout.addWidget(self.user_label)
        right_layout.addWidget(self.user_name)

        right_layout.addSpacing(10)

        # --- Fila 4: Contraseñas de usuario (lado a lado) ---
        self.pass_label = QLabel()
        right_layout.addWidget(self.pass_label)
        
        user_pass_row = QHBoxLayout()
        user_pass_row.setSpacing(8)
        
        # Contraseña usuario (con botón mostrar/ocultar)
        self.user_pass = QLineEdit()
        self.user_pass.setEchoMode(QLineEdit.Password)
        self.user_pass.setFixedWidth(145)
        
        self.btn_show_user_pass = QPushButton("👁")
        self.btn_show_user_pass.setObjectName("togglePassButton")
        self.btn_show_user_pass.setFixedSize(26, 26)
        self.btn_show_user_pass.setCheckable(True)
        self.btn_show_user_pass.clicked.connect(self._toggle_user_pass_visibility)
        
        # Confirmación usuario (sin botón)
        self.user_pass_confirm = QLineEdit()
        self.user_pass_confirm.setEchoMode(QLineEdit.Password)
        self.user_pass_confirm.setFixedWidth(145)
        
        user_pass_row.addWidget(self.user_pass)
        user_pass_row.addWidget(self.btn_show_user_pass)
        user_pass_row.addWidget(self.user_pass_confirm)
        user_pass_row.addStretch()
        
        right_layout.addLayout(user_pass_row)

        # Label de error usuario
        self.user_pass_error = QLabel()
        self.user_pass_error.setObjectName("errorLabel")
        self.user_pass_error.hide()
        right_layout.addWidget(self.user_pass_error)

        right_layout.addSpacing(10)

        # --- Fila 5: Contraseñas de root ---
        self.root_label = QLabel()
        right_layout.addWidget(self.root_label)
        
        root_pass_row = QHBoxLayout()
        root_pass_row.setSpacing(8)
        
        # Contraseña root
        self.root_pass = QLineEdit()
        self.root_pass.setEchoMode(QLineEdit.Password)
        self.root_pass.setFixedWidth(145)
        self.root_pass.setPlaceholderText("Contraseña")
        
        self.btn_show_root_pass = QPushButton("👁")
        self.btn_show_root_pass.setObjectName("togglePassButton")
        self.btn_show_root_pass.setFixedSize(26, 26)
        self.btn_show_root_pass.setCheckable(True)
        self.btn_show_root_pass.clicked.connect(self._toggle_root_pass_visibility)
        
        # Confirmación root
        self.root_pass_confirm = QLineEdit()
        self.root_pass_confirm.setEchoMode(QLineEdit.Password)
        self.root_pass_confirm.setFixedWidth(145)
        
        root_pass_row.addWidget(self.root_pass)
        root_pass_row.addWidget(self.btn_show_root_pass)
        root_pass_row.addWidget(self.root_pass_confirm)
        root_pass_row.addStretch()
        
        right_layout.addLayout(root_pass_row)

        # Label de error root
        self.root_pass_error = QLabel()
        self.root_pass_error.setObjectName("errorLabel")
        self.root_pass_error.hide()
        right_layout.addWidget(self.root_pass_error)

        right_layout.addStretch()

        # --- Añadir widgets al layout horizontal ---
        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        h_layout.setStretch(0, 1)
        h_layout.setStretch(1, 1)

        # --- Añadir al layout principal ---
        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

        # Conectar señales
        self.username_name.textChanged.connect(self._update_login)
        self._update_login(self.username_name.text())
        
        self.user_pass.textChanged.connect(self._validate_user_password)
        self.user_pass_confirm.textChanged.connect(self._validate_user_password)
        self.root_pass.textChanged.connect(self._validate_root_password)
        self.root_pass_confirm.textChanged.connect(self._validate_root_password)
    
    def translate_ui(self):
        self.titl.setText(self.tr("Nombre de equipo y usuarios"))
        self.nombre_label.setText(self.tr("Nombre del equipo (hostname):"))
        self.username_label.setText(self.tr("Nombre completo:"))
        self.user_label.setText(self.tr("Usuario (login):"))
        self.pass_label.setText(self.tr("Contraseña del usuario:"))
        self.root_label.setText(self.tr("Contraseña de root:"))
        

        self.user_pass.setPlaceholderText(self.tr("Contraseña"))
        self.root_pass.setPlaceholderText(self.tr("Contraseña"))
        self.user_pass_confirm.setPlaceholderText(self.tr("Repetir contraseña"))
        self.root_pass_confirm.setPlaceholderText(self.tr("Repetir contraseña"))
        
        self.user_pass_error.setText(self.tr("⚠ Las contraseñas de usuario no coinciden"))
        self.root_pass_error.setText(self.tr("⚠ Las contraseñas de root no coinciden"))

    def _update_login(self, text):
        normalized = unicodedata.normalize("NFKD", text)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

        login = ascii_text.lower()
        login = re.sub(r"[^a-z0-9]+", "-", login)
        login = login.strip("-")

        self.user_name.setText(login)
    
    def _toggle_user_pass_visibility(self, checked):
        self.user_pass.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.btn_show_user_pass.setText("🔒" if checked else "👁")
    
    def _toggle_root_pass_visibility(self, checked):
        self.root_pass.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.btn_show_root_pass.setText("🔒" if checked else "👁")
    
    def _validate_user_password(self):
        pass1 = self.user_pass.text()
        pass2 = self.user_pass_confirm.text()
        
        self.user_pass_error.setText(self.tr("⚠ Las contraseñas de usuario no coinciden"))
        
        if pass1:
            if not pass2:
                self.user_pass_error.setText(self.tr("⚠ Debe repetir la contraseña"))
                self.user_pass_error.show()
                return False
            elif pass1 != pass2:
                self.user_pass_error.show()
                return False
        
        self.user_pass_error.hide()
        return True
    
    def _validate_root_password(self):
        pass1 = self.root_pass.text()
        pass2 = self.root_pass_confirm.text()
        
        self.root_pass_error.setText(self.tr("⚠ Las contraseñas de root no coinciden"))
        
        if pass1:
            if not pass2:
                self.root_pass_error.setText(self.tr("⚠ Debe repetir la contraseña"))
                self.root_pass_error.show()
                return False
            elif pass1 != pass2:
                self.root_pass_error.show()
                return False
        
        self.root_pass_error.hide()
        return True
    
    def validate_passwords(self):
        user_valid = self._validate_user_password()
        root_valid = self._validate_root_password()
        
        if not self.user_pass.text():
            self.user_pass_error.setText(self.tr("⚠ La contraseña de usuario es obligatoria"))
            self.user_pass_error.show()
            user_valid = False
        elif self.user_pass.text() == self.user_pass_confirm.text():
            self.user_pass_error.setText(self.tr("⚠ Las contraseñas de usuario no coinciden"))
        
        if not self.root_pass.text():
            self.root_pass_error.setText(self.tr("⚠ La contraseña de root es obligatoria"))
            self.root_pass_error.show()
            root_valid = False
        elif self.root_pass.text() == self.root_pass_confirm.text():
            self.root_pass_error.setText(self.tr("⚠ Las contraseñas de root no coinciden"))
        
        return user_valid and root_valid
    
    def get_user_password(self):
        if self._validate_user_password() and self.user_pass.text():
            return self.user_pass.text()
        return None
    
    def get_root_password(self):
        if self._validate_root_password() and self.root_pass.text():
            return self.root_pass.text()
        return None
