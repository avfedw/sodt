from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class TabNomenclature(QWidget):
    """Тимчасова заглушка для вкладки номенклатури."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Вкладка номенклатури буде реалізована пізніше.", self)
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addStretch(1)
