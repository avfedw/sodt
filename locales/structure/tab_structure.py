"""Локалізація для вкладки структури."""


tab_Structure = {
    "uk": {
        "name": "Структура",
        "add_button": "Додати одиницю",
        "add_child_button": "Додати дочірню",
        "edit_button": "Редагувати",
        "delete_button": "Видалити",
        "empty_state": "Структура підприємства поки порожня.",
        "headers": ["Назва", "Скорочена назва", "Вид одиниці"],
        "validation_error_title": "Помилка перевірки",
        "type_labels": {
            "section": "Розділ",
            "group": "Група",
            "department": "Підрозділ",
            "division": "Відділення",
            "radio_station": "Радіостанція",
        },
        "dialog": {
            "add_title": "Додавання організаційної одиниці",
            "edit_title": "Редагування організаційної одиниці",
            "name": "Назва",
            "short_name": "Скорочена назва",
            "unit_type": "Вид одиниці",
            "parent": "Батьківська одиниця",
            "no_parent": "Без батьківської одиниці",
            "save": "Зберегти",
            "cancel": "Скасувати",
            "delete_confirmation_title": "Видалення одиниці",
            "delete_confirmation_text": "Видалити вибрану організаційну одиницю?",
            "select_unit_warning": "Спочатку виберіть організаційну одиницю.",
            "no_child_type_warning": "Для вибраної одиниці вже немає нижчого рівня для дочірнього вузла.",
        },
    },
    "en": {
        "name": "Structure",
        "add_button": "Add unit",
        "add_child_button": "Add child unit",
        "edit_button": "Edit",
        "delete_button": "Delete",
        "empty_state": "The enterprise structure is empty.",
        "headers": ["Name", "Short name", "Unit type"],
        "validation_error_title": "Validation error",
        "type_labels": {
            "section": "Section",
            "group": "Group",
            "department": "Department",
            "division": "Division",
            "radio_station": "Radio station",
        },
        "dialog": {
            "add_title": "Add organizational unit",
            "edit_title": "Edit organizational unit",
            "name": "Name",
            "short_name": "Short name",
            "unit_type": "Unit type",
            "parent": "Parent unit",
            "no_parent": "No parent unit",
            "save": "Save",
            "cancel": "Cancel",
            "delete_confirmation_title": "Delete unit",
            "delete_confirmation_text": "Delete the selected organizational unit?",
            "select_unit_warning": "Select an organizational unit first.",
            "no_child_type_warning": "The selected unit already has the lowest possible child level.",
        },
    },
}


def name_for(locale: str) -> str:
    return tab_Structure.get(locale, tab_Structure["en"])["name"]


def add_button_text_for(locale: str) -> str:
    return tab_Structure.get(locale, tab_Structure["en"])["add_button"]


def edit_button_text_for(locale: str) -> str:
    return tab_Structure.get(locale, tab_Structure["en"])["edit_button"]


def add_child_button_text_for(locale: str) -> str:
    return tab_Structure.get(locale, tab_Structure["en"])["add_child_button"]


def delete_button_text_for(locale: str) -> str:
    return tab_Structure.get(locale, tab_Structure["en"])["delete_button"]


def empty_state_text_for(locale: str) -> str:
    return tab_Structure.get(locale, tab_Structure["en"])["empty_state"]


def headers_for(locale: str) -> list[str]:
    return tab_Structure.get(locale, tab_Structure["en"])["headers"]


def validation_error_title_for(locale: str) -> str:
    return tab_Structure.get(locale, tab_Structure["en"])["validation_error_title"]


def dialog_texts_for(locale: str) -> dict:
    return tab_Structure.get(locale, tab_Structure["en"])["dialog"]


def type_labels_for(locale: str) -> dict[str, str]:
    return tab_Structure.get(locale, tab_Structure["en"])["type_labels"]
