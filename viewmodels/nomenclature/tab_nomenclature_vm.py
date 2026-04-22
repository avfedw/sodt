"""ViewModel для вкладки номенклатури."""

from dataclasses import dataclass
from datetime import date, datetime

from db import CardsRepository, NomenclatureRepository, StructureRepository


@dataclass(slots=True)
class NomenclatureRowView:
    """Підготовлений для таблиці рядок номенклатури."""

    row_id: int
    structure_unit_id: int
    card_id: int | None
    status: str
    short_name_chain: str
    job_title: str
    nomenclature_number: str
    admission_form: str
    surname: str
    name_patronymic: str
    appointment_order_number: str
    appointment_order_date: str
    vacancy_order_number: str
    highlight_style: str
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
        self._ensure_initial_row_order()

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
                get_tab_nomenclature_refresh_button_text,
                get_tab_nomenclature_validation_error_title,
            )

            self.title = get_tab_nomenclature_name()
            self.add_button_text = get_tab_nomenclature_add_button_text()
            self.refresh_button_text = get_tab_nomenclature_refresh_button_text()
            self.edit_button_text = get_tab_nomenclature_edit_button_text()
            self.empty_state_text = get_tab_nomenclature_empty_state_text()
            self.headers = get_tab_nomenclature_headers()
            self.validation_error_title = get_tab_nomenclature_validation_error_title()
            self.dialog_texts = get_tab_nomenclature_dialog_texts()
            self.card_picker_texts = get_tab_nomenclature_card_picker_texts()
        except Exception:
            self.title = "Nomenclature"
            self.add_button_text = "Add row"
            self.refresh_button_text = "Refresh"
            self.edit_button_text = "Edit"
            self.empty_state_text = "No nomenclature records have been added yet."
            self.headers = [
                "Status",
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
                "Appointment order number",
                "Appointment order date",
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
                "default_admission_form": "F-2",
                "surname": "Surname",
                "name_patronymic": "Name and patronymic",
                "appointment_order_number": "Appointment order number",
                "appointment_order_date": "Appointment order date",
                "empty_date": "Not specified",
                "save": "Save",
                "cancel": "Cancel",
                "select_row_warning": "Select a nomenclature row first.",
            }
            self.card_picker_texts = {
                "title": "Choose person from cards",
                "headers": ["Surname", "Name", "Patronymic", "Form", "Status"],
                "appointment_order_number": "Appointment order number",
                "appointment_order_date": "Appointment order date",
                "empty_date": "Not specified",
                "select": "Select",
                "vacant": "Vacant position",
                "vacancy_order_number_title": "Vacant position",
                "vacancy_order_number_label": "Position surrender order number",
                "cancel": "Cancel",
                "select_card_warning": "Select a person from cards first.",
            }

    def get_rows(self) -> list[NomenclatureRowView]:
        rows = self.repository.list_rows()
        unit_by_id = self._unit_by_id()
        cards = self.cards_repository.list_cards()
        card_by_id = {card.card_id: card for card in cards}
        card_by_name = {
            self._card_name_key(card.surname, f"{card.name} {card.patronymic}".strip()): card
            for card in cards
            if card.is_current
        }
        admissions_by_card_id = {
            card.card_id: self.cards_repository.list_admissions(card.card_id)
            for card in cards
        }

        return [
            self._build_row_view(row, unit_by_id, card_by_id, card_by_name, admissions_by_card_id)
            for row in rows
        ]

    def create_row(
        self,
        structure_unit_id: int,
        job_title: str,
        nomenclature_number: str,
        admission_form: str,
        surname: str = "",
        name_patronymic: str = "",
    ):
        record = self.repository.create_row(
            structure_unit_id,
            job_title,
            nomenclature_number,
            admission_form,
            surname,
            name_patronymic,
        )
        self._place_row_by_structure_order(record.row_id)
        return record

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
        previous_rows = self.repository.list_rows()
        previous_row = next((row for row in previous_rows if row.row_id == row_id), None)
        record = self.repository.update_row(
            row_id,
            structure_unit_id,
            job_title,
            nomenclature_number,
            admission_form,
            surname,
            name_patronymic,
        )
        if previous_row is not None and previous_row.structure_unit_id != structure_unit_id:
            self._place_row_by_structure_order(record.row_id)
        return record

    def save_row_order(self, row_ids: list[int]) -> None:
        self.repository.save_row_order(row_ids)

    def assign_card_to_row(self, row_id: int, card_id: int, appointment_order_number: str, appointment_order_date: str):
        cards = self.cards_repository.list_cards()
        for card in cards:
            if card.card_id != card_id:
                continue
            return self.repository.update_person(
                row_id,
                card.card_id,
                card.surname,
                f"{card.name} {card.patronymic}".strip(),
                appointment_order_number,
                appointment_order_date,
            )
        raise ValueError("Картку не знайдено.")

    def clear_person_from_row(self, row_id: int, vacancy_order_number: str):
        return self.repository.clear_person(row_id, vacancy_order_number)

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

    def _ensure_initial_row_order(self) -> None:
        rows = self.repository.list_rows()
        if not rows or all(row.sort_order is not None for row in rows):
            return

        unit_by_id = self._unit_by_id()
        ordered_rows = self._rows_in_structure_order(rows, unit_by_id)
        self.repository.save_row_order([row.row_id for row in ordered_rows])

    def _append_structure_options(self, options: list[tuple[int, str]], children_by_parent: dict[int | None, list], unit_by_id: dict[int, object], parent_id: int | None, depth: int):
        for unit in children_by_parent.get(parent_id, []):
            prefix = "    " * depth
            path = self._short_name_chain(unit.unit_id, unit_by_id)
            label = f"{prefix}{path} | {unit.name}" if path else f"{prefix}{unit.name}"
            options.append((unit.unit_id, label))
            self._append_structure_options(options, children_by_parent, unit_by_id, unit.unit_id, depth + 1)

    def _build_row_view(
        self,
        row,
        unit_by_id: dict[int, object],
        card_by_id: dict[int, object],
        card_by_name: dict[tuple[str, str], object],
        admissions_by_card_id: dict[int, list],
    ) -> NomenclatureRowView:
        path = self._structure_path(row.structure_unit_id, unit_by_id)
        assigned_card = self._resolve_assigned_card(row, card_by_id, card_by_name)
        return NomenclatureRowView(
            row_id=row.row_id,
            structure_unit_id=row.structure_unit_id,
            card_id=assigned_card.card_id if assigned_card is not None else row.card_id,
            status=self._build_status(row, assigned_card, admissions_by_card_id.get(assigned_card.card_id, []) if assigned_card is not None else []),
            short_name_chain=self._short_name_chain(row.structure_unit_id, unit_by_id),
            job_title=row.job_title,
            nomenclature_number=row.nomenclature_number,
            admission_form=row.admission_form,
            surname=row.surname,
            name_patronymic=row.name_patronymic,
            appointment_order_number=row.appointment_order_number,
            appointment_order_date=row.appointment_order_date,
            vacancy_order_number=row.vacancy_order_number,
            highlight_style=self._build_highlight_style(row, assigned_card, admissions_by_card_id.get(assigned_card.card_id, []) if assigned_card is not None else []),
            section_name=path.get("section", ""),
            group_name=path.get("group", ""),
            department_name=path.get("department", ""),
            division_name=path.get("division", ""),
            radio_station_name=path.get("radio_station", ""),
        )

    def _resolve_assigned_card(self, row, card_by_id: dict[int, object], card_by_name: dict[tuple[str, str], object]):
        if row.card_id is not None:
            card = card_by_id.get(row.card_id)
            if card is not None:
                return card

        if not row.surname and not row.name_patronymic:
            return None

        return card_by_name.get(self._card_name_key(row.surname, row.name_patronymic))

    def _build_status(self, row, assigned_card, admissions: list) -> str:
        if assigned_card is None:
            return "ВАКАНТ"

        if self._has_pending_security_service_review(admissions):
            return "СБУ"

        if self._is_form_missing_or_lower(assigned_card.form, row.admission_form):
            return "ОФ"

        if not getattr(assigned_card, "has_zalik", False):
            return "залік"

        return ""

    def _build_highlight_style(self, row, assigned_card, admissions: list) -> str:
        status = self._build_status(row, assigned_card, admissions)
        if status != "ОФ":
            return ""

        overdue_days = self._appointment_overdue_days(row.appointment_order_date)
        if overdue_days is None:
            return ""
        if overdue_days > 30:
            return "critical"
        if overdue_days > 10:
            return "warning"
        return ""

    def _card_name_key(self, surname: str, name_patronymic: str) -> tuple[str, str]:
        return (surname.strip().casefold(), " ".join(name_patronymic.strip().split()).casefold())

    def _has_pending_security_service_review(self, admissions: list) -> bool:
        for admission in admissions:
            has_escort = bool(admission.escort_number and admission.escort_date)
            missing_response = not (admission.response_number and admission.response_date)
            missing_order = not (admission.order_number and admission.order_date)
            if has_escort and (missing_response or missing_order):
                return True
        return False

    def _is_form_missing_or_lower(self, actual_form: str, required_form: str) -> bool:
        actual_level = self._admission_form_level(actual_form)
        required_level = self._admission_form_level(required_form)
        if required_level is None:
            return False
        if actual_level is None:
            return True
        return actual_level < required_level

    def _admission_form_level(self, value: str) -> int | None:
        normalized_value = value.strip().upper().replace("Ф", "F")
        if normalized_value in {"F-1", "F-2", "F-3"}:
            return int(normalized_value[-1])
        return None

    def _appointment_overdue_days(self, value: str) -> int | None:
        normalized_value = value.strip()
        if not normalized_value:
            return None

        try:
            appointment_date = datetime.strptime(normalized_value, "%d.%m.%Y").date()
        except ValueError:
            return None

        return (date.today() - appointment_date).days

    def _place_row_by_structure_order(self, row_id: int) -> None:
        rows = self.repository.list_rows()
        unit_by_id = self._unit_by_id()
        row_by_id = {row.row_id: row for row in rows}
        target_row = row_by_id.get(row_id)
        if target_row is None:
            return

        remaining_rows = [row for row in rows if row.row_id != row_id]
        target_key = self._row_structure_sort_key(target_row, unit_by_id)
        insert_index = len(remaining_rows)
        for index, row in enumerate(remaining_rows):
            if self._row_structure_sort_key(row, unit_by_id) > target_key:
                insert_index = index
                break

        remaining_rows.insert(insert_index, target_row)
        self.repository.save_row_order([row.row_id for row in remaining_rows])

    def _unit_by_id(self) -> dict[int, object]:
        return {unit.unit_id: unit for unit in self.structure_repository.list_units()}

    def _rows_in_structure_order(self, rows: list, unit_by_id: dict[int, object]) -> list:
        return sorted(rows, key=lambda row: self._row_structure_sort_key(row, unit_by_id))

    def _row_structure_sort_key(self, row, unit_by_id: dict[int, object]) -> tuple:
        return self._structure_order_key(row.structure_unit_id, unit_by_id) + (row.row_id,)

    def _structure_order_key(self, unit_id: int, unit_by_id: dict[int, object]) -> tuple[int, ...]:
        key_parts: list[int] = []
        path = []
        current_id = unit_id
        while current_id is not None and current_id in unit_by_id:
            unit = unit_by_id[current_id]
            path.append(unit)
            current_id = unit.parent_id

        for unit in reversed(path):
            key_parts.extend((unit.sort_order, unit.unit_id))
        return tuple(key_parts)

    def _short_name_chain(self, unit_id: int, unit_by_id: dict[int, object]) -> str:
        chain: list[str] = []
        current_id = unit_id
        while current_id is not None and current_id in unit_by_id:
            unit = unit_by_id[current_id]
            if unit.unit_type != "section":
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