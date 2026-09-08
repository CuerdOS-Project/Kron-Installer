from pathlib import Path
import shutil

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices, QTextCursor
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QPlainTextEdit,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
)

from ui.title_widget import make_page_title


class InstallationErrorPage(QWidget):
    # Pantalla final para errores de instalación y gestión del registro.

    retry_requested = Signal()

    def __init__(self, parent=None, log_path="/tmp/installation.log"):
        super().__init__(parent)
        self.log_path = Path(log_path)
        self.error_message = ""
        self.setup_ui()
        self.translate_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 12)
        main_layout.setSpacing(0)

        self.titl = QLabel()
        self.titl.setObjectName("title")
        main_layout.addWidget(make_page_title(self.titl, "dialog-error"))
        main_layout.addSpacing(12)

        card = QFrame()
        card.setObjectName("formCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 24, 30, 24)
        card_layout.setSpacing(14)

        self.error_title = QLabel()
        self.error_title.setObjectName("errorLabel")
        self.error_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.error_title)

        self.error_summary = QLabel()
        self.error_summary.setObjectName("completionSubtitle")
        self.error_summary.setAlignment(Qt.AlignCenter)
        self.error_summary.setWordWrap(True)
        card_layout.addWidget(self.error_summary)

        self.error_detail = QLabel()
        self.error_detail.setObjectName("errorDetailLabel")
        self.error_detail.setAlignment(Qt.AlignCenter)
        self.error_detail.setWordWrap(True)
        self.error_detail.setTextInteractionFlags(Qt.TextSelectableByMouse)
        card_layout.addWidget(self.error_detail)

        self.log_hint = QLabel()
        self.log_hint.setObjectName("completionSubtitle")
        self.log_hint.setAlignment(Qt.AlignCenter)
        self.log_hint.setWordWrap(True)
        card_layout.addWidget(self.log_hint)

        self.log_preview = QPlainTextEdit()
        self.log_preview.setObjectName("installTerminal")
        self.log_preview.setReadOnly(True)
        self.log_preview.setMinimumHeight(170)
        self.log_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card_layout.addWidget(self.log_preview, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addStretch()

        self.btn_open_log = QPushButton()
        self.btn_open_log.setObjectName("actionButton")
        self.btn_open_log.clicked.connect(self.open_log)
        buttons.addWidget(self.btn_open_log)

        self.btn_export_log = QPushButton()
        self.btn_export_log.setObjectName("warnButton")
        self.btn_export_log.clicked.connect(self.export_log)
        buttons.addWidget(self.btn_export_log)
        buttons.addStretch()
        card_layout.addLayout(buttons)

        main_layout.addWidget(card, 1)

    def translate_ui(self):
        self.titl.setText(self.tr("Instalación fallida"))
        self.error_title.setText(self.tr("La instalación no se pudo completar."))
        self.error_summary.setText(self.tr("Se produjo el siguiente error:"))
        self.log_hint.setText(self.tr("El registro puede ayudar a diagnosticar el problema."))
        self.btn_open_log.setText(self.tr("Abrir log"))
        self.btn_export_log.setText(self.tr("Exportar log"))
        if self.error_message:
            self._update_detail()

    def _update_detail(self):
        self.error_detail.setText(self.error_message)

    def set_error(self, message, log_path=None):
        self.error_message = message or self.tr("Error desconocido")
        if log_path:
            self.log_path = Path(log_path)
        self._update_detail()
        self._load_log_preview()

    def _load_log_preview(self):
        if not self.log_path.is_file():
            self.log_preview.setPlainText(self.tr("El archivo de registro no está disponible."))
            return
        try:
            content = self.log_path.read_text(encoding="utf-8", errors="replace")
        except OSError as error:
            content = f"{self.tr('No se pudo abrir el registro de instalación.')}: {error}"
        self.log_preview.setPlainText(content[-12000:])
        self.log_preview.moveCursor(QTextCursor.MoveOperation.End)

    def open_log(self):
        if not self.log_path.is_file():
            QMessageBox.warning(
                self,
                self.tr("Registro no disponible"),
                self.tr("El archivo de registro no está disponible."),
            )
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.log_path))):
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("No se pudo abrir el registro de instalación."),
            )

    def export_log(self):
        if not self.log_path.is_file():
            QMessageBox.warning(
                self,
                self.tr("Registro no disponible"),
                self.tr("El archivo de registro no está disponible."),
            )
            return
        destination, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Exportar registro de instalación"),
            str(Path.home() / "kron-installation.log"),
            "Log files (*.log);;All files (*)",
        )
        if not destination:
            return
        try:
            shutil.copyfile(self.log_path, destination)
        except OSError as error:
            QMessageBox.critical(
                self,
                self.tr("Error"),
                f"{self.tr('No se pudo exportar el registro de instalación.')}: {error}",
            )
            return
        QMessageBox.information(
            self,
            self.tr("Registro exportado"),
            self.tr("El registro se exportó correctamente."),
        )
