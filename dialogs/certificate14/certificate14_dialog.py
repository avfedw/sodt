from PySide6.QtWidgets import QCheckBox, QDialogButtonBox, QFormLayout, QLineEdit, QTextEdit, QVBoxLayout

from dialogs.base_dialog import CenteredDialog
from dialogs.helpers import create_date_input, read_date_input_value


class Certificate14Dialog(CenteredDialog):
    """Діалог редагування довідки 14."""

    def __init__(self, texts: dict, full_name: str, current_record=None, parent=None):
        super().__init__(parent)
        self.texts = texts
        self.full_name = full_name
        self.current_record = current_record
        self.is_edit_mode = current_record is not None
        self.setWindowTitle(self.texts["edit_title"] if self.is_edit_mode else self.texts["add_title"])
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.certificate_number_input = QLineEdit(self.current_record.certificate_number if self.is_edit_mode else "", self)
        form_layout.addRow(self.texts["number"], self.certificate_number_input)

        self.certificate_date_input = create_date_input(self, self.current_record.certificate_date if self.is_edit_mode else "")
        form_layout.addRow(self.texts["certificate_date"], self.certificate_date_input)

        self.full_name_input = QLineEdit(self.full_name, self)
        self.full_name_input.setReadOnly(True)
        form_layout.addRow(self.texts["full_name"], self.full_name_input)

        self.expiration_date_input = create_date_input(self, self.current_record.expiration_date if self.is_edit_mode else "")
        form_layout.addRow(self.texts["expiration_date"], self.expiration_date_input)

        self.recipient_surname_input = QLineEdit(self.current_record.recipient_surname if self.is_edit_mode else "", self)
        form_layout.addRow(self.texts["recipient_surname"], self.recipient_surname_input)

        self.returned_input = QCheckBox(self.texts["returned"], self)
        self.returned_input.setChecked(self.current_record.is_returned if self.is_edit_mode else False)
        form_layout.addRow("", self.returned_input)

        self.note_input = QTextEdit(self)
        self.note_input.setPlainText(self.current_record.note if self.is_edit_mode else "")
        self.note_input.setMinimumHeight(90)
        form_layout.addRow(self.texts["note"], self.note_input)

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def get_input(self) -> tuple[str, str, str, str, bool, str]:
        return (
            self.certificate_number_input.text(),
            read_date_input_value(self.certificate_date_input),
            read_date_input_value(self.expiration_date_input),
            self.recipient_surname_input.text(),
            self.returned_input.isChecked(),
            self.note_input.toPlainText(),
        )