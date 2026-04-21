from PySide6.QtWidgets import QDialog


class CenteredDialog(QDialog):
    """Базовий діалог, який з'являється по центру головного вікна."""

    def showEvent(self, event):
        super().showEvent(event)
        self._center_on_parent_window()

    def _center_on_parent_window(self):
        parent_window = self.parentWidget()
        if parent_window is None:
            return

        geometry = self.frameGeometry()
        geometry.moveCenter(parent_window.frameGeometry().center())
        self.move(geometry.topLeft())