"""Локалізація для вкладки історії призначень."""


tab_assignment_history = {
    "uk": {
        "name": "Історія призначень",
        "refresh_button": "Оновити",
        "empty_state": "Історія призначень ще порожня.",
        "position_filter": "Фільтр за посадою",
        "person_filter": "Фільтр за людиною",
        "headers": [
            "Скорочена назва",
            "Найменування посади",
            "Прізвище",
            "Ім'я та по батькові",
            "Номер наказу\nпризначення",
            "Дата наказу\nпризначення",
        ],
    },
    "en": {
        "name": "Assignment history",
        "refresh_button": "Refresh",
        "empty_state": "Assignment history is empty.",
        "position_filter": "Filter by position",
        "person_filter": "Filter by person",
        "headers": [
            "Short name",
            "Job title",
            "Surname",
            "Name and patronymic",
            "Appointment order\nnumber",
            "Appointment order\ndate",
        ],
    },
}


def name_for(locale: str) -> str:
    return tab_assignment_history.get(locale, tab_assignment_history["en"])["name"]


def refresh_button_text_for(locale: str) -> str:
    return tab_assignment_history.get(locale, tab_assignment_history["en"])["refresh_button"]


def empty_state_for(locale: str) -> str:
    return tab_assignment_history.get(locale, tab_assignment_history["en"])["empty_state"]


def position_filter_placeholder_for(locale: str) -> str:
    return tab_assignment_history.get(locale, tab_assignment_history["en"])["position_filter"]


def person_filter_placeholder_for(locale: str) -> str:
    return tab_assignment_history.get(locale, tab_assignment_history["en"])["person_filter"]


def headers_for(locale: str) -> list[str]:
    return tab_assignment_history.get(locale, tab_assignment_history["en"])["headers"]
