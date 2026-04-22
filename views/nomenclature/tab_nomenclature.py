from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QBrush, QColor, QDropEvent
from PySide6.QtWidgets import QAbstractItemView, QHBoxLayout, QHeaderView, QInputDialog, QLabel, QMessageBox, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from dialogs.nomenclature import NomenclatureCardPickerDialog, NomenclatureRowDialog
from viewmodels.nomenclature import TabNomenclatureViewModel


class NomenclatureTableWidget(QTableWidget):
    """Таблиця номенклатури з повідомленням про завершене перетягування рядків."""

    def __init__(self, on_rows_reordered, parent=None):
        super().__init__(parent)
        self._on_rows_reordered = on_rows_reordered

    def dropEvent(self, event: QDropEvent):
        if event.source() is self:
            selected_indexes = self.selectedIndexes()
            if not selected_indexes:
                event.ignore()
                return

            source_row = selected_indexes[0].row()
            target_row = self._drop_row(event)
            if self._can_reorder(source_row, target_row):
                event.acceptProposedAction()
                if self._on_rows_reordered is not None:
                    QTimer.singleShot(0, lambda: self._on_rows_reordered(source_row, target_row))
                return

        super().dropEvent(event)

    def _can_reorder(self, source_row: int, target_row: int) -> bool:
        if source_row < 0 or source_row >= self.rowCount():
            return False

        bounded_target_row = max(0, min(target_row, self.rowCount()))
        if bounded_target_row > source_row:
            bounded_target_row -= 1
        return bounded_target_row != source_row

    def _drop_row(self, event: QDropEvent) -> int:
        position = event.position().toPoint()
        row = self.rowAt(position.y())
        if row < 0:
            return self.rowCount()

        indicator_position = self.dropIndicatorPosition()
        if indicator_position == QAbstractItemView.DropIndicatorPosition.BelowItem:
            return row + 1
        if indicator_position == QAbstractItemView.DropIndicatorPosition.OnViewport:
            return self.rowCount()
        return row


