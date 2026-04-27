"""Діалог вибору нового пароля для перекодування бази даних."""

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QMessageBox, QVBoxLayout


class ChangeDatabasePasswordDialog(QDialog):
    """Збирає новий пароль для вже зашифрованої бази даних."""

    def __init__(self, initial_current_password: str = "", parent=None):
        super().__init__(parent)
        self._initial_current_password = initial_current_password
        self.setWindowTitle("Зміна пароля бази даних")
        self.setModal(True)
        self.setMinimumWidth(420)
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        description_label = QLabel(
            "Введіть поточний і новий пароль. Після підтвердження база даних буде перекодована на новий ключ шифрування.",
            self,
        )
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)

        form_layout = QFormLayout()

        self.current_password_input = QLineEdit(self)
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password_input.setText(self._initial_current_password)
        form_layout.addRow("Поточний пароль", self.current_password_input)

        self.new_password_input = QLineEdit(self)
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Новий пароль", self.new_password_input)

        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Підтвердження", self.confirm_password_input)

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.accepted.connect(self._accept_if_valid)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def new_password(self) -> str:
        """Повертає новий пароль після успішної перевірки форми."""

        return self.new_password_input.text()

    def current_password(self) -> str:
        """Повертає поточний пароль після успішної перевірки форми."""

        return self.current_password_input.text()

    def _accept_if_valid(self) -> None:
        current_password = self.current_password().strip()
        new_password = self.new_password().strip()
        confirm_password = self.confirm_password_input.text().strip()

        if not current_password:
            QMessageBox.warning(self, "Поточний пароль", "Поточний пароль не може бути порожнім.")
            return

        if not new_password:
            QMessageBox.warning(self, "Порожній пароль", "Новий пароль не може бути порожнім.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Невідповідність паролів", "Новий пароль і підтвердження не збігаються.")
            return

        self.accept()