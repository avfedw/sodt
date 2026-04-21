"""Робота з рядками номенклатури у SQLite."""

from dataclasses import dataclass
from pathlib import Path
import sqlite3


@dataclass(slots=True)
class NomenclatureRecord:
    """Один запис номенклатури."""

    row_id: int
    structure_unit_id: int
    job_title: str
    nomenclature_number: str
    admission_form: str
    surname: str
    name_patronymic: str


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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS nomenclature_rows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    structure_unit_id INTEGER NOT NULL,
                    job_title TEXT NOT NULL DEFAULT '',
                    nomenclature_number TEXT NOT NULL DEFAULT '',
                    admission_form TEXT NOT NULL DEFAULT '',
                    surname TEXT NOT NULL DEFAULT '',
                    name_patronymic TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(structure_unit_id) REFERENCES structure_units(id) ON DELETE RESTRICT
                )
                """
            )

    def list_rows(self) -> list[NomenclatureRecord]:
        """Повертає всі записи номенклатури у порядку створення."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id,
                       structure_unit_id,
                       job_title,
                       nomenclature_number,
                       admission_form,
                       surname,
                       name_patronymic
                FROM nomenclature_rows
                ORDER BY id
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
                    job_title,
                    nomenclature_number,
                    admission_form,
                    surname,
                    name_patronymic
                ) VALUES (?, ?, ?, ?, ?, ?)
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

    def update_person(self, row_id: int, surname: str, name_patronymic: str) -> NomenclatureRecord:
        """Оновлює в записі лише ПІБ людини, вибраної з карток."""

        normalized_surname = self._normalize_optional_text(surname)
        normalized_name_patronymic = self._normalize_optional_text(name_patronymic)
        if not normalized_surname or not normalized_name_patronymic:
            raise ValueError("Потрібно вибрати людину з карток.")

        with self._connect() as connection:
            self._get_row_by_id(connection, row_id)
            connection.execute(
                "UPDATE nomenclature_rows SET surname = ?, name_patronymic = ? WHERE id = ?",
                (normalized_surname, normalized_name_patronymic, row_id),
            )
            row = self._get_row_by_id(connection, row_id)

        return self._build_record(row)

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

    def _get_row_by_id(self, connection: sqlite3.Connection, row_id: int) -> sqlite3.Row:
        row = connection.execute(
            """
            SELECT id,
                   structure_unit_id,
                   job_title,
                   nomenclature_number,
                   admission_form,
                   surname,
                   name_patronymic
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
            job_title=row["job_title"],
            nomenclature_number=row["nomenclature_number"],
            admission_form=row["admission_form"],
            surname=row["surname"],
            name_patronymic=row["name_patronymic"],
        )