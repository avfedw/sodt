"""Спільні валідатори для полів введення в діалогах."""

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QWidget


UKRAINIAN_LETTERS = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя"


def create_ukrainian_name_validator(parent: QWidget) -> QRegularExpressionValidator:
    """Повертає валідатор для ПІБ з українськими літерами та апострофом."""

    return QRegularExpressionValidator(
        QRegularExpression(f"[{UKRAINIAN_LETTERS}'’ ]*"),
        parent,
    )