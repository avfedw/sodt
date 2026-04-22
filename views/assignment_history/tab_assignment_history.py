from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from viewmodels.assignment_history import TabAssignmentHistoryViewModel


class TabAssignmentHistory(QWidget):
    """Інтерфейс для перегляду історії призначень з фільтрами."""

    def __init__(self, parent=None, viewmodel: TabAssignmentHistoryViewModel | None = None):
        super().__init__(parent)
        self.viewmodel = viewmodel or TabAssignmentHistoryViewModel()
        self._column_widths = [260, 240, 150, 220, 180, 150]
        self._rows = []
        self._init_ui()
        self._load_rows()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        controls_layout = QHBoxLayout()
        self.position_filter_input = QLineEdit(self)
        self.position_filter_input.setPlaceholderText(self.viewmodel.position_filter_placeholder)
        self.position_filter_input.textChanged.connect(self._load_rows)
        controls_layout.addWidget(self.position_filter_input)

        self.person_filter_input = QLineEdit(self)
        self.person_filter_input.setPlaceholderText(self.viewmodel.person_filter_placeholder)
        self.person_filter_input.textChanged.connect(self._load_rows)
        controls_layout.addWidget(self.person_filter_input)

        self.refresh_button = QPushButton(self.viewmodel.refresh_button_text, self)
        self.refresh_button.clicked.connect(self._load_rows)
        controls_layout.addWidget(self.refresh_button)
        layout.addLayout(controls_layout)

        self.empty_state_label = QLabel(self.viewmodel.empty_state_text, self)
        self.empty_state_label.setWordWrap(True)
        layout.addWidget(self.empty_state_label)

        self.table = QTableWidget(self)
        self.table.setColumnCount(len(self.viewmodel.headers))
        self.table.setHorizontalHeaderLabels(self.viewmodel.headers)
        self.table.setRowCount(0)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        for column_index, width in enumerate(self._column_widths):
            self.table.setColumnWidth(column_index, width)

        layout.addWidget(self.table)

    def _load_rows(self) -> None:
        self._rows = self.viewmodel.get_rows(
            self.position_filter_input.text(),
            self.person_filter_input.text(),
        )
        self.table.setRowCount(len(self._rows))
        self.empty_state_label.setVisible(not self._rows)

        for row_index, row in enumerate(self._rows):
            values = [
                row.short_name_chain,
                row.job_title,
                row.surname,
                row.name_patronymic,
                row.appointment_order_number,
                row.appointment_order_date,
            ]
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, row.history_id)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_index, column_index, item)
