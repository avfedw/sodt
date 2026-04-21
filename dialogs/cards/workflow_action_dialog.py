from PySide6.QtWidgets import QDialogButtonBox, QLabel, QLineEdit, QSizePolicy, QVBoxLayout, QWidget

from ..base_dialog import CenteredDialog
from ..helpers import create_date_input, read_date_input_value


class WorkflowActionDialog(CenteredDialog):
    """Піддіалог для дій відправлення або знищення картки."""

    def __init__(self, texts: dict, requires_target: bool, parent=None):
        super().__init__(parent)
        self.texts = texts
        # Одне й те саме вікно перевикористовується для відправлення, знищення й повернення,
        # а відмінності задаються лише набором текстів і ознакою обов'язковості адресата.
        self.requires_target = requires_target
        self.setWindowTitle(self.texts["title"])
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)
        self.setMinimumWidth(420)

        self.number_label = QLabel(self.texts["number"], self)
        main_layout.addWidget(self.number_label)

        self.number_input = QLineEdit(self)
        self.number_input.setMinimumWidth(220)
        self.number_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(self.number_input)

        self.date_label = QLabel(self.texts["date"], self)
        main_layout.addWidget(self.date_label)

        self.date_input = create_date_input(self)
        self.date_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        main_layout.addWidget(self.date_input)

        self.target_input = QLineEdit(self)
        self.target_input.setEnabled(self.requires_target)
        self.target_input.setMinimumWidth(220)
        self.target_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if self.requires_target:
            self.target_label = QLabel(self.texts["target"], self)
            main_layout.addWidget(self.target_label)
            main_layout.addWidget(self.target_input)
        else:
            # Для сценаріїв без адресата поле повністю приховуємо,
            # щоб не залишати в інтерфейсі зайвий порожній елемент.
            self.target_input.hide()

        button_box = QDialogButtonBox(self)
        confirm_button = button_box.addButton(self.texts["confirm"], QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = button_box.addButton(self.texts["cancel"], QDialogButtonBox.ButtonRole.RejectRole)
        confirm_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        main_layout.addWidget(button_box)

    def get_input(self) -> tuple[str, str, str]:
        # Навіть коли адресат не потрібен, повертаємо єдину форму кортежу,
        # щоб викликаючий код розбирав результат однаково для всіх дій.
        return (
            self.number_input.text(),
            read_date_input_value(self.date_input),
            self.target_input.text(),
        )