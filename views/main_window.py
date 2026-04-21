from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMainWindow, QTabWidget
from .cards import TabCards
from locales import get_tab_cards_name


class MainWindow(QMainWindow):
    """Головне вікно застосунку з контейнером вкладок."""

    def __init__(self):
        super().__init__()
        # Перший показ обробляємо окремо, щоб гарантовано розгорнути вікно,
        # навіть якщо окремі платформи ігнорують початковий WindowState.
        self._maximize_on_first_show = True
        self.setWindowTitle("SODT")
        self._init_ui()
        self._configure_window()

    def _init_ui(self):
        """Створює базову структуру вкладок і підключає доступні розділи."""

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        # Кожна вкладка підключається через власний пакет,
        # щоб зі зростанням проєкту код не збирався в одному каталозі.
        cards_tab = TabCards(self)
        self.tabs.addTab(cards_tab, get_tab_cards_name())

    def _configure_window(self):
        """Налаштовує стартову геометрію головного вікна відносно поточного екрана."""

        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            self.setGeometry(screen.availableGeometry())

        self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)

    def showEvent(self, event):
        super().showEvent(event)

        if self._maximize_on_first_show:
            self._maximize_on_first_show = False
            self.showMaximized()

    def center_dialog(self, dialog):
        """Центрує дочірній діалог відносно рамки головного вікна."""

        geometry = dialog.frameGeometry()
        geometry.moveCenter(self.frameGeometry().center())
        dialog.move(geometry.topLeft())
