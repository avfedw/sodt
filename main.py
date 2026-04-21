"""Точка входу до настільного застосунку SODT."""

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from views.main_window import MainWindow


def main():
    """Створює Qt-застосунок, головне вікно та запускає цикл обробки подій."""

    app = QApplication(sys.argv)
    # Єдиний шрифт на рівні застосунку гарантує однаковий вигляд усіх вкладок і діалогів.
    app.setFont(QFont("Times New Roman", 11))
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    # Окремий виклик через guard дозволяє безпечно імпортувати модуль у тестах.
    main()
