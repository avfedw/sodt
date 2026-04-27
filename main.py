"""Точка входу до настільного застосунку SODT."""

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from db.database import (
    DatabaseMigrationError,
    DatabasePasswordError,
    DatabaseRekeyError,
    change_database_password,
    get_database_state,
    initialize_database_access,
)
from dialogs.database_password_dialog import DatabasePasswordDialog
from views.main_window import MainWindow


def _request_database_access() -> bool:
    """Запитує пароль до БД перед створенням головного вікна."""

    while True:
        dialog = DatabasePasswordDialog(get_database_state())
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False

        try:
            if dialog.selected_action == "change_password":
                change_database_password(dialog.current_password_for_change(), dialog.new_password())
                QMessageBox.information(None, "Пароль змінено", "Пароль бази даних успішно змінено.")
                return True
            initialize_database_access(dialog.password())
            return True
        except (DatabasePasswordError, DatabaseMigrationError, DatabaseRekeyError) as error:
            QMessageBox.critical(None, "Помилка доступу до бази даних", str(error))


def main():
    """Створює Qt-застосунок, головне вікно та запускає цикл обробки подій."""

    app = QApplication(sys.argv)
    # Єдиний шрифт на рівні застосунку гарантує однаковий вигляд усіх вкладок і діалогів.
    app.setFont(QFont("Times New Roman", 11))

    if not _request_database_access():
        return 0

    window = MainWindow()
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    # Окремий виклик через guard дозволяє безпечно імпортувати модуль у тестах.
    sys.exit(main())
