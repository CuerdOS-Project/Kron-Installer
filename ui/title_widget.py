from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize


def make_page_title(title_label: QLabel, icon_name: str, size: int = 22) -> QWidget:
    """Envuelve el QLabel de titulo (objectName='title') en una fila con un
    icono del tema del sistema a la izquierda. El titulo debe crearse antes
    y ya tener setObjectName('title') aplicado; esta funcion solo lo inserta
    en una fila junto al icono, conservando su estilo.

    *icon_name* debe ser un nombre de icono freedesktop.org (icon-naming-spec),
    p.ej. "system-users", "drive-harddisk", "network-server". Si el tema
    actual no lo tiene, la fila simplemente se muestra sin icono.
    """
    row = QWidget()
    row.setObjectName("titleRow")

    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)

    icon_label = QLabel()
    icon_label.setObjectName("titleIcon")
    icon_label.setFixedSize(size, size)

    icon = QIcon.fromTheme(icon_name)
    if not icon.isNull():
        icon_label.setPixmap(icon.pixmap(QSize(size, size)))
        layout.addWidget(icon_label)

    layout.addWidget(title_label, 1)

    return row
