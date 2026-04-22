"""Робота з рядками номенклатури у SQLite."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3


@dataclass(slots=True)
class NomenclatureRecord:
    """Один запис номенклатури."""

    row_id: int
    structure_unit_id: int
    card_id: int | None
    job_title: str
    nomenclature_number: str
    admission_form: str
    surname: str
    name_patronymic: str
    appointment_order_number: str
    appointment_order_date: str
    vacancy_order_number: str
    sort_order: int | None


@dataclass(slots=True)
class AssignmentHistoryRecord:
    """Один запис історії призначення на посаду."""

    history_id: int
    row_id: int
    structure_unit_id: int
    card_id: int | None
    job_title: str
    surname: str
    name_patronymic: str
    appointment_order_number: str
    appointment_order_date: str


class NomenclatureRepository:
    """Репозиторій для збереження та читання рядків номенклатури."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or Path(__file__).resolve().parent / "sodt.sqlite3"
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            table_exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'nomenclature_rows'"
            ).fetchone()

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS nomenclature_rows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    structure_unit_id INTEGER NOT NULL,
                    card_id INTEGER NULL,
                    job_title TEXT NOT NULL DEFAULT '',
                    nomenclature_number TEXT NOT NULL DEFAULT '',
                    admission_form TEXT NOT NULL DEFAULT '',
                    surname TEXT NOT NULL DEFAULT '',
                    name_patronymic TEXT NOT NULL DEFAULT '',
                    appointment_order_number TEXT NOT NULL DEFAULT '',
                    appointment_order_date TEXT NOT NULL DEFAULT '',
                    vacancy_order_number TEXT NOT NULL DEFAULT '',
                    sort_order INTEGER NULL,
                    FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE SET NULL,
                    FOREIGN KEY(structure_unit_id) REFERENCES structure_units(id) ON DELETE RESTRICT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS nomenclature_assignment_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nomenclature_row_id INTEGER NOT NULL,
                    structure_unit_id INTEGER NOT NULL,
                    card_id INTEGER NULL,
                    job_title TEXT NOT NULL DEFAULT '',
                    surname TEXT NOT NULL DEFAULT '',
                    name_patronymic TEXT NOT NULL DEFAULT '',
                    appointment_order_number TEXT NOT NULL DEFAULT '',
                    appointment_order_date TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(nomenclature_row_id) REFERENCES nomenclature_rows(id) ON DELETE RESTRICT,
                    FOREIGN KEY(structure_unit_id) REFERENCES structure_units(id) ON DELETE RESTRICT,
                    FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE SET NULL
                )
                """
            )

            if table_exists is None:
                return

            columns = [row["name"] for row in connection.execute("PRAGMA table_info(nomenclature_rows)").fetchall()]
            if "sort_order" not in columns:
                connection.execute(
                    "ALTER TABLE nomenclature_rows ADD COLUMN sort_order INTEGER NULL"
                )
            if "card_id" not in columns:
                connection.execute(
                    "ALTER TABLE nomenclature_rows ADD COLUMN card_id INTEGER NULL"
                )
            if "appointment_order_number" not in columns:
                connection.execute(
                    "ALTER TABLE nomenclature_rows ADD COLUMN appointment_order_number TEXT NOT NULL DEFAULT ''"
                )
            if "appointment_order_date" not in columns:
                connection.execute(
                    "ALTER TABLE nomenclature_rows ADD COLUMN appointment_order_date TEXT NOT NULL DEFAULT ''"
                )
            if "vacancy_order_number" not in columns:
                connection.execute(
                    "ALTER TABLE nomenclature_rows ADD COLUMN vacancy_order_number TEXT NOT NULL DEFAULT ''"
                )

    def list_rows(self) -> list[NomenclatureRecord]:
        """Повертає всі записи номенклатури у збереженому порядку."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id,
                       structure_unit_id,
                      card_id,
                       job_title,
                       nomenclature_number,
                       admission_form,
                       surname,
                                             name_patronymic,
                                             appointment_order_number,
                                             appointment_order_date,
                                             vacancy_order_number,
                                             sort_order
                FROM nomenclature_rows
                  ORDER BY sort_order IS NULL, sort_order, id
                """
            ).fetchall()

        return [self._build_record(row) for row in rows]

    def create_row(
        self,
        structure_unit_id: int,
        job_title: str,
        nomenclature_number: str,
        admission_form: str,
        surname: str = "",
        name_patronymic: str = "",
    ) -> NomenclatureRecord:
        """Створює запис номенклатури після базової перевірки полів."""

        normalized_values = self._normalize_values(
            structure_unit_id,
            job_title,
            nomenclature_number,
            admission_form,
            surname,
            name_patronymic,
        )

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO nomenclature_rows (
                    structure_unit_id,
                    card_id,
                    job_title,
                    nomenclature_number,
                    admission_form,
                    surname,
                    name_patronymic,
                    appointment_order_number,
                    appointment_order_date,
                    vacancy_order_number,
                    sort_order
                ) VALUES (?, NULL, ?, ?, ?, ?, ?, '', '', '', NULL)
                """,
                normalized_values,
            )
            row = self._get_row_by_id(connection, cursor.lastrowid)

        return self._build_record(row)

    def update_row(
        self,
        row_id: int,
        structure_unit_id: int,
        job_title: str,
        nomenclature_number: str,
        admission_form: str,
        surname: str | None = None,
        name_patronymic: str | None = None,
    ) -> NomenclatureRecord:
        """Оновлює запис номенклатури."""

        with self._connect() as connection:
            current_row = self._get_row_by_id(connection, row_id)
            normalized_values = self._normalize_values(
                structure_unit_id,
                job_title,
                nomenclature_number,
                admission_form,
                current_row["surname"] if surname is None else surname,
                current_row["name_patronymic"] if name_patronymic is None else name_patronymic,
            )
            connection.execute(
                """
                UPDATE nomenclature_rows
                SET structure_unit_id = ?,
                    job_title = ?,
                    nomenclature_number = ?,
                    admission_form = ?,
                    surname = ?,
                    name_patronymic = ?
                WHERE id = ?
                """,
                (*normalized_values, row_id),
            )
            row = self._get_row_by_id(connection, row_id)

        return self._build_record(row)

    def update_person(
        self,
        row_id: int,
        card_id: int,
        surname: str,
        name_patronymic: str,
        appointment_order_number: str,
        appointment_order_date: str,
    ) -> NomenclatureRecord:
        """Оновлює в записі лише ПІБ людини, вибраної з карток."""

        normalized_card_id = int(card_id)
        if normalized_card_id <= 0:
            raise ValueError("Потрібно вибрати людину з карток.")
        normalized_surname = self._normalize_optional_text(surname)
        normalized_name_patronymic = self._normalize_optional_text(name_patronymic)
        if not normalized_surname or not normalized_name_patronymic:
            raise ValueError("Потрібно вибрати людину з карток.")
        normalized_appointment_order_number = self._normalize_text(
            appointment_order_number,
            "Номер наказу призначення не може бути порожнім.",
        )
        normalized_appointment_order_date = self._normalize_date_value(
            appointment_order_date,
            "Дата наказу призначення не може бути порожньою.",
        )

        with self._connect() as connection:
            current_row = self._get_row_by_id(connection, row_id)
            connection.execute(
                """
                UPDATE nomenclature_rows
                SET card_id = NULL,
                    surname = '',
                    name_patronymic = '',
                    appointment_order_number = '',
                    appointment_order_date = '',
                    vacancy_order_number = ?
                WHERE card_id = ? AND id != ?
                """,
                (
                    normalized_appointment_order_number,
                    normalized_card_id,
                    row_id,
                ),
            )
            connection.execute(
                """
                UPDATE nomenclature_rows
                SET card_id = ?,
                    surname = ?,
                    name_patronymic = ?,
                    appointment_order_number = ?,
                    appointment_order_date = ?,
                    vacancy_order_number = ''
                WHERE id = ?
                """,
                (
                    normalized_card_id,
                    normalized_surname,
                    normalized_name_patronymic,
                    normalized_appointment_order_number,
                    normalized_appointment_order_date,
                    row_id,
                ),
            )
            self._insert_assignment_history(
                connection,
                row_id=row_id,
                structure_unit_id=int(current_row["structure_unit_id"]),
                card_id=normalized_card_id,
                job_title=str(current_row["job_title"]),
                surname=normalized_surname,
                name_patronymic=normalized_name_patronymic,
                appointment_order_number=normalized_appointment_order_number,
                appointment_order_date=normalized_appointment_order_date,
            )
            row = self._get_row_by_id(connection, row_id)

        return self._build_record(row)

    def clear_person(self, row_id: int, vacancy_order_number: str) -> NomenclatureRecord:
        """Очищає призначену людину для вакансії."""

        normalized_vacancy_order_number = self._normalize_text(
            vacancy_order_number,
            "Номер наказу на здачу посади не може бути порожнім.",
        )

        with self._connect() as connection:
            self._get_row_by_id(connection, row_id)
            connection.execute(
                """
                UPDATE nomenclature_rows
                SET card_id = NULL,
                    surname = '',
                    name_patronymic = '',
                    appointment_order_number = '',
                    appointment_order_date = '',
                    vacancy_order_number = ?
                WHERE id = ?
                """,
                (normalized_vacancy_order_number, row_id),
            )
            row = self._get_row_by_id(connection, row_id)

        return self._build_record(row)

    def list_assignment_history(self) -> list[AssignmentHistoryRecord]:
        """Повертає журнал усіх призначень на посади."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id,
                       nomenclature_row_id,
                       structure_unit_id,
                       card_id,
                       job_title,
                       surname,
                       name_patronymic,
                       appointment_order_number,
                       appointment_order_date
                FROM nomenclature_assignment_history
                ORDER BY appointment_order_date DESC, id DESC
                """
            ).fetchall()

        return [self._build_assignment_history_record(row) for row in rows]

    def save_row_order(self, row_ids: list[int]) -> None:
        """Зберігає явний порядок рядків номенклатури."""

        normalized_ids = [int(row_id) for row_id in row_ids]
        if len(normalized_ids) != len(set(normalized_ids)):
            raise ValueError("Порядок номенклатури містить дублікати.")

        with self._connect() as connection:
            existing_rows = connection.execute("SELECT id FROM nomenclature_rows ORDER BY id").fetchall()
            existing_ids = [int(row["id"]) for row in existing_rows]
            if normalized_ids != existing_ids and set(normalized_ids) != set(existing_ids):
                raise ValueError("Не вдалося зберегти порядок номенклатури.")

            for sort_order, row_id in enumerate(normalized_ids):
                connection.execute(
                    "UPDATE nomenclature_rows SET sort_order = ? WHERE id = ?",
                    (sort_order, row_id),
                )

    def _normalize_values(
        self,
        structure_unit_id: int,
        job_title: str,
        nomenclature_number: str,
        admission_form: str,
        surname: str,
        name_patronymic: str,
    ) -> tuple[int, str, str, str, str, str]:
        if int(structure_unit_id) <= 0:
            raise ValueError("Потрібно вибрати одиницю структури.")

        normalized_job_title = self._normalize_text(job_title, "Найменування посади не може бути порожнім.")
        normalized_nomenclature_number = self._normalize_text(
            nomenclature_number,
            "Номер по номенклатурі не може бути порожнім.",
        )
        normalized_admission_form = self._normalize_text(admission_form, "Форма допуску не може бути порожньою.")
        normalized_surname = self._normalize_optional_text(surname)
        normalized_name_patronymic = self._normalize_optional_text(name_patronymic)
        return (
            int(structure_unit_id),
            normalized_job_title,
            normalized_nomenclature_number,
            normalized_admission_form,
            normalized_surname,
            normalized_name_patronymic,
        )

    def _normalize_text(self, value: str, empty_message: str) -> str:
        normalized_value = " ".join(value.strip().split())
        if not normalized_value:
            raise ValueError(empty_message)
        return normalized_value

    def _normalize_optional_text(self, value: str) -> str:
        return " ".join(value.strip().split())

    def _normalize_date_value(self, value: str, empty_message: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError(empty_message)

        try:
            return datetime.strptime(normalized_value, "%d.%m.%Y").strftime("%d.%m.%Y")
        except ValueError as error:
            raise ValueError("Дата наказу призначення має бути у форматі дд.мм.рррр.") from error

    def _get_row_by_id(self, connection: sqlite3.Connection, row_id: int) -> sqlite3.Row:
        row = connection.execute(
            """
            SELECT id,
                   structure_unit_id,
                     card_id,
                   job_title,
                   nomenclature_number,
                   admission_form,
                   surname,
                                     name_patronymic,
                                     appointment_order_number,
                                     appointment_order_date,
                                     vacancy_order_number,
                                     sort_order
            FROM nomenclature_rows
            WHERE id = ?
            """,
            (row_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Запис номенклатури не знайдено.")
        return row

    def _build_record(self, row: sqlite3.Row) -> NomenclatureRecord:
        return NomenclatureRecord(
            row_id=int(row["id"]),
            structure_unit_id=int(row["structure_unit_id"]),
            card_id=None if row["card_id"] is None else int(row["card_id"]),
            job_title=row["job_title"],
            nomenclature_number=row["nomenclature_number"],
            admission_form=row["admission_form"],
            surname=row["surname"],
            name_patronymic=row["name_patronymic"],
            appointment_order_number=row["appointment_order_number"],
            appointment_order_date=row["appointment_order_date"],
            vacancy_order_number=row["vacancy_order_number"],
            sort_order=None if row["sort_order"] is None else int(row["sort_order"]),
        )

    def _build_assignment_history_record(self, row: sqlite3.Row) -> AssignmentHistoryRecord:
        return AssignmentHistoryRecord(
            history_id=int(row["id"]),
            row_id=int(row["nomenclature_row_id"]),
            structure_unit_id=int(row["structure_unit_id"]),
            card_id=None if row["card_id"] is None else int(row["card_id"]),
            job_title=row["job_title"],
            surname=row["surname"],
            name_patronymic=row["name_patronymic"],
            appointment_order_number=row["appointment_order_number"],
            appointment_order_date=row["appointment_order_date"],
        )

    def _insert_assignment_history(
        self,
        connection: sqlite3.Connection,
        *,
        row_id: int,
        structure_unit_id: int,
        card_id: int,
        job_title: str,
        surname: str,
        name_patronymic: str,
        appointment_order_number: str,
        appointment_order_date: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO nomenclature_assignment_history (
                nomenclature_row_id,
                structure_unit_id,
                card_id,
                job_title,
                surname,
                name_patronymic,
                appointment_order_number,
                appointment_order_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row_id,
                structure_unit_id,
                card_id,
                job_title,
                surname,
                name_patronymic,
                appointment_order_number,
                appointment_order_date,
            ),
        )