from PySide6.QtCore import QDate
from PySide6.QtWidgets import QCheckBox, QComboBox, QDateEdit, QDialogButtonBox, QFormLayout, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from .base_dialog import CenteredDialog


class AccessDialog(CenteredDialog):
    """Діалог додавання або редагування запису доступу."""

    def __init__(self, texts: dict, access_record=None, parent=None):
        super().__init__(parent)
        self.texts = texts
        self.access_record = access_record
        self.is_edit_mode = access_record is not None
        self.setWindowTitle(self.texts["edit_title"] if self.is_edit_mode else self.texts["add_title"])
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.access_date_input = QDateEdit(self)
        self.access_date_input.setCalendarPopup(True)
        self.access_date_input.setDisplayFormat("dd.MM.yyyy")
        if self.is_edit_mode and self.access_record.access_date:
            self.access_date_input.setDate(QDate.fromString(self.access_record.access_date, "dd.MM.yyyy"))
        else:
            self.access_date_input.setDate(QDate.currentDate())
        form_layout.addRow(self.texts["access_date"], self.access_date_input)

        self.order_number_input = QLineEdit(self.access_record.order_number if self.is_edit_mode else "", self)
        form_layout.addRow(self.texts["order_number"], self.order_number_input)

        self.access_type_inputs = {}
        access_type_widget = QWidget(self)
        access_type_layout = QHBoxLayout(access_type_widget)
        access_type_layout.setContentsMargins(0, 0, 0, 0)
        selected_types = self._selected_access_types(self.access_record.access_type if self.is_edit_mode else "")
        for option in self.texts["access_type_options"]:
            checkbox = QCheckBox(option, access_type_widget)
            checkbox.setChecked(option in selected_types)
            checkbox.checkStateChanged.connect(self._sync_access_type_inputs)
            access_type_layout.addWidget(checkbox)
            self.access_type_inputs[option] = checkbox
        access_type_layout.addStretch(1)
        form_layout.addRow(self.texts["access_type"], access_type_widget)

        self.status_input = QComboBox(self)
        self.status_input.addItems(self.texts["status_options"])
        if self.is_edit_mode:
            current_index = self.status_input.findText(self.access_record.status)
            self.status_input.setCurrentIndex(max(0, current_index))
        form_layout.addRow(self.texts["status"], self.status_input)

        self._sync_access_type_inputs()

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(self)
        save_button = button_box.addButton(self.texts["save"], QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = button_box.addButton(self.texts["cancel"], QDialogButtonBox.ButtonRole.RejectRole)
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        main_layout.addWidget(button_box)

    def _selected_access_types(self, value: str) -> set[str]:
        return {item.strip() for item in value.split(",") if item.strip()}

    def _sync_access_type_inputs(self, _state: int | None = None):
        has_ov = self.access_type_inputs["ОВ"].isChecked()
        has_ct = self.access_type_inputs["ЦТ"].isChecked()
        has_t = self.access_type_inputs["Т"].isChecked()

        if has_ov:
            self.access_type_inputs["ЦТ"].setChecked(True)
            self.access_type_inputs["Т"].setChecked(True)
            return

        if has_ct:
            self.access_type_inputs["Т"].setChecked(True)
            return

        if not has_t:
            self.access_type_inputs["ОВ"].setChecked(False)
            self.access_type_inputs["ЦТ"].setChecked(False)

    def _access_type_value(self) -> str:
        if self.access_type_inputs["ОВ"].isChecked():
            return "ОВ,ЦТ,Т"
        if self.access_type_inputs["ЦТ"].isChecked():
            return "ЦТ,Т"
        if self.access_type_inputs["Т"].isChecked():
            return "Т"
        return ""

    def get_input(self) -> tuple[str, str, str, str]:
        return (
            self.access_date_input.date().toString("dd.MM.yyyy"),
            self.order_number_input.text(),
            self._access_type_value(),
            self.status_input.currentText(),
        )