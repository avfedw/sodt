"""Робота з таблицею карток у SQLite."""

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re
import sqlite3

from .cards_state import AdmissionState, AccessState, build_access_state_by_card_id, build_admission_state_by_card_id, derive_workflow_status


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
        # За замовчуванням працюємо з основною SQLite-базою проєкту,
        # але шлях можна підмінити в тестах або тимчасових сценаріях перевірки.
        self.db_path = db_path or Path(__file__).resolve().parent / "sodt.sqlite3"
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        """Створює з'єднання з Row-рядками для доступу до полів за назвами."""

        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        """Перевіряє структуру таблиць і за потреби створює або оновлює її."""

        with self._connect() as connection:
            table_exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'cards'"
            ).fetchone()

            if table_exists is not None:
                columns = [
                    row["name"]
                    for row in connection.execute("PRAGMA table_info(cards)").fetchall()
                ]
                # Для локального десктопного застосунку тут простіше перестворити таблицю,
                # ніж підтримувати складні міграції для кожної проміжної версії схеми.
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
                # Окремо підтримуємо м'яке оновлення старої схеми, де ще не було access_type,
                # щоб існуючу локальну базу можна було підняти без ручного втручання.
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
        """Повертає всі картки разом із похідним станом допусків і доступів."""

        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM cards ORDER BY id").fetchall()
            admission_rows = connection.execute(
                "SELECT id, card_id, admission_form, admission_status, order_date FROM admissions"
            ).fetchall()
            access_rows = connection.execute(
                "SELECT id, card_id, status, access_date FROM accesses"
            ).fetchall()

        admission_state_by_card_id = build_admission_state_by_card_id(admission_rows)
        access_state_by_card_id = build_access_state_by_card_id(access_rows)

        # Похідний стан розраховується пакетно для всіх карток,
        # щоб доменна логіка залишалась в одному місці й не дублювалась по циклу.
        return [
            self._build_card_record_from_row(
                row,
                admission_state=admission_state_by_card_id.get(row["id"], AdmissionState(form=row["form"])),
                access_state=access_state_by_card_id.get(row["id"], AccessState()),
            )
            for row in rows
        ]

    def create_card(self, surname: str, name: str, patronymic: str) -> CardRecord:
        """Створює нову картку з автоматичним присвоєнням літери та номера."""

        normalized_surname = self._normalize_name_part(surname, "Прізвище")
        normalized_name = self._normalize_name_part(name, "Ім'я")
        normalized_patronymic = self._normalize_name_part(patronymic, "По батькові")
        letter = self._build_letter(normalized_surname)

        with self._connect() as connection:
            # Номер у межах літери видається послідовно, щоб користувачеві
            # не потрібно було вручну шукати наступне вільне значення.
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
            # Перша картка в групі пов'язується сама з собою,
            # а надалі цей ключ використовується для історії змін прізвища та відправлень.
            row = connection.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()

        return self._build_card_record_from_row(row)

    def list_accesses(self, card_id: int) -> list[AccessRecord]:
        """Повертає історію доступів для конкретної картки."""

        with self._connect() as connection:
            self._ensure_card_exists(connection, card_id)
            rows = connection.execute(
                "SELECT * FROM accesses WHERE card_id = ? ORDER BY id",
                (card_id,),
            ).fetchall()

        return [self._build_access_record_from_row(row) for row in rows]

    def create_access(self, card_id: int, access_date: str, order_number: str, access_type: str, status: str) -> AccessRecord:
        """Створює новий запис доступу після нормалізації та валідації полів."""

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
        """Оновлює наявний запис доступу й повертає його актуальний стан."""

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
        """Повертає історію допусків для конкретної картки."""

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
        """Створює первинний запис допуску для картки."""

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
        """Доповнює або змінює запис допуску службовими реквізитами та статусом."""

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
        """Оновлює картку або створює нову пов'язану картку при зміні літери прізвища."""

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
                # Поки літера лишається тією самою, картку можна виправити на місці
                # без створення додаткового запису в пов'язаній групі.
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

            # Якщо прізвище перейшло на іншу літеру, історично зберігаємо стару картку,
            # а поточний стан переносимо в новий запис з новим кодом.
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
        """Позначає картку та всі пов'язані з нею записи як відправлені."""

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

            # Відправлення стосується всієї пов'язаної групи карток,
            # бо користувач сприймає її як одну історію з кількома перевипусками.
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
        """Фіксує знищення поточної картки за реквізитами акта."""

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
        """Повертає відправлену картку в активний стан і очищає реквізити відправлення."""

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

            # Повернення, як і відправлення, синхронізуємо по всій групі пов'язаних карток,
            # щоб старі записи не лишались у хибному стані "відправлено".
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
        """Оновлює службову примітку картки без зміни інших полів."""

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
        """Повертає всі id карток, що належать до однієї історичної групи."""

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
        # Редагування дозволене лише для поточної активної картки:
        # історичні, відправлені та знищені записи мають лишатися незмінними.
        if not bool(row["is_current"]):
            raise ValueError("Ця картка неактивна після зміни прізвища і не може редагуватися.")
        if row["lifecycle_state"] == "sent":
            raise ValueError("Відправлену картку не можна редагувати, її можна лише позначити повернутою.")
        if row["lifecycle_state"] == "destroyed":
            raise ValueError("Знищену картку не можна редагувати.")

    def _normalize_name_part(self, value: str, field_name: str) -> str:
        # Тут не лише обрізаємо пробіли, а й стискаємо повтори,
        # щоб у базу не потрапляли візуально однакові, але різні рядки.
        normalized_value = " ".join(value.strip().split())
        if not normalized_value:
            raise ValueError(f"Поле «{field_name}» не може бути порожнім.")

        if not _UKRAINIAN_NAME_PATTERN.fullmatch(normalized_value):
            raise ValueError(
                f"Поле «{field_name}» може містити лише українські літери, апостроф і пробіл."
            )

        return normalized_value

    def _build_letter(self, surname: str) -> str:
        # Літеру картки беремо з першої української літери прізвища,
        # і саме вона визначає внутрішню серію нумерації.
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
        # Обов'язкові поля залежать від типу документа:
        # супровід потребує адресата, акт - лише номер і дату, службові події - тільки дату.
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
        # Для доступу перевіряємо весь набір реквізитів разом, бо помилка будь-якого поля
        # робить запис юридично неповним для подальших похідних розрахунків.
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
        # Допоміжна перевірка для кількох однотипних пар "номер-дата",
        # щоб правила не дублювалися окремо для супроводу, відповіді й розпорядження.
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
        # Тут збираємо всі реквізити допуску в єдину послідовність,
        # яку потім напряму використовують INSERT та UPDATE запити.
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
        # Службові нотатки накопичуються як журнал подій, тому нові фрагменти
        # додаються в кінець без втрати попередньої історії.
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
        # Зміна прізвища має відбитися на всіх пов'язаних картках,
        # інакше історія однієї особи роз'їдеться по різних написаннях.
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
        """Підтверджує, що картка існує, перш ніж працювати з її підлеглими записами."""

        row = connection.execute("SELECT 1 FROM cards WHERE id = ?", (card_id,)).fetchone()
        if row is None:
            raise ValueError("Картку не знайдено.")

    def _build_card_record_from_row(
        self,
        row: sqlite3.Row,
        admission_state: AdmissionState | None = None,
        access_state: AccessState | None = None,
        derived_workflow_status: str | None = None,
    ) -> CardRecord:
        # Тут з'єднуємо сирий рядок таблиці cards з похідним доменним станом,
        # який було обчислено окремо за історією допусків і доступів.
        resolved_admission_state = admission_state or AdmissionState(form=row["form"])
        resolved_access_state = access_state or AccessState()
        resolved_workflow_status = derived_workflow_status or derive_workflow_status(
            row["lifecycle_state"],
            resolved_admission_state,
            resolved_access_state,
        )
        return CardRecord(
            card_id=row["id"],
            letter=row["letter"],
            number=row["number"],
            card_date=row["card_date"],
            surname=row["surname"],
            name=row["name"],
            patronymic=row["patronymic"],
            form=resolved_admission_state.form,
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
            has_active_admission=resolved_admission_state.has_active,
            has_active_access=resolved_access_state.has_active,
            access_revoked_after_grant=resolved_access_state.revoked_after_grant,
            access_revoked_date=resolved_access_state.revoked_date,
            admission_revoked_after_grant=resolved_admission_state.revoked_after_grant,
            admission_revoked_date=resolved_admission_state.revoked_date,
            reissue_date=resolved_admission_state.reissue_date,
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
        """Зчитує одну картку з бази та перетворює її на доменну модель."""

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
        # У межах однієї літери номер має бути унікальним,
        # інакше користувач не зможе однозначно знайти картку за кодом.
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
        """Повертає наступний вільний числовий номер у межах заданої літери."""

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
