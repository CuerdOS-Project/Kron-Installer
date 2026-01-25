#Autor: PabloGA
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QStackedWidget, QComboBox, QCheckBox, QLineEdit, QSizePolicy, QPlainTextEdit, QProgressBar, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from system_utils import SystemDetector
from install_thread import InstallWorker
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
        
        # --- DETECCIÓN DE HARDWARE AL INICIO ---
        self.system_data = {
            "efi": SystemDetector.detect_efi(),
            "timezones": SystemDetector.detect_timezones(),
            "locales": SystemDetector.detect_locales(),
            "keymaps": SystemDetector.detect_keymaps(),
            "partitions": SystemDetector.get_flat_partitions()
        }

        # Crear páginas (Pasamos datos a las que lo necesitan)
        self.pag_bienvenida = PagBienvenida()
        self.pag_idiomas = PagIdiomas(self.system_data) # <--- CAMBIO AQUÍ
        self.pag_mirrors = PagMirrors()
        self.pag_usuarios = PagUsuarios()
        self.pag_discos = PagDiscos(self.system_data)   # <--- CAMBIO AQUÍ
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

        # Estado inicial
        self.actualizar_botones()
    
    def ir_siguiente(self):
            index = self.stack.currentIndex()
            curr_widget = self.stack.currentWidget()

            # Si estamos en la página de Discos, el siguiente paso es INSTALAR
            if isinstance(curr_widget, PagDiscos):
                # Recopilar datos de todas las páginas
                config = self.recolectar_datos()
                
                if config: # Si la validación pasó
                    # Pasar a la pantalla de instalación
                    self.stack.setCurrentIndex(index + 1)
                    self.actualizar_botones()
                    # Iniciar el proceso real
                    self.pag_instalacion.iniciar_instalacion(config)
                return

            # Comportamiento normal para otras páginas
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
        total = self.stack.count()

        # Primera página: ocultar botón atrás
        self.btn_atras.setVisible(index != 0)

        # Última página: ocultar botón "Siguiente"
        if index == total - 1:
            self.btn_siguiente.hide()
        else:
            self.btn_siguiente.show()

        # Página de discos: botón Siguiente = Instalar (rojo)
        if isinstance(self.stack.currentWidget(), PagDiscos):
            self.btn_siguiente.setText("Instalar")
            self.btn_siguiente.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        else:
            self.btn_siguiente.setText("Siguiente")
            self.btn_siguiente.setStyleSheet("")  # resetea estilo para otras páginas

    def recolectar_datos(self):
            data = {}
            try:
                # 1. Idiomas
                data["LOCALE"] = self.pag_idiomas.idioma_combo.currentText().split(" ")[0] # Simplificación
                # Lógica para zona horaria (Region/Ciudad)
                tz_region = self.pag_idiomas.region_combo.currentText()
                tz_city = self.pag_idiomas.ciudad_combo.currentText()
                data["TIMEZONE"] = f"{tz_region}/{tz_city}"
                data["KEYMAP"] = self.pag_idiomas.teclado_combo.currentText()

                # 2. Source (Simplificado: Local si no se tocó nada en mirrors)
                data["SOURCE"] = "local"

                # 3. Usuarios
                data["HOSTNAME"] = self.pag_usuarios.nombre_equipo.text() or "void-pc"
                data["USERLOGIN"] = self.pag_usuarios.user_name.text()
                data["USERNAME"] = self.pag_usuarios.username_name.text()
                data["USERPASSWORD"] = self.pag_usuarios.user_pass.text()
                data["ROOTPASSWORD"] = self.pag_usuarios.root_pass.text()
                data["USERGROUPS"] = "wheel,audio,video,users,network,optical,cdrom"

                if not data["ROOTPASSWORD"]:
                    QMessageBox.warning(self, "Faltan datos", "La contraseña de Root es obligatoria.")
                    return None

                # 4. Repo y software
                data["MIRROR"] = self.pag_mirrors.mirror_combo.currentText()
                data["NONFREE"] = "1" if self.pag_mirrors.chk_nonfree.isChecked() else "0"
                data["NVIDIA"] = "1" if self.pag_mirrors.chk_nvidia.isChecked() else "0"
                data["INTEL"] = "1" if self.pag_mirrors.chk_intel.isChecked() else "0"

                # 5. Discos (Mapeo de tu GUI al Backend)
                raw_parts = self.pag_discos.obtener_seleccion()
                partitions = []

                # Función para limpiar texto "/dev/sda1 (50G)" -> "/dev/sda1"
                def clean(txt): return txt.split(" ")[0]

                if "Seleccionar" in raw_parts["root"]:
                    QMessageBox.warning(self, "Error", "Debe seleccionar una partición Raíz (/).")
                    return None
                
                # RAÍZ (Siempre formatear)
                partitions.append({"dev": clean(raw_parts["root"]), "point": "/", "fs": "ext4", "format": "1"})

                # EFI (Si aplica)
                if self.system_data["efi"]:
                    if "Seleccionar" in raw_parts["efi"]:
                        QMessageBox.warning(self, "Error", "Sistema EFI: Seleccione partición EFI.")
                        return None
                    partitions.append({"dev": clean(raw_parts["efi"]), "point": "/boot/efi", "fs": "vfat", "format": "1"})
                
                # SWAP
                if "Seleccionar" not in raw_parts["swap"]:
                    partitions.append({"dev": clean(raw_parts["swap"]), "point": "none", "fs": "swap", "format": "1"})

                # HOME (No formatear para preservar datos)
                if "Seleccionar" not in raw_parts["home"]:
                    partitions.append({"dev": clean(raw_parts["home"]), "point": "/home", "fs": "ext4", "format": "0"})

                data["PARTITIONS"] = partitions

                # BOOTLOADER (Instalar en el disco de la raíz)
                import re
                root_dev = clean(raw_parts["root"]) # ej: /dev/sda1
                # Quitar números finales para obtener el disco (/dev/sda)
                disk_dev = re.sub(r'\d+$', '', root_dev)
                if "nvme" in disk_dev and disk_dev.endswith("p"): disk_dev = disk_dev[:-1]
                
                data["BOOTLOADER"] = disk_dev

                return data
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error procesando datos: {e}")
                return None

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
    def __init__(self, sys_data=None):
        super().__init__()

        # --- Layouts ---
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        h_layout = QHBoxLayout()

        # --- Izquierda ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addStretch()
        imagen = QLabel()
        pixmap = QPixmap("idiomas.png")
        imagen.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        imagen.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(imagen)
        left_layout.addStretch()

        # --- Derecha ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignTop)

        titl = QLabel("Configuración regional")
        titl.setStyleSheet("font-size: 24px; font-weight: 500; padding-bottom: 10px;")
        right_layout.addStretch()
        right_layout.addWidget(titl)
    
        form_layout = QFormLayout()
        
        # Inicializamos los combos vacíos primero para evitar errores
        self.region_combo = QComboBox()
        self.ciudad_combo = QComboBox() # <--- IMPORTANTE: Inicializarlo siempre
        self.idioma_combo = QComboBox()
        self.teclado_combo = QComboBox()

        if sys_data:
            # Datos reales
            self.timezones = sys_data["timezones"]
            self.region_combo.addItems(sorted(self.timezones.keys()))
            
            # Conectar cambio de región
            self.region_combo.currentTextChanged.connect(self.actualizar_ciudades)
            # Llenar ciudades iniciales
            self.actualizar_ciudades(self.region_combo.currentText())

            self.idioma_combo.addItems(sys_data["locales"])
            self.teclado_combo.addItems(sys_data["keymaps"])
        else:
            # Fallback
            self.region_combo.addItems(["UTC"])
            self.ciudad_combo.addItems(["UTC"])
            self.idioma_combo.addItems(["en_US.UTF-8"])
            self.teclado_combo.addItems(["us"])

        # Estilos y Anchos
        self.region_combo.setFixedWidth(200)
        self.ciudad_combo.setFixedWidth(200) # <--- CORREGIDO (antes self.ciudad)
        self.idioma_combo.setFixedWidth(200)
        self.teclado_combo.setFixedWidth(200)

        form_layout.addRow("Zona Horaria:", self.region_combo)
        form_layout.addRow("Ciudad:", self.ciudad_combo)
        form_layout.addRow("Idioma:", self.idioma_combo)
        form_layout.addRow("Teclado:", self.teclado_combo)

        right_layout.addLayout(form_layout)
        right_layout.addStretch()

        h_layout.addWidget(left_widget)
        h_layout.addWidget(right_widget)
        main_layout.addLayout(h_layout)

    def actualizar_ciudades(self, region):
        self.ciudad_combo.clear()
        if hasattr(self, 'timezones') and region in self.timezones:
            self.ciudad_combo.addItems(self.timezones[region])

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
        pixmap = QPixmap("repos.png")
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
        titl = QLabel("Repositorios y software")
        titl.setWordWrap(True)
        titl.setAlignment(Qt.AlignLeft)
        titl.setStyleSheet("font-size: 24px; font-weight: 500; padding-bottom: 10px;")
        right_layout.addWidget(titl)

        # Mirror
        mirror_label = QLabel("Servidor de descarga (mirror)")
        self.mirror_combo = QComboBox()
        self.mirror_combo.addItems(["Predeterminado", "Europa, Finlandia", "Europa, Alemania", "Global, CDN", "Norte América, EEUU"])
        self.mirror_combo.setFixedWidth(200)

        right_layout.addWidget(mirror_label)
        right_layout.addWidget(self.mirror_combo)

        # Espaciado
        right_layout.addSpacing(15)

        # Software no libre
        self.chk_nonfree = QCheckBox("Activar repositorios no libres")
        self.chk_nvidia = QCheckBox("Instalar drivers NVIDIA")
        self.chk_nvidia.setToolTip(
            "Instala los drivers propietarios de NVIDIA, optimizando el rendimiento gráfico y la compatibilidad con juegos y aplicaciones 3D."
        )
        self.chk_intel = QCheckBox("Instalar microcódigos Intel")
        self.chk_intel.setToolTip(
            "Instala microcódigos recientes de Intel para mejorar seguridad, estabilidad y compatibilidad con CPUs Intel modernas."
        )

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

    def actualizar_nonfree(self, activo):
        self.chk_nvidia.setEnabled(activo)
        self.chk_intel.setEnabled(activo)

        if not activo:
            self.chk_nvidia.setChecked(False)
            self.chk_intel.setChecked(False)

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
        pixmap = QPixmap("userpc.png")
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

