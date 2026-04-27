"""Робота з записами довідки 14 у SQLite."""

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re
import sqlite3

from .database import connection_scope, get_database_path


_CERTIFICATE14_NUMBER_PATTERN = re.compile(r"\d+")


@dataclass(slots=True)
class Certificate14Record:
    """Один запис виданої довідки 14."""

    certificate_id: int
    card_id: int
    certificate_number: str
    certificate_date: str
    surname: str
    name: str
    patronymic: str
    expiration_date: str
    recipient_surname: str
    is_returned: bool
    note: str


class Certificate14Repository:
    """Репозиторій для збереження та читання довідок 14."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = get_database_path(db_path)
        self._ensure_schema()

    def _connect(self):
        return connection_scope(self.db_path)

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS certificate14_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER NOT NULL,
                    certificate_number TEXT NOT NULL DEFAULT '',
                    certificate_date TEXT NOT NULL DEFAULT '',
                    surname TEXT NOT NULL DEFAULT '',
                    name TEXT NOT NULL DEFAULT '',
                    patronymic TEXT NOT NULL DEFAULT '',
                    expiration_date TEXT NOT NULL DEFAULT '',
                    recipient_surname TEXT NOT NULL DEFAULT '',
                    is_returned INTEGER NOT NULL DEFAULT 0,
                    note TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE RESTRICT
                )
                """
            )

    def list_records(self) -> list[Certificate14Record]:
        """Повертає всі записи довідки 14 в порядку створення."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id,
                       card_id,
                       certificate_number,
                       certificate_date,
                       surname,
                       name,
                       patronymic,
                       expiration_date,
                       recipient_surname,
                       is_returned,
                       note
                FROM certificate14_records
                ORDER BY certificate_date DESC, id DESC
                """
            ).fetchall()

        return [self._build_record(row) for row in rows]

    def create_record(
        self,
        card_id: int,
        certificate_number: str,
        certificate_date: str,
        surname: str,
        name: str,
        patronymic: str,
        expiration_date: str,
        recipient_surname: str,
        note: str,
    ) -> Certificate14Record:
        """Створює новий запис довідки 14."""

        normalized_values = self._normalize_values(
            card_id,
            certificate_number,
            certificate_date,
            surname,
            name,
            patronymic,
            expiration_date,
            recipient_surname,
            True,
            note,
        )

        with self._connect() as connection:
            self._ensure_card_has_no_active_certificate(connection, normalized_values[0])
            certificate_number_value = normalized_values[1] or self._get_next_certificate_number(connection)
            cursor = connection.execute(
                """
                INSERT INTO certificate14_records (
                    card_id,
                    certificate_number,
                    certificate_date,
                    surname,
                    name,
                    patronymic,
                    expiration_date,
                    recipient_surname,
                    is_returned,
                    note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized_values[0],
                    certificate_number_value,
                    normalized_values[2],
                    normalized_values[3],
                    normalized_values[4],
                    normalized_values[5],
                    normalized_values[6],
                    normalized_values[7],
                    normalized_values[8],
                    normalized_values[9],
                ),
            )
            row = self._get_row_by_id(connection, cursor.lastrowid)

        return self._build_record(row)

    def update_record(
        self,
        certificate_id: int,
        certificate_number: str,
        certificate_date: str,
        expiration_date: str,
        recipient_surname: str,
        is_returned: bool,
        note: str,
    ) -> Certificate14Record:
        """Оновлює існуючий запис довідки 14."""

        with self._connect() as connection:
            current_row = self._get_row_by_id(connection, certificate_id)
            normalized_values = self._normalize_values(
                int(current_row["card_id"]),
                certificate_number,
                certificate_date,
                current_row["surname"],
                current_row["name"],
                current_row["patronymic"],
                expiration_date,
                recipient_surname,
                is_returned,
                note,
            )
            connection.execute(
                """
                UPDATE certificate14_records
                SET certificate_number = ?,
                    certificate_date = ?,
                    expiration_date = ?,
                    recipient_surname = ?,
                    is_returned = ?,
                    note = ?
                WHERE id = ?
                """,
                (
                    normalized_values[1],
                    normalized_values[2],
                    normalized_values[6],
                    normalized_values[7],
                    normalized_values[8],
                    normalized_values[9],
                    certificate_id,
                ),
            )
            row = self._get_row_by_id(connection, certificate_id)

        return self._build_record(row)

    def list_active_card_ids(self) -> set[int]:
        """Повертає картки, для яких є видана і не повернута довідка 14."""

        with self._connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT card_id FROM certificate14_records WHERE is_returned = 0"
            ).fetchall()
        return {int(row["card_id"]) for row in rows}

    def _normalize_values(
        self,
        card_id: int,
        certificate_number: str,
        certificate_date: str,
        surname: str,
        name: str,
        patronymic: str,
        expiration_date: str,
        recipient_surname: str,
        is_returned: bool,
        note: str,
    ) -> tuple[int, str, str, str, str, str, str, str, int, str]:
        normalized_card_id = int(card_id)
        if normalized_card_id <= 0:
            raise ValueError("Потрібно вибрати картку.")

        return (
            normalized_card_id,
            self._normalize_number(certificate_number),
            self._normalize_date(certificate_date, "Дата довідки не може бути порожньою."),
            self._normalize_text(surname, "Прізвище не може бути порожнім."),
            self._normalize_text(name, "Ім'я не може бути порожнім."),
            self._normalize_text(patronymic, "По батькові не може бути порожнім."),
            self._normalize_date(expiration_date, "Термін дії не може бути порожнім."),
            self._normalize_optional_text(recipient_surname),
            1 if is_returned else 0,
            "\n".join(part.rstrip() for part in note.strip().splitlines()),
        )

    def _normalize_number(self, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            return ""
        if not _CERTIFICATE14_NUMBER_PATTERN.fullmatch(normalized_value):
            raise ValueError("Номер довідки має містити лише цифри.")
        return str(int(normalized_value))

    def _normalize_text(self, value: str, error_text: str) -> str:
        normalized_value = " ".join(value.strip().split())
        if not normalized_value:
            raise ValueError(error_text)
        return normalized_value

    def _normalize_optional_text(self, value: str) -> str:
        return " ".join(value.strip().split())

    def _normalize_date(self, value: str, error_text: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError(error_text)
        try:
            datetime.strptime(normalized_value, "%d.%m.%Y")
        except ValueError as error:
            raise ValueError("Дата повинна бути у форматі ДД.ММ.РРРР.") from error
        return normalized_value

    def _ensure_card_has_no_active_certificate(self, connection: sqlite3.Connection, card_id: int) -> None:
        row = connection.execute(
            "SELECT 1 FROM certificate14_records WHERE card_id = ? AND is_returned = 0 LIMIT 1",
            (card_id,),
        ).fetchone()
        if row is not None:
            raise ValueError("Для цієї картки вже видано довідку 14 без позначки про повернення.")

    def _get_next_certificate_number(self, connection: sqlite3.Connection) -> str:
        row = connection.execute(
            """
            SELECT COALESCE(MAX(CAST(certificate_number AS INTEGER)), 0) AS max_number
            FROM certificate14_records
            WHERE TRIM(certificate_number) <> ''
              AND certificate_number GLOB '[0-9]*'
            """
        ).fetchone()
        return str(int(row["max_number"]) + 1)

    def _get_row_by_id(self, connection: sqlite3.Connection, certificate_id: int) -> sqlite3.Row:
        row = connection.execute(
            """
            SELECT id,
                   card_id,
                   certificate_number,
                   certificate_date,
                   surname,
                   name,
                   patronymic,
                   expiration_date,
                   recipient_surname,
                   is_returned,
                   note
            FROM certificate14_records
            WHERE id = ?
            """,
            (certificate_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Запис довідки 14 не знайдено.")
        return row

    def _build_record(self, row: sqlite3.Row) -> Certificate14Record:
        return Certificate14Record(
            certificate_id=int(row["id"]),
            card_id=int(row["card_id"]),
            certificate_number=row["certificate_number"],
            certificate_date=row["certificate_date"],
            surname=row["surname"],
            name=row["name"],
            patronymic=row["patronymic"],
            expiration_date=row["expiration_date"],
            recipient_surname=row["recipient_surname"],
            is_returned=bool(row["is_returned"]),
            note=row["note"],
        )


def default_expiration_date() -> str:
    """Повертає типовий термін дії: 31 грудня поточного року."""

    return date.today().replace(month=12, day=31).strftime("%d.%m.%Y")


def default_certificate_date() -> str:
    """Повертає поточну дату для нової довідки."""

    return date.today().strftime("%d.%m.%Y")