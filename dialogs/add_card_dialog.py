from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout

from .base_dialog import CenteredDialog


_UKRAINIAN_LETTERS = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя"


class AddCardDialog(CenteredDialog):
    """Діалог додавання нової картки."""

    def __init__(self, texts: dict, parent=None):
        super().__init__(parent)
        self.texts = texts
        self.setWindowTitle(self.texts["title"])
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        validator = QRegularExpressionValidator(
            QRegularExpression(f"[{_UKRAINIAN_LETTERS}'’ ]*"),
            self,
        )

        self.surname_input = QLineEdit(self)
        self.surname_input.setValidator(validator)
        form_layout.addRow(self.texts["surname"], self.surname_input)

        self.name_input = QLineEdit(self)
        self.name_input.setValidator(validator)
        form_layout.addRow(self.texts["name"], self.name_input)

        self.patronymic_input = QLineEdit(self)
        self.patronymic_input.setValidator(validator)
        form_layout.addRow(self.texts["patronymic"], self.patronymic_input)

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(self)
        save_button = button_box.addButton(self.texts["save"], QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = button_box.addButton(self.texts["cancel"], QDialogButtonBox.ButtonRole.RejectRole)
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        main_layout.addWidget(button_box)

    def get_card_input(self) -> tuple[str, str, str]:
        return (
            self.surname_input.text(),
            self.name_input.text(),
            self.patronymic_input.text(),
        )