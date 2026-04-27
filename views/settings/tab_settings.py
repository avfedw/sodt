from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from viewmodels.settings import TabSettingsViewModel


class TabSettings(QWidget):
    """Інтерфейс вкладки налаштувань."""

    def __init__(self, parent=None, viewmodel: TabSettingsViewModel | None = None):
        super().__init__(parent)
        self.viewmodel = viewmodel or TabSettingsViewModel()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        title_label = QLabel(self.viewmodel.title_text, self)
        font = title_label.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)

        description_label = QLabel(self.viewmodel.description_text, self)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        buttons_layout = QHBoxLayout()
        self.export_button = QPushButton(self.viewmodel.export_button_text, self)
        self.export_button.clicked.connect(self._export_database)
        buttons_layout.addWidget(self.export_button)

        self.import_button = QPushButton(self.viewmodel.import_button_text, self)
        self.import_button.clicked.connect(self._import_database)
        buttons_layout.addWidget(self.import_button)
        buttons_layout.addStretch(1)
        layout.addLayout(buttons_layout)
        layout.addStretch(1)

    def _export_database(self) -> None:
        target_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            self.viewmodel.file_dialog_texts["export_title"],
            str(Path.cwd() / self.viewmodel.file_dialog_texts["default_export_name"]),
            self.viewmodel.file_dialog_texts["filter"],
        )
        if not target_path:
            return

        try:
            self.viewmodel.export_database(target_path)
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.messages["error_title"], str(error))
            return
        except Exception as error:
            QMessageBox.warning(self, self.viewmodel.messages["error_title"], str(error))
            return

        QMessageBox.information(self, self.viewmodel.messages["success_title"], self.viewmodel.messages["export_success"])

    def _import_database(self) -> None:
        source_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            self.viewmodel.file_dialog_texts["import_title"],
            str(Path.cwd()),
            self.viewmodel.file_dialog_texts["filter"],
        )
        if not source_path:
            return

        answer = QMessageBox.question(
            self,
            self.viewmodel.messages["error_title"],
            self.viewmodel.messages["import_confirm"],
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.viewmodel.import_database(source_path)
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.messages["error_title"], str(error))
            return
        except Exception as error:
            QMessageBox.warning(self, self.viewmodel.messages["error_title"], str(error))
            return

        QMessageBox.information(self, self.viewmodel.messages["success_title"], self.viewmodel.messages["import_success"])