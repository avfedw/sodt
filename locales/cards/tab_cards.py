"""Локалізація для вкладки Cards."""

# Верхньорівневі підписи самої вкладки та головних кнопок.
tab_Cards = {
    "uk": {
        "name": "Картки",
        "add_button": "Додати картку",
        "edit_button": "Редагувати",
        "validation_error_title": "Помилка перевірки",
    },
    "en": {
        "name": "Cards",
        "add_button": "Add card",
        "edit_button": "Edit",
        "validation_error_title": "Validation error",
    },
}

tab_Cards_admission = {
    "uk": {"name": "Допуск", "add_button": "Додати допуск", "edit_button": "Редагувати"},
    "en": {"name": "Admission", "add_button": "Add admission", "edit_button": "Edit"},
}

tab_Cards_access = {
    "uk": {"name": "Доступ", "add_button": "Додати доступ", "edit_button": "Редагувати"},
    "en": {"name": "Access", "add_button": "Add access", "edit_button": "Edit"},
}

# Тексти нижньої таблиці допусків і пов'язаних з нею дій.
tab_Cards_admission_dialog = {
    "uk": {
        "add_title": "Надання/скасування допуску",
        "edit_title": "Надання/скасування допуску",
        "escort_number": "Номер супроводу",
        "escort_date": "Дата супроводу",
        "response_number": "Номер відповіді",
        "response_date": "Дата відповіді",
        "order_number": "Номер розпорядження",
        "order_date": "Дата розпорядження",
        "admission_form": "Форма допуску",
        "admission_form_options": ["Ф-1", "Ф-2", "Ф-3"],
        "default_admission_form": "Ф-2",
        "admission_status": "Статус",
        "admission_status_options": ["надано", "скасовано"],
        "empty_date": "Не вказано",
        "save": "Зберегти",
        "cancel": "Скасувати",
        "select_card_warning": "Спочатку виберіть картку.",
        "select_admission_warning": "Спочатку виберіть запис у нижній таблиці.",
    },
    "en": {
        "add_title": "Grant/revoke admission",
        "edit_title": "Grant/revoke admission",
        "escort_number": "Escort number",
        "escort_date": "Escort date",
        "response_number": "Response number",
        "response_date": "Response date",
        "order_number": "Order number",
        "order_date": "Order date",
        "admission_form": "Admission form",
        "admission_form_options": ["F-1", "F-2", "F-3"],
        "default_admission_form": "F-2",
        "admission_status": "Status",
        "admission_status_options": ["granted", "revoked"],
        "empty_date": "Not specified",
        "save": "Save",
        "cancel": "Cancel",
        "select_card_warning": "Select a card first.",
        "select_admission_warning": "Select a row in the lower table first.",
    },
}

tab_Cards_table_headers = {
    "uk": ["Літера - номер", "Дата", "Прізвище", "Ім'я", "По батькові", "Форма", "Документ / подія", "Статус", "Примітка"],
    "en": ["Letter - Number", "Date", "Surname", "Name", "Patronymic", "Form", "Document / Event", "Status", "Note"],
}

# Заголовки таблиць тримаємо окремо від решти текстів,
# бо вони часто використовуються незалежно від діалогів.
tab_Cards_admission_headers = {
    "uk": ["Номер супровіду", "Дата супровіду", "Номер відповіді", "Дата відповіді", "Номер розпорядження", "Дата розпорядження", "Форма допуску", "Статус"],
    "en": ["Escort number", "Escort date", "Response number", "Response date", "Order number", "Order date", "Admission Form", "Status"],
}

tab_Cards_access_headers = {
    "uk": ["Дата", "Номер наказу", "Доступ", "Статус"],
    "en": ["Date", "Order number", "Access", "Status"],
}

