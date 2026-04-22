from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QDialogButtonBox, QFormLayout, QHeaderView, QLineEdit, QTableWidget, QTableWidgetItem, QVBoxLayout

from ..base_dialog import CenteredDialog
from ..helpers import create_date_input, read_date_input_value


class NomenclatureCardPickerDialog(CenteredDialog):
    """Діалог вибору людини з наявних карток."""

    def __init__(self, texts: dict, cards: list, current_record=None, parent=None):
        super().__init__(parent)
        self.texts = texts
        self.cards = cards
        self.current_record = current_record
        self._vacancy_selected = False
        self._column_widths = [180, 150, 190, 90, 260]
        self.setWindowTitle(self.texts["title"])
        self.setMinimumWidth(920)
        self._init_ui()
        self.resize(980, 520)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        self.surname_filter_input = QLineEdit(self)
        self.surname_filter_input.setPlaceholderText(self.texts["surname_filter_placeholder"])
        self.surname_filter_input.textChanged.connect(self._apply_surname_filter)
        main_layout.addWidget(self.surname_filter_input)

        form_layout = QFormLayout()
        self.appointment_order_number_input = QLineEdit(self)
        self.appointment_order_number_input.setText("")
        form_layout.addRow(self.texts["appointment_order_number"], self.appointment_order_number_input)

        self.appointment_order_date_input = create_date_input(
            self,
            "",
            allow_empty=True,
            empty_text=self.texts["empty_date"],
        )
        form_layout.addRow(self.texts["appointment_order_date"], self.appointment_order_date_input)
        main_layout.addLayout(form_layout)

        self.table = QTableWidget(self)
        self.table.setColumnCount(len(self.texts["headers"]))
        self.table.setHorizontalHeaderLabels(self.texts["headers"])
        self.table.setRowCount(len(self.cards))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.cellDoubleClicked.connect(self.accept)

        for column_index, width in enumerate(self._column_widths):
            self.table.setColumnWidth(column_index, width)

        for row_index, card in enumerate(self.cards):
            values = [card.surname, card.name, card.patronymic, card.form, card.derived_workflow_status]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, card.card_id)
                self.table.setItem(row_index, column_index, item)

        main_layout.addWidget(self.table)

        button_box = QDialogButtonBox(self)
        select_button = button_box.addButton(self.texts["select"], QDialogButtonBox.ButtonRole.AcceptRole)
        vacant_button = button_box.addButton(self.texts["vacant"], QDialogButtonBox.ButtonRole.ActionRole)
        cancel_button = button_box.addButton(self.texts["cancel"], QDialogButtonBox.ButtonRole.RejectRole)
        select_button.clicked.connect(self.accept)
        vacant_button.clicked.connect(self._accept_vacancy)
        cancel_button.clicked.connect(self.reject)
        main_layout.addWidget(button_box)

    def _apply_surname_filter(self, value: str):
        filter_value = value.strip().casefold()
        for row_index, card in enumerate(self.cards):
            matches = not filter_value or filter_value in card.surname.casefold()
            self.table.setRowHidden(row_index, not matches)

    def get_selected_card(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        card_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        for card in self.cards:
            if card.card_id == card_id:
                return card
        return None

    def is_vacancy_selected(self) -> bool:
        return self._vacancy_selected

    def get_assignment_input(self) -> tuple[str, str]:
        return (
            self.appointment_order_number_input.text(),
            read_date_input_value(self.appointment_order_date_input, allow_empty=True),
        )

    def _accept_vacancy(self):
        self._vacancy_selected = True
        self.accept()