import sys
from pathlib import Path

import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc

import pandas as pd
import numpy as np

from project_state import ProjectState


class DataFrameModel(qtc.QAbstractTableModel):
    def __init__(self, df: pd.DataFrame | None = None):
        super().__init__()
        self._df = df if df is not None else pd.DataFrame()

    def set_df(self, df: pd.DataFrame):
        self.beginResetModel()
        self._df = df
        self.endResetModel()

    def rowCount(self, parent=qtc.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=qtc.QModelIndex()):
        return len(self._df.columns)

    def data(self, index, role=qtc.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role in (qtc.Qt.ItemDataRole.DisplayRole, qtc.Qt.ItemDataRole.EditRole):
            val = self._df.iat[index.row(), index.column()]
            if pd.isna(val):
                return ""
            return str(val)
        return None

    def headerData(self, section, orientation, role=qtc.Qt.ItemDataRole.DisplayRole):
        if role != qtc.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == qtc.Qt.Orientation.Horizontal:
            return str(self._df.columns[section])
        return str(self._df.index[section])


# Main Window
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tec Table Analyzer")
        self.resize(1250, 750)

        self.state = ProjectState()
        self.current_sheet = None
        self.visible_rows = []
        self.visible_cols = []
        self.current_table_id = None
        self._updating_plate_table = False  # guard to avoid signal loops
        self.norm_control_by_plate = {} # track which sheet is set as normalization control

        # Central layout
        central = qtw.QWidget()
        self.setCentralWidget(central)
        root = qtw.QHBoxLayout(central)

        # Left controls
        left = qtw.QVBoxLayout()
        root.addLayout(left, 1)

        # Right main area
        right = qtw.QVBoxLayout()
        root.addLayout(right, 3)

        # ---- Buttons row
        btn_row = qtw.QHBoxLayout()
        self.btn_load = qtw.QPushButton("Load Excel files")
        self.btn_export = qtw.QPushButton("Export to Excel")
        btn_row.addWidget(self.btn_load)
        btn_row.addWidget(self.btn_export)
        left.addLayout(btn_row)

        self.btn_load.clicked.connect(self.on_load_files)
        self.btn_export.clicked.connect(self.on_export)

        # ---- Loaded files list
        left.addWidget(qtw.QLabel("Loaded files:"))
        self.files_list = qtw.QListWidget()
        left.addWidget(self.files_list)

        # ---- Sheet selection
        left.addSpacing(10)
        left.addWidget(qtw.QLabel("Select plate (sheet group):"))
        self.sheet_combo = qtw.QComboBox()
        left.addWidget(self.sheet_combo)
        self.sheet_combo.currentTextChanged.connect(self.on_sheet_changed)

        # ---- Table selection for preview
        left.addWidget(qtw.QLabel("Select extracted table (preview):"))
        self.table_combo = qtw.QComboBox()
        left.addWidget(self.table_combo)
        self.table_combo.currentTextChanged.connect(self.on_table_changed)

        # ---- Metadata editor for selected well
        left.addSpacing(15)
        left.addWidget(qtw.QLabel("Selected well metadata:"))
        form = qtw.QFormLayout()
        left.addLayout(form)

        self.lbl_selected = qtw.QLabel("(none)")
        self.edit_condition = qtw.QLineEdit()
        self.spin_cuboids = qtw.QSpinBox()
        self.spin_cuboids.setRange(0, 999)
        self.chk_background = qtw.QCheckBox("Background")

        form.addRow("Well:", self.lbl_selected)
        form.addRow("Condition:", self.edit_condition)
        form.addRow("Cuboids:", self.spin_cuboids)
        form.addRow("", self.chk_background)

        self.btn_apply = qtw.QPushButton("Apply to selected well")
        left.addWidget(self.btn_apply)
        self.btn_apply.clicked.connect(self.on_apply_metadata)

        # Clear metadata button (for all selected wells at a time)
        self.btn_clear = qtw.QPushButton("Clear selected well metadata")
        left.addWidget(self.btn_clear)
        self.btn_clear.clicked.connect(self.on_clear_metadata)

        left.addStretch(1)

        # Normalization button added (within Selected well metadata)
        left.addSpacing(10)
        left.addWidget(qtw.QLabel("Normalize ratio tables:"))

        self.norm_combo = qtw.QComboBox()
        self.norm_combo.setEditable(False)
        left.addWidget(self.norm_combo)

        self.btn_norm_export = qtw.QPushButton("Set as control for normalization")
        left.addWidget(self.btn_norm_export)
        self.btn_norm_export.clicked.connect(self.on_set_normalization_control)

        self.lbl_norm_status = qtw.QLabel("Control: (not set)")
        left.addWidget(self.lbl_norm_status)

        # Right: Split into plate editor + preview
        splitter = qtw.QSplitter(qtc.Qt.Orientation.Vertical)
        right.addWidget(splitter)

        # Plate editor panel
        plate_panel = qtw.QWidget()
        plate_layout = qtw.QVBoxLayout(plate_panel)
        plate_layout.addWidget(qtw.QLabel("Well plate editor (click a well):"))

        self.plate_table = qtw.QTableWidget()
        self.plate_table.setEditTriggers(
            qtw.QAbstractItemView.EditTrigger.NoEditTriggers
        )  # we edit via controls, not directly
        self.plate_table.setSelectionMode(qtw.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.plate_table.setSelectionBehavior(qtw.QAbstractItemView.SelectionBehavior.SelectItems)
        self.plate_table.cellClicked.connect(self.on_plate_cell_clicked)

        # Preview panel
        preview_panel = qtw.QWidget()
        preview_layout = qtw.QVBoxLayout(preview_panel)
        preview_layout.addWidget(qtw.QLabel("Extracted table preview (from raw_tables):"))

        self.preview_view = qtw.QTableView()
        self.preview_model = DataFrameModel(pd.DataFrame())
        self.preview_view.setModel(self.preview_model)
        self.preview_view.setAlternatingRowColors(True)
        self.preview_view.horizontalHeader().setStretchLastSection(True)

        plate_layout.addWidget(self.plate_table)
        splitter.addWidget(plate_panel)

        preview_layout.addWidget(self.preview_view)
        splitter.addWidget(preview_panel)
        
        splitter.setSizes([420, 320])

        # Style tweaks (optional)
        self._set_default_font()

    # UI helpers
    def _set_default_font(self):
        f = self.font()
        f.setPointSize(11)
        self.setFont(f)

    def _refresh_sheet_groups_ui(self):
        self.sheet_combo.blockSignals(True)
        self.sheet_combo.clear()
        names = list(self.state.get_sheet_group_names())
        self.sheet_combo.addItems(names)
        self.sheet_combo.blockSignals(False)

        if names:
            self.sheet_combo.setCurrentText(names[0])

    def _refresh_tables_ui(self, sheet_name: str):
        self.table_combo.blockSignals(True)
        self.table_combo.clear()
        if not sheet_name:
            self.table_combo.blockSignals(False)
            return

        table_ids = sorted([tid for (s, tid) in self.state.raw_tables.keys() if s == sheet_name])
        self.table_combo.addItems(table_ids)
        self.table_combo.blockSignals(False)

        if table_ids:
            self.table_combo.setCurrentText(table_ids[0])

    def _build_plate_grid(self, sheet_name: str):
        """
        Build the plate grid from SheetGroup rows/columns.
        """
        # group = self.state.sheet_groups.get(sheet_name)
        # if not group:
        #     self.plate_table.clear()
        #     self.plate_table.setRowCount(0)
        #     self.plate_table.setColumnCount(0)
        #     return

        # rows = [str(r) for r in group.rows]
        # cols = [str(c) for c in group.columns]

        group = self.state.sheet_groups.get(sheet_name)
        if not group:
            self.plate_table.clear()
            self.plate_table.setRowCount(0)
            self.plate_table.setColumnCount(0)
            return

        # Prefer the currently selected raw table shape for this plate
        df = None
        if self.current_table_id:
            df = self.state.raw_tables.get((sheet_name, self.current_table_id))

        if df is not None:
            rows = [str(r) for r in df.index]
            cols = [str(c) for c in df.columns]
        else:
            rows = [str(r) for r in group.rows]
            cols = [str(c) for c in group.columns]

        # remember what is currently visible in the editor
        self.visible_rows = rows
        self.visible_cols = cols

        self._updating_plate_table = True
        try:
            self.plate_table.clear()
            self.plate_table.setRowCount(len(rows))
            self.plate_table.setColumnCount(len(cols))
            self.plate_table.setVerticalHeaderLabels(rows)
            self.plate_table.setHorizontalHeaderLabels(cols)

            # reasonable sizing
            self.plate_table.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.ResizeMode.ResizeToContents)
            self.plate_table.verticalHeader().setSectionResizeMode(qtw.QHeaderView.ResizeMode.ResizeToContents)

            # fill cells with short summary: condition + cuboids + background flag
            for r_i in range(len(rows)):
                for c_i in range(len(cols)):
                    item = qtw.QTableWidgetItem()
                    item.setTextAlignment(qtc.Qt.AlignmentFlag.AlignCenter)

                    # cond = group.condition_names[r_i, c_i]
                    # cub = group.cuboids_count[r_i, c_i]
                    # bg = group.is_background[r_i, c_i]

                    r_label = rows[r_i]
                    c_label = cols[c_i]

                    ri = group.rows.index(r_label) if r_label in group.rows else None
                    # cj = group.columns.index(c_label) if c_label in group.columns else None

                    if c_label in group.columns:
                        cj = group.columns.index(c_label)
                    else:
                        try:
                            cj = group.columns.index(int(c_label))
                        except (ValueError, TypeError):
                            cj = None

                    if ri is None or cj is None:
                        cond, cub, bg = "", np.nan, False
                    else:
                        cond = group.condition_names[ri, cj]
                        cub = group.cuboids_count[ri, cj]
                        bg = group.is_background[ri, cj]

                    # compact display
                    parts = []
                    if cond:
                        parts.append(cond)
                    if not pd.isna(cub) and int(cub) != 0:
                        parts.append(f"n={int(cub)}")
                    if bg:
                        parts.append("BG")

                    item.setText("\n".join(parts))

                    # subtle background cue
                    if bg:
                        item.setBackground(qtg.QBrush(qtg.QColor(230, 230, 230)))

                    self.plate_table.setItem(r_i, c_i, item)

        finally:
            self._updating_plate_table = False

    def _update_selected_well_editor(self, sheet_name: str, r_i: int, c_i: int):
        """
        Populate editor controls from SheetGroup arrays.
        """
        group = self.state.sheet_groups.get(sheet_name)
        if not group:
            return

        # Label well as RowLetter + ColumnNumber
        row_label = str(group.rows[r_i])
        col_label = str(group.columns[c_i])
        self.lbl_selected.setText(f"{sheet_name}  {row_label}{col_label}")

        self.edit_condition.setText(str(group.condition_names[r_i, c_i]) if group.condition_names[r_i, c_i] else "")
        cub = group.cuboids_count[r_i, c_i]
        self.spin_cuboids.setValue(0 if pd.isna(cub) else int(cub))
        self.chk_background.setChecked(bool(group.is_background[r_i, c_i]))

    def _refresh_one_plate_cell(self, sheet_name: str, r_i: int, c_i: int):
        """
        Refresh only one cell in the QTableWidget after edits.
        """
        group = self.state.sheet_groups.get(sheet_name)
        if not group:
            return

        item = self.plate_table.item(r_i, c_i)
        if item is None:
            item = qtw.QTableWidgetItem()
            item.setTextAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
            self.plate_table.setItem(r_i, c_i, item)

        cond = group.condition_names[r_i, c_i]
        cub = group.cuboids_count[r_i, c_i]
        bg = group.is_background[r_i, c_i]

        parts = []
        if cond:
            parts.append(cond)
        if not pd.isna(cub) and int(cub) != 0:
            parts.append(f"n={int(cub)}")
        if bg:
            parts.append("BG")

        item.setText("\n".join(parts))

        if bg:
            item.setBackground(qtg.QBrush(qtg.QColor(230, 230, 230)))
        else:
            item.setBackground(qtg.QBrush())  # reset

    def _show_preview_table(self, sheet_name: str, table_id: str):
        df = self.state.raw_tables.get((sheet_name, table_id))
        self.preview_model.set_df(df if df is not None else pd.DataFrame())

    # Slots
    def on_load_files(self):
        files, _ = qtw.QFileDialog.getOpenFileNames(
            self,
            "Select Excel files",
            str(Path.cwd()),
            "Excel Files (*.xlsx *.xls)"
        )
        if not files:
            return

        for f in files:
            try:
                self.state.load_workbook(f, mode="all")
                self.files_list.addItem(f)
            except Exception as e:
                qtw.QMessageBox.critical(self, "Load error", f"Failed to load:\n{f}\n\n{e}")

        self._refresh_sheet_groups_ui()

        # Force-refresh view immediately (no need to double click to be able to see the tables)
        if self.sheet_combo.count() > 0:
            first_sheet = self.sheet_combo.itemText(0)
            self.sheet_combo.setCurrentText(first_sheet)      # triggers on_sheet_changed

            # In case signal doesn't fire (sometimes same text), force call:
            self.on_sheet_changed(first_sheet)

            # Force preview to always show the first table
            if self.table_combo.count() > 0:
                first_table = self.table_combo.itemText(0)
                self.table_combo.setCurrentText(first_table)
                self.on_table_changed(first_table)

    def on_export(self):
        desktop = Path.home() / "Desktop"

        out_path, _ = qtw.QFileDialog.getSaveFileName(
            self,
            "Export to Excel",
            str(desktop / "name?.xlsx"),   # default location Desktop
            "Excel Files (*.xlsx)"
        )

        if not out_path:
            return
        try:
            self.state.export_to_excel(out_path)
            qtw.QMessageBox.information(self, "Export", f"Exported:\n{out_path}")
        except Exception as e:
            qtw.QMessageBox.critical(self, "Export error", str(e))

    def on_sheet_changed(self, sheet_name: str):
        self.current_sheet = sheet_name
        self._refresh_tables_ui(sheet_name)
        self._build_plate_grid(sheet_name)

        if self.table_combo.count() > 0:
            self.current_table_id = self.table_combo.currentText()
            self._show_preview_table(sheet_name, self.current_table_id)

        # clear selection editor
        self.lbl_selected.setText("(none)")
        self.edit_condition.clear()
        self.spin_cuboids.setValue(0)
        self.chk_background.setChecked(False)

        self._refresh_norm_combo(sheet_name)

    def _refresh_norm_combo(self, sheet_name: str):
        # get conditions currently used in this plate's metadata grid
        group = self.state.sheet_groups.get(sheet_name)
        self.norm_combo.clear()
        if not group:
            return

        conds = sorted({str(x).strip() for x in group.condition_names.flatten() if str(x).strip()})
        self.norm_combo.addItems(conds)

        # restore previously chosen control if exists
        if sheet_name in self.norm_control_by_plate:
            control = self.norm_control_by_plate[sheet_name]
            idx = self.norm_combo.findText(control)
            if idx >= 0:
                self.norm_combo.setCurrentIndex(idx)

        control = self.norm_control_by_plate.get(sheet_name, None)
        self.lbl_norm_status.setText(f"Control: {control if control else '(not set)'}")

    def on_set_normalization_control(self):
        if not self.current_sheet:
            return
        control = self.norm_combo.currentText().strip()
        if not control:
            return
        self.norm_control_by_plate[self.current_sheet] = control
        self.lbl_norm_status.setText(f"Control: {control}")
        self.state.set_norm_control(self.current_sheet, control)
        
    def on_table_changed(self, table_id: str):
        self.current_table_id = table_id
        if self.current_sheet and table_id:
            self._show_preview_table(self.current_sheet, table_id)
            self._build_plate_grid(self.current_sheet)  # rebuild plate grid to match new table shape (if different from master)

    def on_plate_cell_clicked(self, r_i: int, c_i: int):
        if self._updating_plate_table:
            return
        if not self.current_sheet:
            return
        # self._update_selected_well_editor(self.current_sheet, r_i, c_i)
        row_label = self.visible_rows[r_i]
        col_label = self.visible_cols[c_i]
        self._update_selected_well_editor_by_label(self.current_sheet, row_label, col_label)
    
    def _update_selected_well_editor_by_label(self, sheet_name: str, row_label: str, col_label: str):
        group = self.state.sheet_groups.get(sheet_name)
        if not group:
            return

        self.lbl_selected.setText(f"{sheet_name}  {row_label}{col_label}")

        # map labels into master grid
        if row_label not in group.rows or col_label not in group.columns:
            self.edit_condition.setText("")
            self.spin_cuboids.setValue(0)
            self.chk_background.setChecked(False)
            return

        ri = group.rows.index(row_label)
        cj = group.columns.index(col_label)

        self.edit_condition.setText(group.condition_names[ri, cj] or "")
        cub = group.cuboids_count[ri, cj]
        self.spin_cuboids.setValue(0 if pd.isna(cub) else int(cub))
        self.chk_background.setChecked(bool(group.is_background[ri, cj]))

    def on_apply_metadata(self):
        if not self.current_sheet:
            qtw.QMessageBox.warning(self, "No plate selected", "Select a plate first.")
            return

        selected = self.plate_table.selectedIndexes()
        if not selected:
            qtw.QMessageBox.warning(self, "No wells selected", "Select one or more wells first.")
            return

        condition = self.edit_condition.text().strip()
        cuboids = int(self.spin_cuboids.value())
        is_bg = bool(self.chk_background.isChecked())

        for idx in selected:
            # r_i, c_i = idx.row(), idx.column()
            # self.state.set_condition_name(self.current_sheet, r_i, c_i, condition)
            # self.state.set_cuboids_count(self.current_sheet, r_i, c_i, cuboids)
            # self.state.set_is_background(self.current_sheet, r_i, c_i, is_bg)
            r_i, c_i = idx.row(), idx.column()
            row_label = self.visible_rows[r_i]
            col_label = self.visible_cols[c_i]

            # map to master indices
            group = self.state.sheet_groups[self.current_sheet]
            ri = group.rows.index(row_label)

            # normalize column label to match master grid type
            if col_label in group.columns:
                cj = group.columns.index(col_label)
            else:
                try:
                    col_numeric = int(col_label)
                    cj = group.columns.index(col_numeric)
                except (ValueError, TypeError):
                    continue

            self.state.set_condition_name(self.current_sheet, ri, cj, condition)
            self.state.set_cuboids_count(self.current_sheet, ri, cj, cuboids)
            self.state.set_is_background(self.current_sheet, ri, cj, is_bg)

            self._refresh_one_plate_cell(self.current_sheet, r_i, c_i)  # refresh visible cell

            # refresh the cell text/background in the plate table
            self._refresh_one_plate_cell(self.current_sheet, r_i, c_i)


    def on_clear_metadata(self):
        if not self.current_sheet:
            return

        selected = self.plate_table.selectedIndexes()
        if not selected:
            return

        group = self.state.sheet_groups.get(self.current_sheet)
        if not group:
            return

        for idx in selected:
            r_i, c_i = idx.row(), idx.column()

            # visible labels from the currently displayed plate grid
            row_label = self.visible_rows[r_i]
            col_label = self.visible_cols[c_i]

            # map labels -> master grid indices
            if row_label not in group.rows or col_label not in group.columns:
                continue

            ri = group.rows.index(row_label)
            cj = group.columns.index(col_label)

            # clear backend metadata on the MASTER grid
            self.state.set_condition_name(self.current_sheet, ri, cj, "")
            self.state.set_cuboids_count(self.current_sheet, ri, cj, 0)
            self.state.set_is_background(self.current_sheet, ri, cj, False)

            # refresh the VISIBLE cell in the UI
            self._refresh_one_plate_cell(self.current_sheet, r_i, c_i)

        # reset editor controls
        self.lbl_selected.setText("(none)")
        self.edit_condition.clear()
        self.spin_cuboids.setValue(0)
        self.chk_background.setChecked(False)
    # def on_clear_metadata(self):
    #     if not self.current_sheet:
    #         return

    #     selected = self.plate_table.selectedIndexes()
    #     if not selected:
    #         return

    #     for idx in selected:
    #         r_i, c_i = idx.row(), idx.column()

    #         # Clear metadata in backend
    #         self.state.set_condition_name(self.current_sheet, r_i, c_i, "")
    #         self.state.set_cuboids_count(self.current_sheet, r_i, c_i, 0)
    #         self.state.set_is_background(self.current_sheet, r_i, c_i, False)

    #         # Refresh UI cell
    #         self._refresh_one_plate_cell(self.current_sheet, r_i, c_i)

    #     # Reset editor panel
    #     self.lbl_selected.setText("(none)")
    #     self.edit_condition.clear()
    #     self.spin_cuboids.setValue(0)
    #     self.chk_background.setChecked(False)

def main():
    app = qtw.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()