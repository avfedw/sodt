"""Робота з таблицею карток у SQLite."""

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re
import sqlite3


_UKRAINIAN_LETTERS = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
_UKRAINIAN_NAME_PATTERN = re.compile(rf"^[{_UKRAINIAN_LETTERS}'’ ]+$")
_UKRAINIAN_LETTER_PATTERN = re.compile(rf"[{_UKRAINIAN_LETTERS}]")
_CARD_NUMBER_PATTERN = re.compile(r"^[0-9]+$")
_DOCUMENT_KINDS = {"", "escort", "act", "planned_cancellation", "planned_destruction"}
_WORKFLOW_STATUSES = {"", "на скасування", "на знищення", "знищено", "відправлено"}
_LIFECYCLE_STATES = {"", "sent", "destroyed"}
_EXPECTED_CARD_COLUMNS = [
    "id",
    "letter",
    "number",
    "card_date",
    "surname",
    "name",
    "patronymic",
    "form",
    "workflow_status",
    "document_kind",
    "document_number",
    "document_date",
    "document_target",
    "service_note",
    "user_note",
    "relation_group_id",
    "is_current",
    "lifecycle_state",
]
_EXPECTED_ADMISSION_COLUMNS = [
    "id",
    "card_id",
    "escort_number",
    "escort_date",
    "response_number",
    "response_date",
    "order_number",
    "order_date",
    "admission_form",
    "admission_status",
]
_EXTENDED_ADMISSION_COLUMNS = [
    "id",
    "card_id",
    "escort_number",
    "escort_date",
    "response_number",
    "response_date",
    "order_number",
    "order_date",
    "admission_form",
    "admission_type",
    "admission_status",
]
_EXPECTED_ACCESS_COLUMNS = [
    "id",
    "card_id",
    "access_date",
    "order_number",
    "access_type",
    "status",
]
_ADMISSION_FORMS = {"", "Ф-1", "Ф-2", "Ф-3", "F-1", "F-2", "F-3"}
_ACCESS_TYPES = {"Т", "ЦТ,Т", "ОВ,ЦТ,Т"}
_ADMISSION_STATUSES = {"", "надано", "скасовано", "granted", "revoked"}


@dataclass(slots=True)
class CardRecord:
    """Модель одного запису картки з наскрізним ключем."""

    card_id: int
    letter: str
    number: str
    card_date: str
    surname: str
    name: str
    patronymic: str
    form: str
    workflow_status: str
    document_kind: str
    document_number: str
    document_date: str
    document_target: str
    service_note: str
    user_note: str
    relation_group_id: int
    is_current: bool
    lifecycle_state: str
    derived_workflow_status: str = ""
    has_active_admission: bool = False
    has_active_access: bool = False
    access_revoked_after_grant: bool = False
    access_revoked_date: str = ""
    admission_revoked_after_grant: bool = False
    admission_revoked_date: str = ""
    reissue_date: str = ""

    @property
    def note(self) -> str:
        """Повертає об'єднану примітку для відображення в таблиці."""

        note_parts = [part for part in (self.service_note, self.user_note) if part]
        return "\n".join(note_parts)

    @property
    def workflow_document(self) -> str:
        """Повертає багаторядковий опис документа або події для таблиці."""

        if self.document_kind == "escort":
            return "\n".join(
                value
                for value in (
                    f"№ супроводу {self.document_number}" if self.document_number else "",
                    self.document_date,
                    self.document_target,
                )
                if value
            )

        if self.document_kind == "act":
            return "\n".join(
                value
                for value in (
                    f"Акт знищення № {self.document_number}" if self.document_number else "",
                    self.document_date,
                )
                if value
            )

        if self.document_kind in {"planned_cancellation", "planned_destruction"}:
            return self.document_date

        return ""

    @property
    def can_edit(self) -> bool:
        """Ознака, що картка доступна для редагування."""

        return self.is_current and self.lifecycle_state == ""

    @property
    def can_return(self) -> bool:
        """Ознака, що картку можна позначити повернутою."""

        return self.lifecycle_state == "sent"

    @property
    def inactive_reason(self) -> str:
        """Повертає код причини неактивності картки."""

        if self.lifecycle_state == "destroyed":
            return "destroyed"
        if self.lifecycle_state == "sent":
            return "sent"
        if not self.is_current:
            return "surname_changed"
        return ""

    def visible_values(self) -> list[str]:
        """Повертає лише ті значення, що мають відображатися в таблиці."""

        card_code = f"{self.letter}-{self.number}" if self.letter and self.number else self.letter or self.number

        return [
            card_code,
            self.card_date,
            self.surname,
            self.name,
            self.patronymic,
            self.form,
            self.workflow_document,
            self.derived_workflow_status,
            self.note,
        ]


@dataclass(slots=True)
class AccessRecord:
    """Модель одного запису доступу для вибраної картки."""

    access_id: int
    card_id: int
    access_date: str
    order_number: str
    access_type: str
    status: str

    def visible_values(self) -> list[str]:
        """Повертає значення для таблиці доступу."""

        return [
            self.access_date,
            self.order_number,
            self.access_type,
            self.status,
        ]


@dataclass(slots=True)
class AdmissionRecord:
    """Модель одного запису розшифровки для вибраної картки."""

    admission_id: int
    card_id: int
    escort_number: str
    escort_date: str
    response_number: str
    response_date: str
    order_number: str
    order_date: str
    admission_form: str
    admission_status: str

    def visible_values(self) -> list[str]:
        """Повертає значення для нижньої таблиці."""

        return [
            self.escort_number,
            self.escort_date,
            self.response_number,
            self.response_date,
            self.order_number,
            self.order_date,
            self.admission_form,
            self.admission_status,
        ]


