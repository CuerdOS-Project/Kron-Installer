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
from ui.about import AboutDialog
from utils.system_utils import SystemDetector
from install.config_collector import InstallerConfigCollector
import subprocess
import os


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
    def __init__(self, images_dir=None, demo=False):
        super().__init__()
        self._images_dir = images_dir
        self.demo = demo
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
        self.pag_bienvenida = WelcomePage(self.system_data, images_dir=self._images_dir)
        self.pag_bienvenida.languageChanged.connect(self.set_language)

        self.pag_idiomas = LanguagePage(self.system_data)
        self.pag_mirrors = MirrorsPage(self.system_data)
        self.pag_usuarios = UsersPage()
        self.pag_discos = DisksPage(self.system_data)
        self.pag_instalacion = InstallationPage(demo=self.demo)

        # --- Definir orden de pasos ---
        self.steps = [
            ("welcome", self.tr("Bienvenida")),
            ("language", self.tr("Regional")),
            ("mirrors", self.tr("Repositorios")),
            ("users", self.tr("Usuarios")),
            ("disks", self.tr("Discos")),
            ("install", self.tr("Instalación")),
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
        logo_path = os.path.join(self._images_dir, "identity.png") if self._images_dir else "images/identity.png"
        logo_pixmap = QPixmap(logo_path)
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

        self.btn_about = QPushButton()
        self.btn_about.setObjectName("sidebarAboutButton")
        self.btn_about.clicked.connect(lambda: AboutDialog(self).exec())
        sidebar_layout.addWidget(self.btn_about)

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

        self.btn_toggle_log = QPushButton()
        self.btn_toggle_log.setObjectName("actionButton")
        self.btn_toggle_log.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_toggle_log.clicked.connect(self._on_toggle_log_clicked)
        self.btn_toggle_log.hide()

        center_wrap = QWidget()
        center_wrap.setObjectName("footerCenterWrap")
        center_layout = QHBoxLayout(center_wrap)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(16)
        center_layout.addStretch()
        center_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.btn_siguiente = QPushButton()
        self.btn_siguiente.setObjectName("nextButton")
        self.btn_siguiente.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        footer_layout.addWidget(self.btn_atras)
        footer_layout.addWidget(self.btn_toggle_log)
        footer_layout.addWidget(center_wrap)
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

        # Boton "Mostrar/Ocultar log": solo visible en la pagina de instalacion
        self.pag_instalacion.log_state_changed.connect(self._sync_log_button_text)
        self.stack.currentChanged.connect(self._on_stack_page_changed)

        # Estado inicial
        self.actualizar_botones()
        self._update_stepper()

        # Cargar idioma por defecto
        self.set_language("en_US")

    def translate_ui(self):
        title = self.tr("Instalador Kron")
        if self.demo:
            title += " " + self.tr("(Modo demo)")
        self.setWindowTitle(title)
        self.btn_atras.setText(self.tr("Atrás"))
        self.btn_siguiente.setText(self.tr("Siguiente"))
        self.btn_about.setText(self.tr("Acerca de"))
        self._sync_log_button_text(self.pag_instalacion._showing_log)
        self._translate_stepper()

    def _translate_stepper(self):
        texts = {
            "welcome": self.tr("Bienvenida"),
            "language": self.tr("Regional"),
            "mirrors": self.tr("Repositorios"),
            "users": self.tr("Usuarios"),
            "disks": self.tr("Discos"),
            "install": self.tr("Instalación"),
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


    def _on_stack_page_changed(self, index):
        is_install_page = isinstance(self.stack.widget(index), InstallationPage)
        self.btn_toggle_log.setVisible(is_install_page)
        if is_install_page:
            self._sync_log_button_text(self.pag_instalacion._showing_log)

    def _sync_log_button_text(self, showing_log):
        self.btn_toggle_log.setText(
            self.tr("Ocultar log") if showing_log else self.tr("Mostrar log")
        )

    def _on_toggle_log_clicked(self):
        self.pag_instalacion.toggle_log()

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
                self.pag_instalacion.iniciar_instalacion(config)
            return

        if isinstance(curr_widget, InstallationPage):
            if self.demo:
                self.close()
                return
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

    # --- Boton 'Atrás' ---
    def ir_atras(self):
        index = self.stack.currentIndex()
        if index > 0:
            self.stack.setCurrentIndex(index - 1)
        self.actualizar_botones()
        self._update_stepper()

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
            self.tr("¿Salir del instalador?"),
            self.tr("¿Estás seguro de que deseas salir? La instalación no ha finalizado."),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()