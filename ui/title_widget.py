from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize


def make_page_title(title_label: QLabel, icon_name: str, size: int = 22) -> QWidget:
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
