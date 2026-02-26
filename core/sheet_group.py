import numpy as np

# class SheetGroup:
#     def __init__(self, columns, rows, filename, table_vals):
#         self.columns = columns
#         self.rows = rows
#         self.shape = table_vals.shape

#         self.table_vals = {}
#         self.drug_names = np.full(self.shape, None, dtype=object)
#         self.cuboids_count = np.zeros(self.shape, dtype=int)
#         self.is_background = np.zeros(self.shape, dtype=bool)

#         self.table_vals[filename] = table_vals

class SheetGroup:
    def __init__(self, columns, rows, first_table_id, first_table_vals):
        self.columns = list(columns)
        self.rows = list(rows)

        # stored tables: id -> numpy 2D
        self.table_vals = {first_table_id: first_table_vals}

        # metadata arrays aligned to master grid
        self.condition_names = np.full((len(rows), len(columns)), "", dtype=object)
        self.cuboids_count = np.full((len(self.rows), len(self.columns)), np.nan, dtype=float)
        self.is_background = np.full((len(self.rows), len(self.columns)), False, dtype=bool)

    
    def _expand_master_grid(self, new_rows, new_cols):
        """
        Expand self.rows/self.columns to include new labels.
        Also expands metadata arrays and existing stored tables with NaN padding.
        """
        old_rows = list(self.rows)
        old_cols = list(self.columns)

        # union while preserving existing order, append new at end
        for r in new_rows:
            if r not in self.rows:
                self.rows.append(r)
        for c in new_cols:
            if c not in self.columns:
                self.columns.append(c)

        # if no change, nothing to do
        if self.rows == old_rows and self.columns == old_cols:
            return

        new_shape = (len(self.rows), len(self.columns))

        # expand metadata arrays
        def pad_array(arr, fill_value):
            out = np.full(new_shape, fill_value, dtype=arr.dtype)
            # map old indices into new
            row_map = {r: i for i, r in enumerate(self.rows)}
            col_map = {c: j for j, c in enumerate(self.columns)}
            for i_old, r in enumerate(old_rows):
                for j_old, c in enumerate(old_cols):
                    out[row_map[r], col_map[c]] = arr[i_old, j_old]
            return out

        self.condition_names = pad_array(self.condition_names, "")
        self.cuboids_count = pad_array(self.cuboids_count, np.nan)
        self.is_background = pad_array(self.is_background, False)

        # expand existing stored tables
        new_table_vals = {}
        row_map = {r: i for i, r in enumerate(self.rows)}
        col_map = {c: j for j, c in enumerate(self.columns)}

        for table_id, arr in self.table_vals.items():
            out = np.full(new_shape, np.nan, dtype=float)

            # old arr might not be float—convert safely
            arr_num = arr.astype(float) if arr.dtype != float else arr

            for i_old, r in enumerate(old_rows):
                for j_old, c in enumerate(old_cols):
                    out[row_map[r], col_map[c]] = arr_num[i_old, j_old]

            new_table_vals[table_id] = out

        self.table_vals = new_table_vals

    def add_new_sheet(self, table_id, table_vals, table_rows, table_cols):
        """
        Add a new table, aligning it to the master grid by row/col labels.
        """
        table_rows = list(table_rows)
        table_cols = list(table_cols)

        # 1) expand master grid to include any new labels
        self._expand_master_grid(table_rows, table_cols)

        # 2) create aligned array with NaNs
        out = np.full((len(self.rows), len(self.columns)), np.nan, dtype=float)

        row_map = {r: i for i, r in enumerate(self.rows)}
        col_map = {c: j for j, c in enumerate(self.columns)}

        # 3) place incoming values by label
        table_vals_num = table_vals.astype(float) if table_vals.dtype != float else table_vals

        for i, r in enumerate(table_rows):
            for j, c in enumerate(table_cols):
                out[row_map[r], col_map[c]] = table_vals_num[i, j]

        self.table_vals[table_id] = out

    # def add_new_sheet(self, filename, table_vals):
    #     self.table_vals[filename] = table_vals

    def set_condition_name(self, row, col, condition_name):
        """
        Sets the condition name of a given cell.
        """
        self.condition_names[row, col] = condition_name

    def set_cuboids_count(self, row, col, cuboids_count):
        self.cuboids_count[row, col] = cuboids_count

    def set_is_background(self, row, col, is_background):
        self.is_background[row, col] = is_background

    def get_file_names(self):
      return self.table_vals.keys()

    def get_unique_condition_names(self):
        return np.unique(self.condition_names)

    # backward-compatible alias (optional)
    def get_unique_drug_names(self):
        return self.get_unique_condition_names()