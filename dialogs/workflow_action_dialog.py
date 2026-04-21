from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit, QDialogButtonBox, QLabel, QLineEdit, QSizePolicy, QVBoxLayout, QWidget

from .base_dialog import CenteredDialog


class WorkflowActionDialog(CenteredDialog):
    """Піддіалог для дій відправлення або знищення картки."""

    def __init__(self, texts: dict, requires_target: bool, parent=None):
        super().__init__(parent)
        self.texts = texts
        self.requires_target = requires_target
        self.setWindowTitle(self.texts["title"])
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)
        self.setMinimumWidth(420)

        self.number_label = QLabel(self.texts["number"], self)
        main_layout.addWidget(self.number_label)

        self.number_input = QLineEdit(self)
        self.number_input.setMinimumWidth(220)
        self.number_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(self.number_input)

        self.date_label = QLabel(self.texts["date"], self)
        main_layout.addWidget(self.date_label)

        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd.MM.yyyy")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(self.date_input)

        self.target_input = QLineEdit(self)
        self.target_input.setEnabled(self.requires_target)
        self.target_input.setMinimumWidth(220)
        self.target_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if self.requires_target:
            self.target_label = QLabel(self.texts["target"], self)
            main_layout.addWidget(self.target_label)
            main_layout.addWidget(self.target_input)
        else:
            self.target_input.hide()

        button_box = QDialogButtonBox(self)
        confirm_button = button_box.addButton(self.texts["confirm"], QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = button_box.addButton(self.texts["cancel"], QDialogButtonBox.ButtonRole.RejectRole)
        confirm_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        main_layout.addWidget(button_box)

    def get_input(self) -> tuple[str, str, str]:
        return (
            self.number_input.text(),
            self.date_input.date().toString("dd.MM.yyyy"),
            self.target_input.text(),
        )