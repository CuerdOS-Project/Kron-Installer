from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QProgressBar, QMessageBox, QPushButton, QFrame, QSizePolicy,
    QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QTimer
from install.install_thread import InstallWorker


class _SlideWidget(QFrame):
    """Un slide individual: titulo + parrafo, centrado."""

    def __init__(self, title, body, parent=None):
        super().__init__(parent)
        self.setObjectName("slideWidget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.addStretch()

        lbl_title = QLabel(title)
        lbl_title.setObjectName("slideTitle")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setWordWrap(True)
        layout.addWidget(lbl_title)

        layout.addSpacing(12)

        lbl_body = QLabel(body)
        lbl_body.setObjectName("slideBody")
        lbl_body.setAlignment(Qt.AlignCenter)
        lbl_body.setWordWrap(True)
        layout.addWidget(lbl_body)

        layout.addStretch()


class InstallationPage(QWidget):
    finished_success = Signal()
    finished_error = Signal(str)

    # Datos de slides: (titulo, cuerpo). Editar a gusto.
    SLIDES_DATA = [
        (
            "Bienvenido a CuerdOS",
            "CuerdOS es una distribucion GNU/Linux basada en Void Linux, "
            "pensada para ofrecer una experiencia limpia, rapida y personalizable. "
            "Gracias por elegirla."
        ),
        (
            "Gestor de paquetes XBPS",
            "CuerdOS utiliza XBPS, un gestor de paquetes extremadamente rapido "
            "que resuelve dependencias de forma transaccional y eficiente. "
            "Instala software con: xbps-install <paquete>"
        ),
        (
            "Runlevel por defecto: runit",
            "A diferencia de systemd, CuerdOS usa runit como sistema de init. "
            "Es simple, ligero y facil de entender. "
            "Los servicios se gestionan en /etc/sv/"
        ),
        (
            "Personaliza tu escritorio",
            "Tras la instalacion puedes instalar el entorno de escritorio "
            "que prefieras: KDE Plasma, GNOME, XFCE, i3, y muchos mas. "
            "Solo ejecuta: xbps-install <entorno>"
        ),
        (
            "Mantente actualizado",
            "Para mantener tu sistema al dia solo necesitas dos comandos: "
            "xbps-install -Su para actualizar paquetes y "
            "xpkg-upgrade para una actualizacion completa del sistema."
        ),
        (
            "Comunidad y recursos",
            "Unete a la comunidad de CuerdOS para obtener ayuda, "
            "reportar errores y compartir tu experiencia. "
            "Encuentranos en nuestros canales oficiales."
        ),
    ]

    def __init__(self):
        super().__init__()
        self.install_finished = False
        self._current_slide = 0
        self._slide_count = len(self.SLIDES_DATA)
        self._showing_log = False
        self.setup_ui()
        self.translate_ui()

    # ------------------------------------------------------------------ #
    #  UI
    # ------------------------------------------------------------------ #
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 12)
        main_layout.setSpacing(0)

        # Titulo de pagina
        self.titl = QLabel()
        self.titl.setObjectName("title")
        main_layout.addWidget(self.titl)
        main_layout.addSpacing(12)

        # ---- Zona superior: estado + progreso ----
        top_card = QFrame()
        top_card.setObjectName("formCard")
        top_layout = QVBoxLayout(top_card)
        top_layout.setContentsMargins(24, 16, 24, 16)
        top_layout.setSpacing(12)

        self.texto_label = QLabel()
        self.texto_label.setObjectName("statusLabel")
        self.texto_label.setAlignment(Qt.AlignCenter)
        self.texto_label.setWordWrap(True)
        top_layout.addWidget(self.texto_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_layout.addWidget(self.progress)

        main_layout.addWidget(top_card)
        main_layout.addSpacing(10)

        # ---- Zona central: contenedor compartido (slides / terminal) ----
        container_card = QFrame()
        container_card.setObjectName("formCard")
        container_layout = QVBoxLayout(container_card)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Stack con dos paginas: 0 = slides, 1 = terminal
        self._content_stack = QStackedWidget()

        # --- Pagina 0: Carrusel de slides ---
        slides_page = QWidget()
        slides_page.setObjectName("slidesPage")
        sp_layout = QVBoxLayout(slides_page)
        sp_layout.setContentsMargins(0, 0, 0, 0)
        sp_layout.setSpacing(0)

        self.slide_stack = QStackedWidget()
        for title, body in self.SLIDES_DATA:
            self.slide_stack.addWidget(_SlideWidget(title, body))
        sp_layout.addWidget(self.slide_stack, 1)

        # Barra de navegacion de slides
        nav_bar = QWidget()
        nav_bar.setObjectName("slideNavBar")
        nav_bar.setFixedHeight(40)
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(16, 0, 16, 0)

        self.btn_slide_prev = QPushButton("<")
        self.btn_slide_prev.setObjectName("slideNavButton")
        self.btn_slide_prev.setFixedSize(28, 28)
        self.btn_slide_prev.clicked.connect(self._prev_slide)
        nav_layout.addWidget(self.btn_slide_prev)

        nav_layout.addStretch()

        self.dots_layout = QHBoxLayout()
        self.dots_layout.setSpacing(8)
        self.dots_layout.setAlignment(Qt.AlignCenter)
        self.dot_labels = []
        for i in range(self._slide_count):
            dot = QLabel("\u25CF")  # ●
            dot.setObjectName("slideDot")
            dot.setFixedSize(12, 12)
            dot.setAlignment(Qt.AlignCenter)
            self.dot_labels.append(dot)
            self.dots_layout.addWidget(dot)
        nav_layout.addLayout(self.dots_layout)

        nav_layout.addStretch()

        self.btn_slide_next = QPushButton(">")
        self.btn_slide_next.setObjectName("slideNavButton")
        self.btn_slide_next.setFixedSize(28, 28)
        self.btn_slide_next.clicked.connect(self._next_slide)
        nav_layout.addWidget(self.btn_slide_next)

        sp_layout.addWidget(nav_bar)
        self._content_stack.addWidget(slides_page)

        # --- Pagina 1: Terminal ---
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setObjectName("installTerminal")
        self._content_stack.addWidget(self.terminal)

        container_layout.addWidget(self._content_stack)
        main_layout.addWidget(container_card, 1)
        main_layout.addSpacing(10)

        # ---- Boton toggle log ----
        self.btn_toggle_log = QPushButton()
        self.btn_toggle_log.setObjectName("actionButton")
        self.btn_toggle_log.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_toggle_log.clicked.connect(self._toggle_log)

        log_row = QHBoxLayout()
        log_row.addStretch()
        log_row.addWidget(self.btn_toggle_log)
        log_row.addStretch()
        main_layout.addLayout(log_row)

        # Timer para auto-rotar slides
        self._slide_timer = QTimer(self)
        self._slide_timer.setInterval(8000)
        self._slide_timer.timeout.connect(self._next_slide)
        self._slide_timer.start()

        # Estado inicial de dots
        self._update_dots()

    # ------------------------------------------------------------------ #
    #  Slides
    # ------------------------------------------------------------------ #
    def _next_slide(self):
        self._current_slide = (self._current_slide + 1) % self._slide_count
        self.slide_stack.setCurrentIndex(self._current_slide)
        self._update_dots()
        self._slide_timer.start()

    def _prev_slide(self):
        self._current_slide = (self._current_slide - 1) % self._slide_count
        self.slide_stack.setCurrentIndex(self._current_slide)
        self._update_dots()
        self._slide_timer.start()

    def _update_dots(self):
        for i, dot in enumerate(self.dot_labels):
            if i == self._current_slide:
                dot.setStyleSheet(
                    "color: #6fa67a; font-size: 14px; background: transparent;"
                )
            else:
                dot.setStyleSheet(
                    "color: #3a4a42; font-size: 10px; background: transparent;"
                )

    # ------------------------------------------------------------------ #
    #  Toggle log (slides <-> terminal en el mismo espacio)
    # ------------------------------------------------------------------ #
    def _toggle_log(self):
        if self._showing_log:
            # Volver a slides
            self._content_stack.setCurrentIndex(0)
            self._slide_timer.start()
            self._showing_log = False
            self.btn_toggle_log.setText(self.tr("Mostrar log"))
        else:
            # Mostrar terminal
            self._content_stack.setCurrentIndex(1)
            self._slide_timer.stop()
            self._showing_log = True
            self.btn_toggle_log.setText(self.tr("Ocultar log"))

    # ------------------------------------------------------------------ #
    #  Instalacion
    # ------------------------------------------------------------------ #
    def iniciar_instalacion(self, config_data):
        self.texto_label.setText(self.tr("Iniciando motor de instalacion (Root)..."))
        self.progress.setValue(0)

        self.worker = InstallWorker(config_data)

        self.worker.status_update.connect(self.on_status_update)
        self.worker.progress_update.connect(self.progress.setValue)
        self.worker.log_update.connect(self.terminal.appendPlainText)
        self.worker.finished_success.connect(self.on_success)
        self.worker.finished_error.connect(self.on_error)

        self.worker.start()

    def on_status_update(self, token: str):
        texto = self.UI_STATUS_TEXTS.get(token)
        if texto:
            self.texto_label.setText(texto)
        else:
            self.texto_label.setText(self.tr("Realizando tareas del sistema..."))

    def translate_ui(self):
        self.titl.setText(self.tr("Instalacion"))
        self.texto_label.setText(self.tr("Preparando instalacion..."))

        self.UI_STATUS_TEXTS = {
            "INIT": self.tr("Iniciando motor de instalacion..."),
            "CREATE_FS": self.tr("Creando sistemas de archivos..."),
            "COPY": self.tr("Copiando el sistema base..."),
            "REGIONAL_CONFIG": self.tr("Configurando idioma y zona horaria..."),
            "UPDATE": self.tr("Actualizando el sistema..."),
            "MIRROR": self.tr("Configurando servidor de repositorios..."),
            "NON-FREE": self.tr("Configurando repositorios de software propietario."),
            "NVIDIA": self.tr("Instalando controladores NVIDIA..."),
            "INTEL": self.tr("Instalando microcodigos de Intel..."),
            "USER_CONFIG": self.tr("Creando usuarios y contrasenas..."),
            "GRUB_INSTALL": self.tr("Instalando el cargador de arranque..."),
            "DONE": self.tr("Instalacion completada correctamente"),
        }

        self.btn_toggle_log.setText(self.tr("Mostrar log"))

    def on_success(self):
        self._slide_timer.stop()
        self.install_finished = True
        self.texto_label.setText(self.tr("Instalacion Completada!"))
        self.progress.setValue(100)
        QMessageBox.information(
            self, self.tr("Exito"),
            self.tr("CuerdOS se ha instalado correctamente.\n"
                   "Puede reiniciar su equipo.")
        )
        self.finished_success.emit()

    def on_error(self, msg):
        self._slide_timer.stop()
        self.texto_label.setObjectName("errorStatusLabel")
        self.texto_label.setStyle(self.texto_label.style())
        self.texto_label.setText(self.tr("Error en la instalacion"))
        QMessageBox.critical(self, self.tr("Error Fatal"), msg)