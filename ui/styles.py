# styles.py — Paleta de colores Kron Installer
# Colores base:
#   Fondo principal:  #1f2421
#   Fondo tarjetas:   #2a312d
#   Acento verde:     #6fa67a
#   Texto principal:  #e6f1ea
#   Texto secundario: #9fb7a7
#   Texto terciario:  #7f9688

def global_stylesheet():
    return """
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
        font-size: 24px;
        font-weight: 600;
        color: #dff5e4;
    }

    QLabel#welcomeTitle {
        font-size: 34px;
        font-weight: 600;
        color: #dff5e4;
    }

    QLabel#welcomeSubtitle {
        font-size: 16px;
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
       BOTONES DE NAVEGACION
       ============================ */
    QPushButton#navButton {
        background-color: #2c332f;
        padding: 8px 24px;
        border-radius: 8px;
        color: #d7efe0;
        font-weight: 500;
        font-size: 14px;
        border: 1px solid transparent;
    }

    QPushButton#navButton:hover {
        background-color: #3e5f4a;
        border: 1px solid #7bcf93;
    }

    QPushButton#navButton:pressed {
        background-color: #2b4a38;
    }

    /* Boton Atras */
    QPushButton#backButton {
        background-color: #2c332f;
        padding: 8px 24px;
        border-radius: 8px;
        color: #d7efe0;
        font-weight: 500;
        font-size: 14px;
        border: 1px solid transparent;
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
        padding: 8px 24px;
        border-radius: 8px;
        color: #d7efe0;
        font-weight: 500;
        font-size: 14px;
        border: 1px solid transparent;
    }

    QPushButton#nextButton:hover {
        background-color: #3e5f4a;
        border: 1px solid #7bcf93;
    }

    QPushButton#nextButton:pressed {
        background-color: #2b4a38;
    }

    /* Boton Instalar (estado rojo en pagina Discos) */
    QPushButton#installButton {
        background-color: #6fa67a;
        border-radius: 8px;
        padding: 8px 24px;
        font-weight: 600;
        font-size: 14px;
        color: #ffffff;
        border: 1px solid #6fa67a;
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
        padding: 8px 24px;
        font-weight: 600;
        font-size: 14px;
        color: #ffffff;
        border: 1px solid #6fa67a;
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
        padding: 8px 14px;
        border: 1px solid transparent;
        color: #d7efe0;
        font-weight: 500;
    }

    QPushButton#actionButton:hover {
        background-color: #323b36;
        border: 1px solid #6fa67a;
    }

    QPushButton#actionButton:pressed {
        background-color: #26302a;
    }

    /* Boton Autoparticionado (estilo warning/destacado) */
    QPushButton#warnButton {
        background-color: #6fa67a;
        border-radius: 8px;
        padding: 8px 14px;
        font-weight: 600;
        color: #ffffff;
        border: 1px solid #6fa67a;
    }

    QPushButton#warnButton:hover {
        background-color: #323b36;
        border: 1px solid #6fa67a;
    }

    QPushButton#warnButton:pressed {
        background-color: #26302a;
    }

    /* Boton mostrar/ocultar contrasena */
    QPushButton#togglePassButton {
        background-color: #2a312d;
        border-radius: 4px;
        padding: 2px;
        border: 1px solid #3a4a42;
        color: #d7efe0;
        font-size: 12px;
    }

    QPushButton#togglePassButton:hover {
        background-color: #323b36;
        border: 1px solid #6fa67a;
    }

    QPushButton#togglePassButton:pressed {
        background-color: #26302a;
    }

    /* ============================
       COMBO BOX
       ============================ */
    QComboBox {
        background-color: #2a312d;
        border: 1px solid #3a4a42;
        border-radius: 6px;
        padding: 6px 10px;
        color: #e6f1ea;
        min-height: 20px;
        padding-right: 30px;
    }

    QComboBox:hover {
        border: 1px solid #6fa67a;
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 28px;
        border-left: 1px solid #3a4a42;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
        background-color: #2a312d;
    }

    QComboBox::down-arrow {
        width: 16px;
        height: 16px;
        image: url(ui/assets/arrow-down.svg);
    }

    QComboBox QAbstractItemView {
        background-color: #2a312d;
        border: 1px solid #3a4a42;
        border-radius: 4px;
        color: #e6f1ea;
        selection-background-color: #3e5f4a;
        selection-color: #ffffff;
        outline: none;
    }

    QComboBox QAbstractItemView::item {
        padding: 5px 10px;
        min-height: 24px;
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
        padding: 6px 10px;
        color: #e6f1ea;
        selection-background-color: #3e5f4a;
    }

    QLineEdit:hover {
        border: 1px solid #6fa67a;
    }

    QLineEdit:focus {
        border: 1px solid #6fa67a;
    }

    /* ============================
       CHECKBOX
       ============================ */
    QCheckBox {
        spacing: 8px;
        color: #b7d6c2;
    }

    QCheckBox::indicator {
        width: 16px;
        height: 16px;
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
        min-height: 20px;
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
        border-radius: 6px;
        font-family: "Noto Sans Mono", monospace;
        font-size: 12px;
        padding: 6px;
    }

    /* ============================
       TARJETA RED (Online/Offline)
       ============================ */
    QWidget#netCardOnline {
        background-color: #2a5a3a;
        border-radius: 8px;
        border: 1px solid #3a7a4a;
    }

    QWidget#netCardOffline {
        background-color: #5a3a1a;
        border-radius: 8px;
        border: 1px solid #7a5a2a;
    }

    /* ============================
       SCROLLBAR
       ============================ */
    QScrollBar:vertical {
        background: #1f2421;
        width: 10px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background: #3a4a42;
        border-radius: 5px;
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
        height: 10px;
        margin: 0px;
    }

    QScrollBar::handle:horizontal {
        background: #3a4a42;
        border-radius: 5px;
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
        border-radius: 6px;
        padding: 6px 20px;
        color: #d7efe0;
        font-weight: 500;
        min-width: 80px;
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
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
    }

    /* ============================
       FORM LAYOUT LABELS
       ============================ */
    QFormLayout QLabel {
        color: #9fb7a7;
        font-size: 13px;
    }
    """
