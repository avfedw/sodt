"""ViewModel для вкладки номенклатури."""

from dataclasses import dataclass

from db import CardsRepository, NomenclatureRepository, StructureRepository


@dataclass(slots=True)
class NomenclatureRowView:
    """Підготовлений для таблиці рядок номенклатури."""

    row_id: int
    structure_unit_id: int
    short_name_chain: str
    job_title: str
    nomenclature_number: str
    admission_form: str
    surname: str
    name_patronymic: str
    section_name: str
    group_name: str
    department_name: str
    division_name: str
    radio_station_name: str


class TabNomenclatureViewModel:
    """Постачає локалізовані тексти для стартового інтерфейсу номенклатури."""

    def __init__(self, nomenclature_repository: NomenclatureRepository | None = None, structure_repository: StructureRepository | None = None, cards_repository: CardsRepository | None = None):
        self.repository = nomenclature_repository or NomenclatureRepository()
        self.structure_repository = structure_repository or StructureRepository()
        self.cards_repository = cards_repository or CardsRepository()
        self._load_texts()

    def _load_texts(self):
        try:
            from locales import (
                get_tab_nomenclature_add_button_text,
                get_tab_nomenclature_card_picker_texts,
                get_tab_nomenclature_dialog_texts,
                get_tab_nomenclature_edit_button_text,
                get_tab_nomenclature_empty_state_text,
                get_tab_nomenclature_headers,
                get_tab_nomenclature_name,
                get_tab_nomenclature_validation_error_title,
            )

            self.title = get_tab_nomenclature_name()
            self.add_button_text = get_tab_nomenclature_add_button_text()
            self.edit_button_text = get_tab_nomenclature_edit_button_text()
            self.empty_state_text = get_tab_nomenclature_empty_state_text()
            self.headers = get_tab_nomenclature_headers()
            self.validation_error_title = get_tab_nomenclature_validation_error_title()
            self.dialog_texts = get_tab_nomenclature_dialog_texts()
            self.card_picker_texts = get_tab_nomenclature_card_picker_texts()
        except Exception:
            self.title = "Nomenclature"
            self.add_button_text = "Add row"
            self.edit_button_text = "Edit"
            self.empty_state_text = "No nomenclature records have been added yet."
            self.headers = [
                "Short name",
                "Job title",
                "Nomenclature number",
                "Admission form",
                "Surname",
                "Name and patronymic",
                "Section",
                "Group",
                "Department",
                "Division",
                "Radio station",
            ]
            self.validation_error_title = "Validation error"
            self.dialog_texts = {
                "add_title": "Add nomenclature row",
                "edit_title": "Edit nomenclature row",
                "structure_unit": "Structure unit",
                "job_title": "Job title",
                "nomenclature_number": "Nomenclature number",
                "admission_form": "Admission form",
                "admission_form_options": ["F-1", "F-2", "F-3"],
                "surname": "Surname",
                "name_patronymic": "Name and patronymic",
                "save": "Save",
                "cancel": "Cancel",
                "select_row_warning": "Select a nomenclature row first.",
            }
            self.card_picker_texts = {
                "title": "Choose person from cards",
                "headers": ["Surname", "Name", "Patronymic", "Form", "Status"],
                "select": "Select",
                "cancel": "Cancel",
                "select_card_warning": "Select a person from cards first.",
            }

    def get_rows(self) -> list[NomenclatureRowView]:
        rows = self.repository.list_rows()
        units = self.structure_repository.list_units()
        unit_by_id = {unit.unit_id: unit for unit in units}

        return [self._build_row_view(row, unit_by_id) for row in rows]

    def create_row(
        self,
        structure_unit_id: int,
        job_title: str,
        nomenclature_number: str,
        admission_form: str,
        surname: str = "",
        name_patronymic: str = "",
    ):
        return self.repository.create_row(
            structure_unit_id,
            job_title,
            nomenclature_number,
            admission_form,
            surname,
            name_patronymic,
        )

    def update_row(
        self,
        row_id: int,
        structure_unit_id: int,
        job_title: str,
        nomenclature_number: str,
        admission_form: str,
        surname: str | None = None,
        name_patronymic: str | None = None,
    ):
        return self.repository.update_row(
            row_id,
            structure_unit_id,
            job_title,
            nomenclature_number,
            admission_form,
            surname,
            name_patronymic,
        )

    def assign_card_to_row(self, row_id: int, card_id: int):
        cards = self.cards_repository.list_cards()
        for card in cards:
            if card.card_id != card_id:
                continue
            return self.repository.update_person(
                row_id,
                card.surname,
                f"{card.name} {card.patronymic}".strip(),
            )
        raise ValueError("Картку не знайдено.")

    def card_options(self) -> list:
        cards = self.cards_repository.list_cards()
        return sorted(
            [card for card in cards if card.is_current and card.lifecycle_state != "destroyed"],
            key=lambda card: (card.surname.casefold(), card.name.casefold(), card.patronymic.casefold(), card.card_id),
        )

    def structure_unit_options(self) -> list[tuple[int, str]]:
        units = self.structure_repository.list_units()
        unit_by_id = {unit.unit_id: unit for unit in units}
        children_by_parent: dict[int | None, list] = {}
        for unit in units:
            children_by_parent.setdefault(unit.parent_id, []).append(unit)

        options: list[tuple[int, str]] = []
        self._append_structure_options(options, children_by_parent, unit_by_id, parent_id=None, depth=0)
        return options

    def _append_structure_options(self, options: list[tuple[int, str]], children_by_parent: dict[int | None, list], unit_by_id: dict[int, object], parent_id: int | None, depth: int):
        for unit in children_by_parent.get(parent_id, []):
            prefix = "    " * depth
            path = self._short_name_chain(unit.unit_id, unit_by_id)
            options.append((unit.unit_id, f"{prefix}{path} | {unit.name}"))
            self._append_structure_options(options, children_by_parent, unit_by_id, unit.unit_id, depth + 1)

    def _build_row_view(self, row, unit_by_id: dict[int, object]) -> NomenclatureRowView:
        path = self._structure_path(row.structure_unit_id, unit_by_id)
        return NomenclatureRowView(
            row_id=row.row_id,
            structure_unit_id=row.structure_unit_id,
            short_name_chain=self._short_name_chain(row.structure_unit_id, unit_by_id),
            job_title=row.job_title,
            nomenclature_number=row.nomenclature_number,
            admission_form=row.admission_form,
            surname=row.surname,
            name_patronymic=row.name_patronymic,
            section_name=path.get("section", ""),
            group_name=path.get("group", ""),
            department_name=path.get("department", ""),
            division_name=path.get("division", ""),
            radio_station_name=path.get("radio_station", ""),
        )

    def _short_name_chain(self, unit_id: int, unit_by_id: dict[int, object]) -> str:
        chain: list[str] = []
        current_id = unit_id
        while current_id is not None and current_id in unit_by_id:
            unit = unit_by_id[current_id]
            chain.append((unit.short_name or unit.name).strip())
            current_id = unit.parent_id
        return " ".join(chain)

    def _structure_path(self, unit_id: int, unit_by_id: dict[int, object]) -> dict[str, str]:
        path: dict[str, str] = {}
        current_id = unit_id
        while current_id is not None and current_id in unit_by_id:
            unit = unit_by_id[current_id]
            path[unit.unit_type] = unit.name
            current_id = unit.parent_id
        return path