"""Локалізація для вкладки номенклатури."""


tab_Nomenclature = {
    "uk": {
        "name": "Номенклатура",
        "add_button": "Додати рядок",
        "refresh_button": "Оновити",
        "edit_button": "Редагувати",
        "empty_state": "Записи номенклатури ще не додані.",
        "validation_error_title": "Помилка перевірки",
        "headers": [
            "Статус",
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
            "Номер наказу\nпризначення",
            "Дата наказу\nпризначення",
        ],
        "dialog": {
            "add_title": "Додавання рядка номенклатури",
            "edit_title": "Редагування рядка номенклатури",
            "structure_unit": "Одиниця структури",
            "job_title": "Найменування посади",
            "nomenclature_number": "Номер по номенклатурі",
            "admission_form": "Форма допуску",
            "admission_form_options": ["Ф-1", "Ф-2", "Ф-3"],
            "default_admission_form": "Ф-2",
            "surname": "Прізвище",
            "name_patronymic": "Ім'я та по батькові",
            "save": "Зберегти",
            "cancel": "Скасувати",
            "select_row_warning": "Спочатку виберіть рядок номенклатури.",
        },
        "card_picker": {
            "title": "Вибір людини з карток",
            "headers": ["Прізвище", "Ім'я", "По батькові", "Форма", "Статус"],
            "surname_filter_placeholder": "Фільтр за прізвищем",
            "appointment_order_number": "Номер наказу призначення",
            "appointment_order_date": "Дата наказу призначення",
            "empty_date": "Не вказано",
            "select": "Вибрати",
            "vacant": "Посада вакантна",
            "vacancy_order_number_title": "Посада вакантна",
            "vacancy_order_number_label": "Номер наказу на здачу посади",
            "cancel": "Скасувати",
            "select_card_warning": "Спочатку виберіть людину з карток.",
        },
    },
    "en": {
        "name": "Nomenclature",
        "add_button": "Add row",
        "refresh_button": "Refresh",
        "edit_button": "Edit",
        "empty_state": "No nomenclature records have been added yet.",
        "validation_error_title": "Validation error",
        "headers": [
            "Status",
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
            "Appointment order\nnumber",
            "Appointment order\ndate",
        ],
        "dialog": {
            "add_title": "Add nomenclature row",
            "edit_title": "Edit nomenclature row",
            "structure_unit": "Structure unit",
            "job_title": "Job title",
            "nomenclature_number": "Nomenclature number",
            "admission_form": "Admission form",
            "admission_form_options": ["F-1", "F-2", "F-3"],
            "default_admission_form": "F-2",
            "surname": "Surname",
            "name_patronymic": "Name and patronymic",
            "save": "Save",
            "cancel": "Cancel",
            "select_row_warning": "Select a nomenclature row first.",
        },
        "card_picker": {
            "title": "Choose person from cards",
            "headers": ["Surname", "Name", "Patronymic", "Form", "Status"],
            "surname_filter_placeholder": "Filter by surname",
            "appointment_order_number": "Appointment order number",
            "appointment_order_date": "Appointment order date",
            "empty_date": "Not specified",
            "select": "Select",
            "vacant": "Vacant position",
            "vacancy_order_number_title": "Vacant position",
            "vacancy_order_number_label": "Position surrender order number",
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


def refresh_button_text_for(locale: str) -> str:
    return tab_Nomenclature.get(locale, tab_Nomenclature["en"])["refresh_button"]


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
