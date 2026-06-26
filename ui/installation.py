from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QProgressBar, QMessageBox, QPushButton, QFrame, QSizePolicy,
    QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap
import os
from install.install_thread import InstallWorker

_ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
_SLIDES_DIR = os.path.join(_ASSETS_DIR, "assets", "slides")


class _SlideWidget(QFrame):
    """Un slide individual: imagen a un lado, titulo y parrafo al otro,
    todo centrado como un unico bloque dentro del slide. La imagen se
    reescala segun el espacio disponible para que nunca quede recortada."""

    IMAGE_SIZE = 512

    def __init__(self, title, body, image=None, parent=None):
        super().__init__(parent)
        self.setObjectName("slideWidget")

        outer = QHBoxLayout(self)
        outer.setContentsMargins(32, 16, 32, 16)
        outer.setSpacing(0)
        outer.addStretch(1)

        content = QHBoxLayout()
        content.setSpacing(32)

        self._orig_pixmap = None
        self._lbl_image = None

        if image:
            image_path = os.path.join(_SLIDES_DIR, image)
            if os.path.isfile(image_path):
                pm = QPixmap(image_path)
                if not pm.isNull():
                    self._orig_pixmap = pm
                    lbl_image = QLabel()
                    lbl_image.setObjectName("slideImage")
                    lbl_image.setAlignment(Qt.AlignCenter)
                    lbl_image.setScaledContents(False)
                    lbl_image.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
                    self._lbl_image = lbl_image
                    content.addWidget(lbl_image, 0, Qt.AlignCenter)

        has_image = self._orig_pixmap is not None

        text_col = QVBoxLayout()
        text_col.setSpacing(12)
        text_col.addStretch()

        lbl_title = QLabel(title)
        lbl_title.setObjectName("slideTitle")
        lbl_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter if has_image else Qt.AlignCenter)
        lbl_title.setWordWrap(True)
        text_col.addWidget(lbl_title)

        lbl_body = QLabel(body)
        lbl_body.setObjectName("slideBody")
        lbl_body.setAlignment(Qt.AlignLeft | Qt.AlignVCenter if has_image else Qt.AlignCenter)
        lbl_body.setWordWrap(True)
        lbl_body.setMaximumWidth(420)
        text_col.addWidget(lbl_body)

        text_col.addStretch()

        text_wrap = QWidget()
        text_wrap.setLayout(text_col)
        text_wrap.setMaximumWidth(420)
        content.addWidget(text_wrap, 0, Qt.AlignVCenter)

        outer.addLayout(content)
        outer.addStretch(1)

        self._lbl_title = lbl_title
        self._lbl_body = lbl_body

        self._update_image_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_image_pixmap()

    def _update_image_pixmap(self):
        if self._orig_pixmap is None or self._lbl_image is None:
            return

        # Espacio vertical disponible dentro del slide (restando margenes
        # y un colchon para que nunca se desborde ni se vea recortada).
        available_h = max(self.height() - 64, 60)
        available_w = max(int(self.width() * 0.45), 60)
        target = min(self.IMAGE_SIZE, available_h, available_w)

        scaled = self._orig_pixmap.scaled(
            target, target,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._lbl_image.setPixmap(scaled)
        self._lbl_image.setFixedSize(scaled.size())

    def update_text(self, title, body):
        self._lbl_title.setText(title)
        self._lbl_body.setText(body)


class InstallationPage(QWidget):
    finished_success = Signal()
    finished_error = Signal(str)
    log_state_changed = Signal(bool)

    # Imagenes de cada slide, en el mismo orden que _slide_texts().
    SLIDE_IMAGES = [
        "welcome.webp",
        "package.webp",
        "init.webp",
        "desktop.webp",
        "update.webp",
        "community.webp",
    ]

    def _slide_texts(self):
        """Textos de los slides (titulo, cuerpo), traducibles y pensados
        para cualquier persona, sin tecnicismos."""
        return [
            (
                self.tr("Bienvenido a CuerdOS"),
                self.tr(
                    "Estás a punto de descubrir un sistema rápido, ligero "
                    "y pensado para que todo simplemente funcione. "
                    "Gracias por darle una oportunidad."
                ),
            ),
            (
                self.tr("Instalar programas, muy fácil"),
                self.tr(
                    "Encontrar y añadir nuevas aplicaciones es tan sencillo "
                    "como un par de clics, sin complicaciones ni pasos "
                    "técnicos de por medio."
                ),
            ),
            (
                self.tr("Rápido desde que enciendes"),
                self.tr(
                    "Tu equipo arrancará en segundos. Por debajo, CuerdOS "
                    "está optimizado para que tú solo te preocupes de usarlo."
                ),
            ),
            (
                self.tr("Tu escritorio, a tu gusto"),
                self.tr(
                    "Elige el aspecto que más te guste: simple y minimalista, "
                    "o lleno de detalles. Tú decides cómo se ve tu equipo."
                ),
            ),
            (
                self.tr("Siempre al día, sin esfuerzo"),
                self.tr(
                    "Mantener tu sistema actualizado es muy sencillo: con un "
                    "clic tendrás las últimas mejoras y parches de seguridad."
                ),
            ),
            (
                self.tr("Una comunidad que te acompaña"),
                self.tr(
                    "Si tienes dudas o quieres compartir tu experiencia, "
                    "nuestra comunidad está lista para ayudarte en todo momento."
                ),
            ),
        ]

    def __init__(self, demo=False):
        super().__init__()
        self.demo = demo
        self.install_finished = False
        self.install_error = False
        self.worker = None
        self._current_slide = 0
        self._slide_count = len(self.SLIDE_IMAGES)
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
        self._slide_widgets = []
        for (title, body), image in zip(self._slide_texts(), self.SLIDE_IMAGES):
            widget = _SlideWidget(title, body, image=image)
            self._slide_widgets.append(widget)
            self.slide_stack.addWidget(widget)
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
    def toggle_log(self):
        if self._showing_log:
            # Volver a slides
            self._content_stack.setCurrentIndex(0)
            self._slide_timer.start()
            self._showing_log = False
        else:
            # Mostrar terminal
            self._content_stack.setCurrentIndex(1)
            self._slide_timer.stop()
            self._showing_log = True
        self.log_state_changed.emit(self._showing_log)

    # ------------------------------------------------------------------ #
    #  Instalacion
    # ------------------------------------------------------------------ #
    def iniciar_instalacion(self, config_data):
        if self.demo:
            self.texto_label.setText(self.tr("Iniciando simulación (modo demo)..."))
        else:
            self.texto_label.setText(self.tr("Iniciando motor de instalación (Root)..."))
        self.progress.setValue(0)

        self.worker = InstallWorker(config_data, demo=self.demo)

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
        self.titl.setText(self.tr("Instalación"))

        self.UI_STATUS_TEXTS = {
            "INIT": self.tr("Iniciando motor de instalación..."),
            "CREATE_FS": self.tr("Creando sistemas de archivos..."),
            "COPY": self.tr("Copiando el sistema base..."),
            "REGIONAL_CONFIG": self.tr("Configurando idioma y zona horaria..."),
            "UPDATE": self.tr("Actualizando el sistema..."),
            "MIRROR": self.tr("Configurando servidor de repositorios..."),
            "NON-FREE": self.tr("Configurando repositorios de software propietario."),
            "NVIDIA": self.tr("Instalando controladores NVIDIA..."),
            "INTEL": self.tr("Instalando microcódigos de Intel..."),
            "USER_CONFIG": self.tr("Creando usuarios y contraseñas..."),
            "GRUB_INSTALL": self.tr("Instalando el cargador de arranque..."),
            "DONE": self.tr("Instalación completada correctamente"),
        }

        # No pisar el estado actual si la instalacion ya termino (bien o mal):
        # solo se usa este texto inicial mientras aun no ha arrancado nada.
        if not self.install_finished and not self.install_error and self.worker is None:
            self.texto_label.setText(self.tr("Preparando instalación..."))
        elif self.install_finished:
            self.texto_label.setText(self.tr("¡Instalación completada!"))
        elif self.install_error:
            self.texto_label.setText(self.tr("Error en la instalación"))

        for widget, (title, body) in zip(self._slide_widgets, self._slide_texts()):
            widget.update_text(title, body)

    def on_success(self):
        self._slide_timer.stop()
        self.install_finished = True
        self.texto_label.setText(self.tr("¡Instalación completada!"))
        self.progress.setValue(100)
        QMessageBox.information(
            self, self.tr("Éxito"),
            self.tr("CuerdOS se ha instalado correctamente.\n"
                   "Puede reiniciar su equipo.")
        )
        self.finished_success.emit()

    def on_error(self, msg):
        self._slide_timer.stop()
        self.install_error = True
        self.texto_label.setObjectName("errorStatusLabel")
        self.texto_label.setStyle(self.texto_label.style())
        self.texto_label.setText(self.tr("Error en la instalación"))
        QMessageBox.critical(self, self.tr("Error Fatal"), msg)