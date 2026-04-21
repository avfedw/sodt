"""Локалізація для вкладки номенклатури."""


tab_Nomenclature = {
    "uk": {
        "name": "Номенклатура",
        "add_button": "Додати рядок",
        "edit_button": "Редагувати",
        "empty_state": "Записи номенклатури ще не додані.",
        "validation_error_title": "Помилка перевірки",
        "headers": [
            "Скорочена назва",
            "Найменування посади",
            "Номер по номенклатурі",
            "Форма допуску",
            "Прізвище",
            "Ім'я та по батькові",
            "Розділ",
            "Група",
            "Підрозділ",
            "Відділення",
            "Радіостанція",
        ],
        "dialog": {
            "add_title": "Додавання рядка номенклатури",
            "edit_title": "Редагування рядка номенклатури",
            "structure_unit": "Одиниця структури",
            "job_title": "Найменування посади",
            "nomenclature_number": "Номер по номенклатурі",
            "admission_form": "Форма допуску",
            "admission_form_options": ["Ф-1", "Ф-2", "Ф-3"],
            "surname": "Прізвище",
            "name_patronymic": "Ім'я та по батькові",
            "save": "Зберегти",
            "cancel": "Скасувати",
            "select_row_warning": "Спочатку виберіть рядок номенклатури.",
        },
        "card_picker": {
            "title": "Вибір людини з карток",
            "headers": ["Прізвище", "Ім'я", "По батькові", "Форма", "Статус"],
            "select": "Вибрати",
            "cancel": "Скасувати",
            "select_card_warning": "Спочатку виберіть людину з карток.",
        },
    },
    "en": {
        "name": "Nomenclature",
        "add_button": "Add row",
        "edit_button": "Edit",
        "empty_state": "No nomenclature records have been added yet.",
        "validation_error_title": "Validation error",
        "headers": [
            "Short name",
            "Job title",
            "Nomenclature number",
            "Admission form",
            "Surname",
            "Name and patronymic",
            "Section",
            "Group",
            "Department",
            "Division",
            "Radio station",
        ],
        "dialog": {
            "add_title": "Add nomenclature row",
            "edit_title": "Edit nomenclature row",
            "structure_unit": "Structure unit",
            "job_title": "Job title",
            "nomenclature_number": "Nomenclature number",
            "admission_form": "Admission form",
            "admission_form_options": ["F-1", "F-2", "F-3"],
            "surname": "Surname",
            "name_patronymic": "Name and patronymic",
            "save": "Save",
            "cancel": "Cancel",
            "select_row_warning": "Select a nomenclature row first.",
        },
        "card_picker": {
            "title": "Choose person from cards",
            "headers": ["Surname", "Name", "Patronymic", "Form", "Status"],
            "select": "Select",
            "cancel": "Cancel",
            "select_card_warning": "Select a person from cards first.",
        },
    },
}


def name_for(locale: str) -> str:
    return tab_Nomenclature.get(locale, tab_Nomenclature["en"])["name"]


def empty_state_for(locale: str) -> str:
    return tab_Nomenclature.get(locale, tab_Nomenclature["en"])["empty_state"]


def add_button_text_for(locale: str) -> str:
    return tab_Nomenclature.get(locale, tab_Nomenclature["en"])["add_button"]


def edit_button_text_for(locale: str) -> str:
    return tab_Nomenclature.get(locale, tab_Nomenclature["en"])["edit_button"]


def validation_error_title_for(locale: str) -> str:
    return tab_Nomenclature.get(locale, tab_Nomenclature["en"])["validation_error_title"]


def headers_for(locale: str) -> list[str]:
    return tab_Nomenclature.get(locale, tab_Nomenclature["en"])["headers"]


def dialog_texts_for(locale: str) -> dict:
    return tab_Nomenclature.get(locale, tab_Nomenclature["en"])["dialog"]


def card_picker_texts_for(locale: str) -> dict:
    return tab_Nomenclature.get(locale, tab_Nomenclature["en"])["card_picker"]
