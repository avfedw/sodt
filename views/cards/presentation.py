"""Допоміжні функції представлення для вкладки карток."""

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

if TYPE_CHECKING:
    from db.cards_repository import CardRecord


# Індекси колонок винесені в константи, щоб логіка висоти рядка й оформлення
# не залежала від "магічних чисел" усередині великого віджета вкладки.
DOCUMENT_EVENT_COLUMN = 6
STATUS_COLUMN = 7
TABLE_ITEM_ALIGNMENT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
# Єдиний stylesheet дозволяє зберігати однаковий вигляд усіх таблиць карток.
TABLE_GRID_STYLESHEET = """
    QTableWidget {
        gridline-color: #2f2f2f;
        border: 1px solid #2f2f2f;
    }
    QHeaderView::section {
        border: 1px solid #2f2f2f;
        padding: 4px;
    }
"""


def cards_row_height(value: str) -> int:
    """Повертає висоту рядка з урахуванням кількості рядків у клітинці."""

    explicit_line_count = max(1, value.count("\n") + 1) if value else 1
    return 30 + (explicit_line_count - 1) * 12


def card_row_colors(card: "CardRecord") -> tuple[QColor | None, QColor | None]:
    """Повертає фон і текст для рядка картки залежно від її стану."""

    # Колір тут не просто декоративний: він швидко підсвічує оператору
    # різні службові сценарії без читання повного тексту статусу.
    if card.lifecycle_state == "destroyed":
        return QColor("#f4b6c2"), QColor("#6b1111")
    if card.lifecycle_state == "sent":
        return QColor("#0b5d1e"), QColor("#f4df58")
    if card.access_revoked_after_grant:
        return QColor("#3f3f3f"), QColor("#ff2d2d")
    if card.admission_revoked_after_grant:
        return QColor("#6f1010"), QColor("#f5ecb8")
    if card.has_active_admission and not card.has_active_access:
        return QColor("#ff2d2d"), QColor("#0b5d1e")
    return None, None