tab_Cards_access_dialog = {
    "uk": {
        "add_title": "Надання/скасування доступу",
        "edit_title": "Надання/скасування доступу",
        "access_date": "Дата",
        "order_number": "Номер наказу",
        "access_type": "Доступ",
        "access_type_options": ["ОВ", "ЦТ", "Т"],
        "status": "Статус",
        "status_options": ["надано", "скасовано"],
        "save": "Зберегти",
        "cancel": "Скасувати",
        "select_card_warning": "Спочатку виберіть картку.",
        "select_access_warning": "Спочатку виберіть запис у таблиці доступу.",
    },
    "en": {
        "add_title": "Grant/revoke access",
        "edit_title": "Grant/revoke access",
        "access_date": "Date",
        "order_number": "Order number",
        "access_type": "Access",
        "access_type_options": ["ОВ", "ЦТ", "Т"],
        "status": "Status",
        "status_options": ["granted", "revoked"],
        "save": "Save",
        "cancel": "Cancel",
        "select_card_warning": "Select a card first.",
        "select_access_warning": "Select a row in the access table first.",
    },
}

# Локалізація діалогу створення картки.
tab_Cards_add_dialog = {
    "uk": {
        "title": "Додавання картки",
        "surname": "Прізвище",
        "name": "Ім'я",
        "patronymic": "По батькові",
        "save": "Зберегти",
        "cancel": "Скасувати",
    },
    "en": {
        "title": "Add card",
        "surname": "Surname",
        "name": "Name",
        "patronymic": "Patronymic",
        "save": "Save",
        "cancel": "Cancel",
    },
}

# Найбільший словник стосується редагування картки й піддіалогів дій,
# тому всі пов'язані тексти зібрані тут в одному місці.
tab_Cards_edit_dialog = {
    "uk": {
        "title": "Редагування картки",
        "surname": "Прізвище",
        "name": "Ім'я",
        "patronymic": "По батькові",
        "number": "Номер у літері",
        "card_date": "Дата картки",
        "workflow_status": "Статус",
        "document_kind": "Тип документа або події",
        "document_number": "Номер документа",
        "document_date": "Дата документа або події",
        "document_target": "Куди відправлено",
        "service_note": "Службова примітка",
        "user_note": "Примітка",
        "inactive_state": "Стан картки",
        "inactive_messages": {
            "surname_changed": "Ця картка неактивна, бо після зміни прізвища створено нову поточну картку.",
            "sent": "Картку відправлено. Редагування недоступне, але її можна позначити повернутою.",
            "destroyed": "Картку знищено. Редагування недоступне.",
        },
        "empty_date": "Не вказано",
        "send_button": "Відправити",
        "destroy_button": "Знищити",
        "return_button": "Позначити повернутою",
        "document_kind_options": [
            ("", "Не вказано"),
            ("escort", "Супровід"),
            ("act", "Акт"),
            ("planned_cancellation", "Планове скасування"),
            ("planned_destruction", "Планове знищення"),
        ],
        "workflow_status_options": [
            ("", "Не вказано"),
            ("на скасування", "На скасування"),
            ("на знищення", "На знищення"),
            ("знищено", "Знищено"),
            ("відправлено", "Відправлено"),
        ],
        "send_dialog": {
            "title": "Відправлення картки",
            "number": "Номер супроводу",
            "date": "Дата супроводу",
            "target": "Установа",
            "confirm": "Відправити",
            "cancel": "Скасувати",
        },
        "destroy_dialog": {
            "title": "Знищення картки",
            "number": "Номер акту",
            "date": "Дата акту",
            "confirm": "Знищити",
            "cancel": "Скасувати",
        },
        "return_dialog": {
            "title": "Повернення картки",
            "number": "Номер листа",
            "date": "Дата листа",
            "target": "З якої установи",
            "confirm": "Повернути",
            "cancel": "Скасувати",
        },
        "save": "Зберегти",
        "cancel": "Скасувати",
    },
    "en": {
        "title": "Edit card",
        "surname": "Surname",
        "name": "Name",
        "patronymic": "Patronymic",
        "number": "Number within letter",
        "card_date": "Card date",
        "workflow_status": "Status",
        "document_kind": "Document or event type",
        "document_number": "Document number",
        "document_date": "Document or event date",
        "document_target": "Sent to",
        "service_note": "Service note",
        "user_note": "Note",
        "inactive_state": "Card state",
        "inactive_messages": {
            "surname_changed": "This card is inactive because a new current card was created after surname change.",
            "sent": "The card has been sent. Editing is unavailable, but it can be marked as returned.",
            "destroyed": "The card has been destroyed. Editing is unavailable.",
        },
        "empty_date": "Not specified",
        "send_button": "Send",
        "destroy_button": "Destroy",
        "return_button": "Mark as returned",
        "document_kind_options": [
            ("", "Not specified"),
            ("escort", "Escort"),
            ("act", "Act"),
            ("planned_cancellation", "Planned cancellation"),
            ("planned_destruction", "Planned destruction"),
        ],
        "workflow_status_options": [
            ("", "Not specified"),
            ("на скасування", "For cancellation"),
            ("на знищення", "For destruction"),
            ("знищено", "Destroyed"),
            ("відправлено", "Sent"),
        ],
        "send_dialog": {
            "title": "Send card",
            "number": "Escort number",
            "date": "Escort date",
            "target": "Institution",
            "confirm": "Send",
            "cancel": "Cancel",
        },
        "destroy_dialog": {
            "title": "Destroy card",
            "number": "Act number",
            "date": "Act date",
            "confirm": "Destroy",
            "cancel": "Cancel",
        },
        "return_dialog": {
            "title": "Return card",
            "number": "Return letter number",
            "date": "Return date",
            "target": "Institution",
            "confirm": "Return",
            "cancel": "Cancel",
        },
        "save": "Save",
        "cancel": "Cancel",
    },
}


