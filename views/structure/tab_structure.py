from PySide6.QtCore import Qt
from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QAbstractItemView, QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from dialogs.structure import StructureUnitDialog
from viewmodels.structure import TabStructureViewModel


class StructureTreeWidget(QTreeWidget):
    """Дерево структури з повідомленням про завершене перетягування вузла."""

    def __init__(self, on_items_reordered, parent=None):
        super().__init__(parent)
        self._on_items_reordered = on_items_reordered

    def dropEvent(self, event: QDropEvent):
        super().dropEvent(event)
        if event.isAccepted() and self._on_items_reordered is not None:
            self._on_items_reordered()


class TabStructure(QWidget):
    """Вкладка керування структурою підприємства."""

    def __init__(self, parent=None, viewmodel: TabStructureViewModel | None = None):
        super().__init__(parent)
        self.viewmodel = viewmodel or TabStructureViewModel()
        self._units = []
        self._init_ui()
        self._load_units()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.add_button = QPushButton(self.viewmodel.add_button_text, self)
        self.add_button.clicked.connect(self._open_add_unit_dialog)
        button_layout.addWidget(self.add_button)

        self.add_child_button = QPushButton(self.viewmodel.add_child_button_text, self)
        self.add_child_button.clicked.connect(self._open_add_child_unit_dialog)
        button_layout.addWidget(self.add_child_button)

        self.edit_button = QPushButton(self.viewmodel.edit_button_text, self)
        self.edit_button.clicked.connect(self._open_edit_unit_dialog)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton(self.viewmodel.delete_button_text, self)
        self.delete_button.clicked.connect(self._delete_selected_unit)
        button_layout.addWidget(self.delete_button)

        main_layout.addLayout(button_layout)

        self.empty_state_label = QLabel(self.viewmodel.empty_state_text, self)
        self.empty_state_label.setWordWrap(True)
        main_layout.addWidget(self.empty_state_label)

        self.tree = StructureTreeWidget(self._handle_tree_reordered, self)
        self.tree.setColumnCount(len(self.viewmodel.headers))
        self.tree.setHeaderLabels(self.viewmodel.headers)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.setRootIsDecorated(True)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.itemSelectionChanged.connect(self._update_buttons_state)
        self.tree.itemDoubleClicked.connect(self._open_edit_unit_dialog)
        main_layout.addWidget(self.tree)

        self._update_buttons_state()

    def _load_units(self):
        self._units = self.viewmodel.get_units()
        self._refresh_tree()

    def _refresh_tree(self):
        self.tree.clear()
        self.empty_state_label.setVisible(not self._units)
        self.tree.setVisible(bool(self._units))
        if not self._units:
            self._update_buttons_state()
            return

        children_by_parent: dict[int | None, list] = {}
        for unit in self._units:
            children_by_parent.setdefault(unit.parent_id, []).append(unit)

        for items in children_by_parent.values():
            items.sort(key=lambda unit: (unit.sort_order, unit.unit_id))

        self._append_children(None, None, children_by_parent)
        self.tree.expandAll()
        self._update_buttons_state()

    def _handle_tree_reordered(self):
        selected_unit = self._selected_unit()
        selected_unit_id = selected_unit.unit_id if selected_unit is not None else None

        try:
            self.viewmodel.save_tree_order(self._serialize_tree())
        except ValueError as error:
            self._load_units()
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_units()
        if selected_unit_id is not None:
            self._restore_selection(selected_unit_id)

    def _append_children(self, parent_item: QTreeWidgetItem | None, parent_id: int | None, children_by_parent: dict[int | None, list]):
        for unit in children_by_parent.get(parent_id, []):
            item = QTreeWidgetItem([
                unit.name,
                unit.short_name,
                self.viewmodel.unit_type_label(unit.unit_type),
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, unit.unit_id)
            if parent_item is None:
                self.tree.addTopLevelItem(item)
            else:
                parent_item.addChild(item)
            self._append_children(item, unit.unit_id, children_by_parent)

    def _serialize_tree(self) -> list[dict]:
        serialized_items = []
        for index in range(self.tree.topLevelItemCount()):
            serialized_items.append(self._serialize_item(self.tree.topLevelItem(index)))
        return serialized_items

    def _serialize_item(self, item: QTreeWidgetItem) -> dict:
        children = []
        for index in range(item.childCount()):
            children.append(self._serialize_item(item.child(index)))
        return {
            "unit_id": item.data(0, Qt.ItemDataRole.UserRole),
            "children": children,
        }

    def _selected_unit(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return None

        selected_unit_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        for unit in self._units:
            if unit.unit_id == selected_unit_id:
                return unit
        return None

    def _restore_selection(self, unit_id: int):
        matching_items = self.tree.findItems("", Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive, 0)
        for item in matching_items:
            if item.data(0, Qt.ItemDataRole.UserRole) == unit_id:
                self.tree.setCurrentItem(item)
                return

    def _update_buttons_state(self):
        selected_unit = self._selected_unit()
        has_selection = selected_unit is not None
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.add_child_button.setEnabled(has_selection and self._next_child_unit_type(selected_unit) is not None)

    def _open_add_unit_dialog(self):
        dialog = StructureUnitDialog(
            self.viewmodel.dialog_texts,
            self.viewmodel.unit_type_options(),
            self._units,
            current_unit=None,
            initial_parent_id=None,
            parent=self.window(),
        )
        if dialog.exec() == 0:
            return

        try:
            self.viewmodel.create_unit(*dialog.get_input())
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_units()

    def _open_add_child_unit_dialog(self):
        selected_unit = self._selected_unit()
        if selected_unit is None:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.dialog_texts["select_unit_warning"])
            return

        initial_unit_type = self._next_child_unit_type(selected_unit)
        if initial_unit_type is None:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.dialog_texts["no_child_type_warning"])
            return

        dialog = StructureUnitDialog(
            self.viewmodel.dialog_texts,
            self.viewmodel.unit_type_options(),
            self._units,
            current_unit=None,
            initial_parent_id=selected_unit.unit_id,
            initial_unit_type=initial_unit_type,
            parent=self.window(),
        )
        if dialog.exec() == 0:
            return

        try:
            self.viewmodel.create_unit(*dialog.get_input())
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_units()

    def _open_edit_unit_dialog(self, *_args):
        selected_unit = self._selected_unit()
        if selected_unit is None:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.dialog_texts["select_unit_warning"])
            return

        dialog = StructureUnitDialog(
            self.viewmodel.dialog_texts,
            self.viewmodel.unit_type_options(),
            self._units,
            current_unit=selected_unit,
            initial_parent_id=selected_unit.parent_id,
            parent=self.window(),
        )
        if dialog.exec() == 0:
            return

        try:
            self.viewmodel.update_unit(selected_unit.unit_id, *dialog.get_input())
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_units()

    def _delete_selected_unit(self):
        selected_unit = self._selected_unit()
        if selected_unit is None:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, self.viewmodel.dialog_texts["select_unit_warning"])
            return

        answer = QMessageBox.question(
            self,
            self.viewmodel.dialog_texts["delete_confirmation_title"],
            self.viewmodel.dialog_texts["delete_confirmation_text"],
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.viewmodel.delete_unit(selected_unit.unit_id)
        except ValueError as error:
            QMessageBox.warning(self, self.viewmodel.validation_error_title, str(error))
            return

        self._load_units()

    def _unit_rank(self, unit_type: str) -> int:
        unit_type_codes = self.viewmodel.get_unit_type_codes()
        try:
            return unit_type_codes.index(unit_type)
        except ValueError:
            return len(unit_type_codes)

    def _next_child_unit_type(self, unit) -> str | None:
        if unit is None:
            return None
        return self.viewmodel.next_child_unit_type(unit.unit_type)
