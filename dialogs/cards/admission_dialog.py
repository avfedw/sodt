from PySide6.QtWidgets import QComboBox, QDateEdit, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout

from ..base_dialog import CenteredDialog
from ..helpers import create_date_input, read_date_input_value, set_empty_date


class AdmissionDialog(CenteredDialog):
    """Діалог додавання або редагування запису розшифровки."""

    def __init__(self, texts: dict, admission=None, parent=None):
        super().__init__(parent)
        self.texts = texts
        self.admission = admission
        self.is_edit_mode = admission is not None
        self.selected_action = "save"
        self.setWindowTitle(self.texts["edit_title"] if self.is_edit_mode else self.texts["add_title"])
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.escort_number_input = QLineEdit(self.admission.escort_number if self.is_edit_mode else "", self)
        form_layout.addRow(self.texts["escort_number"], self.escort_number_input)

        self.escort_date_input = self._create_date_input(self.admission.escort_date if self.is_edit_mode else "", allow_empty=True)
        form_layout.addRow(self.texts["escort_date"], self.escort_date_input)

        self.admission_form_input = QComboBox(self)
        self.admission_form_input.addItems(self.texts["admission_form_options"])
        # У режимі створення одразу підставляємо типову форму,
        # а в режимі редагування відновлюємо фактичне значення запису.
        current_form = self.admission.admission_form if self.is_edit_mode else self.texts["default_admission_form"]
        current_form_index = self.admission_form_input.findText(current_form)
        self.admission_form_input.setCurrentIndex(max(0, current_form_index))
        form_layout.addRow(self.texts["admission_form"], self.admission_form_input)

        if self.is_edit_mode:
            self.response_number_input = QLineEdit(self.admission.response_number, self)
            form_layout.addRow(self.texts["response_number"], self.response_number_input)

            self.response_date_input = self._create_date_input(self.admission.response_date, allow_empty=True)
            form_layout.addRow(self.texts["response_date"], self.response_date_input)

            self.order_number_input = QLineEdit(self.admission.order_number, self)
            form_layout.addRow(self.texts["order_number"], self.order_number_input)

            self.order_date_input = self._create_date_input(self.admission.order_date, allow_empty=True)
            form_layout.addRow(self.texts["order_date"], self.order_date_input)

            self.admission_status_input = QComboBox(self)
            self.admission_status_input.addItems(self.texts["admission_status_options"])
            current_status_index = self.admission_status_input.findText(self.admission.admission_status)
            self.admission_status_input.setCurrentIndex(max(0, current_status_index))
            form_layout.addRow(self.texts["admission_status"], self.admission_status_input)

            self.response_number_input.textChanged.connect(self._update_number_date_states)
            self.order_number_input.textChanged.connect(self._update_number_date_states)
        else:
            self.response_number_input = None
            self.response_date_input = None
            self.order_number_input = None
            self.order_date_input = None
            self.admission_status_input = None

        self.escort_number_input.textChanged.connect(self._update_number_date_states)
        # При відкритті діалогу одразу приводимо стан пар "номер-дата"
        # до фактичних значень, а не чекаємо першого редагування користувачем.
        self._update_number_date_states()

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(self)
        save_button = button_box.addButton(self.texts["save"], QDialogButtonBox.ButtonRole.AcceptRole)
        if self.is_edit_mode:
            delete_button = button_box.addButton(self.texts["delete_button"], QDialogButtonBox.ButtonRole.ActionRole)
        cancel_button = button_box.addButton(self.texts["cancel"], QDialogButtonBox.ButtonRole.RejectRole)
        save_button.clicked.connect(self._accept_save)
        if self.is_edit_mode:
            delete_button.clicked.connect(self._accept_delete)
        cancel_button.clicked.connect(self.reject)
        main_layout.addWidget(button_box)

    def _accept_save(self):
        self.selected_action = "save"
        self.accept()

    def _accept_delete(self):
        self.selected_action = "delete"
        self.accept()

    def _create_date_input(self, value: str, allow_empty: bool) -> QDateEdit:
        # Обгортка лишає в одному місці прив'язку до локалізованого тексту порожньої дати.
        return create_date_input(self, value, allow_empty=allow_empty, empty_text=self.texts["empty_date"])

    def _clear_date_input(self, date_input: QDateEdit):
        set_empty_date(date_input, allow_empty=True)

    def _date_input_value(self, date_input: QDateEdit, number_input: QLineEdit | None = None) -> str:
        # Якщо номер документа не введено, пов'язана дата не повинна просочитись у модель,
        # навіть якщо користувач тимчасово виставляв її в полі календаря.
        if number_input is not None and not number_input.text().strip():
            return ""

        return read_date_input_value(date_input, allow_empty=True)

    def _toggle_pair_date_state(self, number_input: QLineEdit, date_input: QDateEdit):
        is_enabled = bool(number_input.text().strip())
        date_input.setEnabled(is_enabled)
        if not is_enabled:
            # Якщо номер документа відсутній, пов'язану дату також очищуємо.
            self._clear_date_input(date_input)

    def _update_number_date_states(self):
        # У діалозі є кілька однотипних зв'язок між номером і датою,
        # тому централізуємо оновлення, щоб вони поводились однаково.
        self._toggle_pair_date_state(self.escort_number_input, self.escort_date_input)
        if self.response_number_input is not None and self.response_date_input is not None:
            self._toggle_pair_date_state(self.response_number_input, self.response_date_input)
        if self.order_number_input is not None and self.order_date_input is not None:
            self._toggle_pair_date_state(self.order_number_input, self.order_date_input)

    def get_input(self) -> tuple[str, ...]:
        # Порядок значень тут навмисно збігається з сигнатурами create/update у ViewModel,
        # щоб не будувати додаткові проміжні структури лише заради діалогу.
        if not self.is_edit_mode:
            return (
                self.escort_number_input.text(),
                self._date_input_value(self.escort_date_input, self.escort_number_input),
                self.admission_form_input.currentText(),
            )

        return (
            self.escort_number_input.text(),
            self._date_input_value(self.escort_date_input, self.escort_number_input),
            self.response_number_input.text(),
            self._date_input_value(self.response_date_input, self.response_number_input),
            self.order_number_input.text(),
            self._date_input_value(self.order_date_input, self.order_number_input),
            self.admission_form_input.currentText(),
            self.admission_status_input.currentText(),
        )