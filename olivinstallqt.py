#Autor: PabloGA
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QStackedWidget, QComboBox, QCheckBox, QLineEdit, QSizePolicy, QPlainTextEdit, QProgressBar
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
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
        self.pag_usuarios = PagUsuarios()
        self.pag_discos = PagDiscos()
        self.pag_instalacion = PagInstalacion()

        # Añadir páginas a stack
        self.stack.addWidget(self.pag_bienvenida)
        self.stack.addWidget(self.pag_idiomas)
        self.stack.addWidget(self.pag_mirrors)
        self.stack.addWidget(self.pag_usuarios)
        self.stack.addWidget(self.pag_discos)
        self.stack.addWidget(self.pag_instalacion)

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

        # Primera página: ocultar botón atrás
        self.btn_atras.setVisible(index != 0)

        # Última página: botón Siguiente = Finalizar
        if index == self.stack.count() - 1:
            self.btn_siguiente.setText("Finalizar")
            self.btn_siguiente.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        # Página de discos: botón Siguiente = Instalar (rojo)
        elif isinstance(self.stack.currentWidget(), PagDiscos):
            self.btn_siguiente.setText("Instalar")
            self.btn_siguiente.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        else:
            self.btn_siguiente.setText("Siguiente")
            self.btn_siguiente.setStyleSheet("")  # resetea estilo para otras páginas

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
                200, 200,
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

        sbtitl = QLabel('"Raíz que sostiene, ramas que responden"')
        sbtitl.setWordWrap(True)
        sbtitl.setAlignment(Qt.AlignCenter)
        sbtitl.setStyleSheet("font-size: 16px; font-weight: 500")

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
        right_layout.setSpacing(15)
        right_layout.setAlignment(Qt.AlignTop)  # Bloque derecho pegado arriba

        # Título
        titl = QLabel("Configuración regional")
        titl.setWordWrap(True)
        titl.setAlignment(Qt.AlignLeft)
        titl.setStyleSheet("font-size: 24px; font-weight: 500; padding-bottom: 10px;")
        right_layout.addWidget(titl)

        # Formulario
        form_layout = QFormLayout()
        self.region_combo = QComboBox()
        self.region_combo.addItems(["España", "Francia", "Alemania"])
        self.idioma_combo = QComboBox()
        self.idioma_combo.addItems(["Español", "Inglés", "Francés"])
        self.teclado_combo = QComboBox()
        self.teclado_combo.addItems(["Español", "Inglés", "Francés"])

        # Anchos fijos
        self.region_combo.setFixedWidth(200)
        self.idioma_combo.setFixedWidth(200)
        self.teclado_combo.setFixedWidth(200)

        form_layout.addRow("Zona Horaria:", self.region_combo)
        form_layout.addRow("Idioma del Sistema:", self.idioma_combo)
        form_layout.addRow("Distribución de Teclado", self.teclado_combo)

        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setVerticalSpacing(10)

        right_layout.addLayout(form_layout)
        right_layout.addStretch()  # empuja contenido hacia arriba

        # --- Añadir widgets izquierdo/derecho al layout horizontal ---
        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        h_layout.setStretch(0, 1)  # izquierda 50%
        h_layout.setStretch(1, 1)  # derecha 50% (puedes cambiar 1:1 a 2:3 si quieres más espacio para formulario)

        # --- Añadir layout horizontal al layout principal ---
        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

