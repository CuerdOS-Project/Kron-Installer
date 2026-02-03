from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPlainTextEdit, QProgressBar, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
from install.install_thread import InstallWorker

class InstallationPage(QWidget):
    # Declaración de señales
    finished_success = Signal()
    finished_error   = Signal(str)

    def __init__(self):
        super().__init__()
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
            pixmap.scaled(400, 174, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.img_label.setAlignment(Qt.AlignCenter)

        # --- Texto de estado ---
        self.texto_label = QLabel()
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
        self.texto_label.setText(self.tr("Iniciando motor de instalación (Root)..."))
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

    def translate_ui(self):
        self.texto_label.setText(self.tr("Preparando instalación..."))

    def on_success(self):
        self.texto_label.setText(self.tr("¡Instalación Completada!"))
        self.progress.setValue(100)
        self.terminal.appendPlainText(self.tr("\n>>> PUEDE REINICIAR SU EQUIPO."))
        QMessageBox.information(self, self.tr("Éxito"), self.tr("OlivOS se ha instalado correctamente."))
        self.finished_success.emit()

    def on_error(self, msg):
        self.texto_label.setText(self.tr("Error en la instalación"))
        self.texto_label.setStyleSheet("color: red; font-size: 18px;")
        QMessageBox.critical(self, self.tr("Error Fatal"), msg)