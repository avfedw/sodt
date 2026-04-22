"""ViewModel для вкладки структури підприємства."""

from db import StructureRepository


class TabStructureViewModel:
    """Координує тексти інтерфейсу вкладки структури та роботу з репозиторієм."""

    def __init__(self):
        self.repository = StructureRepository()
        self._load_texts()

    def _load_texts(self):
        try:
            from locales import (
                get_tab_structure_add_button_text,
                get_tab_structure_add_child_button_text,
                get_tab_structure_delete_button_text,
                get_tab_structure_dialog_texts,
                get_tab_structure_edit_button_text,
                get_tab_structure_empty_state_text,
                get_tab_structure_headers,
                get_tab_structure_name,
                get_tab_structure_type_labels,
                get_tab_structure_validation_error_title,
            )

            self.title = get_tab_structure_name()
            self.add_button_text = get_tab_structure_add_button_text()
            self.add_child_button_text = get_tab_structure_add_child_button_text()
            self.edit_button_text = get_tab_structure_edit_button_text()
            self.delete_button_text = get_tab_structure_delete_button_text()
            self.headers = get_tab_structure_headers()
            self.empty_state_text = get_tab_structure_empty_state_text()
            self.validation_error_title = get_tab_structure_validation_error_title()
            self.dialog_texts = get_tab_structure_dialog_texts()
            self.type_labels = get_tab_structure_type_labels()
        except Exception:
            self.title = "Structure"
            self.add_button_text = "Add unit"
            self.add_child_button_text = "Add child unit"
            self.edit_button_text = "Edit"
            self.delete_button_text = "Delete"
            self.headers = ["Name", "Short name", "Type"]
            self.empty_state_text = "Structure is empty."
            self.validation_error_title = "Validation error"
            self.dialog_texts = {
                "add_title": "Add organizational unit",
                "edit_title": "Edit organizational unit",
                "name": "Name",
                "short_name": "Short name",
                "unit_type": "Type",
                "parent": "Parent unit",
                "no_parent": "No parent unit",
                "save": "Save",
                "delete_button": "Delete",
                "cancel": "Cancel",
                "delete_confirmation_title": "Delete unit",
                "delete_confirmation_text": "Delete the selected unit?",
                "select_unit_warning": "Select an organizational unit first.",
                "no_child_type_warning": "The selected unit already has the lowest possible child level.",
            }
            self.type_labels = {
                "section": "Section",
                "group": "Group",
                "department": "Department",
                "division": "Division",
                "radio_station": "Radio station",
            }

    def get_units(self):
        return self.repository.list_units()

    def create_unit(self, name: str, short_name: str, unit_type: str, parent_id: int | None):
        return self.repository.create_unit(name, short_name, unit_type, parent_id)

    def update_unit(self, unit_id: int, name: str, short_name: str, unit_type: str, parent_id: int | None):
        return self.repository.update_unit(unit_id, name, short_name, unit_type, parent_id)

    def delete_unit(self, unit_id: int):
        self.repository.delete_unit(unit_id)

    def save_tree_order(self, units_tree: list[dict]) -> None:
        self.repository.save_tree_order(units_tree)

    def get_unit_type_codes(self) -> list[str]:
        return self.repository.unit_type_codes()

    def unit_type_options(self) -> list[tuple[str, str]]:
        return [(code, self.type_labels[code]) for code in self.get_unit_type_codes()]

    def unit_type_label(self, unit_type: str) -> str:
        return self.type_labels.get(unit_type, unit_type)

    def next_child_unit_type(self, parent_unit_type: str) -> str | None:
        unit_type_codes = self.get_unit_type_codes()
        try:
            parent_index = unit_type_codes.index(parent_unit_type)
        except ValueError:
            return None

        child_index = parent_index + 1
        if child_index >= len(unit_type_codes):
            return None
        return unit_type_codes[child_index]
