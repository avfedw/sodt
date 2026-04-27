"""Локалізація для вкладки налаштувань."""


tab_settings = {
    "uk": {
        "name": "Налаштування",
        "title": "Перенос бази даних через Excel",
        "description": "Тут можна експортувати поточну базу даних у файл Excel або імпортувати дані з раніше збереженого Excel-файла.",
        "export_button": "Експорт в Excel",
        "import_button": "Імпорт з Excel",
        "file_dialog": {
            "export_title": "Експорт бази даних в Excel",
            "import_title": "Імпорт бази даних з Excel",
            "filter": "Файли Excel (*.xlsx);;Усі файли (*.*)",
            "default_export_name": "sodt-export.xlsx",
        },
        "messages": {
            "success_title": "Операцію виконано",
            "export_success": "Дані бази даних успішно експортовано в Excel.",
            "import_success": "Дані з Excel успішно імпортовано в базу даних.",
            "error_title": "Помилка переносу бази даних",
            "import_confirm": "Поточні дані в базі будуть замінені даними з вибраного Excel-файла. Продовжити?",
        },
    },
    "en": {
        "name": "Settings",
        "title": "Database transfer via Excel",
        "description": "Here you can export the current database to an Excel file or import data from a previously saved Excel file.",
        "export_button": "Export to Excel",
        "import_button": "Import from Excel",
        "file_dialog": {
            "export_title": "Export database to Excel",
            "import_title": "Import database from Excel",
            "filter": "Excel files (*.xlsx);;All files (*.*)",
            "default_export_name": "sodt-export.xlsx",
        },
        "messages": {
            "success_title": "Completed",
            "export_success": "The database data was exported to Excel successfully.",
            "import_success": "The Excel data was imported into the database successfully.",
            "error_title": "Database transfer error",
            "import_confirm": "The current database data will be replaced with the data from the selected Excel file. Continue?",
        },
    },
}


def name_for(locale: str) -> str:
    return tab_settings.get(locale, tab_settings["en"])["name"]


def title_for(locale: str) -> str:
    return tab_settings.get(locale, tab_settings["en"])["title"]


def description_for(locale: str) -> str:
    return tab_settings.get(locale, tab_settings["en"])["description"]


def export_button_text_for(locale: str) -> str:
    return tab_settings.get(locale, tab_settings["en"])["export_button"]


def import_button_text_for(locale: str) -> str:
    return tab_settings.get(locale, tab_settings["en"])["import_button"]


def file_dialog_texts_for(locale: str) -> dict:
    return tab_settings.get(locale, tab_settings["en"])["file_dialog"]


def messages_for(locale: str) -> dict:
    return tab_settings.get(locale, tab_settings["en"])["messages"]