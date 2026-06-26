import os
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QIcon, QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QWidget,
)

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_NAME     = "Kron Installer"
APP_SUBTITLE = "\u00a9 2026 CuerdOS Project"
APP_WEBSITE  = "https://cuerdos.github.io"
ICON_PATH    = os.path.join(_BASE_DIR, "resources", "kron.svg")

_C = {
    "header_bg":   "#181d1a",
    "body_bg":     "#1f2421",
    "row_alt":     "#2a312d",
    "footer_bg":   "#181d1a",
    "accent":      "#6fa67a",
    "text":        "#e6f1ea",
    "text_dim":    "#7f9688",
    "btn_web_bg":  "#2c332f",
    "btn_web_fg":  "#7bcf93",
    "btn_web_br":  "#3a4a42",
    "btn_web_hov": "#3e5f4a",
    "btn_cls_bg":  "#2c332f",
    "btn_cls_fg":  "#e6f1ea",
    "btn_cls_br":  "#3a4a42",
    "btn_cls_hov": "#323b36",
    "sep":         "#2a312d",
}


def _hsep():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet(f"background:{_C['sep']}; border:none;")
    return line


def _btn(label, bg, fg, border, hover):
    btn = QPushButton(label)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(
        f"QPushButton {{ background:{bg}; color:{fg}; border:1px solid {border};"
        f" border-radius:5px; padding:5px 14px; font-size:11px; }}"
        f"QPushButton:hover {{ background:{hover}; }}"
    )
    return btn


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Acerca de {app_name}").format(app_name=APP_NAME))
        if os.path.isfile(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.setFixedWidth(460)
        self.setModal(True)

        APP_DESC = self.tr("Instalador gráfico para CuerdOS GNU/Linux.")
        INFO_ROWS = [
            (self.tr("Versión"),  "1.0.0"),
            (self.tr("Licencia"), "GNU GPL v3.0"),
            (self.tr("Autores"),  "CuerdOS Dev. Team"),
        ]

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background:{_C['header_bg']};")
        hl = QVBoxLayout(header)
        hl.setContentsMargins(0, 24, 0, 20)
        hl.setSpacing(0)
        hl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        if os.path.isfile(ICON_PATH):
            pm = QPixmap(ICON_PATH).scaled(
                72, 72,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            lbl_icon = QLabel()
            lbl_icon.setPixmap(pm)
            lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_icon.setStyleSheet("background:transparent;")
            hl.addWidget(lbl_icon)
            hl.addSpacing(10)

        lbl_name = QLabel(APP_NAME)
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_name.setStyleSheet(
            "font-size:20px; font-weight:bold; color:#dff5e4; background:transparent;")
        hl.addWidget(lbl_name)

        lbl_sub = QLabel(APP_SUBTITLE)
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet(
            f"font-size:11px; color:{_C['accent']}; background:transparent; margin-top:3px;")
        hl.addWidget(lbl_sub)

        outer.addWidget(header)
        outer.addWidget(_hsep())

        # Body
        body = QWidget()
        body.setStyleSheet(f"background:{_C['body_bg']};")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(28, 16, 28, 16)
        bl.setSpacing(0)

        for i, (label, value) in enumerate(INFO_ROWS):
            row_w = QWidget()
            row_w.setStyleSheet(
                f"background:{_C['row_alt']}; border-radius:6px;"
                if i % 2 == 0 else
                f"background:{_C['body_bg']};")
            rl = QHBoxLayout(row_w)
            rl.setContentsMargins(12, 8, 12, 8)
            rl.setSpacing(8)

            lbl_l = QLabel(label)
            lbl_l.setStyleSheet(
                f"color:{_C['accent']}; font-size:11px; font-weight:bold;"
                " min-width:80px; background:transparent;")

            lbl_v = QLabel(value)
            lbl_v.setStyleSheet(
                f"color:{_C['text']}; font-size:11px; background:transparent;")
            lbl_v.setWordWrap(True)

            rl.addWidget(lbl_l)
            rl.addWidget(lbl_v, 1)
            bl.addWidget(row_w)

        if APP_DESC:
            bl.addSpacing(12)
            lbl_desc = QLabel(APP_DESC)
            lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_desc.setStyleSheet(
                f"color:{_C['text_dim']}; font-size:10px;"
                " font-style:italic; background:transparent;")
            bl.addWidget(lbl_desc)

        outer.addWidget(body)
        outer.addWidget(_hsep())

        # Footer
        footer = QWidget()
        footer.setFixedHeight(52)
        footer.setStyleSheet(f"background:{_C['footer_bg']};")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(24, 0, 24, 0)
        fl.setSpacing(8)
        fl.addStretch()

        if APP_WEBSITE:
            btn_web = _btn(self.tr("Visitar página web"),
                           _C["btn_web_bg"], _C["btn_web_fg"],
                           _C["btn_web_br"], _C["btn_web_hov"])
            btn_web.clicked.connect(
                lambda: QDesktopServices.openUrl(QUrl(APP_WEBSITE)))
            fl.addWidget(btn_web)

        btn_close = _btn(self.tr("Cerrar"),
                         _C["btn_cls_bg"], _C["btn_cls_fg"],
                         _C["btn_cls_br"], _C["btn_cls_hov"])
        btn_close.clicked.connect(self.accept)
        fl.addWidget(btn_close)

        outer.addWidget(footer)
