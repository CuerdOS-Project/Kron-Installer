from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPlainTextEdit, QProgressBar, QMessageBox, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
from install.install_thread import InstallWorker

class InstallationPage(QWidget):
    # Declaración de señales
    finished_success = Signal()
    finished_error   = Signal(str)

    def __init__(self):
        super().__init__()
        self.install_finished = False
        self.setup_ui()
        self.translate_ui()

    def setup_ui(self):
        # --- Layout principal ---
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # --- Imagen de instalación ---
        self.img_label = QLabel()
        pixmap = QPixmap("images/instalar.png")
        self.img_label.setPixmap(
            pixmap.scaled(600, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.img_label.setAlignment(Qt.AlignCenter)

        # --- Texto de estado ---
        self.texto_label = QLabel()
        self.texto_label.setObjectName("statusLabel")
        self.texto_label.setAlignment(Qt.AlignCenter)
        self.texto_label.setWordWrap(True)

        # --- Barra de progreso ---
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)

        # --- Pseudo-terminal ---
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFixedHeight(150)
        self.terminal.hide()

        # --- Botón mostrar/ocultar log ---
        self.btn_toggle_log = QPushButton()
        self.btn_toggle_log.setObjectName("actionButton")
        self.btn_toggle_log.setFixedWidth(200)
        self.btn_toggle_log.clicked.connect(self.toggle_terminal_log)

        # --- Añadir widgets al layout ---
        main_layout.addStretch()
        main_layout.addWidget(self.img_label)
        main_layout.addWidget(self.texto_label)
        main_layout.addWidget(self.progress)
        main_layout.addWidget(self.terminal)
        main_layout.addWidget(self.btn_toggle_log, alignment=Qt.AlignCenter) 
        main_layout.addStretch()

    def toggle_terminal_log(self):
        if self.terminal.isVisible():
            self.terminal.hide()
            self.btn_toggle_log.setText(self.tr("Mostrar log"))
            self.log_visible = False
        else:
            self.terminal.show()
            self.btn_toggle_log.setText(self.tr("Ocultar log"))
            self.log_visible = True

    def iniciar_instalacion(self, config_data):
        self.texto_label.setText(self.tr("Iniciando motor de instalación (Root)..."))
        self.progress.setValue(0)
        
        # Crear Worker
        self.worker = InstallWorker(config_data)
        
        # Conectar señales del Thread a la GUI
        self.worker.status_update.connect(self.on_status_update)
        self.worker.progress_update.connect(self.progress.setValue)
        self.worker.log_update.connect(self.terminal.appendPlainText)
        self.worker.finished_success.connect(self.on_success)
        self.worker.finished_error.connect(self.on_error)
        
        # Iniciar
        self.worker.start()

    def on_status_update(self, token: str):
        texto = self.UI_STATUS_TEXTS.get(token)
    
        if texto:
            self.texto_label.setText(texto)
        else:
            self.texto_label.setText(self.tr("Realizando tareas del sistema…"))

    def translate_ui(self):
        self.texto_label.setText(self.tr("Preparando instalación..."))

        self.UI_STATUS_TEXTS = {
            "INIT": self.tr("Iniciando motor de instalación…"),
            "CREATE_FS": self.tr("Creando sistemas de archivos…"),
            "COPY": self.tr("Copiando el sistema base…"),
            "REGIONAL_CONFIG": self.tr("Configurando idioma y zona horaria…"),
            "UPDATE": self.tr("Actualizando el sistema…"),
            "MIRROR": self.tr("Configurando servidor de repositorios…"),
            "NON-FREE": self.tr("Configurando repositorios de software propietario."),
            "NVIDIA": self.tr("Instalando controladores NVIDIA…"),
            "INTEL": self.tr("Instalando microcódigo de Intel…"),
            "USER_CONFIG": self.tr("Creando usuarios y contraseñas…"),
            "GRUB_INSTALL": self.tr("Instalando el cargador de arranque…"),
            "DONE": self.tr("Instalación completada correctamente")
        }

        self.btn_toggle_log.setText(self.tr("Mostrar log"))

    def on_success(self):
        self.install_finished = True
        self.texto_label.setText(self.tr("¡Instalación Completada!"))
        self.progress.setValue(100)
        QMessageBox.information(self, self.tr("Éxito"), self.tr("CuerdOS se ha instalado correctamente.\nPuede reiniciar su equipo."))
        self.finished_success.emit()

    def on_error(self, msg):
        self.texto_label.setObjectName("errorStatusLabel")
        self.texto_label.setStyle(self.texto_label.style())
        self.texto_label.setText(self.tr("Error en la instalación"))
        QMessageBox.critical(self, self.tr("Error Fatal"), msg)
