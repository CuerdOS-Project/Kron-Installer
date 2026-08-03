from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPixmap, QFont, QFontMetrics
import os
from ui.title_widget import make_page_title

_UI_DIR = os.path.dirname(os.path.abspath(__file__))


class AdaptiveLabel(QLabel):
    """Un QLabel que ajusta automáticamente su tamaño de fuente para caber en su ancho."""
    
    def __init__(self, text="", min_font_size=10, max_font_size=28, parent=None):
        super().__init__(text, parent)
        self.min_font_size = min_font_size
        self.max_font_size = max_font_size
        self.setWordWrap(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_font_size()

    def setText(self, text):
        super().setText(text)
        self.adjust_font_size()

    def adjust_font_size(self):
        text = self.text()
        if not text:
            return

        # Comenzar con el tamaño máximo
        current_font = self.font()
        font_size = self.max_font_size
        
        while font_size >= self.min_font_size:
            current_font.setPointSize(font_size)
            metrics = QFontMetrics(current_font)
            
            # Calcular el rectángulo que ocuparía el texto con este tamaño de fuente
            # Usamos el ancho actual del widget menos un margen de seguridad
            rect = metrics.boundingRect(0, 0, self.width() - 10, 1000, 
                                      Qt.AlignHCenter | Qt.TextWordWrap, text)
            
            # Si el texto cabe en una o dos líneas (dependiendo de la importancia)
            # Para el título queremos que sea preferiblemente 1 o 2 líneas
            # Para el mensaje podemos permitir más pero con fuente legible
            if rect.height() <= self.height() or font_size == self.min_font_size:
                break
                
            font_size -= 1
            
        self.setFont(current_font)


class CompletionPage(QWidget):
    """Página de finalización que se muestra después de completar la instalación."""

    def __init__(self, images_dir=None):
        super().__init__()
        self._images_dir = images_dir
        self.setup_ui()
        self.translate_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 12)
        main_layout.setSpacing(0)

        # Titulo de pagina
        self.titl = QLabel()
        self.titl.setObjectName("title")
        main_layout.addWidget(make_page_title(self.titl, "system-software-install"))
        main_layout.addSpacing(12)

        # Contenedor principal con la imagen y el mensaje
        content_card = QWidget()
        content_card.setObjectName("formCard")
        content_layout = QVBoxLayout(content_card)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(15)
        content_layout.addStretch(1)

        # Imagen de finalización
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        ps2_path = os.path.join(self._images_dir, "ps2.webp") if self._images_dir else "images/ps2.webp"
        pixmap = QPixmap(ps2_path)
        if not pixmap.isNull():
            image_label.setPixmap(
                pixmap.scaled(500, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            image_label.setText(self.tr("Imagen de finalización"))
            image_label.setStyleSheet("color: #7f9688; font-size: 14px;")
        content_layout.addWidget(image_label, alignment=Qt.AlignCenter)

        content_layout.addSpacing(10)

        # Título de éxito adaptable
        self.success_title = AdaptiveLabel(min_font_size=16, max_font_size=32)
        self.success_title.setObjectName("completionTitle")
        self.success_title.setAlignment(Qt.AlignCenter)
        self.success_title.setFixedHeight(80) # Altura fija para dar espacio al escalado
        content_layout.addWidget(self.success_title, alignment=Qt.AlignCenter)

        # Mensaje de finalización adaptable
        self.success_msg = AdaptiveLabel(min_font_size=12, max_font_size=16)
        self.success_msg.setObjectName("completionSubtitle")
        self.success_msg.setAlignment(Qt.AlignCenter)
        self.success_msg.setFixedHeight(60)
        content_layout.addWidget(self.success_msg, alignment=Qt.AlignCenter)

        content_layout.addStretch(1)
        main_layout.addWidget(content_card, 1)

    def translate_ui(self):
        self.titl.setText(self.tr("Instalación completada"))
        self.success_title.setText(self.tr("¡Bienvenido a CuerdOS!"))
        self.success_msg.setText(
            self.tr(
                "Tu sistema ha sido instalado correctamente.\n"
                "Haz clic en 'Reiniciar' para completar el proceso."
            )
        )
