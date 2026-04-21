"""Робота зі структурою підприємства у SQLite."""

from dataclasses import dataclass
from pathlib import Path
import sqlite3


_UNIT_TYPE_ORDER = [
    "section",
    "group",
    "department",
    "division",
    "radio_station",
]
_UNIT_TYPE_RANK = {unit_type: index for index, unit_type in enumerate(_UNIT_TYPE_ORDER)}
_EXPECTED_STRUCTURE_COLUMNS = ["id", "name", "short_name", "unit_type", "parent_id", "sort_order"]


@dataclass(slots=True)
class StructureUnitRecord:
    """Одна організаційна одиниця підприємства."""

    unit_id: int
    name: str
    short_name: str
    unit_type: str
    parent_id: int | None
    sort_order: int = 0
    parent_name: str = ""


class StructureRepository:
    """Репозиторій для збереження та читання структури підприємства."""

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
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'structure_units'"
            ).fetchone()

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS structure_units (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL DEFAULT '',
                    short_name TEXT NOT NULL DEFAULT '',
                    unit_type TEXT NOT NULL DEFAULT '',
                    parent_id INTEGER NULL,
                    sort_order INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(parent_id) REFERENCES structure_units(id) ON DELETE RESTRICT
                )
                """
            )

            if table_exists is None:
                return

            columns = [
                row["name"]
                for row in connection.execute("PRAGMA table_info(structure_units)").fetchall()
            ]
            if "sort_order" not in columns:
                connection.execute(
                    "ALTER TABLE structure_units ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
                )
                self._rebuild_sort_order(connection)
            if "short_name" not in columns:
                connection.execute(
                    "ALTER TABLE structure_units ADD COLUMN short_name TEXT NOT NULL DEFAULT ''"
                )

    def list_units(self) -> list[StructureUnitRecord]:
        """Повертає всі оргодиниці структури з назвами батьківських вузлів."""

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT unit.id,
                       unit.name,
                      unit.short_name,
                       unit.unit_type,
                       unit.parent_id,
                      unit.sort_order,
                       parent.name AS parent_name
                FROM structure_units AS unit
                LEFT JOIN structure_units AS parent ON parent.id = unit.parent_id
                  ORDER BY unit.parent_id IS NOT NULL, unit.parent_id, unit.sort_order, unit.id
                """
            ).fetchall()

        return [self._build_unit_record(row) for row in rows]

    def create_unit(self, name: str, short_name: str, unit_type: str, parent_id: int | None) -> StructureUnitRecord:
        """Створює нову організаційну одиницю з перевіркою її місця в ієрархії."""

        normalized_name = self._normalize_name(name)
        normalized_short_name = self._normalize_short_name(short_name)
        normalized_type = self._normalize_unit_type(unit_type)

        with self._connect() as connection:
            self._validate_parent_relation(connection, normalized_type, parent_id, current_unit_id=None)
            sort_order = self._next_sort_order(connection, parent_id)
            cursor = connection.execute(
                "INSERT INTO structure_units (name, short_name, unit_type, parent_id, sort_order) VALUES (?, ?, ?, ?, ?)",
                (normalized_name, normalized_short_name, normalized_type, parent_id, sort_order),
            )
            row = self._get_unit_row_by_id(connection, cursor.lastrowid)

        return self._build_unit_record(row)

    def update_unit(self, unit_id: int, name: str, short_name: str, unit_type: str, parent_id: int | None) -> StructureUnitRecord:
        """Оновлює оргодиницю і перевіряє, чи не ламає зміна ієрархію."""

        normalized_name = self._normalize_name(name)
        normalized_short_name = self._normalize_short_name(short_name)
        normalized_type = self._normalize_unit_type(unit_type)

        with self._connect() as connection:
            current_row = self._get_unit_row_by_id(connection, unit_id)
            self._validate_parent_relation(connection, normalized_type, parent_id, current_unit_id=unit_id)
            self._validate_children_relation(connection, unit_id, normalized_type)
            sort_order = current_row["sort_order"]
            if current_row["parent_id"] != parent_id:
                self._close_sort_order_gap(connection, current_row["parent_id"], sort_order, excluded_unit_id=unit_id)
                sort_order = self._next_sort_order(connection, parent_id)
            connection.execute(
                "UPDATE structure_units SET name = ?, short_name = ?, unit_type = ?, parent_id = ?, sort_order = ? WHERE id = ?",
                (normalized_name, normalized_short_name, normalized_type, parent_id, sort_order, unit_id),
            )
            row = self._get_unit_row_by_id(connection, unit_id)

        return self._build_unit_record(row)

    def delete_unit(self, unit_id: int) -> None:
        """Видаляє оргодиницю, якщо в неї немає дочірніх вузлів."""

        with self._connect() as connection:
            current_row = self._get_unit_row_by_id(connection, unit_id)
            child_row = connection.execute(
                "SELECT 1 FROM structure_units WHERE parent_id = ? LIMIT 1",
                (unit_id,),
            ).fetchone()
            if child_row is not None:
                raise ValueError("Спочатку видаліть або перенесіть дочірні одиниці.")

            connection.execute("DELETE FROM structure_units WHERE id = ?", (unit_id,))
            self._close_sort_order_gap(
                connection,
                current_row["parent_id"],
                int(current_row["sort_order"]),
                excluded_unit_id=unit_id,
            )

    def save_tree_order(self, units_tree: list[dict]) -> None:
        """Зберігає повний порядок дерева після перетягування вузлів у UI."""

        with self._connect() as connection:
            self._save_tree_branch(connection, parent_id=None, units_tree=units_tree)

    def _save_tree_branch(self, connection: sqlite3.Connection, parent_id: int | None, units_tree: list[dict]) -> None:
        for sort_order, unit_data in enumerate(units_tree):
            unit_id = int(unit_data["unit_id"])
            row = self._get_unit_row_by_id(connection, unit_id)
            self._validate_parent_relation(
                connection,
                row["unit_type"],
                parent_id,
                current_unit_id=unit_id,
            )
            connection.execute(
                "UPDATE structure_units SET parent_id = ?, sort_order = ? WHERE id = ?",
                (parent_id, sort_order, unit_id),
            )
            self._save_tree_branch(connection, unit_id, unit_data.get("children", []))

    def unit_type_codes(self) -> list[str]:
        """Повертає коди типів одиниць у порядку від вищого до нижчого."""

        return list(_UNIT_TYPE_ORDER)

    def _normalize_name(self, value: str) -> str:
        normalized_value = " ".join(value.strip().split())
        if not normalized_value:
            raise ValueError("Назва організаційної одиниці не може бути порожньою.")
        return normalized_value

    def _normalize_short_name(self, value: str) -> str:
        normalized_value = " ".join(value.strip().split())
        if not normalized_value:
            raise ValueError("Скорочена назва організаційної одиниці не може бути порожньою.")
        return normalized_value

    def _normalize_unit_type(self, value: str) -> str:
        normalized_value = value.strip()
        if normalized_value not in _UNIT_TYPE_RANK:
            raise ValueError("Вид організаційної одиниці має недопустиме значення.")
        return normalized_value

    def _validate_parent_relation(
        self,
        connection: sqlite3.Connection,
        unit_type: str,
        parent_id: int | None,
        current_unit_id: int | None,
    ) -> None:
        if parent_id is None:
            return

        if current_unit_id is not None and parent_id == current_unit_id:
            raise ValueError("Одиниця не може бути батьківською сама для себе.")

        parent_row = self._get_unit_row_by_id(connection, parent_id)
        if _UNIT_TYPE_RANK[parent_row["unit_type"]] >= _UNIT_TYPE_RANK[unit_type]:
            raise ValueError("Батьківська одиниця повинна бути вищого рівня.")

        if current_unit_id is not None and parent_id in self._collect_descendant_ids(connection, current_unit_id):
            raise ValueError("Не можна вкладати одиницю у власний дочірній вузол.")

    def _validate_children_relation(self, connection: sqlite3.Connection, unit_id: int, unit_type: str) -> None:
        child_rows = connection.execute(
            "SELECT unit_type FROM structure_units WHERE parent_id = ?",
            (unit_id,),
        ).fetchall()

        current_rank = _UNIT_TYPE_RANK[unit_type]
        for child_row in child_rows:
            if _UNIT_TYPE_RANK[child_row["unit_type"]] <= current_rank:
                raise ValueError("Новий вид одиниці не сумісний з наявними дочірніми вузлами.")

    def _collect_descendant_ids(self, connection: sqlite3.Connection, unit_id: int) -> set[int]:
        descendants: set[int] = set()
        pending = [unit_id]

        while pending:
            current_id = pending.pop()
            child_rows = connection.execute(
                "SELECT id FROM structure_units WHERE parent_id = ?",
                (current_id,),
            ).fetchall()
            for child_row in child_rows:
                child_id = int(child_row["id"])
                if child_id in descendants:
                    continue
                descendants.add(child_id)
                pending.append(child_id)

        return descendants

    def _next_sort_order(self, connection: sqlite3.Connection, parent_id: int | None) -> int:
        row = connection.execute(
            "SELECT COALESCE(MAX(sort_order), -1) AS max_sort_order FROM structure_units WHERE parent_id IS ?",
            (parent_id,),
        ).fetchone()
        return int(row["max_sort_order"]) + 1

    def _close_sort_order_gap(
        self,
        connection: sqlite3.Connection,
        parent_id: int | None,
        removed_sort_order: int,
        excluded_unit_id: int,
    ) -> None:
        connection.execute(
            """
            UPDATE structure_units
            SET sort_order = sort_order - 1
            WHERE parent_id IS ?
              AND sort_order > ?
              AND id != ?
            """,
            (parent_id, removed_sort_order, excluded_unit_id),
        )

    def _rebuild_sort_order(self, connection: sqlite3.Connection) -> None:
        parent_rows = connection.execute(
            "SELECT DISTINCT parent_id FROM structure_units ORDER BY parent_id"
        ).fetchall()

        for parent_row in parent_rows:
            parent_id = parent_row["parent_id"]
            rows = connection.execute(
                """
                SELECT id
                FROM structure_units
                WHERE parent_id IS ?
                ORDER BY name, id
                """,
                (parent_id,),
            ).fetchall()
            for sort_order, row in enumerate(rows):
                connection.execute(
                    "UPDATE structure_units SET sort_order = ? WHERE id = ?",
                    (sort_order, row["id"]),
                )

    def _get_unit_row_by_id(self, connection: sqlite3.Connection, unit_id: int) -> sqlite3.Row:
        row = connection.execute(
            """
            SELECT unit.id,
                   unit.name,
                     unit.short_name,
                   unit.unit_type,
                   unit.parent_id,
                     unit.sort_order,
                   parent.name AS parent_name
            FROM structure_units AS unit
            LEFT JOIN structure_units AS parent ON parent.id = unit.parent_id
            WHERE unit.id = ?
            """,
            (unit_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Організаційну одиницю не знайдено.")
        return row

    def _build_unit_record(self, row: sqlite3.Row) -> StructureUnitRecord:
        return StructureUnitRecord(
            unit_id=int(row["id"]),
            name=row["name"],
            short_name=row["short_name"],
            unit_type=row["unit_type"],
            parent_id=row["parent_id"],
            sort_order=int(row["sort_order"]),
            parent_name=row["parent_name"] or "",
        )