# Página configuración
class PagMirrors(QWidget):
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
        pixmap = QPixmap("repos.png")  # Cambié la imagen para mirrors
        imagen.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        left_layout.addWidget(imagen, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # --- Lado derecho: formulario y checkboxes ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        right_layout.setAlignment(Qt.AlignTop)  # Bloque derecho pegado arriba

        # Título
        titl = QLabel("Repositorios y software")
        titl.setWordWrap(True)
        titl.setAlignment(Qt.AlignLeft)
        titl.setStyleSheet("font-size: 24px; font-weight: 500; padding-bottom: 10px;")
        right_layout.addWidget(titl)

        # Mirror
        mirror_label = QLabel("Servidor de descarga (mirror)")
        self.mirror_combo = QComboBox()
        self.mirror_combo.addItems(["España", "Francia", "Alemania"])
        self.mirror_combo.setFixedWidth(200)

        right_layout.addWidget(mirror_label)
        right_layout.addWidget(self.mirror_combo)

        # Espaciado
        right_layout.addSpacing(15)

        # Software no libre
        self.chk_nonfree = QCheckBox("Activar repositorios no libres")
        self.chk_codecs = QCheckBox("Instalar codecs propietarios")
        self.chk_nvidia = QCheckBox("Instalar drivers NVIDIA")

        # Inicialmente deshabilitados
        self.chk_codecs.setEnabled(False)
        self.chk_nvidia.setEnabled(False)

        # Conectar toggle
        self.chk_nonfree.toggled.connect(self.actualizar_nonfree)

        right_layout.addWidget(self.chk_nonfree, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.chk_codecs, alignment=Qt.AlignLeft)
        right_layout.addWidget(self.chk_nvidia, alignment=Qt.AlignLeft)

        right_layout.addStretch()  # empuja contenido hacia arriba

        # --- Añadir widgets izquierdo/derecho al layout horizontal ---
        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        h_layout.setStretch(0, 1)  # izquierda = 50%
        h_layout.setStretch(1, 1)  # derecha = 50%

        # --- Añadir layout horizontal al layout principal ---
        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

    def actualizar_nonfree(self, activo):
        self.chk_codecs.setEnabled(activo)
        self.chk_nvidia.setEnabled(activo)

        if not activo:
            self.chk_codecs.setChecked(False)
            self.chk_nvidia.setChecked(False)

class PagUsuarios(QWidget):
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
        pixmap = QPixmap("userpc.png")  # Imagen representativa
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
        titl = QLabel("Nombre de equipo y usuarios")
        titl.setWordWrap(True)
        titl.setAlignment(Qt.AlignLeft)
        titl.setStyleSheet("font-size: 24px; font-weight: 500; padding-bottom: 10px;")
        titl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        titl.adjustSize()
        right_layout.addWidget(titl)

        # --- Nombre de equipo ---
        nombre_label = QLabel("Nombre del equipo (hostname):")
        self.nombre_equipo = QLineEdit()
        self.nombre_equipo.setFixedWidth(250)

        right_layout.addWidget(nombre_label)
        right_layout.addWidget(self.nombre_equipo)

        right_layout.addSpacing(15)

        # --- Usuario principal ---
        user_label = QLabel("Usuario (login):")
        self.user_name = QLineEdit()
        self.user_name.setFixedWidth(250)

        username_label = QLabel("Nombre completo:")
        self.username_name = QLineEdit()
        self.username_name.setFixedWidth(250)

        pass_label = QLabel("Contraseña del usuario:")
        self.user_pass = QLineEdit()
        self.user_pass.setEchoMode(QLineEdit.Password)
        self.user_pass.setFixedWidth(250)

        right_layout.addWidget(user_label)
        right_layout.addWidget(self.user_name)
        right_layout.addWidget(username_label)
        right_layout.addWidget(self.username_name)
        right_layout.addWidget(pass_label)
        right_layout.addWidget(self.user_pass)

        right_layout.addSpacing(15)

        # --- Root ---
        root_label = QLabel("Contraseña de root:")
        self.root_pass = QLineEdit()
        self.root_pass.setEchoMode(QLineEdit.Password)
        self.root_pass.setFixedWidth(250)

        right_layout.addWidget(root_label)
        right_layout.addWidget(self.root_pass)

        right_layout.addStretch()  # empuja todo hacia arriba

        # --- Añadir widgets izquierdo/derecho al layout horizontal ---
        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        h_layout.setStretch(0, 1)  # izquierda = 50%
        h_layout.setStretch(1, 1)  # derecha = 50%

        # --- Añadir layout horizontal al layout principal ---
        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

class PagDiscos(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        # --- Layout horizontal ---
        h_layout = QHBoxLayout()

        # --- Izquierda: imagen ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addStretch()
        imagen = QLabel()
        pixmap = QPixmap("disco.png")
        imagen.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        left_layout.addWidget(imagen, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # --- Derecha: formulario ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # Título
        titl = QLabel("Discos y particiones")
        titl.setStyleSheet("font-size: 24px; font-weight: 500; padding: 10px;")
        right_layout.addWidget(titl)

        # Botón abrir KDE Partition Manager
        self.btn_partman = QPushButton("Abrir KDE Partition Manager")
        self.btn_partman.setFixedWidth(250)
        self.btn_partman.clicked.connect(self.abrir_partition_manager)
        right_layout.addWidget(self.btn_partman)
        right_layout.setSpacing(30)

        # Formulario de particiones
        form_layout = QFormLayout()
        self.raiz_combo = QComboBox()
        self.efi_combo = QComboBox()
        self.home_combo = QComboBox()
        self.swap_combo = QComboBox()
        self.grub_combo = QComboBox()

        # Aquí podrías rellenar los combos con particiones reales usando lsblk o parted
        for c in [self.raiz_combo, self.efi_combo, self.home_combo, self.swap_combo, self.grub_combo]:
            c.addItem("Seleccionar...")  # placeholder
            c.setFixedWidth(200)

        form_layout.addRow("Raíz (/):", self.raiz_combo)
        form_layout.addRow("EFI (/boot/efi):", self.efi_combo)
        form_layout.addRow("Home (/home):", self.home_combo)
        form_layout.addRow("Swap:", self.swap_combo)
        form_layout.addRow("Grub Legacy:", self.grub_combo)

        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setVerticalSpacing(10)

        right_layout.addLayout(form_layout)
        right_layout.addStretch()

        # --- Layout horizontal ---
        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        h_layout.setStretch(0, 1)
        h_layout.setStretch(1, 1)

        main_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

    def abrir_partition_manager(self):
        import subprocess
        try:
            subprocess.Popen(["partitionmanager"])
        except Exception as e:
            print("No se pudo abrir KDE Partition Manager:", e)

class PagInstalacion(QWidget):
    def __init__(self):
        super().__init__()

        # --- Layout principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # --- Imagen de instalación ---
        self.img_label = QLabel()
        pixmap = QPixmap("instalar.png")  # Cambia por tu imagen
        self.img_label.setPixmap(
            pixmap.scaled(400, 174, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.img_label.setAlignment(Qt.AlignCenter)

        # --- Texto de estado ---
        self.texto_label = QLabel("Preparando instalación...")
        self.texto_label.setAlignment(Qt.AlignCenter)
        self.texto_label.setWordWrap(True)
        self.texto_label.setStyleSheet("font-size: 18px;")

        # --- Barra de progreso ---
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)

        # --- Pseudo-terminal ---
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet(
            "background-color: black; color: lime; font-family: monospace; font-size: 12px;"
        )
        self.terminal.setFixedHeight(150)

        # --- Añadir widgets al layout ---
        main_layout.addStretch()
        main_layout.addWidget(self.img_label)
        main_layout.addWidget(self.texto_label)
        main_layout.addWidget(self.progress)
        main_layout.addWidget(self.terminal)
        main_layout.addStretch()

        # --- Simulación de instalación ---
        self.pasos = [
            ("Montando sistemas de archivos...", "Montando / y /boot/efi"),
            ("Instalando paquetes base...", "Extrayendo paquetes..."),
            ("Configurando red y usuario...", "Creando usuario y password"),
            ("Instalando GRUB...", "Configurando cargador de arranque"),
            ("Finalizando instalación...", "Limpiando temporal...")
        ]
        self.paso_actual = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.simular_paso)
        self.timer.start(1500)  # cada 1.5s

    def simular_paso(self):
        if self.paso_actual >= len(self.pasos):
            self.texto_label.setText("¡Instalación completada!")
            self.terminal.appendPlainText(">>> Sistema instalado con éxito.\n")
            self.progress.setValue(100)
            self.timer.stop()
            return

        titulo, detalle = self.pasos[self.paso_actual]
        self.texto_label.setText(titulo)
        self.terminal.appendPlainText(f"$ {detalle}")
        porcentaje = int((self.paso_actual + 1) / len(self.pasos) * 100)
        self.progress.setValue(porcentaje)
        self.paso_actual += 1
        
# Mostrar ventana
if __name__ == "__main__":
    app = QApplication(sys.argv)
    vent = VentInstalador()
    vent.show()
    sys.exit(app.exec())