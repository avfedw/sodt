"""Допоміжні функції для однотипних полів дат у діалогах."""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit, QWidget


EMPTY_DATE = QDate(1900, 1, 1)


def create_date_input(parent: QWidget, value: str = "", allow_empty: bool = False, empty_text: str = "") -> QDateEdit:
    """Створює стандартне поле дати з однаковими параметрами відображення."""

    date_input = QDateEdit(parent)
    date_input.setCalendarPopup(True)
    date_input.setDisplayFormat("dd.MM.yyyy")

    if allow_empty:
        date_input.setMinimumDate(EMPTY_DATE)
        date_input.setSpecialValueText(empty_text)
        date_input.setDate(EMPTY_DATE)
        if value:
            date_input.setDate(QDate.fromString(value, "dd.MM.yyyy"))
    else:
        current_date = QDate.fromString(value, "dd.MM.yyyy")
        date_input.setDate(current_date if current_date.isValid() else QDate.currentDate())

    return date_input


def set_empty_date(date_input: QDateEdit, allow_empty: bool = False) -> None:
    """Повертає поле дати у порожній або поточний стан залежно від режиму."""

    if allow_empty:
        date_input.setDate(EMPTY_DATE)
        return

    date_input.setDate(QDate.currentDate())


def read_date_input_value(date_input: QDateEdit, allow_empty: bool = False) -> str:
    """Зчитує значення дати у внутрішньому строковому форматі застосунку."""

    if allow_empty and date_input.date() == EMPTY_DATE:
        return ""

    return date_input.date().toString("dd.MM.yyyy")