class CardsRepository:
    """Репозиторій для читання та підготовки таблиці карток."""

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
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'cards'"
            ).fetchone()

            if table_exists is not None:
                columns = [
                    row["name"]
                    for row in connection.execute("PRAGMA table_info(cards)").fetchall()
                ]
                if columns != _EXPECTED_CARD_COLUMNS:
                    connection.execute("DROP TABLE cards")

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    letter TEXT NOT NULL DEFAULT '',
                    number TEXT NOT NULL DEFAULT '',
                    card_date TEXT NOT NULL DEFAULT '',
                    surname TEXT NOT NULL DEFAULT '',
                    name TEXT NOT NULL DEFAULT '',
                    patronymic TEXT NOT NULL DEFAULT '',
                    form TEXT NOT NULL DEFAULT '',
                    workflow_status TEXT NOT NULL DEFAULT '',
                    document_kind TEXT NOT NULL DEFAULT '',
                    document_number TEXT NOT NULL DEFAULT '',
                    document_date TEXT NOT NULL DEFAULT '',
                    document_target TEXT NOT NULL DEFAULT '',
                    service_note TEXT NOT NULL DEFAULT '',
                    user_note TEXT NOT NULL DEFAULT '',
                    relation_group_id INTEGER NOT NULL DEFAULT 0,
                    is_current INTEGER NOT NULL DEFAULT 1,
                    lifecycle_state TEXT NOT NULL DEFAULT ''
                )
                """
            )

            admission_table_exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'admissions'"
            ).fetchone()

            if admission_table_exists is not None:
                admission_columns = [
                    row["name"]
                    for row in connection.execute("PRAGMA table_info(admissions)").fetchall()
                ]
                if (
                    admission_columns != _EXPECTED_ADMISSION_COLUMNS
                    and admission_columns != _EXTENDED_ADMISSION_COLUMNS
                ):
                    connection.execute("DROP TABLE admissions")

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS admissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER NOT NULL,
                    escort_number TEXT NOT NULL DEFAULT '',
                    escort_date TEXT NOT NULL DEFAULT '',
                    response_number TEXT NOT NULL DEFAULT '',
                    response_date TEXT NOT NULL DEFAULT '',
                    order_number TEXT NOT NULL DEFAULT '',
                    order_date TEXT NOT NULL DEFAULT '',
                    admission_form TEXT NOT NULL DEFAULT '',
                    admission_type TEXT NOT NULL DEFAULT '',
                    admission_status TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
                )
                """
            )

            access_table_exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'accesses'"
            ).fetchone()

            if access_table_exists is not None:
                access_columns = [
                    row["name"]
                    for row in connection.execute("PRAGMA table_info(accesses)").fetchall()
                ]
                if access_columns == ["id", "card_id", "access_date", "order_number", "status"]:
                    connection.execute(
                        "ALTER TABLE accesses ADD COLUMN access_type TEXT NOT NULL DEFAULT 'Т'"
                    )
                    connection.execute(
                        "UPDATE accesses SET access_type = 'Т' WHERE access_type = ''"
                    )
                    access_columns.append("access_type")
                if access_columns != _EXPECTED_ACCESS_COLUMNS:
                    connection.execute("DROP TABLE accesses")

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS accesses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER NOT NULL,
                    access_date TEXT NOT NULL DEFAULT '',
                    order_number TEXT NOT NULL DEFAULT '',
                    access_type TEXT NOT NULL DEFAULT 'Т',
                    status TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
                )
                """
            )

    def list_cards(self) -> list[CardRecord]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM cards ORDER BY id").fetchall()
            admission_rows = connection.execute(
                "SELECT id, card_id, admission_form, admission_status, order_date FROM admissions"
            ).fetchall()
            access_rows = connection.execute(
                "SELECT id, card_id, status, access_date FROM accesses"
            ).fetchall()

        admission_state_by_card_id = self._build_admission_state_by_card_id(admission_rows)
        access_state_by_card_id = self._build_access_state_by_card_id(access_rows)

        return [
            self._build_card_record_from_row(
                row,
                form_override=admission_state_by_card_id.get(row["id"], (row["form"], False, False, "", ""))[0],
                has_active_admission=admission_state_by_card_id.get(row["id"], (row["form"], False, False, "", ""))[1],
                admission_revoked_after_grant=admission_state_by_card_id.get(row["id"], (row["form"], False, False, "", ""))[2],
                admission_revoked_date=admission_state_by_card_id.get(row["id"], (row["form"], False, False, "", ""))[3],
                reissue_date=admission_state_by_card_id.get(row["id"], (row["form"], False, False, "", ""))[4],
                has_active_access=access_state_by_card_id.get(row["id"], (False, False, ""))[0],
                access_revoked_after_grant=access_state_by_card_id.get(row["id"], (False, False, ""))[1],
                access_revoked_date=access_state_by_card_id.get(row["id"], (False, False, ""))[2],
            )
            for row in rows
        ]

    def _build_admission_state_by_card_id(self, rows: list[sqlite3.Row]) -> dict[int, tuple[str, bool, bool, str, str]]:
        admission_state_by_card_id = {}
        granted_statuses = {"надано", "granted"}
        revoked_statuses = {"скасовано", "revoked"}
        active_sequences_by_card_id: dict[int, list[tuple[int, str]]] = {}

        sorted_rows = sorted(
            rows,
            key=lambda row: (
                self._admission_order_sort_key(row["order_date"]),
                row["id"],
            ),
        )

        for row in sorted_rows:
            card_id = row["card_id"]
            current_form, has_active_admission, revoked_after_grant, revoked_date, reissue_date = admission_state_by_card_id.get(card_id, ("", False, False, "", ""))
            admission_status = row["admission_status"]

            if admission_status in granted_statuses:
                form_level = self._admission_form_level(row["admission_form"])
                current_sequence = active_sequences_by_card_id.get(card_id, [])
                if form_level is not None:
                    current_sequence.append((form_level, row["order_date"]))
                active_sequences_by_card_id[card_id] = current_sequence
                admission_state_by_card_id[card_id] = (
                    row["admission_form"],
                    True,
                    False,
                    "",
                    self._build_reissue_date(current_sequence),
                )
                continue

            if admission_status in revoked_statuses and current_form:
                active_sequences_by_card_id[card_id] = []
                admission_state_by_card_id[card_id] = (current_form, False, True, row["order_date"], "")

        return admission_state_by_card_id

    def _admission_form_level(self, value: str) -> int | None:
        normalized_value = value.strip().upper().replace("Ф", "F")
        if normalized_value in {"F-1", "F-2", "F-3"}:
            return int(normalized_value[-1])
        return None

    def _build_reissue_date(self, active_sequence: list[tuple[int, str]]) -> str:
        if not active_sequence:
            return ""

        current_level, current_date = active_sequence[-1]
        duration_years = {1: 5, 2: 7, 3: 10}.get(current_level)
        if duration_years is None:
            return ""

        base_date = current_date
        if current_level == 2:
            for form_level, grant_date in active_sequence:
                if form_level == 1:
                    base_date = grant_date
                    break
        elif current_level == 3:
            for form_level, grant_date in active_sequence:
                if form_level == 2:
                    base_date = grant_date
                    break

        return self._shift_date(base_date, years=duration_years)

    def _build_access_state_by_card_id(self, rows: list[sqlite3.Row]) -> dict[int, tuple[bool, bool, str]]:
        access_state_by_card_id = {}
        granted_statuses = {"надано", "granted"}
        revoked_statuses = {"скасовано", "revoked"}

        sorted_rows = sorted(
            rows,
            key=lambda row: (
                self._access_sort_key(row["access_date"]),
                row["id"],
            ),
        )

        for row in sorted_rows:
            current_active, revoked_after_grant, revoked_date = access_state_by_card_id.get(row["card_id"], (False, False, ""))
            if row["status"] in granted_statuses:
                access_state_by_card_id[row["card_id"]] = (True, False, "")
                continue

            if row["status"] in revoked_statuses and current_active:
                access_state_by_card_id[row["card_id"]] = (False, True, row["access_date"])
                continue

            if row["status"] in revoked_statuses:
                access_state_by_card_id[row["card_id"]] = (False, revoked_after_grant, revoked_date)

        return access_state_by_card_id

    def _derive_workflow_status(
        self,
        lifecycle_state: str,
        admission_revoked_after_grant: bool,
        admission_revoked_date: str,
        has_active_admission: bool,
        has_active_access: bool,
        reissue_date: str,
        access_revoked_after_grant: bool,
        access_revoked_date: str,
    ) -> str:
        if lifecycle_state == "destroyed":
            return "знищено"
        if lifecycle_state == "sent":
            return "відправлено"
        if admission_revoked_after_grant and admission_revoked_date:
            destruction_date = self._shift_date(admission_revoked_date, years=5)
            return f"на знищення\nДата знищення:\n{destruction_date}"
        if access_revoked_after_grant and access_revoked_date:
            cancellation_date = self._shift_date(access_revoked_date, months=6)
            return f"на скасування\nДата скасування:\n{cancellation_date}"
        if has_active_admission and has_active_access and reissue_date:
            return f"переоформлення\nДата переоформлення:\n{reissue_date}"
        return ""

    def _admission_order_sort_key(self, value: str) -> tuple[int, datetime]:
        if not value:
            return (1, datetime.min)

        try:
            return (0, datetime.strptime(value, "%d.%m.%Y"))
        except ValueError:
            return (1, datetime.min)

    def _access_sort_key(self, value: str) -> tuple[int, datetime]:
        if not value:
            return (1, datetime.min)

        try:
            return (0, datetime.strptime(value, "%d.%m.%Y"))
        except ValueError:
            return (1, datetime.min)

    def _shift_date(self, value: str, years: int = 0, months: int = 0) -> str:
        parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
        target_year = parsed_date.year + years
        target_month = parsed_date.month + months

        while target_month > 12:
            target_year += 1
            target_month -= 12

        while target_month < 1:
            target_year -= 1
            target_month += 12

        day = parsed_date.day
        while True:
            try:
                shifted_date = date(target_year, target_month, day)
                return shifted_date.strftime("%d.%m.%Y")
            except ValueError:
                day -= 1

    def create_card(self, surname: str, name: str, patronymic: str) -> CardRecord:
        normalized_surname = self._normalize_name_part(surname, "Прізвище")
        normalized_name = self._normalize_name_part(name, "Ім'я")
        normalized_patronymic = self._normalize_name_part(patronymic, "По батькові")
        letter = self._build_letter(normalized_surname)

        with self._connect() as connection:
            next_number = self._get_next_number_for_letter(connection, letter)
            cursor = connection.execute(
                """
                INSERT INTO cards (
                    letter,
                    number,
                    card_date,
                    surname,
                    name,
                    patronymic,
                    form,
                    workflow_status,
                    document_kind,
                    document_number,
                    document_date,
                    document_target,
                    service_note,
                    user_note,
                    relation_group_id,
                    is_current,
                    lifecycle_state
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    letter,
                    str(next_number),
                    date.today().strftime("%d.%m.%Y"),
                    normalized_surname,
                    normalized_name,
                    normalized_patronymic,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    0,
                    1,
                    "",
                ),
            )
            card_id = cursor.lastrowid
            connection.execute(
                "UPDATE cards SET relation_group_id = ? WHERE id = ?",
                (card_id, card_id),
            )
            row = connection.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()

        return self._build_card_record_from_row(row)

    def list_accesses(self, card_id: int) -> list[AccessRecord]:
        with self._connect() as connection:
            self._ensure_card_exists(connection, card_id)
            rows = connection.execute(
                "SELECT * FROM accesses WHERE card_id = ? ORDER BY id",
                (card_id,),
            ).fetchall()

        return [self._build_access_record_from_row(row) for row in rows]

    def create_access(self, card_id: int, access_date: str, order_number: str, access_type: str, status: str) -> AccessRecord:
        normalized_access_date, normalized_order_number, normalized_access_type, normalized_status = self._normalize_access_fields(
            access_date,
            order_number,
            access_type,
            status,
        )

        with self._connect() as connection:
            self._ensure_card_exists(connection, card_id)
            cursor = connection.execute(
                """
                INSERT INTO accesses (card_id, access_date, order_number, access_type, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (card_id, normalized_access_date, normalized_order_number, normalized_access_type, normalized_status),
            )
            row = connection.execute(
                "SELECT * FROM accesses WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()

        return self._build_access_record_from_row(row)

    def update_access(self, access_id: int, access_date: str, order_number: str, access_type: str, status: str) -> AccessRecord:
        normalized_access_date, normalized_order_number, normalized_access_type, normalized_status = self._normalize_access_fields(
            access_date,
            order_number,
            access_type,
            status,
        )

        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM accesses WHERE id = ?",
                (access_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Запис доступу не знайдено.")

            connection.execute(
                """
                UPDATE accesses
                SET access_date = ?,
                    order_number = ?,
                    access_type = ?,
                    status = ?
                WHERE id = ?
                """,
                (normalized_access_date, normalized_order_number, normalized_access_type, normalized_status, access_id),
            )
            updated_row = connection.execute(
                "SELECT * FROM accesses WHERE id = ?",
                (access_id,),
            ).fetchone()

        return self._build_access_record_from_row(updated_row)

    def list_admissions(self, card_id: int) -> list[AdmissionRecord]:
        with self._connect() as connection:
            self._ensure_card_exists(connection, card_id)
            rows = connection.execute(
                "SELECT * FROM admissions WHERE card_id = ? ORDER BY id",
                (card_id,),
            ).fetchall()

        return [self._build_admission_record_from_row(row) for row in rows]

    def create_admission(
        self,
        card_id: int,
        escort_number: str,
        escort_date: str,
        admission_form: str,
    ) -> AdmissionRecord:
        normalized_values = self._normalize_admission_fields(
            escort_number=escort_number,
            escort_date=escort_date,
            response_number="",
            response_date="",
            order_number="",
            order_date="",
            admission_form=admission_form,
            admission_status="",
            require_escort=True,
        )

        with self._connect() as connection:
            self._ensure_card_exists(connection, card_id)
            cursor = connection.execute(
                """
                INSERT INTO admissions (
                    card_id,
                    escort_number,
                    escort_date,
                    response_number,
                    response_date,
                    order_number,
                    order_date,
                    admission_form,
                    admission_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (card_id, *normalized_values),
            )
            row = connection.execute(
                "SELECT * FROM admissions WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()

        return self._build_admission_record_from_row(row)

    def update_admission(
        self,
        admission_id: int,
        escort_number: str,
        escort_date: str,
        response_number: str,
        response_date: str,
        order_number: str,
        order_date: str,
        admission_form: str,
        admission_status: str,
    ) -> AdmissionRecord:
        normalized_values = self._normalize_admission_fields(
            escort_number=escort_number,
            escort_date=escort_date,
            response_number=response_number,
            response_date=response_date,
            order_number=order_number,
            order_date=order_date,
            admission_form=admission_form,
            admission_status=admission_status,
            require_escort=False,
        )

        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM admissions WHERE id = ?",
                (admission_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Запис розшифровки не знайдено.")

            connection.execute(
                """
                UPDATE admissions
                SET escort_number = ?,
                    escort_date = ?,
                    response_number = ?,
                    response_date = ?,
                    order_number = ?,
                    order_date = ?,
                    admission_form = ?,
                    admission_status = ?
                WHERE id = ?
                """,
                (*normalized_values, admission_id),
            )
            updated_row = connection.execute(
                "SELECT * FROM admissions WHERE id = ?",
                (admission_id,),
            ).fetchone()

        return self._build_admission_record_from_row(updated_row)

    def update_card(
        self,
        card_id: int,
        surname: str,
        name: str,
        patronymic: str,
        number: str,
        card_date: str,
        document_kind: str,
        document_number: str,
        document_date: str,
        document_target: str,
        user_note: str,
    ) -> CardRecord:
        normalized_surname = self._normalize_name_part(surname, "Прізвище")
        normalized_name = self._normalize_name_part(name, "Ім'я")
        normalized_patronymic = self._normalize_name_part(patronymic, "По батькові")
        normalized_number = self._normalize_card_number(number)
        normalized_card_date = self._normalize_date_value(card_date, "Дата картки", allow_empty=False)
        normalized_document_kind = self._normalize_document_kind(document_kind)
        normalized_document_number, normalized_document_date, normalized_document_target = self._normalize_document_fields(
            normalized_document_kind,
            document_number,
            document_date,
            document_target,
        )
        normalized_user_note = self._normalize_note_part(user_note)
        new_letter = self._build_letter(normalized_surname)

        with self._connect() as connection:
            current_row = connection.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
            if current_row is None:
                raise ValueError("Картку для редагування не знайдено.")

            self._ensure_card_is_editable(current_row)

            old_letter = current_row["letter"]
            old_number = current_row["number"]
            old_surname = current_row["surname"]
            relation_group_id = current_row["relation_group_id"] or current_row["id"]
            surname_changed = old_surname != normalized_surname

            if new_letter == old_letter:
                self._ensure_card_number_is_unique(connection, new_letter, normalized_number, card_id)
                connection.execute(
                    """
                    UPDATE cards
                    SET letter = ?,
                        number = ?,
                        card_date = ?,
                        surname = ?,
                        name = ?,
                        patronymic = ?,
                        form = ?,
                        document_kind = ?,
                        document_number = ?,
                        document_date = ?,
                        document_target = ?,
                        user_note = ?,
                        relation_group_id = ?
                    WHERE id = ?
                    """,
                    (
                        new_letter,
                        normalized_number,
                        normalized_card_date,
                        normalized_surname,
                        normalized_name,
                        normalized_patronymic,
                        current_row["form"],
                        normalized_document_kind,
                        normalized_document_number,
                        normalized_document_date,
                        normalized_document_target,
                        normalized_user_note,
                        relation_group_id,
                        card_id,
                    ),
                )

                if surname_changed:
                    self._propagate_surname_change(connection, relation_group_id, old_surname, normalized_surname)

                return self._get_card_record_by_id(connection, card_id)

            new_number = str(self._get_next_number_for_letter(connection, new_letter))
            old_card_code = self._format_card_code(old_letter, old_number)
            new_card_code = self._format_card_code(new_letter, new_number)

            cursor = connection.execute(
                """
                INSERT INTO cards (
                    letter,
                    number,
                    card_date,
                    surname,
                    name,
                    patronymic,
                    form,
                    document_kind,
                    document_number,
                    document_date,
                    document_target,
                    service_note,
                    user_note,
                    relation_group_id,
                    is_current,
                    lifecycle_state
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_letter,
                    new_number,
                    normalized_card_date,
                    normalized_surname,
                    normalized_name,
                    normalized_patronymic,
                    current_row["form"],
                    normalized_document_kind,
                    normalized_document_number,
                    normalized_document_date,
                    normalized_document_target,
                    self._build_related_note_message(old_card_code, old_surname),
                    normalized_user_note,
                    relation_group_id,
                    1,
                    "",
                ),
            )
            new_card_id = cursor.lastrowid

            old_service_note = self._append_service_note(
                current_row["service_note"],
                self._build_related_note_message(new_card_code, old_surname),
            )
            connection.execute(
                """
                UPDATE cards
                SET card_date = ?,
                    surname = ?,
                    name = ?,
                    patronymic = ?,
                    form = ?,
                    document_kind = ?,
                    document_number = ?,
                    document_date = ?,
                    document_target = ?,
                    service_note = ?,
                    user_note = ?,
                    relation_group_id = ?,
                    is_current = 0
                WHERE id = ?
                """,
                (
                    normalized_card_date,
                    normalized_surname,
                    normalized_name,
                    normalized_patronymic,
                    current_row["form"],
                    normalized_document_kind,
                    normalized_document_number,
                    normalized_document_date,
                    normalized_document_target,
                    old_service_note,
                    normalized_user_note,
                    relation_group_id,
                    card_id,
                ),
            )

            if surname_changed:
                self._propagate_surname_change(connection, relation_group_id, old_surname, normalized_surname)

            return self._get_card_record_by_id(connection, card_id)

    def send_card(self, card_id: int, document_number: str, document_date: str, document_target: str) -> CardRecord:
        normalized_number, normalized_date, normalized_target = self._normalize_document_fields(
            "escort",
            document_number,
            document_date,
            document_target,
        )

        with self._connect() as connection:
            current_row = connection.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
            if current_row is None:
                raise ValueError("Картку для відправлення не знайдено.")

            self._ensure_card_is_editable(current_row)
            relation_group_id = current_row["relation_group_id"] or current_row["id"]
            rows = connection.execute(
                "SELECT id, service_note, user_note FROM cards WHERE relation_group_id = ?",
                (relation_group_id,),
            ).fetchall()
            send_note = self._build_send_note(normalized_number, normalized_date, normalized_target)

            for row in rows:
                updated_service_note = self._append_service_note(row["service_note"], send_note)
                connection.execute(
                    """
                    UPDATE cards
                    SET workflow_status = ?,
                        document_kind = ?,
                        document_number = ?,
                        document_date = ?,
                        document_target = ?,
                        service_note = ?,
                        lifecycle_state = ?
                    WHERE id = ?
                    """,
                    (
                        "відправлено",
                        "escort",
                        normalized_number,
                        normalized_date,
                        normalized_target,
                        updated_service_note,
                        "sent",
                        row["id"],
                    ),
                )

            return self._get_card_record_by_id(connection, card_id)

    def destroy_card(self, card_id: int, document_number: str, document_date: str) -> CardRecord:
        normalized_number, normalized_date, _ = self._normalize_document_fields(
            "act",
            document_number,
            document_date,
            "",
        )

        with self._connect() as connection:
            current_row = connection.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
            if current_row is None:
                raise ValueError("Картку для знищення не знайдено.")

            self._ensure_card_is_editable(current_row)
            destroy_note = self._build_destroy_note(normalized_number, normalized_date)
            updated_service_note = self._append_service_note(current_row["service_note"], destroy_note)
            connection.execute(
                """
                UPDATE cards
                SET workflow_status = ?,
                    document_kind = ?,
                    document_number = ?,
                    document_date = ?,
                    document_target = ?,
                    service_note = ?,
                    lifecycle_state = ?
                WHERE id = ?
                """,
                (
                    "знищено",
                    "act",
                    normalized_number,
                    normalized_date,
                    "",
                    updated_service_note,
                    "destroyed",
                    card_id,
                ),
            )

            return self._get_card_record_by_id(connection, card_id)

    def return_card(self, card_id: int, document_number: str, document_date: str, document_target: str) -> CardRecord:
        normalized_number, normalized_date, normalized_target = self._normalize_document_fields(
            "escort",
            document_number,
            document_date,
            document_target,
        )

        with self._connect() as connection:
            current_row = connection.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
            if current_row is None:
                raise ValueError("Картку для повернення не знайдено.")

            if current_row["lifecycle_state"] != "sent":
                raise ValueError("Повернути можна лише відправлену картку.")

            relation_group_id = current_row["relation_group_id"] or current_row["id"]
            rows = connection.execute(
                "SELECT id, service_note FROM cards WHERE relation_group_id = ?",
                (relation_group_id,),
            ).fetchall()
            return_note = self._build_return_note(
                normalized_number,
                normalized_date,
                normalized_target,
            )

            for row in rows:
                updated_service_note = self._append_service_note(row["service_note"], return_note)
                connection.execute(
                    """
                    UPDATE cards
                    SET workflow_status = ?,
                        document_kind = ?,
                        document_number = ?,
                        document_date = ?,
                        document_target = ?,
                        service_note = ?,
                        lifecycle_state = ?
                    WHERE id = ?
                    """,
                    (
                        "",
                        "",
                        "",
                        "",
                        "",
                        updated_service_note,
                        "",
                        row["id"],
                    ),
                )

            return self._get_card_record_by_id(connection, card_id)

    def update_card_service_note(self, card_id: int, service_note: str) -> CardRecord:
        normalized_service_note = self._normalize_note_part(service_note)

        with self._connect() as connection:
            current_row = connection.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
            if current_row is None:
                raise ValueError("Картку для редагування не знайдено.")

            connection.execute(
                "UPDATE cards SET service_note = ? WHERE id = ?",
                (normalized_service_note, card_id),
            )
            row = connection.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()

        return self._build_card_record_from_row(row)

    def get_related_card_ids(self, card_id: int) -> list[int]:
        with self._connect() as connection:
            current_row = connection.execute(
                "SELECT relation_group_id FROM cards WHERE id = ?",
                (card_id,),
            ).fetchone()

            if current_row is None:
                return []

            relation_group_id = current_row["relation_group_id"] or card_id
            rows = connection.execute(
                "SELECT id FROM cards WHERE relation_group_id = ? ORDER BY id",
                (relation_group_id,),
            ).fetchall()

        return [row["id"] for row in rows]

    def _ensure_card_is_editable(self, row: sqlite3.Row) -> None:
        if not bool(row["is_current"]):
            raise ValueError("Ця картка неактивна після зміни прізвища і не може редагуватися.")
        if row["lifecycle_state"] == "sent":
            raise ValueError("Відправлену картку не можна редагувати, її можна лише позначити повернутою.")
        if row["lifecycle_state"] == "destroyed":
            raise ValueError("Знищену картку не можна редагувати.")

    def _normalize_name_part(self, value: str, field_name: str) -> str:
        normalized_value = " ".join(value.strip().split())
        if not normalized_value:
            raise ValueError(f"Поле «{field_name}» не може бути порожнім.")

        if not _UKRAINIAN_NAME_PATTERN.fullmatch(normalized_value):
            raise ValueError(
                f"Поле «{field_name}» може містити лише українські літери, апостроф і пробіл."
            )

        return normalized_value

    def _build_letter(self, surname: str) -> str:
        match = _UKRAINIAN_LETTER_PATTERN.search(surname)
        if match is None:
            raise ValueError("Не вдалося визначити літеру для картки за прізвищем.")

        return match.group(0).upper()

    def _normalize_card_number(self, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Поле «Номер у літері» не може бути порожнім.")

        if not _CARD_NUMBER_PATTERN.fullmatch(normalized_value):
            raise ValueError("Поле «Номер у літері» має містити лише цифри.")

        return str(int(normalized_value))

    def _normalize_date_value(self, value: str, field_name: str, allow_empty: bool) -> str:
        normalized_value = value.strip()

        if not normalized_value:
            if allow_empty:
                return ""
            raise ValueError(f"Поле «{field_name}» не може бути порожнім.")

        try:
            parsed_date = datetime.strptime(normalized_value, "%d.%m.%Y").date()
        except ValueError as error:
            raise ValueError(f"Поле «{field_name}» має бути у форматі ДД.ММ.РРРР.") from error

        return parsed_date.strftime("%d.%m.%Y")

    def _normalize_workflow_status(self, value: str) -> str:
        normalized_value = " ".join(value.strip().split())
        if normalized_value not in _WORKFLOW_STATUSES:
            raise ValueError("Поле «Статус опрацювання» має недопустиме значення.")
        return normalized_value

    def _normalize_document_kind(self, value: str) -> str:
        normalized_value = value.strip()
        if normalized_value not in _DOCUMENT_KINDS:
            raise ValueError("Поле «Тип документа або події» має недопустиме значення.")
        return normalized_value

    def _normalize_document_fields(
        self,
        document_kind: str,
        document_number: str,
        document_date: str,
        document_target: str,
    ) -> tuple[str, str, str]:
        normalized_number = " ".join(document_number.strip().split())
        normalized_target = " ".join(document_target.strip().split())

        if document_kind == "":
            return "", "", ""

        if document_kind == "escort":
            if not normalized_number:
                raise ValueError("Для супроводу потрібно вказати номер.")
            if not normalized_target:
                raise ValueError("Для супроводу потрібно вказати, куди відправлено.")
            normalized_date = self._normalize_date_value(document_date, "Дата супроводу", allow_empty=False)
            return normalized_number, normalized_date, normalized_target

        if document_kind == "act":
            if not normalized_number:
                raise ValueError("Для акту потрібно вказати номер акту.")
            normalized_date = self._normalize_date_value(document_date, "Дата акту", allow_empty=False)
            return normalized_number, normalized_date, ""

        normalized_date = self._normalize_date_value(document_date, "Дата події", allow_empty=False)
        return "", normalized_date, ""

    def _normalize_note_part(self, value: str) -> str:
        return value.strip()

    def _normalize_text_value(self, value: str) -> str:
        return " ".join(value.strip().split())

    def _normalize_admission_form(self, value: str) -> str:
        normalized_value = self._normalize_text_value(value)
        if normalized_value and normalized_value not in _ADMISSION_FORMS:
            raise ValueError("Поле «Форма допуску» має недопустиме значення.")
        return normalized_value

    def _normalize_admission_status(self, value: str) -> str:
        normalized_value = self._normalize_text_value(value)
        if normalized_value and normalized_value not in _ADMISSION_STATUSES:
            raise ValueError("Поле «Статус» має недопустиме значення.")
        return normalized_value

    def _normalize_access_type(self, value: str) -> str:
        normalized_value = value.replace(" ", "")
        if not normalized_value:
            raise ValueError("Поле «Доступ» не може бути порожнім.")
        if normalized_value not in _ACCESS_TYPES:
            raise ValueError("Поле «Доступ» має недопустиме значення.")
        return normalized_value

    def _normalize_access_fields(self, access_date: str, order_number: str, access_type: str, status: str) -> tuple[str, str, str, str]:
        normalized_access_date = self._normalize_date_value(access_date, "Дата", allow_empty=False)
        normalized_order_number = self._normalize_text_value(order_number)
        if not normalized_order_number:
            raise ValueError("Поле «Номер наказу» не може бути порожнім.")

        normalized_access_type = self._normalize_access_type(access_type)
        normalized_status = self._normalize_admission_status(status)
        if not normalized_status:
            raise ValueError("Поле «Статус» не може бути порожнім.")

        return normalized_access_date, normalized_order_number, normalized_access_type, normalized_status

    def _normalize_number_date_pair(
        self,
        number_value: str,
        date_value: str,
        number_field_name: str,
        date_field_name: str,
        require_number: bool,
    ) -> tuple[str, str]:
        normalized_number = self._normalize_text_value(number_value)
        if not normalized_number:
            if require_number:
                raise ValueError(f"Поле «{number_field_name}» не може бути порожнім.")
            if date_value.strip():
                raise ValueError(
                    f"Поле «{date_field_name}» можна вказати лише разом із полем «{number_field_name}»."
                )
            return "", ""

        normalized_date = self._normalize_date_value(date_value, date_field_name, allow_empty=False)
        return normalized_number, normalized_date

    def _normalize_admission_fields(
        self,
        escort_number: str,
        escort_date: str,
        response_number: str,
        response_date: str,
        order_number: str,
        order_date: str,
        admission_form: str,
        admission_status: str,
        require_escort: bool,
    ) -> tuple[str, str, str, str, str, str, str, str]:
        normalized_escort_number, normalized_escort_date = self._normalize_number_date_pair(
            escort_number,
            escort_date,
            "Номер супроводу",
            "Дата супроводу",
            require_number=require_escort,
        )
        normalized_response_number, normalized_response_date = self._normalize_number_date_pair(
            response_number,
            response_date,
            "Номер відповіді",
            "Дата відповіді",
            require_number=False,
        )
        normalized_order_number, normalized_order_date = self._normalize_number_date_pair(
            order_number,
            order_date,
            "Номер розпорядження",
            "Дата розпорядження",
            require_number=False,
        )
        normalized_admission_form = self._normalize_admission_form(admission_form)
        normalized_admission_status = self._normalize_admission_status(admission_status)

        if normalized_admission_status and not normalized_order_number:
            raise ValueError("Для визначення стану допуску потрібно вказати номер і дату розпорядження.")

        return (
            normalized_escort_number,
            normalized_escort_date,
            normalized_response_number,
            normalized_response_date,
            normalized_order_number,
            normalized_order_date,
            normalized_admission_form,
            normalized_admission_status,
        )

    def _append_service_note(self, current_note: str, extra_note: str) -> str:
        current_value = current_note.strip()
        extra_value = extra_note.strip()
        if not current_value:
            return extra_value
        if not extra_value:
            return current_value
        return f"{current_value}\n{extra_value}"

    def _build_related_note_message(self, related_card_code: str, old_surname: str) -> str:
        return f"[Пов'язана картка] {related_card_code}. Попереднє прізвище: {old_surname}."

    def _build_surname_change_note(self, old_surname: str, new_surname: str) -> str:
        return f"[Зміна прізвища] {old_surname} -> {new_surname}."

    def _build_send_note(self, document_number: str, document_date: str, document_target: str) -> str:
        return (
            f"[Відправлення] № супроводу {document_number} від {document_date}. "
            f"Установа: {document_target}."
        )

    def _build_destroy_note(self, document_number: str, document_date: str) -> str:
        return f"[Знищення] Акт знищення № {document_number} від {document_date}."

    def _build_return_note(self, document_number: str, document_date: str, document_target: str) -> str:
        return (
            f"[Повернення] Лист повернення № {document_number} від {document_date}. "
            f"Установа: {document_target}."
        )

    def _propagate_surname_change(
        self,
        connection: sqlite3.Connection,
        relation_group_id: int,
        old_surname: str,
        new_surname: str,
    ) -> None:
        if old_surname == new_surname:
            return

        rows = connection.execute(
            "SELECT id, service_note FROM cards WHERE relation_group_id = ?",
            (relation_group_id,),
        ).fetchall()
        surname_note = self._build_surname_change_note(old_surname, new_surname)

        for row in rows:
            updated_service_note = self._append_service_note(row["service_note"], surname_note)
            connection.execute(
                "UPDATE cards SET surname = ?, service_note = ? WHERE id = ?",
                (new_surname, updated_service_note, row["id"]),
            )

    def _format_card_code(self, letter: str, number: str) -> str:
        if letter and number:
            return f"{letter}-{number}"
        return letter or number

    def _ensure_card_exists(self, connection: sqlite3.Connection, card_id: int) -> None:
        row = connection.execute("SELECT 1 FROM cards WHERE id = ?", (card_id,)).fetchone()
        if row is None:
            raise ValueError("Картку не знайдено.")

    def _build_card_record_from_row(
        self,
        row: sqlite3.Row,
        form_override: str | None = None,
        derived_workflow_status: str | None = None,
        has_active_admission: bool = False,
        has_active_access: bool = False,
        access_revoked_after_grant: bool = False,
        access_revoked_date: str = "",
        admission_revoked_after_grant: bool = False,
        admission_revoked_date: str = "",
        reissue_date: str = "",
    ) -> CardRecord:
        resolved_workflow_status = derived_workflow_status or self._derive_workflow_status(
            row["lifecycle_state"],
            admission_revoked_after_grant,
            admission_revoked_date,
            has_active_admission,
            has_active_access,
            reissue_date,
            access_revoked_after_grant,
            access_revoked_date,
        )
        return CardRecord(
            card_id=row["id"],
            letter=row["letter"],
            number=row["number"],
            card_date=row["card_date"],
            surname=row["surname"],
            name=row["name"],
            patronymic=row["patronymic"],
            form=row["form"] if form_override is None else form_override,
            workflow_status=row["workflow_status"],
            derived_workflow_status=resolved_workflow_status,
            document_kind=row["document_kind"],
            document_number=row["document_number"],
            document_date=row["document_date"],
            document_target=row["document_target"],
            service_note=row["service_note"],
            user_note=row["user_note"],
            relation_group_id=row["relation_group_id"],
            is_current=bool(row["is_current"]),
            lifecycle_state=row["lifecycle_state"],
            has_active_admission=has_active_admission,
            has_active_access=has_active_access,
            access_revoked_after_grant=access_revoked_after_grant,
            access_revoked_date=access_revoked_date,
            admission_revoked_after_grant=admission_revoked_after_grant,
            admission_revoked_date=admission_revoked_date,
            reissue_date=reissue_date,
        )

    def _build_admission_record_from_row(self, row: sqlite3.Row) -> AdmissionRecord:
        return AdmissionRecord(
            admission_id=row["id"],
            card_id=row["card_id"],
            escort_number=row["escort_number"],
            escort_date=row["escort_date"],
            response_number=row["response_number"],
            response_date=row["response_date"],
            order_number=row["order_number"],
            order_date=row["order_date"],
            admission_form=row["admission_form"],
            admission_status=row["admission_status"],
        )

    def _build_access_record_from_row(self, row: sqlite3.Row) -> AccessRecord:
        return AccessRecord(
            access_id=row["id"],
            card_id=row["card_id"],
            access_date=row["access_date"],
            order_number=row["order_number"],
            access_type=row["access_type"],
            status=row["status"],
        )

    def _get_card_record_by_id(self, connection: sqlite3.Connection, card_id: int) -> CardRecord:
        row = connection.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
        if row is None:
            raise ValueError("Картку для читання не знайдено.")
        return self._build_card_record_from_row(row)

    def _ensure_card_number_is_unique(
        self,
        connection: sqlite3.Connection,
        letter: str,
        number: str,
        card_id: int | None,
    ) -> None:
        if card_id is None:
            row = connection.execute(
                "SELECT id FROM cards WHERE letter = ? AND number = ? LIMIT 1",
                (letter, number),
            ).fetchone()
        else:
            row = connection.execute(
                "SELECT id FROM cards WHERE letter = ? AND number = ? AND id <> ? LIMIT 1",
                (letter, number, card_id),
            ).fetchone()

        if row is not None:
            raise ValueError("Картка з таким номером у межах цієї літери вже існує.")

    def _get_next_number_for_letter(self, connection: sqlite3.Connection, letter: str) -> int:
        row = connection.execute(
            """
            SELECT COALESCE(MAX(CAST(number AS INTEGER)), 0) AS max_number
            FROM cards
            WHERE letter = ?
              AND TRIM(number) <> ''
              AND number GLOB '[0-9]*'
            """,
            (letter,),
        ).fetchone()

        return int(row["max_number"]) + 1
