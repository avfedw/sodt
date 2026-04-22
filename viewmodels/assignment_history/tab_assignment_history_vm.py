"""ViewModel для вкладки історії призначень."""

from dataclasses import dataclass

from db import NomenclatureRepository, StructureRepository


@dataclass(slots=True)
class AssignmentHistoryRowView:
    """Підготовлений для таблиці рядок історії призначень."""

    history_id: int
    short_name_chain: str
    job_title: str
    surname: str
    name_patronymic: str
    appointment_order_number: str
    appointment_order_date: str


class TabAssignmentHistoryViewModel:
    """Постачає дані та фільтрацію для вкладки історії призначень."""

    def __init__(
        self,
        nomenclature_repository: NomenclatureRepository | None = None,
        structure_repository: StructureRepository | None = None,
    ):
        self.repository = nomenclature_repository or NomenclatureRepository()
        self.structure_repository = structure_repository or StructureRepository()
        self._load_texts()

    def _load_texts(self) -> None:
        try:
            from locales import (
                get_tab_assignment_history_empty_state_text,
                get_tab_assignment_history_headers,
                get_tab_assignment_history_name,
                get_tab_assignment_history_person_filter_placeholder,
                get_tab_assignment_history_position_filter_placeholder,
                get_tab_assignment_history_refresh_button_text,
            )

            self.title = get_tab_assignment_history_name()
            self.refresh_button_text = get_tab_assignment_history_refresh_button_text()
            self.empty_state_text = get_tab_assignment_history_empty_state_text()
            self.position_filter_placeholder = get_tab_assignment_history_position_filter_placeholder()
            self.person_filter_placeholder = get_tab_assignment_history_person_filter_placeholder()
            self.headers = get_tab_assignment_history_headers()
        except Exception:
            self.title = "Assignment history"
            self.refresh_button_text = "Refresh"
            self.empty_state_text = "Assignment history is empty."
            self.position_filter_placeholder = "Filter by position"
            self.person_filter_placeholder = "Filter by person"
            self.headers = [
                "Short name",
                "Job title",
                "Surname",
                "Name and patronymic",
                "Appointment order number",
                "Appointment order date",
            ]

    def get_rows(self, position_filter: str = "", person_filter: str = "") -> list[AssignmentHistoryRowView]:
        unit_by_id = {unit.unit_id: unit for unit in self.structure_repository.list_units()}
        normalized_position_filter = position_filter.strip().casefold()
        normalized_person_filter = person_filter.strip().casefold()
        rows: list[AssignmentHistoryRowView] = []

        for record in self.repository.list_assignment_history():
            row = AssignmentHistoryRowView(
                history_id=record.history_id,
                short_name_chain=self._short_name_chain(record.structure_unit_id, unit_by_id),
                job_title=record.job_title,
                surname=record.surname,
                name_patronymic=record.name_patronymic,
                appointment_order_number=record.appointment_order_number,
                appointment_order_date=record.appointment_order_date,
            )
            if not self._matches_filters(row, normalized_position_filter, normalized_person_filter):
                continue
            rows.append(row)

        return rows

    def _matches_filters(
        self,
        row: AssignmentHistoryRowView,
        normalized_position_filter: str,
        normalized_person_filter: str,
    ) -> bool:
        if normalized_position_filter:
            position_haystack = f"{row.short_name_chain} {row.job_title}".strip().casefold()
            if normalized_position_filter not in position_haystack:
                return False

        if normalized_person_filter:
            person_haystack = f"{row.surname} {row.name_patronymic}".strip().casefold()
            if normalized_person_filter not in person_haystack:
                return False

        return True

    def _short_name_chain(self, unit_id: int, unit_by_id: dict[int, object]) -> str:
        parts: list[str] = []
        current_unit = unit_by_id.get(unit_id)
        visited: set[int] = set()
        while current_unit is not None and current_unit.unit_id not in visited:
            visited.add(current_unit.unit_id)
            if current_unit.unit_type != "section":
                short_name = current_unit.short_name.strip() or current_unit.name.strip()
                if short_name:
                    parts.append(short_name)
            if current_unit.parent_id is None:
                break
            current_unit = unit_by_id.get(current_unit.parent_id)
        return " ".join(parts)
