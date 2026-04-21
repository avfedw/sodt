from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QComboBox, QDateEdit, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QVBoxLayout

from ..base_dialog import CenteredDialog
from ..helpers import create_date_input, create_ukrainian_name_validator, read_date_input_value, set_empty_date
from .workflow_action_dialog import WorkflowActionDialog


class EditCardDialog(CenteredDialog):
    """Діалог редагування картки."""

    def __init__(self, texts: dict, card, parent=None):
        super().__init__(parent)
        self.texts = texts
        # У діалог передається вже зібрана доменна модель картки,
        # щоб не дублювати звернення до репозиторію на рівні UI.
        self.card = card
        self.selected_action = "update"
        self.action_payload = ()
        self.setWindowTitle(self.texts["title"])
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        name_validator = create_ukrainian_name_validator(self)
        # Для внутрішнього номера картки окремо дозволяємо лише цифри,
        # бо далі репозиторій спирається на числове порівняння й нумерацію.
        number_validator = QRegularExpressionValidator(QRegularExpression(r"[0-9]*"), self)

        self.surname_input = QLineEdit(self.card.surname, self)
        self.surname_input.setValidator(name_validator)
        form_layout.addRow(self.texts["surname"], self.surname_input)

        self.name_input = QLineEdit(self.card.name, self)
        self.name_input.setValidator(name_validator)
        form_layout.addRow(self.texts["name"], self.name_input)

        self.patronymic_input = QLineEdit(self.card.patronymic, self)
        self.patronymic_input.setValidator(name_validator)
        form_layout.addRow(self.texts["patronymic"], self.patronymic_input)

        self.number_input = QLineEdit(self.card.number, self)
        self.number_input.setValidator(number_validator)
        form_layout.addRow(self.texts["number"], self.number_input)

        self.card_date_input = self._create_date_input(self.card.card_date)
        form_layout.addRow(self.texts["card_date"], self.card_date_input)

        self.workflow_status_value = QLabel(self.card.derived_workflow_status, self)
        self.workflow_status_value.setWordWrap(True)
        # Це поле лише інформує користувача про похідний стан,
        # який формується з історії документів і не редагується напряму тут.
        form_layout.addRow(self.texts["workflow_status"], self.workflow_status_value)

        self.document_kind_input = QComboBox(self)
        self._fill_combo_box(
            self.document_kind_input,
            self.texts["document_kind_options"],
            self.card.document_kind,
        )
        self.document_kind_input.currentIndexChanged.connect(self._update_document_fields_state)
        form_layout.addRow(self.texts["document_kind"], self.document_kind_input)

        self.document_number_input = QLineEdit(self.card.document_number, self)
        form_layout.addRow(self.texts["document_number"], self.document_number_input)

        self.document_date_input = self._create_date_input(self.card.document_date, allow_empty=True)
        form_layout.addRow(self.texts["document_date"], self.document_date_input)

        self.document_target_input = QLineEdit(self.card.document_target, self)
        form_layout.addRow(self.texts["document_target"], self.document_target_input)

        self.service_note_input = QPlainTextEdit(self.card.service_note, self)
        self.service_note_input.setReadOnly(True)
        self.service_note_input.setFixedHeight(70)
        form_layout.addRow(self.texts["service_note"], self.service_note_input)

        self.user_note_input = QPlainTextEdit(self.card.user_note, self)
        self.user_note_input.setFixedHeight(90)
        form_layout.addRow(self.texts["user_note"], self.user_note_input)

        self.inactive_state_label = QLabel(self)
        self.inactive_state_label.setWordWrap(True)
        self._update_inactive_state_label()
        if self.inactive_state_label.text():
            form_layout.addRow(self.texts["inactive_state"], self.inactive_state_label)

        self._update_document_fields_state()

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(self)
        self.save_button = button_box.addButton(self.texts["save"], QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = button_box.addButton(self.texts["cancel"], QDialogButtonBox.ButtonRole.RejectRole)
        self.save_button.clicked.connect(self._accept_update)
        cancel_button.clicked.connect(self.reject)

        action_layout = QHBoxLayout()
        if self.card.can_edit:
            # Додаткові дії не виконуються окремими кнопками в головному вікні,
            # щоб увесь сценарій роботи з карткою лишався в одному діалозі.
            self.send_button = button_box.addButton(self.texts["send_button"], QDialogButtonBox.ButtonRole.ActionRole)
            self.destroy_button = button_box.addButton(self.texts["destroy_button"], QDialogButtonBox.ButtonRole.ActionRole)
            self.send_button.clicked.connect(self._open_send_dialog)
            self.destroy_button.clicked.connect(self._open_destroy_dialog)
        else:
            self._set_editable_state(False)
            self.save_button.setEnabled(False)

            if self.card.can_return:
                self.return_button = button_box.addButton(self.texts["return_button"], QDialogButtonBox.ButtonRole.ActionRole)
                self.return_button.clicked.connect(self._open_return_dialog)

        main_layout.addWidget(button_box)

    def _fill_combo_box(self, combo_box: QComboBox, options: list[tuple[str, str]], current_value: str):
        # У комбобоксі показуємо користувацький підпис, але зберігаємо окреме технічне значення,
        # яке потім іде в репозиторій без зворотного мапінгу по тексту інтерфейсу.
        for value, label in options:
            combo_box.addItem(label, value)

        current_index = combo_box.findData(current_value)
        combo_box.setCurrentIndex(max(0, current_index))

    def _update_inactive_state_label(self):
        # Причина неактивності вже обчислена моделлю картки, а локалізація тут лише
        # перетворює внутрішній код у текстове пояснення для користувача.
        inactive_reason = self.card.inactive_reason
        messages = self.texts.get("inactive_messages", {})
        self.inactive_state_label.setText(messages.get(inactive_reason, ""))

    def _set_editable_state(self, is_enabled: bool):
        # Масово блокуємо поля, коли картка історична або відправлена,
        # але при цьому залишаємо можливість переглянути всі значення в діалозі.
        widgets = [
            self.surname_input,
            self.name_input,
            self.patronymic_input,
            self.number_input,
            self.card_date_input,
            self.document_kind_input,
            self.document_number_input,
            self.document_date_input,
            self.document_target_input,
            self.user_note_input,
        ]
        for widget in widgets:
            widget.setEnabled(is_enabled)

    def _update_document_fields_state(self):
        document_kind = self.document_kind_input.currentData()
        needs_number = document_kind in {"escort", "act"}
        needs_date = document_kind in {"escort", "act", "planned_cancellation", "planned_destruction"}
        needs_target = document_kind == "escort"

        # Вмикаємо лише ті реквізити, які потрібні для вибраного типу події.
        self.document_number_input.setEnabled(needs_number)
        self.document_date_input.setEnabled(needs_date)
        self.document_target_input.setEnabled(needs_target)

        if not needs_number:
            self.document_number_input.clear()
        if not needs_target:
            self.document_target_input.clear()
        if not needs_date:
            set_empty_date(self.document_date_input, allow_empty=True)

    def _create_date_input(self, value: str, allow_empty: bool = False) -> QDateEdit:
        # Єдина точка створення поля дати дозволяє тримати однакову поведінку
        # для всіх дат у діалозі редагування.
        return create_date_input(self, value, allow_empty=allow_empty, empty_text=self.texts["empty_date"])

    def _date_input_value(self, date_input: QDateEdit, allow_empty: bool = False) -> str:
        return read_date_input_value(date_input, allow_empty=allow_empty)

    def _accept_update(self):
        # Замість негайного виклику репозиторію лише фіксуємо намір користувача,
        # а фактичну дію виконує вже викликаючий віджет вкладки.
        self.selected_action = "update"
        self.action_payload = self.get_card_input()
        self.accept()

    def _open_send_dialog(self):
        # Піддіалог збирає реквізити відправлення, а зовнішній код уже вирішує,
        # як саме застосувати їх до картки й пов'язаної групи.
        dialog = WorkflowActionDialog(self.texts["send_dialog"], requires_target=True, parent=self)
        if dialog.exec() == 0:
            return

        self.selected_action = "send"
        self.action_payload = dialog.get_input()
        self.accept()

    def _open_destroy_dialog(self):
        dialog = WorkflowActionDialog(self.texts["destroy_dialog"], requires_target=False, parent=self)
        if dialog.exec() == 0:
            return

        number, action_date, _target = dialog.get_input()
        self.selected_action = "destroy"
        self.action_payload = (number, action_date)
        self.accept()

    def _open_return_dialog(self):
        dialog = WorkflowActionDialog(self.texts["return_dialog"], requires_target=True, parent=self)
        if dialog.exec() == 0:
            return

        self.selected_action = "return"
        self.action_payload = dialog.get_input()
        self.accept()

    def get_card_input(self) -> tuple[str, str, str, str, str, str, str, str, str]:
        # Порядок повернення погоджений із сигнатурою update_card у ViewModel.
        return (
            self.surname_input.text(),
            self.name_input.text(),
            self.patronymic_input.text(),
            self.number_input.text(),
            self._date_input_value(self.card_date_input),
            self.document_kind_input.currentData(),
            self.document_number_input.text(),
            self._date_input_value(self.document_date_input, allow_empty=True),
            self.document_target_input.text(),
            self.user_note_input.toPlainText(),
        )