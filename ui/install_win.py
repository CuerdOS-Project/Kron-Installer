from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox
from PySide6.QtCore import QTranslator
from ui.welcome import WelcomePage
from ui.language import LanguagePage
from ui.mirrors import MirrorsPage
from ui.users import UsersPage
from ui.disks import DisksPage
from ui.installation import InstallationPage
from utils.system_utils import SystemDetector
from install.config_collector import InstallerConfigCollector
import subprocess

class InstallWin(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.translate_ui()

    def setup_ui(self):
        self.translator = QTranslator()
        self.resize(900, 650)

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Widgets "stacked"
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # DETECCIÓN DE HARDWARE AL INICIO
        self.system_data = {
            "efi": SystemDetector.detect_efi(),
            "net" : SystemDetector.has_internet(),
            "timezones": SystemDetector.detect_timezones(),
            "locales": SystemDetector.detect_locales(),
            "keymaps": SystemDetector.detect_keymaps(),
        }

        # Crear páginas (Pasamos datos a las que lo necesitan)
        self.pag_bienvenida = WelcomePage(self.system_data)
        self.pag_bienvenida.languageChanged.connect(self.set_language)

        self.pag_idiomas = LanguagePage(self.system_data)
        self.pag_mirrors = MirrorsPage(self.system_data)
        self.pag_usuarios = UsersPage()
        self.pag_discos = DisksPage(self.system_data)
        self.pag_instalacion = InstallationPage()

        # Añadir páginas a stack
        self.stack.addWidget(self.pag_bienvenida)
        self.stack.addWidget(self.pag_idiomas)

        # Página mirrors solo se añade si hay internet
        if self.system_data["net"]:
            self.stack.addWidget(self.pag_mirrors)
        
        self.stack.addWidget(self.pag_usuarios)
        self.stack.addWidget(self.pag_discos)
        self.stack.addWidget(self.pag_instalacion)
            
        # Barra inferior de botones
        nav_layout = QHBoxLayout()

        self.btn_atras = QPushButton()
        self.btn_atras.setObjectName("backButton")

        self.btn_siguiente = QPushButton()
        self.btn_siguiente.setObjectName("nextButton")

        nav_layout.addWidget(self.btn_atras)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_siguiente)

        main_layout.addLayout(nav_layout)

        # Conexiones
        self.btn_atras.clicked.connect(self.ir_atras)
        self.btn_siguiente.clicked.connect(self.ir_siguiente)

        # Mensaje de finalización PagInstalacion
        self.pag_instalacion.finished_success.connect(
            lambda: self.btn_siguiente.setVisible(True)
        )

        # Estado inicial
        self.actualizar_botones()

        # Cargar idioma por defecto
        self.set_language("en")
    
    def translate_ui(self):
        self.setWindowTitle(self.tr("Instalador Kron"))
        self.btn_atras.setText(self.tr("Atrás"))
        self.btn_siguiente.setText(self.tr("Siguiente"))
    
    # Botón 'Siguiente'
    def ir_siguiente(self):
            index = self.stack.currentIndex()
            curr_widget = self.stack.currentWidget()

            # Si estamos en la página de Discos, el siguiente paso es INSTALAR
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
                
                if config: # Si la validación pasó
                    # Pasar a la pantalla de instalación
                    self.stack.setCurrentIndex(index + 1)
                    self.actualizar_botones()
                    # Iniciar instalación
                    self.pag_instalacion.iniciar_instalacion(config)
                return

            if isinstance(curr_widget, InstallationPage):
                subprocess.Popen(["pkexec", "reboot"])
                return

            # Comportamiento normal para otras páginas
            if index < self.stack.count() - 1:
                self.stack.setCurrentIndex(index + 1)
            self.actualizar_botones()
    
    # Botón 'Atrás'
    def ir_atras(self):
        index = self.stack.currentIndex()
        if index > 0:
            self.stack.setCurrentIndex(index -1)
        self.actualizar_botones()
    
    def actualizar_botones(self):
        index = self.stack.currentIndex()

        # Primera página: ocultar botón atrás
        self.btn_atras.setVisible(index != 0)

        # Cambios de apariencia en botón 'Siguiente'
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
        """Confirmar antes de cerrar la ventana"""
        # Si la instalación ya terminó, no preguntar
        if isinstance(self.stack.currentWidget(), InstallationPage):
            if self.pag_instalacion.install_finished:
                event.accept()
                return
        
        # Mostrar diálogo de confirmación
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
