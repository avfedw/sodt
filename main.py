"""Точка входу до настільного застосунку SODT."""

import sys

from PySide6.QtWidgets import QApplication

from views.main_window import MainWindow


def main():
    """Створює Qt-застосунок, головне вікно та запускає цикл обробки подій."""

    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    # Окремий виклик через guard дозволяє безпечно імпортувати модуль у тестах.
    main()
