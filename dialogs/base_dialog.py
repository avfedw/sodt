from PySide6.QtWidgets import QDialog


class CenteredDialog(QDialog):
    """Базовий діалог, який з'являється по центру головного вікна."""

    def showEvent(self, event):
        # Центруємо діалог саме після появи, коли його розмір уже обчислено Qt.
        super().showEvent(event)
        self._center_on_parent_window()

    def _center_on_parent_window(self):
        """Переміщує діалог у центр батьківського вікна, якщо воно відоме."""

        parent_window = self.parentWidget()
        if parent_window is None:
            return

        geometry = self.frameGeometry()
        geometry.moveCenter(parent_window.frameGeometry().center())
        self.move(geometry.topLeft())