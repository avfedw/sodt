"""Локалізація для вкладки довідки 14."""


tab_certificate14 = {
    "uk": {
        "name": "Довідка 14",
        "add_button": "Додати довідку",
        "refresh_button": "Оновити",
        "edit_button": "Редагувати",
        "export_button": "Експорт",
        "empty_state": "Записи довідки 14 ще не додані.",
        "validation_error_title": "Помилка перевірки",
        "headers": [
            "Номер",
            "Дата довідки",
            "Прізвище, ім'я, по батькові",
            "Термін дії",
            "Прізвище отримувача",
            "У нас",
            "Примітка",
        ],
        "dialog": {
            "add_title": "Додавання довідки 14",
            "edit_title": "Редагування довідки 14",
            "number": "Номер",
            "certificate_date": "Дата довідки",
            "full_name": "Прізвище, ім'я, по батькові",
            "expiration_date": "Термін дії",
            "recipient_surname": "Прізвище отримувача",
            "returned": "У нас",
            "note": "Примітка",
            "select_row_warning": "Спочатку виберіть запис довідки 14.",
        },
        "card_picker": {
            "title": "Вибір картки для довідки 14",
            "headers": ["Прізвище", "Ім'я", "По батькові", "Форма", "Статус"],
            "surname_filter_placeholder": "Фільтр за прізвищем",
            "select_card_warning": "Спочатку виберіть картку.",
        },
        "export_dialog": {
            "select_rows_warning": "Спочатку виберіть одну або кілька довідок 14.",
            "save_title": "Експорт довідок 14",
            "save_filter": "Файли Word (*.docx);;Усі файли (*.*)",
            "default_file_name": "Довідки-Ф14.docx",
            "success_title": "Операцію виконано",
            "success_message": "Довідки 14 успішно експортовано.",
        },
    },
    "en": {
        "name": "Certificate 14",
        "add_button": "Add certificate",
        "refresh_button": "Refresh",
        "edit_button": "Edit",
        "export_button": "Export",
        "empty_state": "No certificate 14 records have been added yet.",
        "validation_error_title": "Validation error",
        "headers": ["Number", "Certificate date", "Full name", "Expiration date", "Recipient surname", "In stock", "Note"],
        "dialog": {
            "add_title": "Add certificate 14",
            "edit_title": "Edit certificate 14",
            "number": "Number",
            "certificate_date": "Certificate date",
            "full_name": "Full name",
            "expiration_date": "Expiration date",
            "recipient_surname": "Recipient surname",
            "returned": "In stock",
            "note": "Note",
            "select_row_warning": "Select a certificate 14 record first.",
        },
        "card_picker": {
            "title": "Choose a card for certificate 14",
            "headers": ["Surname", "Name", "Patronymic", "Form", "Status"],
            "surname_filter_placeholder": "Filter by surname",
            "select_card_warning": "Select a card first.",
        },
        "export_dialog": {
            "select_rows_warning": "Select one or more certificate 14 records first.",
            "save_title": "Export certificates 14",
            "save_filter": "Word files (*.docx);;All files (*.*)",
            "default_file_name": "Certificate14.docx",
            "success_title": "Completed",
            "success_message": "Certificates 14 exported successfully.",
        },
    },
}


def name_for(locale: str) -> str:
    return tab_certificate14.get(locale, tab_certificate14["en"])["name"]


def add_button_text_for(locale: str) -> str:
    return tab_certificate14.get(locale, tab_certificate14["en"])["add_button"]


def refresh_button_text_for(locale: str) -> str:
    return tab_certificate14.get(locale, tab_certificate14["en"])["refresh_button"]


def edit_button_text_for(locale: str) -> str:
    return tab_certificate14.get(locale, tab_certificate14["en"])["edit_button"]


def export_button_text_for(locale: str) -> str:
    return tab_certificate14.get(locale, tab_certificate14["en"])["export_button"]


def empty_state_for(locale: str) -> str:
    return tab_certificate14.get(locale, tab_certificate14["en"])["empty_state"]


def validation_error_title_for(locale: str) -> str:
    return tab_certificate14.get(locale, tab_certificate14["en"])["validation_error_title"]


def headers_for(locale: str) -> list[str]:
    return tab_certificate14.get(locale, tab_certificate14["en"])["headers"]


def dialog_texts_for(locale: str) -> dict:
    return tab_certificate14.get(locale, tab_certificate14["en"])["dialog"]


def card_picker_texts_for(locale: str) -> dict:
    return tab_certificate14.get(locale, tab_certificate14["en"])["card_picker"]


def export_dialog_texts_for(locale: str) -> dict:
    return tab_certificate14.get(locale, tab_certificate14["en"])["export_dialog"]