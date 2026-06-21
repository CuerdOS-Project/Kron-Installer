from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QMessageBox, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QTranslator
from PySide6.QtGui import QPixmap
from ui.welcome import WelcomePage
from ui.language import LanguagePage
from ui.mirrors import MirrorsPage
from ui.users import UsersPage
from ui.disks import DisksPage
from ui.installation import InstallationPage
from utils.system_utils import SystemDetector
from install.config_collector import InstallerConfigCollector
import subprocess


class StepIndicator(QWidget):
    """Un item individual del sidebar stepper."""

    def __init__(self, number, text_key, parent=None):
        super().__init__(parent)
        self.number = number
        self.text_key = text_key
        self.state = "pending"  # "pending", "active", "done"

        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(10)

        # Numero / check en circulo
        self.circle_label = QLabel()
        self.circle_label.setFixedSize(24, 24)
        self.circle_label.setAlignment(Qt.AlignCenter)
        self.circle_label.setStyleSheet(
            "background-color: #3a4a42; border-radius: 12px; "
            "color: #7f9688; font-size: 12px; font-weight: 600;"
        )
        layout.addWidget(self.circle_label)

        # Texto del paso
        self.text_label = QLabel()
        self.text_label.setObjectName("stepLabel")
        self.text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.text_label)

        self._update_appearance()

    def set_state(self, state):
        self.state = state
        self._update_appearance()

    def _update_appearance(self):
        if self.state == "active":
            self.circle_label.setText(str(self.number))
            self.circle_label.setStyleSheet(
                "background-color: #6fa67a; border-radius: 12px; "
                "color: #ffffff; font-size: 12px; font-weight: 700;"
            )
            self.text_label.setObjectName("stepLabelActive")
            self.text_label.setStyleSheet(
                "color: #e6f1ea; font-size: 13px; font-weight: 600; "
                "background-color: transparent;"
            )
        elif self.state == "done":
            self.circle_label.setText("\u2713")
            self.circle_label.setStyleSheet(
                "background-color: #3e5f4a; border-radius: 12px; "
                "color: #7bcf93; font-size: 13px; font-weight: 700;"
            )
            self.text_label.setObjectName("stepLabelDone")
            self.text_label.setStyleSheet(
                "color: #6fa67a; font-size: 13px; font-weight: 500; "
                "background-color: transparent;"
            )
        else:
            self.circle_label.setText(str(self.number))
            self.circle_label.setStyleSheet(
                "background-color: #3a4a42; border-radius: 12px; "
                "color: #7f9688; font-size: 12px; font-weight: 600;"
            )
            self.text_label.setObjectName("stepLabel")
            self.text_label.setStyleSheet(
                "color: #7f9688; font-size: 13px; font-weight: 400; "
                "background-color: transparent;"
            )

    def translate(self, texts):
        self.text_label.setText(texts.get(self.text_key, self.text_key))