class PagDiscos(QWidget):
    def __init__(self, sys_data=None):
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

        # Datos reales
        lista_particiones = ["Seleccionar..."]
        if sys_data:
            lista_particiones += sys_data["partitions"]

        for c in [self.raiz_combo, self.efi_combo, self.home_combo, self.swap_combo, self.grub_combo]:
            c.clear()
            c.addItems(lista_particiones)
            c.setFixedWidth(200)
        
        # Ocultar EFI si es BIOS Legacy
        if sys_data and not sys_data["efi"]:
            self.efi_combo.setVisible(False)
            # Buscar el label asociado en el form layout para ocultarlo sería ideal,
            # pero por simplicidad dejaremos el combo oculto.

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

    def obtener_seleccion(self):
        return {
            "root": self.raiz_combo.currentText(),
            "efi": self.efi_combo.currentText(),
            "home": self.home_combo.currentText(),
            "swap": self.swap_combo.currentText()
        }

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
        pixmap = QPixmap("instalar.png")
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

    def iniciar_instalacion(self, config_data):
        self.texto_label.setText("Iniciando motor de instalación (Root)...")
        self.progress.setValue(0)
        
        # Crear Worker
        self.worker = InstallWorker(config_data)
        
        # Conectar señales del Thread a la GUI
        self.worker.status_update.connect(self.texto_label.setText)
        self.worker.progress_update.connect(self.progress.setValue)
        self.worker.log_update.connect(self.terminal.appendPlainText)
        self.worker.finished_success.connect(self.on_success)
        self.worker.finished_error.connect(self.on_error)
        
        # Iniciar
        self.worker.start()

    def on_success(self):
        self.texto_label.setText("¡Instalación Completada!")
        self.progress.setValue(100)
        self.terminal.appendPlainText("\n>>> PUEDE REINICIAR SU EQUIPO.")
        QMessageBox.information(self, "Éxito", "OlivOS se ha instalado correctamente.")

    def on_error(self, msg):
        self.texto_label.setText("Error en la instalación")
        self.texto_label.setStyleSheet("color: red; font-size: 18px;")
        QMessageBox.critical(self, "Error Fatal", msg)

# Mostrar ventana
if __name__ == "__main__":
    app = QApplication(sys.argv)
    vent = VentInstalador()
    vent.show()
    sys.exit(app.exec())