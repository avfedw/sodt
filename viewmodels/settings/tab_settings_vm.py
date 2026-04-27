"""ViewModel для вкладки налаштувань."""

from db.database import export_database_copy, import_database_copy


class TabSettingsViewModel:
    """Координує тексти та дії вкладки налаштувань."""

    def __init__(self):
        self._load_texts()

    def _load_texts(self) -> None:
        try:
            from locales import (
                get_tab_settings_description_text,
                get_tab_settings_export_button_text,
                get_tab_settings_file_dialog_texts,
                get_tab_settings_import_button_text,
                get_tab_settings_messages,
                get_tab_settings_name,
                get_tab_settings_title_text,
            )

            self.name = get_tab_settings_name()
            self.title_text = get_tab_settings_title_text()
            self.description_text = get_tab_settings_description_text()
            self.export_button_text = get_tab_settings_export_button_text()
            self.import_button_text = get_tab_settings_import_button_text()
            self.file_dialog_texts = get_tab_settings_file_dialog_texts()
            self.messages = get_tab_settings_messages()
        except Exception:
            self.name = "Settings"
            self.title_text = "Database transfer"
            self.description_text = "Import or export the database file."
            self.export_button_text = "Export database"
            self.import_button_text = "Import database"
            self.file_dialog_texts = {
                "export_title": "Export database",
                "import_title": "Import database",
                "filter": "SQLite files (*.sqlite3);;All files (*.*)",
                "default_export_name": "sodt-export.sqlite3",
            }
            self.messages = {
                "success_title": "Completed",
                "export_success": "The database copy was exported successfully.",
                "import_success": "The database was imported successfully.",
                "error_title": "Database transfer error",
                "import_confirm": "The current database will be replaced with the selected file. Continue?",
            }

    def export_database(self, destination_path: str) -> None:
        export_database_copy(destination_path)

    def import_database(self, source_path: str) -> None:
        import_database_copy(source_path)