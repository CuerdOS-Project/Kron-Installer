# styles.py — Paleta de colores Kron Installer (v2 Professional)
# ============================================================
# Fondo principal:  #1f2421
# Fondo sidebar:    #181d1a
# Fondo tarjetas:   #2a312d
# Acento verde:     #6fa67a
# Acento brillante: #7bcf93
# Texto principal:  #e6f1ea
# Texto secundario: #9fb7a7
# Texto terciario:  #7f9688
# Borde sutil:      #3a4a42
# Error:            #d46b6b
# ============================================================

import os

def global_stylesheet(assets_dir=None):
    """Retorna el stylesheet global.

    Si *assets_dir* se proporciona (ruta absoluta al directorio ui/assets),
    la flecha del QComboBox usara esa ruta en vez de una relativa al CWD.
    """
    _arrow_url = "ui/assets/arrow-down.svg"
    if assets_dir:
        _arrow_url = os.path.join(assets_dir, "arrow-down.svg")
    _sheet = """
    /* ============================
       GLOBAL
       ============================ */
    QWidget {
        background-color: #1f2421;
        color: #e6f1ea;
        font-family: "Noto Sans", sans-serif;
    }

    /* ============================
       LABELS
       ============================ */
    QLabel {
        color: #e6f1ea;
        background-color: transparent;
    }

    QLabel#title {
        font-size: 20px;
        font-weight: 600;
        color: #dff5e4;
        padding-bottom: 10px;
        border-bottom: 1px solid #3a4a42;
    }

    QLabel#welcomeTitle {
        font-size: 32px;
        font-weight: 600;
        color: #dff5e4;
    }

    QLabel#welcomeSubtitle {
        font-size: 15px;
        font-weight: 500;
        color: #9fb7a7;
    }

    QLabel#subtitle {
        font-size: 14px;
        color: #9fb7a7;
    }

    QLabel#footer {
        font-size: 13px;
        color: #7f9688;
    }

    QLabel#errorLabel {
        color: #d46b6b;
        font-size: 11px;
        font-weight: bold;
    }

    QLabel#statusLabel {
        font-size: 18px;
        color: #dff5e4;
    }

    QLabel#errorStatusLabel {
        font-size: 18px;
        color: #d46b6b;
    }

    QLabel#netCardLabel {
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
    }

    /* ============================
       SIDEBAR STEPPER
       ============================ */
    QWidget#sidebar {
        background-color: #181d1a;
        border-right: 1px solid #2a312d;
    }

    QLabel#stepLabel {
        color: #7f9688;
        font-size: 13px;
        font-weight: 400;
        background-color: transparent;
    }

    QLabel#stepLabelActive {
        color: #e6f1ea;
        font-size: 13px;
        font-weight: 600;
        background-color: transparent;
    }

    QLabel#stepLabelDone {
        color: #6fa67a;
        font-size: 13px;
        font-weight: 500;
        background-color: transparent;
    }

    QLabel#sidebarLogo {
        background-color: transparent;
    }

    /* ============================
       FORM CARD
       ============================ */
    QFrame#formCard {
        background-color: #2a312d;
        border: 1px solid #3a4a42;
        border-radius: 12px;
    }

    /* ============================
       BOTONES DE NAVEGACION
       ============================ */
    QPushButton#navButton {
        background-color: #2c332f;
        padding: 10px 28px;
        border-radius: 8px;
        color: #d7efe0;
        font-weight: 500;
        font-size: 14px;
        border: 1px solid transparent;
        min-height: 20px;
    }

    QPushButton#navButton:hover {
        background-color: #3e5f4a;
        border: 1px solid #7bcf93;
    }

    QPushButton#navButton:pressed {
        background-color: #2b4a38;
    }

    QPushButton#navButton:disabled {
        background-color: #1f2421;
        color: #4a5a50;
        border: 1px solid #2a312d;
    }

    /* Boton Atras */
    QPushButton#backButton {
        background-color: #2c332f;
        padding: 10px 28px;
        border-radius: 8px;
        color: #d7efe0;
        font-weight: 500;
        font-size: 14px;
        border: 1px solid transparent;
        min-height: 20px;
    }

    QPushButton#backButton:hover {
        background-color: #3e5f4a;
        border: 1px solid #7bcf93;
    }

    QPushButton#backButton:pressed {
        background-color: #2b4a38;
    }

    /* Boton Siguiente (estado normal) */
    QPushButton#nextButton {
        background-color: #2c332f;
        padding: 10px 28px;
        border-radius: 8px;
        color: #d7efe0;
        font-weight: 500;
        font-size: 14px;
        border: 1px solid transparent;
        min-height: 20px;
    }

    QPushButton#nextButton:hover {
        background-color: #3e5f4a;
        border: 1px solid #7bcf93;
    }

    QPushButton#nextButton:pressed {
        background-color: #2b4a38;
    }

    /* Boton Instalar (estado verde en pagina Discos) */
    QPushButton#installButton {
        background-color: #6fa67a;
        border-radius: 8px;
        padding: 10px 28px;
        font-weight: 600;
        font-size: 14px;
        color: #ffffff;
        border: 1px solid #6fa67a;
        min-height: 20px;
    }

    QPushButton#installButton:hover {
        background-color: #323b36;
        border: 1px solid #6fa67a;
    }

    QPushButton#installButton:pressed {
        background-color: #26302a;
    }

    /* Boton Reiniciar (estado en pagina Instalacion completada) */
    QPushButton#rebootButton {
        background-color: #6fa67a;
        border-radius: 8px;
        padding: 10px 28px;
        font-weight: 600;
        font-size: 14px;
        color: #ffffff;
        border: 1px solid #6fa67a;
        min-height: 20px;
    }

    QPushButton#rebootButton:hover {
        background-color: #7bcf93;
        border: 1px solid #7bcf93;
    }

    QPushButton#rebootButton:pressed {
        background-color: #5a8f65;
    }

    /* ============================
       BOTONES DE ACCION
       (Autopart, Partition Manager, Toggle Log)
       ============================ */
    QPushButton#actionButton {
        background-color: #2a312d;
        border-radius: 8px;
        text-align: center;
        padding: 8px 16px;
        border: 1px solid transparent;
        color: #d7efe0;
        font-weight: 500;
        min-height: 20px;
    }

    QPushButton#actionButton:hover {
        background-color: #323b36;
        border: 1px solid #6fa67a;
    }

    QPushButton#actionButton:pressed {
        background-color: #26302a;
    }

    QPushButton#actionButton:disabled {
        background-color: #1f2421;
        color: #4a5a50;
        border: 1px solid #2a312d;
    }

    /* Boton Autoparticionado (estilo warning/destacado) */
    QPushButton#warnButton {
        background-color: #6fa67a;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        color: #ffffff;
        border: 1px solid #6fa67a;
        min-height: 20px;
    }

    QPushButton#warnButton:hover {
        background-color: #323b36;
        border: 1px solid #6fa67a;
        color: #6fa67a;
    }

    QPushButton#warnButton:pressed {
        background-color: #26302a;
    }

    /* Boton mostrar/ocultar contrasena */
    QPushButton#togglePassButton {
        background-color: transparent;
        border: 1px solid #3a4a42;
        border-radius: 6px;
        padding: 4px;
        color: #9fb7a7;
        font-size: 12px;
        min-height: 20px;
    }

    QPushButton#togglePassButton:hover {
        background-color: #323b36;
        border: 1px solid #6fa67a;
        color: #d7efe0;
    }

    QPushButton#togglePassButton:checked {
        color: #6fa67a;
        border: 1px solid #6fa67a;
    }

    /* ============================
       COMBO BOX
       ============================ */
    QComboBox {
        background-color: #2a312d;
        border: 1px solid #3a4a42;
        border-radius: 6px;
        padding: 8px 12px;
        color: #e6f1ea;
        min-height: 20px;
        font-size: 14px;
        padding-right: 30px;
    }

    QComboBox:hover {
        border: 1px solid #6fa67a;
    }

    QComboBox:disabled {
        background-color: #1f2421;
        color: #4a5a50;
        border: 1px solid #2a312d;
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 30px;
        border-left: 1px solid #3a4a42;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
        background-color: #2a312d;
    }

    QComboBox::down-arrow {
        width: 16px;
        height: 16px;
        image: url(_ARROW_URL_PLACEHOLDER_);
    }

    QComboBox QAbstractItemView {
        background-color: #2a312d;
        border: 1px solid #3a4a42;
        border-radius: 6px;
        color: #e6f1ea;
        selection-background-color: #3e5f4a;
        selection-color: #ffffff;
        outline: none;
    }

    QComboBox QAbstractItemView::item {
        padding: 6px 12px;
        min-height: 28px;
    }

    QComboBox QAbstractItemView::item:hover {
        background-color: #323b36;
    }

    /* ============================
       LINE EDIT
       ============================ */
    QLineEdit {
        background-color: #2a312d;
        border: 1px solid #3a4a42;
        border-radius: 6px;
        padding: 8px 12px;
        color: #e6f1ea;
        selection-background-color: #3e5f4a;
        font-size: 14px;
        min-height: 20px;
    }

    QLineEdit:hover {
        border: 1px solid #4a5a50;
    }

    QLineEdit:focus {
        border: 1px solid #6fa67a;
    }

    QLineEdit:disabled {
        background-color: #1f2421;
        color: #4a5a50;
        border: 1px solid #2a312d;
    }

    /* ============================
       CHECKBOX
       ============================ */
    QCheckBox {
        spacing: 8px;
        color: #b7d6c2;
        font-size: 14px;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid #6fa67a;
        background-color: #2a312d;
    }

    QCheckBox::indicator:hover {
        border: 1px solid #7bcf93;
    }

    QCheckBox::indicator:checked {
        background-color: #6fa67a;
        border: 1px solid #6fa67a;
    }

    QCheckBox::indicator:disabled {
        background-color: #1f2421;
        border: 1px solid #2a312d;
    }

    QCheckBox:disabled {
        color: #4a5a50;
    }

    /* ============================
       PROGRESS BAR
       ============================ */
    QProgressBar {
        background-color: #2a312d;
        border: 1px solid #3a4a42;
        border-radius: 8px;
        text-align: center;
        color: #e6f1ea;
        font-weight: 500;
        min-height: 24px;
        font-size: 13px;
    }

    QProgressBar::chunk {
        background-color: #6fa67a;
        border-radius: 7px;
    }

    /* ============================
       PLAIN TEXT EDIT (Terminal)
       ============================ */
    QPlainTextEdit {
        background-color: #0d0f0e;
        color: #8cc997;
        border: 1px solid #2a312d;
        border-radius: 8px;
        font-family: "Noto Sans Mono", monospace;
        font-size: 12px;
        padding: 8px;
    }

    /* ============================
       TARJETA RED (Online/Offline)
       ============================ */
    QWidget#netCardOnline {
        background-color: #2a5a3a;
        border-radius: 10px;
        border: 1px solid #3a7a4a;
    }

    QWidget#netCardOffline {
        background-color: #5a3a1a;
        border-radius: 10px;
        border: 1px solid #7a5a2a;
    }

    /* ============================
       TABLE WIDGET (Particiones)
       ============================ */
    QTableWidget {
        background-color: #2a312d;
        alternate-background-color: #252b28;
        gridline-color: #3a4a42;
        border: 1px solid #3a4a42;
        border-radius: 8px;
        color: #e6f1ea;
        font-size: 13px;
        selection-background-color: #3e5f4a;
        selection-color: #ffffff;
        outline: none;
    }

    QTableWidget::item {
        padding: 8px 10px;
        border-bottom: 1px solid #333b37;
    }

    QTableWidget::item:alternate {
        background-color: #252b28;
    }

    QHeaderView::section {
        background-color: #232926;
        color: #9fb7a7;
        padding: 8px 10px;
        border: none;
        border-bottom: 1px solid #3a4a42;
        border-right: 1px solid #333b37;
        font-weight: 600;
        font-size: 12px;
    }

    QTableWidget QTableWidgetCornerButton::section {
        background-color: #232926;
        border: none;
    }

    /* ============================
       SCROLLBAR
       ============================ */
    QScrollBar:vertical {
        background: #1f2421;
        width: 8px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background: #3a4a42;
        border-radius: 4px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background: #4f6b5c;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: none;
    }

    QScrollBar:horizontal {
        background: #1f2421;
        height: 8px;
        margin: 0px;
    }

    QScrollBar::handle:horizontal {
        background: #3a4a42;
        border-radius: 4px;
        min-width: 20px;
    }

    QScrollBar::handle:horizontal:hover {
        background: #4f6b5c;
    }

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {
        background: none;
    }

    /* ============================
       MESSAGE BOX (Dialogos)
       ============================ */
    QMessageBox {
        background-color: #1f2421;
    }

    QMessageBox QLabel {
        color: #e6f1ea;
        background-color: transparent;
    }

    QMessageBox QPushButton {
        background-color: #2a312d;
        border: 1px solid #3a4a42;
        border-radius: 8px;
        padding: 8px 24px;
        color: #d7efe0;
        font-weight: 500;
        min-width: 90px;
        min-height: 20px;
    }

    QMessageBox QPushButton:hover {
        background-color: #323b36;
        border: 1px solid #6fa67a;
    }

    QMessageBox QPushButton:pressed {
        background-color: #26302a;
    }

    /* ============================
       TOOLTIP
       ============================ */
    QToolTip {
        background-color: #2a312d;
        color: #e6f1ea;
        border: 1px solid #3a4a42;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }

    /* ============================
       FORM LAYOUT LABELS
       ============================ */
    QFormLayout QLabel {
        color: #9fb7a7;
        font-size: 13px;
        font-weight: 500;
    }

    /* ============================
       FOOTER BAR
       ============================ */
    QWidget#footerBar {
        background-color: #181d1a;
        border-top: 1px solid #2a312d;
    }

    QLabel#stepCounter {
        color: #7f9688;
        font-size: 12px;
        background-color: transparent;
    }

    /* ============================
       SLIDES (Carrusel instalacion)
       ============================ */
    QFrame#slideWidget {
        background-color: transparent;
    }

    QLabel#slideTitle {
        color: #dff5e4;
        font-size: 20px;
        font-weight: 600;
        background-color: transparent;
    }

    QLabel#slideBody {
        color: #9fb7a7;
        font-size: 14px;
        background-color: transparent;
    }

    QWidget#slidesPage {
        background-color: transparent;
    }

    QPlainTextEdit#installTerminal {
        background-color: #0d0f0e;
        color: #8cc997;
        border: none;
        border-radius: 0px;
        font-family: "Noto Sans Mono", monospace;
        font-size: 12px;
        padding: 12px;
    }

    QWidget#slideNavBar {
        background-color: #252b28;
        border-top: 1px solid #3a4a42;
        border-radius: 0 0 12px 12px;
    }

    QLabel#slideDot {
        background-color: transparent;
    }

    QPushButton#slideNavButton {
        background-color: transparent;
        border: 1px solid #3a4a42;
        border-radius: 6px;
        color: #9fb7a7;
        font-size: 14px;
        font-weight: bold;
        padding: 0px;
    }

    QPushButton#slideNavButton:hover {
        background-color: #323b36;
        border: 1px solid #6fa67a;
        color: #e6f1ea;
    }

    QPushButton#slideNavButton:pressed {
        background-color: #26302a;
    }
    """.replace("_ARROW_URL_PLACEHOLDER_", _arrow_url)
    return _sheet