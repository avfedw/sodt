"""Діалог стартового введення пароля до зашифрованої бази даних."""

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QMessageBox, QVBoxLayout

from .change_database_password_dialog import ChangeDatabasePasswordDialog


class DatabasePasswordDialog(QDialog):
    """Запитує пароль для відкриття або створення зашифрованої БД."""

    def __init__(self, database_state: str, parent=None):
        super().__init__(parent)
        self.database_state = database_state
        self.selected_action = "open"
        self._current_password = ""
        self._new_password = ""
        self.setWindowTitle("Доступ до бази даних")
        self.setModal(True)
        self.setMinimumWidth(440)
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        description_label = QLabel(self._description_text(), self)
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)

        form_layout = QFormLayout()

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Пароль", self.password_input)

        self.confirm_input = None
        if self.database_state in {"missing", "plaintext"}:
            self.confirm_input = QLineEdit(self)
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            confirm_label = "Підтвердження" if self.database_state == "missing" else "Підтвердження нового пароля"
            form_layout.addRow(confirm_label, self.confirm_input)

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.accepted.connect(self._accept_if_valid)
        button_box.rejected.connect(self.reject)
        if self.database_state == "encrypted":
            change_password_button = button_box.addButton("Змінити пароль", QDialogButtonBox.ButtonRole.ActionRole)
            change_password_button.clicked.connect(self._accept_change_password)
        main_layout.addWidget(button_box)

    def password(self) -> str:
        """Повертає поточне введене значення пароля."""

        return self.password_input.text()

    def new_password(self) -> str:
        """Повертає новий пароль, вибраний для перекодування БД."""

        return self._new_password

    def current_password_for_change(self) -> str:
        """Повертає поточний пароль, введений у діалозі зміни пароля."""

        return self._current_password

    def _description_text(self) -> str:
        if self.database_state == "missing":
            return "Введіть пароль для створення нової зашифрованої бази даних. Цей пароль стане ключем шифрування всієї бази."
        if self.database_state == "plaintext":
            return "Поточна база даних ще не зашифрована. Введіть пароль, яким буде виконано шифрування наявних даних."
        return "Введіть пароль для відкриття зашифрованої бази даних."

    def _accept_if_valid(self) -> None:
        self.selected_action = "open"
        password = self.password().strip()
        if not password:
            QMessageBox.warning(self, "Порожній пароль", "Пароль до бази даних не може бути порожнім.")
            return

        if self.confirm_input is not None and password != self.confirm_input.text().strip():
            QMessageBox.warning(self, "Невідповідність паролів", "Введені паролі не збігаються.")
            return

        self.accept()

    def _accept_change_password(self) -> None:
        change_dialog = ChangeDatabasePasswordDialog(self.password().strip(), self)
        if change_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.selected_action = "change_password"
        self._current_password = change_dialog.current_password()
        self._new_password = change_dialog.new_password()
        self.accept()