from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QHBoxLayout, QHeaderView, QLineEdit, QMessageBox, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from dialogs import AccessDialog, AddCardDialog, AdmissionDialog, EditCardDialog
from viewmodels.tab_cards_vm import TabCardsViewModel


class TabCards(QWidget):
    """Віджет вкладки Cards. Тут розміщується UI та зв'язок із ViewModel."""

    _DOCUMENT_EVENT_COLUMN = 6
    _STATUS_COLUMN = 7
    _TABLE_ITEM_ALIGNMENT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    _TABLE_GRID_STYLESHEET = """
        QTableWidget {
            gridline-color: #2f2f2f;
            border: 1px solid #2f2f2f;
        }
        QHeaderView::section {
            border: 1px solid #2f2f2f;
            padding: 4px;
        }
    """

    def __init__(self, parent=None, viewmodel: TabCardsViewModel = None):
        super().__init__(parent)
        self.viewmodel = viewmodel or TabCardsViewModel()
        self._cards = []
        self._admissions = []
        self._accesses = []
        self._filter_inputs = []
        self._sorted_column = 0
        self._sort_order = Qt.SortOrder.AscendingOrder
        self._cards_table_width_weights = [12, 9, 12, 11, 12, 9, 17, 14, 14]
        self._admission_table_width_weights = [1] * 8
        self._access_table_width_weights = [1, 1, 1, 1]
        main_layout = QVBoxLayout(self)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignLeft)

        add_card_button = QPushButton(self.viewmodel.add_button_text, self)
        add_card_button.setFixedWidth(100)
        add_card_button.clicked.connect(self._open_add_card_dialog)
        button_layout.addWidget(add_card_button)

        main_layout.addLayout(button_layout)

        table_layout = QVBoxLayout()
        table_layout.setSpacing(4)
        self.cards_table = QTableWidget(self)
        self.cards_table.setColumnCount(len(self.viewmodel.table_headers))
        self.cards_table.setHorizontalHeaderLabels(self.viewmodel.table_headers)
        self._configure_table_width(self.cards_table, self._cards_table_width_weights)
        self._apply_table_visual_style(self.cards_table)
        self.cards_table.verticalHeader().setVisible(False)
        self.cards_table.setWordWrap(False)
        self.cards_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cards_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.cards_table.itemSelectionChanged.connect(self._update_cards_row_heights)
        self.cards_table.itemSelectionChanged.connect(self._on_card_selection_changed)
        self.cards_table.horizontalHeader().setSortIndicatorShown(True)
        self.cards_table.horizontalHeader().sectionClicked.connect(self._sort_cards_by_column)
        self.cards_table.cellDoubleClicked.connect(self._open_edit_card_dialog)
        self._create_cards_filter_bar(table_layout)
        self._load_cards()
        self.cards_table.horizontalHeader().setSortIndicator(self._sorted_column, self._sort_order)
        table_layout.addWidget(self.cards_table)

        lower_tables_layout = QHBoxLayout()

        admission_layout = QVBoxLayout()
        admission_layout.addWidget(QLabel(self.viewmodel.admission_table_title, self))
        self.admission_table = QTableWidget(self)
        self.admission_table.setColumnCount(len(self.viewmodel.admission_headers))
        self.admission_table.setHorizontalHeaderLabels(self.viewmodel.admission_headers)
        self._configure_table_width(self.admission_table, self._admission_table_width_weights)
        self._apply_table_visual_style(self.admission_table)
        self.admission_table.verticalHeader().setVisible(False)
        self.admission_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.admission_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.admission_table.itemSelectionChanged.connect(self._update_admission_buttons_state)
        self.admission_table.cellDoubleClicked.connect(self._open_edit_admission_dialog)
        admission_layout.addWidget(self.admission_table)

        admission_buttons = QHBoxLayout()
        admission_buttons.setAlignment(Qt.AlignLeft)
        self.add_admission_button = QPushButton(self.viewmodel.add_admission_button_text, self)
        self.add_admission_button.setFixedWidth(150)
        self.add_admission_button.clicked.connect(self._open_add_admission_dialog)
        admission_buttons.addWidget(self.add_admission_button)
        self.edit_admission_button = QPushButton(self.viewmodel.edit_admission_button_text, self)
        self.edit_admission_button.setFixedWidth(150)
        self.edit_admission_button.clicked.connect(self._open_edit_admission_dialog)
        admission_buttons.addWidget(self.edit_admission_button)
        admission_layout.addLayout(admission_buttons)
        lower_tables_layout.addLayout(admission_layout)

        access_layout = QVBoxLayout()
        access_layout.addWidget(QLabel(self.viewmodel.access_table_title, self))
        self.access_table = QTableWidget(self)
        self.access_table.setColumnCount(len(self.viewmodel.access_headers))
        self.access_table.setHorizontalHeaderLabels(self.viewmodel.access_headers)
        self._configure_table_width(self.access_table, self._access_table_width_weights)
        self._apply_table_visual_style(self.access_table)
        self.access_table.verticalHeader().setVisible(False)
        self.access_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.access_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.access_table.itemSelectionChanged.connect(self._update_access_buttons_state)
        self.access_table.cellDoubleClicked.connect(self._open_edit_access_dialog)
        access_layout.addWidget(self.access_table)

        access_buttons = QHBoxLayout()
        access_buttons.setAlignment(Qt.AlignLeft)
        self.add_access_button = QPushButton(self.viewmodel.add_access_button_text, self)
        self.add_access_button.setFixedWidth(150)
        self.add_access_button.clicked.connect(self._open_add_access_dialog)
        access_buttons.addWidget(self.add_access_button)
        self.edit_access_button = QPushButton(self.viewmodel.edit_access_button_text, self)
        self.edit_access_button.setFixedWidth(150)
        self.edit_access_button.clicked.connect(self._open_edit_access_dialog)
        access_buttons.addWidget(self.edit_access_button)
        access_layout.addLayout(access_buttons)
        lower_tables_layout.addLayout(access_layout)

        table_layout.addLayout(lower_tables_layout)
        main_layout.addLayout(table_layout)

        self.setLayout(main_layout)
        self._clear_admission_table()
        self._clear_access_table()
        self._update_admission_buttons_state()
        self._update_access_buttons_state()

    def _configure_table_width(self, table: QTableWidget, width_weights: list[int]):
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._apply_table_widths(table, width_weights)

    def _apply_table_visual_style(self, table: QTableWidget):
        table.setShowGrid(True)
        table.setStyleSheet(self._TABLE_GRID_STYLESHEET)

    def _create_cards_filter_bar(self, parent_layout: QVBoxLayout):
        self.cards_filter_bar = QWidget(self)
        self.cards_filter_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cards_filter_layout = QHBoxLayout(self.cards_filter_bar)
        self.cards_filter_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_filter_layout.setSpacing(0)
        self._filter_inputs = []

        for _ in range(self.cards_table.columnCount()):
            filter_input = QLineEdit(self.cards_filter_bar)
            filter_input.setClearButtonEnabled(True)
            filter_input.setPlaceholderText("Фільтр")
            filter_font = filter_input.font()
            filter_font.setPointSize(max(8, filter_font.pointSize() - 1))
            filter_input.setFont(filter_font)
            filter_input.setFixedHeight(24)
            filter_input.textChanged.connect(self._apply_cards_filter)
            self.cards_filter_layout.addWidget(filter_input)
            self._filter_inputs.append(filter_input)

        parent_layout.addWidget(self.cards_filter_bar)
        self._sync_cards_filter_widths()

    def _apply_table_widths(self, table: QTableWidget, width_weights: list[int]):
        if table.columnCount() == 0:
            return

        total_weight = sum(width_weights)
        available_width = max(table.viewport().width(), table.width())
        if total_weight <= 0 or available_width <= 0:
            return

        assigned_width = 0
        for column_index, weight in enumerate(width_weights):
            if column_index >= table.columnCount():
                break

            if column_index == table.columnCount() - 1:
                column_width = max(40, available_width - assigned_width)
            else:
                column_width = max(40, int(available_width * weight / total_weight))

            table.setColumnWidth(column_index, column_width)
            assigned_width += column_width

        if table is self.cards_table:
            self._sync_cards_filter_widths()

    def _sync_cards_filter_widths(self):
        if not hasattr(self, "cards_table") or not self._filter_inputs:
            return

        for column_index, filter_input in enumerate(self._filter_inputs):
            if column_index >= self.cards_table.columnCount():
                break

            filter_input.setFixedWidth(self.cards_table.columnWidth(column_index))

    def _load_cards(self):
        self._cards = self.viewmodel.get_cards()
        self._refresh_cards_table()

    def _reload_all_tables(self, card_id: int | None = None):
        self._load_cards()

        if card_id is None:
            return

        for row_index in range(self.cards_table.rowCount()):
            card_item = self.cards_table.item(row_index, 0)
            if card_item is None:
                continue

            if card_item.data(Qt.ItemDataRole.UserRole) == card_id:
                self.cards_table.selectRow(row_index)
                return

    def _load_admissions(self, card_id: int):
        self._admissions = self.viewmodel.get_admissions(card_id)
        self._refresh_admission_table()

    def _load_accesses(self, card_id: int):
        self._accesses = self.viewmodel.get_accesses(card_id)
        self._refresh_access_table()

    def _refresh_cards_table(self):
        self._sort_cards()

        self.cards_table.setRowCount(len(self._cards))
        self.cards_table.clearContents()

        for row_index, card in enumerate(self._cards):
            visible_values = card.visible_values()
            background_color, foreground_color = self._card_row_colors(card)

            for column_index, value in enumerate(visible_values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(self._TABLE_ITEM_ALIGNMENT)
                item.setToolTip(value)
                if background_color is not None:
                    item.setBackground(background_color)
                if foreground_color is not None:
                    item.setForeground(foreground_color)

                if column_index == 0:
                    item.setData(Qt.ItemDataRole.UserRole, card.card_id)

                self.cards_table.setItem(row_index, column_index, item)

        self._update_cards_row_heights()
        self._apply_cards_filter()
        self._on_card_selection_changed()

    def _cards_row_height(self, value: str) -> int:
        explicit_line_count = max(1, value.count("\n") + 1) if value else 1
        return 30 + (explicit_line_count - 1) * 12

    def _update_cards_row_heights(self):
        selected_items = self.cards_table.selectedItems()
        selected_row = selected_items[0].row() if selected_items else -1

        for row_index, card in enumerate(self._cards):
            document_value = card.visible_values()[self._DOCUMENT_EVENT_COLUMN]
            status_value = card.visible_values()[self._STATUS_COLUMN]
            row_height = max(
                self._cards_row_height(document_value),
                self._cards_row_height(status_value),
            )
            if row_index == selected_row:
                row_height = max(row_height, self._cards_row_height(card.note))

            self.cards_table.setRowHeight(row_index, row_height)

    def _card_row_colors(self, card):
        if card.lifecycle_state == "destroyed":
            return QColor("#f4b6c2"), QColor("#6b1111")
        if card.lifecycle_state == "sent":
            return QColor("#0b5d1e"), QColor("#f4df58")
        if card.access_revoked_after_grant:
            return QColor("#3f3f3f"), QColor("#ff2d2d")
        if card.admission_revoked_after_grant:
            return QColor("#6f1010"), QColor("#f5ecb8")
        if card.has_active_admission and not card.has_active_access:
            return QColor("#ff2d2d"), QColor("#0b5d1e")
        return None, None

    def _sort_cards(self):
        sort_keys = {
            0: lambda card: (card.letter, self._number_sort_key(card.number)),
            1: lambda card: self._date_sort_key(card.card_date),
            2: lambda card: card.surname.casefold(),
            3: lambda card: card.name.casefold(),
            4: lambda card: card.patronymic.casefold(),
            5: lambda card: card.form.casefold(),
            6: lambda card: card.workflow_document.casefold(),
            7: lambda card: card.workflow_status.casefold(),
            8: lambda card: card.note.casefold(),
        }
        sort_key = sort_keys.get(self._sorted_column, lambda card: card.visible_values()[self._sorted_column].casefold())
        self._cards.sort(
            key=sort_key,
            reverse=self._sort_order == Qt.SortOrder.DescendingOrder,
        )

    def _sort_cards_by_column(self, column_index: int):
        if column_index == self._sorted_column:
            if self._sort_order == Qt.SortOrder.AscendingOrder:
                self._sort_order = Qt.SortOrder.DescendingOrder
            else:
                self._sort_order = Qt.SortOrder.AscendingOrder
        else:
            self._sorted_column = column_index
            self._sort_order = Qt.SortOrder.AscendingOrder

        self.cards_table.horizontalHeader().setSortIndicator(self._sorted_column, self._sort_order)
        self._refresh_cards_table()

    def _apply_cards_filter(self):
        filter_values = [filter_input.text().strip().casefold() for filter_input in self._filter_inputs]

        for row_index in range(self.cards_table.rowCount()):
            row_matches = True

            for column_index, filter_value in enumerate(filter_values):
                if not filter_value:
                    continue

                item = self.cards_table.item(row_index, column_index)
                item_text = item.text().casefold() if item is not None else ""

                if filter_value not in item_text:
                    row_matches = False
                    break

            self.cards_table.setRowHidden(row_index, not row_matches)

    def _refresh_admission_table(self):
        if not hasattr(self, "admission_table"):
            return

        self.admission_table.setRowCount(len(self._admissions))
        self.admission_table.clearContents()

        for row_index, admission in enumerate(self._admissions):
            for column_index, value in enumerate(admission.visible_values()):
                item = QTableWidgetItem(value)
                item.setTextAlignment(self._TABLE_ITEM_ALIGNMENT)
                item.setToolTip(value)
                if column_index == 0:
                    item.setData(Qt.ItemDataRole.UserRole, admission.admission_id)

                self.admission_table.setItem(row_index, column_index, item)

        self._update_admission_buttons_state()

    def _refresh_access_table(self):
        if not hasattr(self, "access_table"):
            return

        self.access_table.setRowCount(len(self._accesses))
        self.access_table.clearContents()

        for row_index, access_record in enumerate(self._accesses):
            for column_index, value in enumerate(access_record.visible_values()):
                item = QTableWidgetItem(value)
                item.setTextAlignment(self._TABLE_ITEM_ALIGNMENT)
                item.setToolTip(value)
                if column_index == 0:
                    item.setData(Qt.ItemDataRole.UserRole, access_record.access_id)

                self.access_table.setItem(row_index, column_index, item)

        self._update_access_buttons_state()

    def _clear_admission_table(self):
        self._admissions = []
        if not hasattr(self, "admission_table"):
            return

        self.admission_table.setRowCount(0)
        self.admission_table.clearContents()

    def _clear_access_table(self):
        self._accesses = []
        if not hasattr(self, "access_table"):
            return

        self.access_table.setRowCount(0)
        self.access_table.clearContents()

    def _selected_card(self):
        selected_items = self.cards_table.selectedItems()
        if not selected_items:
            return None

        card_item = self.cards_table.item(selected_items[0].row(), 0)
        if card_item is None:
            return None

        return self._find_card_by_id(card_item.data(Qt.ItemDataRole.UserRole))

    def _selected_admission(self):
        selected_items = self.admission_table.selectedItems()
        if not selected_items:
            return None

        admission_item = self.admission_table.item(selected_items[0].row(), 0)
        if admission_item is None:
            return None

        admission_id = admission_item.data(Qt.ItemDataRole.UserRole)
        for admission in self._admissions:
            if admission.admission_id == admission_id:
                return admission

        return None

    def _selected_access(self):
        selected_items = self.access_table.selectedItems()
        if not selected_items:
            return None

        access_item = self.access_table.item(selected_items[0].row(), 0)
        if access_item is None:
            return None

        access_id = access_item.data(Qt.ItemDataRole.UserRole)
        for access_record in self._accesses:
            if access_record.access_id == access_id:
                return access_record

        return None

    def _on_card_selection_changed(self):
        selected_card = self._selected_card()
        if selected_card is None:
            self._clear_admission_table()
            self._clear_access_table()
            self._update_admission_buttons_state()
            self._update_access_buttons_state()
            return

        self._load_admissions(selected_card.card_id)
        self._load_accesses(selected_card.card_id)

    def _update_admission_buttons_state(self):
        if not hasattr(self, "add_admission_button") or not hasattr(self, "edit_admission_button"):
            return

        has_card = self._selected_card() is not None
        has_admission = self._selected_admission() is not None
        self.add_admission_button.setEnabled(has_card)
        self.edit_admission_button.setEnabled(has_card and has_admission)

    def _update_access_buttons_state(self):
        if not hasattr(self, "add_access_button") or not hasattr(self, "edit_access_button"):
            return

        has_card = self._selected_card() is not None
        has_access = self._selected_access() is not None
        self.add_access_button.setEnabled(has_card)
        self.edit_access_button.setEnabled(has_card and has_access)

    def _number_sort_key(self, value: str):
        if value.isdigit():
            return (0, int(value))

        return (1, value.casefold())

    def _date_sort_key(self, value: str):
        if not value:
            return (1, datetime.min)

        try:
            return (0, datetime.strptime(value, "%d.%m.%Y"))
        except ValueError:
            return (1, datetime.min)

    def _open_add_card_dialog(self):
        dialog = AddCardDialog(self.viewmodel.add_dialog_texts, self.window())
        if dialog.exec() == 0:
            return

        surname, name, patronymic = dialog.get_card_input()

        try:
            self.viewmodel.create_card(surname, name, patronymic)
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_cards()

    def _open_add_admission_dialog(self):
        selected_card = self._selected_card()
        if selected_card is None:
            QMessageBox.warning(
                self,
                self.viewmodel.validation_error_title,
                self.viewmodel.admission_dialog_texts["select_card_warning"],
            )
            return

        dialog = AdmissionDialog(self.viewmodel.admission_dialog_texts, parent=self.window())
        if dialog.exec() == 0:
            return

        try:
            self.viewmodel.create_admission(selected_card.card_id, *dialog.get_input())
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._reload_all_tables(selected_card.card_id)

    def _open_add_access_dialog(self):
        selected_card = self._selected_card()
        if selected_card is None:
            QMessageBox.warning(
                self,
                self.viewmodel.validation_error_title,
                self.viewmodel.access_dialog_texts["select_card_warning"],
            )
            return

        dialog = AccessDialog(self.viewmodel.access_dialog_texts, parent=self.window())
        if dialog.exec() == 0:
            return

        try:
            self.viewmodel.create_access(selected_card.card_id, *dialog.get_input())
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._reload_all_tables(selected_card.card_id)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_table_widths(self.cards_table, self._cards_table_width_weights)
        self._apply_table_widths(self.admission_table, self._admission_table_width_weights)
        self._apply_table_widths(self.access_table, self._access_table_width_weights)

    def _open_edit_card_dialog(self, row_index: int, _column_index: int):
        card_item = self.cards_table.item(row_index, 0)
        if card_item is None:
            return

        card_id = card_item.data(Qt.ItemDataRole.UserRole)
        card = self._find_card_by_id(card_id)
        if card is None:
            return

        dialog = EditCardDialog(self.viewmodel.edit_dialog_texts, card, self.window())
        if dialog.exec() == 0:
            return

        try:
            if dialog.selected_action == "update":
                self.viewmodel.update_card(card.card_id, *dialog.action_payload)
            elif dialog.selected_action == "send":
                self.viewmodel.send_card(card.card_id, *dialog.action_payload)
            elif dialog.selected_action == "destroy":
                self.viewmodel.destroy_card(card.card_id, *dialog.action_payload)
            elif dialog.selected_action == "return":
                self.viewmodel.return_card(card.card_id, *dialog.action_payload)
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_cards()

    def _open_edit_admission_dialog(self, _row_index: int = -1, _column_index: int = -1):
        selected_card = self._selected_card()
        if selected_card is None:
            QMessageBox.warning(
                self,
                self.viewmodel.validation_error_title,
                self.viewmodel.admission_dialog_texts["select_card_warning"],
            )
            return

        admission = self._selected_admission()
        if admission is None:
            QMessageBox.warning(
                self,
                self.viewmodel.validation_error_title,
                self.viewmodel.admission_dialog_texts["select_admission_warning"],
            )
            return

        dialog = AdmissionDialog(self.viewmodel.admission_dialog_texts, admission=admission, parent=self.window())
        if dialog.exec() == 0:
            return

        try:
            self.viewmodel.update_admission(admission.admission_id, *dialog.get_input())
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._reload_all_tables(selected_card.card_id)

    def _open_edit_access_dialog(self, _row_index: int = -1, _column_index: int = -1):
        selected_card = self._selected_card()
        if selected_card is None:
            QMessageBox.warning(
                self,
                self.viewmodel.validation_error_title,
                self.viewmodel.access_dialog_texts["select_card_warning"],
            )
            return

        access_record = self._selected_access()
        if access_record is None:
            QMessageBox.warning(
                self,
                self.viewmodel.validation_error_title,
                self.viewmodel.access_dialog_texts["select_access_warning"],
            )
            return

        dialog = AccessDialog(self.viewmodel.access_dialog_texts, access_record=access_record, parent=self.window())
        if dialog.exec() == 0:
            return

        try:
            self.viewmodel.update_access(access_record.access_id, *dialog.get_input())
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._reload_all_tables(selected_card.card_id)

    def _find_card_by_id(self, card_id: int):
        for card in self._cards:
            if card.card_id == card_id:
                return card

        return None