class TabNomenclature(QWidget):
    """Початковий інтерфейс вкладки номенклатури з широкою таблицею."""

    def __init__(self, parent=None, viewmodel: TabNomenclatureViewModel | None = None):
        super().__init__(parent)
        self.viewmodel = viewmodel or TabNomenclatureViewModel()
        self._column_widths = [110, 260, 220, 170, 130, 150, 210, 130, 130, 150, 150, 150, 170, 145]
        self._rows = []
        self._init_ui()
        self._load_rows()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.add_button = QPushButton(self.viewmodel.add_button_text, self)
        self.add_button.clicked.connect(self._open_add_row_dialog)
        button_layout.addWidget(self.add_button)

        self.refresh_button = QPushButton(self.viewmodel.refresh_button_text, self)
        self.refresh_button.clicked.connect(self._load_rows)
        button_layout.addWidget(self.refresh_button)

        self.edit_button = QPushButton(self.viewmodel.edit_button_text, self)
        self.edit_button.clicked.connect(self._open_edit_position_dialog)
        button_layout.addWidget(self.edit_button)
        layout.addLayout(button_layout)

        self.empty_state_label = QLabel(self.viewmodel.empty_state_text, self)
        self.empty_state_label.setWordWrap(True)
        layout.addWidget(self.empty_state_label)

        self.table = NomenclatureTableWidget(self._handle_rows_reordered, self)
        self.table.setColumnCount(len(self.viewmodel.headers))
        self.table.setHorizontalHeaderLabels(self.viewmodel.headers)
        self.table.setRowCount(0)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.table.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.setDropIndicatorShown(True)
        self.table.setWordWrap(False)
        self.table.cellDoubleClicked.connect(self._open_card_picker_dialog)
        self.table.itemSelectionChanged.connect(self._update_buttons_state)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        for column_index, width in enumerate(self._column_widths):
            self.table.setColumnWidth(column_index, width)

        layout.addWidget(self.table)
        self._update_buttons_state()

    def _load_rows(self):
        self._rows = self.viewmodel.get_rows()
        selected_row = self._selected_row()
        selected_row_id = selected_row.row_id if selected_row is not None else None
        self.table.setRowCount(len(self._rows))
        self.empty_state_label.setVisible(not self._rows)

        for row_index, row in enumerate(self._rows):
            values = [
                row.status,
                row.short_name_chain,
                row.job_title,
                row.nomenclature_number,
                row.admission_form,
                row.surname,
                row.name_patronymic,
                row.section_name,
                row.group_name,
                row.department_name,
                row.division_name,
                row.radio_station_name,
                row.appointment_order_number,
                row.appointment_order_date,
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, row.row_id)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_index, column_index, item)
            self._apply_row_style(row_index, row.highlight_style)

        if selected_row_id is not None:
            self._restore_selection(selected_row_id)

    def _selected_row(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        row_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        for row in self._rows:
            if row.row_id == row_id:
                return row
        return None

    def _update_buttons_state(self):
        self.edit_button.setEnabled(self._selected_row() is not None)

    def _handle_rows_reordered(self, source_row: int, target_row: int):
        selected_row = self._selected_row()
        selected_row_id = selected_row.row_id if selected_row is not None else None

        row_ids = [row.row_id for row in self._rows]
        bounded_target_row = max(0, min(target_row, len(row_ids)))
        if bounded_target_row > source_row:
            bounded_target_row -= 1
        moved_row_id = row_ids.pop(source_row)
        row_ids.insert(bounded_target_row, moved_row_id)

        try:
            self.viewmodel.save_row_order(row_ids)
        except ValueError as error:
            self._load_rows()
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_rows()
        if selected_row_id is not None:
            self._restore_selection(selected_row_id)

    def _restore_selection(self, row_id: int):
        for row_index in range(self.table.rowCount()):
            item = self.table.item(row_index, 0)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == row_id:
                self.table.selectRow(row_index)
                return

    def _open_add_row_dialog(self):
        dialog = NomenclatureRowDialog(
            self.viewmodel.dialog_texts,
            self.viewmodel.structure_unit_options(),
            current_record=None,
            parent=self.window(),
        )
        if dialog.exec() == 0:
            return

        try:
            self.viewmodel.create_row(*dialog.get_input())
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_rows()

    def _open_edit_position_dialog(self):
        selected_row = self._selected_row()
        if selected_row is None:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.dialog_texts["select_row_warning"])
            return

        dialog = NomenclatureRowDialog(
            self.viewmodel.dialog_texts,
            self.viewmodel.structure_unit_options(),
            current_record=selected_row,
            parent=self.window(),
        )
        if dialog.exec() == 0:
            return

        try:
            self.viewmodel.update_row(selected_row.row_id, *dialog.get_input())
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_rows()

    def _open_card_picker_dialog(self, *_args):
        selected_row = self._selected_row()
        if selected_row is None:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.dialog_texts["select_row_warning"])
            return

        dialog = NomenclatureCardPickerDialog(
            self.viewmodel.card_picker_texts,
            self.viewmodel.card_options(),
            current_record=selected_row,
            parent=self.window(),
        )
        if dialog.exec() == 0:
            return

        selected_card = dialog.get_selected_card()
        if dialog.is_vacancy_selected():
            vacancy_order_number, accepted = QInputDialog.getText(
                self,
                self.viewmodel.card_picker_texts["vacancy_order_number_title"],
                self.viewmodel.card_picker_texts["vacancy_order_number_label"],
                text=selected_row.vacancy_order_number,
            )
            if not accepted:
                return

            try:
                self.viewmodel.clear_person_from_row(selected_row.row_id, vacancy_order_number)
            except ValueError as error:
                QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
                return

            self._load_rows()
            return

        if selected_card is None:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.card_picker_texts["select_card_warning"])
            return

        try:
            appointment_order_number, appointment_order_date = dialog.get_assignment_input()
            self.viewmodel.assign_card_to_row(
                selected_row.row_id,
                selected_card.card_id,
                appointment_order_number,
                appointment_order_date,
            )
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_rows()

    def _apply_row_style(self, row_index: int, style_name: str):
        background_brush = None
        foreground_brush = None

        if style_name == "warning":
            background_brush = QBrush(QColor("#ffb3b3"))
        elif style_name == "critical":
            background_brush = QBrush(QColor("#000000"))
            foreground_brush = QBrush(QColor("#ff0000"))

        for column_index in range(self.table.columnCount()):
            item = self.table.item(row_index, column_index)
            if item is None:
                continue
            if background_brush is not None:
                item.setBackground(background_brush)
            if foreground_brush is not None:
                item.setForeground(foreground_brush)
