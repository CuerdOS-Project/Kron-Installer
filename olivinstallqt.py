#Autor: PabloGA
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QStackedWidget, QComboBox, QCheckBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import sys

class VentInstalador(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Instalador de OlivOS")
        self.resize(900, 650)

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Widgets "stacked"
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Crear páginas
        self.pag_bienvenida = PagBienvenida()
        self.pag_idiomas = PagIdiomas()
        self.pag_mirrors = PagMirrors()

        # Añadir páginas a stack
        self.stack.addWidget(self.pag_bienvenida)
        self.stack.addWidget(self.pag_idiomas)
        self.stack.addWidget(self.pag_mirrors)

        # Barra inferior de botones
        nav_layout = QHBoxLayout()

        self.btn_atras = QPushButton("Atrás")
        self.btn_siguiente = QPushButton("Siguiente")

        nav_layout.addWidget(self.btn_atras)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_siguiente)

        main_layout.addLayout(nav_layout)

        # Conexiones
        self.btn_atras.clicked.connect(self.ir_atras)
        self.btn_siguiente.clicked.connect(self.ir_siguiente)

        # Estadio inicial
        self.actualizar_botones()
    
    def ir_siguiente(self):
        index = self.stack.currentIndex()
        if index < self.stack.count() - 1:
            self.stack.setCurrentIndex(index + 1)
        self.actualizar_botones()

    def ir_atras(self):
        index = self.stack.currentIndex()
        if index > 0:
            self.stack.setCurrentIndex(index -1)
        self.actualizar_botones()
    
    def actualizar_botones(self):
        index = self.stack.currentIndex()

        # Primera página
        self.btn_atras.setVisible(index != 0)

        # Última página
        if index == self.stack.count() -1:
            self.btn_siguiente.setText("Finalizar")
        else:
            self.btn_siguiente.setText("Siguiente")

# Página principal
class PagBienvenida(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("olivos-logo.png")

        logo.setPixmap(
            pixmap.scaled(
                350, 350,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        
        logo.setAlignment(Qt.AlignCenter)

        # Mensaje bienvenida
        titl = QLabel("¡Bienvenido a OlivOS!")
        titl.setWordWrap(True)
        titl.setAlignment(Qt.AlignCenter)
        titl.setStyleSheet("font-size: 34px; font-weight: 500")

        sbtitl = QLabel("Cultivado con criterio.")
        sbtitl.setWordWrap(True)
        sbtitl.setAlignment(Qt.AlignCenter)
        sbtitl.setStyleSheet("font-size: 19px; font-weight: 500")

        # Añadimos widgets al layout
        layout.addStretch()
        layout.addWidget(logo)
        layout.addWidget(titl)
        layout.addWidget(sbtitl)
        layout.addStretch()

class PagIdiomas(QWidget):
    def __init__(self):
        super().__init__()

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
        pixmap = QPixmap("idiomas.png")
        imagen.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        left_layout.addWidget(imagen, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # --- Lado derecho: formulario ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)

        # Título
        titl = QLabel("Configuración regional")
        titl.setWordWrap(True)
        titl.setAlignment(Qt.AlignLeft)  # alineado arriba-izquierda
        titl.setStyleSheet("font-size: 24px; font-weight: 500; padding: 10px;")
        right_layout.addWidget(titl)

        # Formulario
        form_layout = QFormLayout()
        self.region_combo = QComboBox()
        self.region_combo.addItems(["España", "Francia", "Alemania"])
        self.idioma_combo = QComboBox()
        self.idioma_combo.addItems(["Español", "Inglés", "Francés"])
        self.teclado_combo = QComboBox()
        self.teclado_combo.addItems(["Español", "Inglés", "Francés"])

        self.region_combo.setFixedWidth(200)
        self.idioma_combo.setFixedWidth(200)
        self.teclado_combo.setFixedWidth(200)

        form_layout.addRow("Zona Horaria:", self.region_combo)
        form_layout.addRow("Idioma del Sistema:", self.idioma_combo)
        form_layout.addRow("Distribución de Teclado", self.teclado_combo)
        form_layout.setVerticalSpacing(10)

        right_layout.addLayout(form_layout)
        right_layout.addStretch()  # empuja el contenido hacia arriba

        # --- Añadir widgets izquierdo/derecho al layout horizontal ---
        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        h_layout.setStretch(0, 1)  # izquierda = 50%
        h_layout.setStretch(1, 1)  # derecha = 50%

        # --- Añadir layout horizontal al layout principal ---
        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

# Página configuración
class PagMirrors(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        # Título
        titl = QLabel("Repositorios y software")
        titl.setAlignment(Qt.AlignCenter)
        titl.setStyleSheet("font-size: 24px; font-weight: 500; padding: 10px;")

        # Imagen
        imagen = QLabel()
        pixmap = QPixmap("idiomas.png")
        imagen.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        # --- Contenido derecho ---
        right_layout = QVBoxLayout()

        # Mirror
        mirror_label = QLabel("Servidor de descarga (mirror)")
        self.mirror_combo = QComboBox()
        self.mirror_combo.addItems([
            "España",
            "Francia",
            "Alemania"
        ])

        self.mirror_combo.setFixedWidth(200)

        # Software no libre
        self.chk_nonfree = QCheckBox("Activar repositorios no libres")
        self.chk_codecs = QCheckBox("Instalar codecs propietarios")
        self.chk_nvidia = QCheckBox("Instalar drivers NVIDIA")

        self.chk_codecs.setEnabled(False)
        self.chk_nvidia.setEnabled(False)

        self.chk_nonfree.toggled.connect(self.actualizar_nonfree)

        # Añadir a layout derecho
        right_layout.addWidget(titl)
        right_layout.addWidget(mirror_label, alignment=Qt.AlignCenter)
        right_layout.addWidget(self.mirror_combo, alignment=Qt.AlignCenter)
        right_layout.addSpacing(15)
        right_layout.addWidget(self.chk_nonfree, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.chk_codecs, alignment=Qt.AlignCenter)
        right_layout.addWidget(self.chk_nvidia, alignment=Qt.AlignCenter)
        right_layout.addStretch()

        # --- Layout horizontal ---
        h_layout = QHBoxLayout()
        h_layout.addWidget(imagen, alignment=Qt.AlignHCenter)
        h_layout.addLayout(right_layout)
        h_layout.setStretch(0, 1)
        h_layout.setStretch(1, 3)

        # --- Layout final ---
        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

    def actualizar_nonfree(self, activo):
        self.chk_codecs.setEnabled(activo)
        self.chk_nvidia.setEnabled(activo)

        if not activo:
            self.chk_codecs.setChecked(False)
            self.chk_nvidia.setChecked(False)

# Mostrar ventana
if __name__ == "__main__":
    app = QApplication(sys.argv)
    vent = VentInstalador()
    vent.show()
    sys.exit(app.exec())