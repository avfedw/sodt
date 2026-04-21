from PySide6.QtWidgets import QComboBox, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout

from ..base_dialog import CenteredDialog


class StructureUnitDialog(CenteredDialog):
    """Діалог створення або редагування організаційної одиниці."""

    def __init__(self, texts: dict, unit_type_options: list[tuple[str, str]], units: list, current_unit=None, initial_parent_id: int | None = None, initial_unit_type: str | None = None, parent=None):
        super().__init__(parent)
        self.texts = texts
        self.unit_type_options = unit_type_options
        self.units = units
        self.current_unit = current_unit
        self.initial_parent_id = initial_parent_id
        self.initial_unit_type = initial_unit_type
        self.is_edit_mode = current_unit is not None
        self._current_parent_id = current_unit.parent_id if current_unit is not None else initial_parent_id
        self.setWindowTitle(self.texts["edit_title"] if self.is_edit_mode else self.texts["add_title"])
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit(self.current_unit.name if self.is_edit_mode else "", self)
        form_layout.addRow(self.texts["name"], self.name_input)

        self.short_name_input = QLineEdit(self.current_unit.short_name if self.is_edit_mode else "", self)
        form_layout.addRow(self.texts["short_name"], self.short_name_input)

        self.unit_type_input = QComboBox(self)
        for unit_type, label in self.unit_type_options:
            self.unit_type_input.addItem(label, unit_type)
        if self.current_unit is not None:
            current_index = self.unit_type_input.findData(self.current_unit.unit_type)
            self.unit_type_input.setCurrentIndex(max(0, current_index))
        elif self.initial_unit_type is not None:
            current_index = self.unit_type_input.findData(self.initial_unit_type)
            self.unit_type_input.setCurrentIndex(max(0, current_index))
        self.unit_type_input.currentIndexChanged.connect(self._rebuild_parent_options)
        form_layout.addRow(self.texts["unit_type"], self.unit_type_input)

        self.parent_input = QComboBox(self)
        form_layout.addRow(self.texts["parent"], self.parent_input)
        self._rebuild_parent_options()

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(self)
        save_button = button_box.addButton(self.texts["save"], QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = button_box.addButton(self.texts["cancel"], QDialogButtonBox.ButtonRole.RejectRole)
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        main_layout.addWidget(button_box)

    def _rebuild_parent_options(self):
        selected_type = self.unit_type_input.currentData()
        selected_parent_id = self.parent_input.currentData() if self.parent_input.count() else self._current_parent_id
        self.parent_input.blockSignals(True)
        self.parent_input.clear()
        self.parent_input.addItem(self.texts["no_parent"], None)

        for unit in self._parent_candidates_for(selected_type):
            self.parent_input.addItem(self._parent_option_label(unit), unit.unit_id)

        restored_index = self.parent_input.findData(selected_parent_id)
        self.parent_input.setCurrentIndex(max(0, restored_index))
        self.parent_input.blockSignals(False)

    def _parent_candidates_for(self, unit_type: str):
        unit_type_rank = self._unit_type_rank(unit_type)
        excluded_ids = self._excluded_unit_ids()
        candidates = [
            unit
            for unit in self.units
            if unit.unit_id not in excluded_ids and self._unit_type_rank(unit.unit_type) < unit_type_rank
        ]
        return sorted(candidates, key=lambda unit: (self._unit_type_rank(unit.unit_type), unit.name.casefold(), unit.unit_id))

    def _excluded_unit_ids(self) -> set[int]:
        if self.current_unit is None:
            return set()

        excluded_ids = {self.current_unit.unit_id}
        child_map: dict[int | None, list[int]] = {}
        for unit in self.units:
            child_map.setdefault(unit.parent_id, []).append(unit.unit_id)

        pending = [self.current_unit.unit_id]
        while pending:
            current_id = pending.pop()
            for child_id in child_map.get(current_id, []):
                if child_id in excluded_ids:
                    continue
                excluded_ids.add(child_id)
                pending.append(child_id)

        return excluded_ids

    def _unit_type_rank(self, unit_type: str) -> int:
        for index, (code, _label) in enumerate(self.unit_type_options):
            if code == unit_type:
                return index
        return len(self.unit_type_options)

    def _parent_option_label(self, unit) -> str:
        label_by_type = {code: label for code, label in self.unit_type_options}
        return f"{label_by_type.get(unit.unit_type, unit.unit_type)}: {unit.name}"

    def get_input(self) -> tuple[str, str, str, int | None]:
        return (
            self.name_input.text(),
            self.short_name_input.text(),
            self.unit_type_input.currentData(),
            self.parent_input.currentData(),
        )
