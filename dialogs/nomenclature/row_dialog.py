from PySide6.QtWidgets import QComboBox, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout

from ..base_dialog import CenteredDialog


class NomenclatureRowDialog(CenteredDialog):
    """Діалог створення або редагування рядка номенклатури."""

    def __init__(self, texts: dict, structure_options: list[tuple[int, str]], current_record=None, parent=None):
        super().__init__(parent)
        self.texts = texts
        self.structure_options = structure_options
        self.current_record = current_record
        self.is_edit_mode = current_record is not None
        self.setWindowTitle(self.texts["edit_title"] if self.is_edit_mode else self.texts["add_title"])
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.structure_unit_input = QComboBox(self)
        for unit_id, label in self.structure_options:
            self.structure_unit_input.addItem(label, unit_id)
        if self.current_record is not None:
            current_index = self.structure_unit_input.findData(self.current_record.structure_unit_id)
            self.structure_unit_input.setCurrentIndex(max(0, current_index))
        form_layout.addRow(self.texts["structure_unit"], self.structure_unit_input)

        self.job_title_input = QLineEdit(self.current_record.job_title if self.is_edit_mode else "", self)
        form_layout.addRow(self.texts["job_title"], self.job_title_input)

        self.nomenclature_number_input = QLineEdit(self.current_record.nomenclature_number if self.is_edit_mode else "", self)
        form_layout.addRow(self.texts["nomenclature_number"], self.nomenclature_number_input)

        self.admission_form_input = QComboBox(self)
        for option in self.texts["admission_form_options"]:
            self.admission_form_input.addItem(option, option)
        if self.current_record is not None:
            current_index = self.admission_form_input.findData(self.current_record.admission_form)
            self.admission_form_input.setCurrentIndex(max(0, current_index))
        else:
            default_value = self.texts.get("default_admission_form", "Ф-2")
            default_index = self.admission_form_input.findData(default_value)
            self.admission_form_input.setCurrentIndex(max(0, default_index))
        form_layout.addRow(self.texts["admission_form"], self.admission_form_input)

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(self)
        save_button = button_box.addButton(self.texts["save"], QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = button_box.addButton(self.texts["cancel"], QDialogButtonBox.ButtonRole.RejectRole)
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        main_layout.addWidget(button_box)

    def get_input(self) -> tuple[int, str, str, str]:
        return (
            int(self.structure_unit_input.currentData()),
            self.job_title_input.text(),
            self.nomenclature_number_input.text(),
            self.admission_form_input.currentData(),
        )