class InstallWin(QWidget):
    def __init__(self):
        super().__init__()
        self.translator = QTranslator()
        self.has_net = True
        self._confirm_install = False
        self.setup_ui()
        self.translate_ui()

    def setup_ui(self):
        self.setMinimumSize(900, 520)
        self.resize(1024, 600)

        # --- DETECCION DE HARDWARE ---
        self.system_data = {
            "efi": SystemDetector.detect_efi(),
            "net": SystemDetector.has_internet(),
            "timezones": SystemDetector.detect_timezones(),
            "locales": SystemDetector.detect_locales(),
            "keymaps": SystemDetector.detect_keymaps(),
        }
        self.has_net = self.system_data["net"]

        # --- Crear paginas ---
        self.pag_bienvenida = WelcomePage(self.system_data)
        self.pag_bienvenida.languageChanged.connect(self.set_language)

        self.pag_idiomas = LanguagePage(self.system_data)
        self.pag_mirrors = MirrorsPage(self.system_data)
        self.pag_usuarios = UsersPage()
        self.pag_discos = DisksPage(self.system_data)
        self.pag_instalacion = InstallationPage()

        # --- Definir orden de pasos ---
        self.steps = [
            ("welcome", self.tr("Bienvenida")),
            ("language", self.tr("Regional")),
            ("mirrors", self.tr("Repositorios")),
            ("users", self.tr("Usuarios")),
            ("disks", self.tr("Discos")),
            ("install", self.tr("Instalacion")),
        ]
        if not self.has_net:
            # Sin internet: quitar mirrors
            self.steps = [s for s in self.steps if s[0] != "mirrors"]

        # --- Layout principal horizontal: sidebar + central ---
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ===== SIDEBAR =====
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(190)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(4)

        # Logo en sidebar
        sidebar_logo = QLabel()
        sidebar_logo.setObjectName("sidebarLogo")
        sidebar_logo.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap("images/identity.png")
        if not logo_pixmap.isNull():
            sidebar_logo.setPixmap(
                logo_pixmap.scaled(100, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        sidebar_layout.addWidget(sidebar_logo)
        sidebar_layout.addSpacing(16)

        # Stepper items
        self.step_indicators = []
        for i, (key, label) in enumerate(self.steps):
            indicator = StepIndicator(i + 1, key)
            indicator.translate({key: label})
            self.step_indicators.append(indicator)
            sidebar_layout.addWidget(indicator)

        sidebar_layout.addStretch()

        # Texto version pequeno
        version_label = QLabel("Kron Installer")
        version_label.setObjectName("stepLabel")
        version_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(version_label)

        root_layout.addWidget(self.sidebar)

        # ===== CENTRAL AREA (stack + footer) =====
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Stack de paginas
        self.stack = QStackedWidget()

        # Anadir paginas al stack en orden
        self.stack.addWidget(self.pag_bienvenida)
        self.stack.addWidget(self.pag_idiomas)
        if self.has_net:
            self.stack.addWidget(self.pag_mirrors)
        self.stack.addWidget(self.pag_usuarios)
        self.stack.addWidget(self.pag_discos)
        self.stack.addWidget(self.pag_instalacion)

        central_layout.addWidget(self.stack, 1)

        # ===== FOOTER BAR =====
        self.footer_bar = QWidget()
        self.footer_bar.setObjectName("footerBar")
        self.footer_bar.setFixedHeight(52)
        footer_layout = QHBoxLayout(self.footer_bar)
        footer_layout.setContentsMargins(20, 0, 20, 0)

        self.btn_atras = QPushButton()
        self.btn_atras.setObjectName("backButton")
        self.btn_atras.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.step_counter = QLabel()
        self.step_counter.setObjectName("stepCounter")
        self.step_counter.setAlignment(Qt.AlignCenter)
        self.step_counter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.btn_siguiente = QPushButton()
        self.btn_siguiente.setObjectName("nextButton")
        self.btn_siguiente.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        footer_layout.addWidget(self.btn_atras)
        footer_layout.addWidget(self.step_counter)
        footer_layout.addWidget(self.btn_siguiente)

        central_layout.addWidget(self.footer_bar)

        root_layout.addLayout(central_layout, 1)

        # --- Conexiones ---
        self.btn_atras.clicked.connect(self.ir_atras)
        self.btn_siguiente.clicked.connect(self.ir_siguiente)

        # Mensaje de finalizacion
        self.pag_instalacion.finished_success.connect(
            lambda: self.btn_siguiente.setVisible(True)
        )

        # Estado inicial
        self.actualizar_botones()
        self._update_stepper()

        # Cargar idioma por defecto
        self.set_language("en_US")

    def translate_ui(self):
        self.setWindowTitle(self.tr("Instalador Kron"))
        self.btn_atras.setText(self.tr("Atras"))
        self.btn_siguiente.setText(self.tr("Siguiente"))
        self._update_step_counter()
        self._translate_stepper()

    def _translate_stepper(self):
        texts = {
            "welcome": self.tr("Bienvenida"),
            "language": self.tr("Regional"),
            "mirrors": self.tr("Repositorios"),
            "users": self.tr("Usuarios"),
            "disks": self.tr("Discos"),
            "install": self.tr("Instalacion"),
        }
        for ind in self.step_indicators:
            ind.translate(texts)

    def _update_stepper(self):
        idx = self.stack.currentIndex()
        for i, ind in enumerate(self.step_indicators):
            if i < idx:
                ind.set_state("done")
            elif i == idx:
                ind.set_state("active")
            else:
                ind.set_state("pending")

    def _update_step_counter(self):
        idx = self.stack.currentIndex()
        total = self.stack.count()
        self.step_counter.setText(f"{idx + 1} / {total}")

    # --- Boton 'Siguiente' ---
    def ir_siguiente(self):
        index = self.stack.currentIndex()
        curr_widget = self.stack.currentWidget()

        if isinstance(curr_widget, DisksPage):
            if not getattr(self, "_confirm_install", False):
                self._confirm_install = True
                self.btn_siguiente.setText(self.tr("Pulsa otra vez para instalar"))
                return
            self._confirm_install = False

            collector = InstallerConfigCollector(
                parent=self,
                paginas={
                    "idiomas": self.pag_idiomas,
                    "usuarios": self.pag_usuarios,
                    "mirrors": self.pag_mirrors,
                    "discos": self.pag_discos,
                },
                system_data=self.system_data
            )
            config = collector.collect_data()

            if config:
                self.stack.setCurrentIndex(index + 1)
                self.actualizar_botones()
                self._update_stepper()
                self._update_step_counter()
                self.pag_instalacion.iniciar_instalacion(config)
            return

        if isinstance(curr_widget, InstallationPage):
            subprocess.Popen(
                ["pkexec", "reboot"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return

        if index < self.stack.count() - 1:
            self.stack.setCurrentIndex(index + 1)
        self.actualizar_botones()
        self._update_stepper()
        self._update_step_counter()

    # --- Boton 'Atras' ---
    def ir_atras(self):
        index = self.stack.currentIndex()
        if index > 0:
            self.stack.setCurrentIndex(index - 1)
        self.actualizar_botones()
        self._update_stepper()
        self._update_step_counter()

    def actualizar_botones(self):
        index = self.stack.currentIndex()

        # Primera pagina: ocultar boton atras
        self.btn_atras.setVisible(index != 0)

        if isinstance(self.stack.currentWidget(), DisksPage):
            self.btn_siguiente.setText(self.tr("Instalar"))
            self.btn_siguiente.setObjectName("installButton")
            self.btn_siguiente.setStyle(self.btn_siguiente.style())
            self._confirm_install = False
        elif isinstance(self.stack.currentWidget(), InstallationPage):
            self.btn_siguiente.setText(self.tr("Reiniciar"))
            self.btn_siguiente.setObjectName("rebootButton")
            self.btn_siguiente.setStyle(self.btn_siguiente.style())
            self.btn_atras.setVisible(False)
            self.btn_siguiente.setVisible(False)
        else:
            self.btn_siguiente.setText(self.tr("Siguiente"))
            self.btn_siguiente.setObjectName("nextButton")
            self.btn_siguiente.setStyle(self.btn_siguiente.style())

        self._update_step_counter()

    def set_language(self, lang_code):
        QApplication.instance().removeTranslator(self.translator)

        if self.translator.load(f"i18n/{lang_code}.qm"):
            QApplication.instance().installTranslator(self.translator)

        self.translate_ui()
        self.pag_bienvenida.translate_ui()
        self.pag_idiomas.translate_ui()
        self.pag_mirrors.translate_ui()
        self.pag_usuarios.translate_ui()
        self.pag_discos.translate_ui()
        self.pag_instalacion.translate_ui()

    def closeEvent(self, event):
        if isinstance(self.stack.currentWidget(), InstallationPage):
            if self.pag_instalacion.install_finished:
                event.accept()
                return

        reply = QMessageBox.question(
            self,
            self.tr("Salir del instalador?"),
            self.tr("Estas seguro de que deseas salir? La instalacion no ha finalizado."),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()