def get_tab_cards_table_headers(locale: str) -> list:
    return tab_Cards_table_headers.get(locale, tab_Cards_table_headers["en"])


def get_tab_cards_admission_headers(locale: str) -> list:
    return tab_Cards_admission_headers.get(locale, tab_Cards_admission_headers["en"])


def get_tab_cards_access_headers(locale: str) -> list:
    return tab_Cards_access_headers.get(locale, tab_Cards_access_headers["en"])


def name_for(locale: str) -> str:
    return tab_Cards.get(locale, tab_Cards["en"])["name"]


def add_button_text_for(locale: str) -> str:
    return tab_Cards.get(locale, tab_Cards["en"])["add_button"]


def edit_button_text_for(locale: str) -> str:
    return tab_Cards.get(locale, tab_Cards["en"])["edit_button"]


def admission_add_button_text_for(locale: str) -> str:
    return tab_Cards_admission.get(locale, tab_Cards_admission["en"])["add_button"]


def admission_edit_button_text_for(locale: str) -> str:
    return tab_Cards_admission.get(locale, tab_Cards_admission["en"])["edit_button"]


def admission_name_for(locale: str) -> str:
    return tab_Cards_admission.get(locale, tab_Cards_admission["en"])["name"]


def access_add_button_text_for(locale: str) -> str:
    return tab_Cards_access.get(locale, tab_Cards_access["en"])["add_button"]


def access_edit_button_text_for(locale: str) -> str:
    return tab_Cards_access.get(locale, tab_Cards_access["en"])["edit_button"]


def access_name_for(locale: str) -> str:
    return tab_Cards_access.get(locale, tab_Cards_access["en"])["name"]


def validation_error_title_for(locale: str) -> str:
    return tab_Cards.get(locale, tab_Cards["en"])["validation_error_title"]


def add_dialog_texts_for(locale: str) -> dict:
    return tab_Cards_add_dialog.get(locale, tab_Cards_add_dialog["en"])


def edit_dialog_texts_for(locale: str) -> dict:
    return tab_Cards_edit_dialog.get(locale, tab_Cards_edit_dialog["en"])


def admission_dialog_texts_for(locale: str) -> dict:
    return tab_Cards_admission_dialog.get(locale, tab_Cards_admission_dialog["en"])


def access_dialog_texts_for(locale: str) -> dict:
    return tab_Cards_access_dialog.get(locale, tab_Cards_access_dialog["en"])
