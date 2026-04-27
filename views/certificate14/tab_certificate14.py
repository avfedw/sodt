from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from dialogs.certificate14 import Certificate14CardPickerDialog, Certificate14Dialog
from viewmodels.certificate14 import TabCertificate14ViewModel


class TabCertificate14(QWidget):
    """Інтерфейс вкладки довідки 14."""

    def __init__(self, parent=None, viewmodel: TabCertificate14ViewModel | None = None):
        super().__init__(parent)
        self.viewmodel = viewmodel or TabCertificate14ViewModel()
        self._records_cache = []
        self._rows = []
        self._column_widths = [110, 120, 260, 140, 160, 110, 280]
        self._init_ui()
        self._load_rows()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.add_button = QPushButton(self.viewmodel.add_button_text, self)
        self.add_button.clicked.connect(self._open_add_dialog)
        button_layout.addWidget(self.add_button)

        self.refresh_button = QPushButton(self.viewmodel.refresh_button_text, self)
        self.refresh_button.clicked.connect(self._load_rows)
        button_layout.addWidget(self.refresh_button)

        self.export_button = QPushButton(self.viewmodel.export_button_text, self)
        self.export_button.clicked.connect(self._export_selected_records)
        button_layout.addWidget(self.export_button)

        self.edit_button = QPushButton(self.viewmodel.edit_button_text, self)
        self.edit_button.clicked.connect(self._open_edit_dialog)
        button_layout.addWidget(self.edit_button)
        layout.addLayout(button_layout)

        self.empty_state_label = QLabel(self.viewmodel.empty_state_text, self)
        self.empty_state_label.setWordWrap(True)
        layout.addWidget(self.empty_state_label)

        self.table = QTableWidget(self)
        self.table.setColumnCount(len(self.viewmodel.headers))
        self.table.setHorizontalHeaderLabels(self.viewmodel.headers)
        self.table.setRowCount(0)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setWordWrap(False)
        self.table.cellDoubleClicked.connect(self._open_edit_dialog)
        self.table.itemSelectionChanged.connect(self._update_buttons_state)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(False)
        for column_index, width in enumerate(self._column_widths):
            self.table.setColumnWidth(column_index, width)
        layout.addWidget(self.table)
        self._update_buttons_state()

    def _load_rows(self):
        self._records_cache = self.viewmodel.repository.list_records()
        self._rows = self.viewmodel.get_rows()
        selected_row = self._selected_row()
        selected_id = selected_row.certificate_id if selected_row is not None else None
        self.table.setRowCount(len(self._rows))
        self.empty_state_label.setVisible(not self._rows)

        for row_index, row in enumerate(self._rows):
            values = [row.number, row.certificate_date, row.full_name, row.expiration_date, row.recipient_surname, row.returned_mark, row.note]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, row.certificate_id)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_index, column_index, item)

        if selected_id is not None:
            self._restore_selection(selected_id)

    def _selected_row(self):
        selected_rows = self._selected_rows()
        if len(selected_rows) != 1:
            return None

        return selected_rows[0]

    def _selected_rows(self):
        selected_certificate_ids = []
        for row_index in range(self.table.rowCount()):
            item = self.table.item(row_index, 0)
            if item is None:
                continue
            if not self.table.selectionModel().isRowSelected(row_index, self.table.rootIndex()):
                continue
            selected_certificate_ids.append(item.data(Qt.ItemDataRole.UserRole))

        rows_by_id = {
            row.certificate_id: row
            for row in self._rows
        }
        return [rows_by_id[certificate_id] for certificate_id in selected_certificate_ids if certificate_id in rows_by_id]

    def _restore_selection(self, certificate_id: int):
        for row_index in range(self.table.rowCount()):
            item = self.table.item(row_index, 0)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == certificate_id:
                self.table.selectRow(row_index)
                return

    def _update_buttons_state(self):
        selected_rows = self._selected_rows()
        self.edit_button.setEnabled(len(selected_rows) == 1)
        self.export_button.setEnabled(len(selected_rows) >= 1)

    def _open_add_dialog(self):
        picker_dialog = Certificate14CardPickerDialog(self.viewmodel.card_picker_texts, self.viewmodel.card_options(), parent=self.window())
        if picker_dialog.exec() == 0:
            return

        selected_card = picker_dialog.get_selected_card()
        if selected_card is None:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.card_picker_texts["select_card_warning"])
            return

        try:
            self.viewmodel.create_record(selected_card)
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_rows()

    def _open_edit_dialog(self, *_args):
        selected_row = self._selected_row()
        if selected_row is None:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.dialog_texts["select_row_warning"])
            return

        current_record = next((record for record in self._records_cache if record.certificate_id == selected_row.certificate_id), None)
        if current_record is None:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.dialog_texts["select_row_warning"])
            return

        dialog = Certificate14Dialog(self.viewmodel.dialog_texts, full_name=selected_row.full_name, current_record=current_record, parent=self.window())
        if dialog.exec() == 0:
            return

        try:
            certificate_number, certificate_date, expiration_date, recipient_surname, is_returned, note = dialog.get_input()
            self.viewmodel.update_record(selected_row.certificate_id, certificate_number, certificate_date, expiration_date, recipient_surname, is_returned, note)
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_rows()

    def _export_selected_records(self):
        selected_rows = self._selected_rows()
        if not selected_rows:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.export_dialog_texts["select_rows_warning"])
            return

        destination_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            self.viewmodel.export_dialog_texts["save_title"],
            str(Path.cwd() / self.viewmodel.export_dialog_texts["default_file_name"]),
            self.viewmodel.export_dialog_texts["save_filter"],
        )
        if not destination_path:
            return

        try:
            self.viewmodel.export_records(
                [row.certificate_id for row in selected_rows],
                destination_path,
            )
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return
        except Exception as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        QMessageBox.information(
            self,
            self.viewmodel.export_dialog_texts["success_title"],
            self.viewmodel.export_dialog_texts["success_message"],
        )