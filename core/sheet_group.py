import numpy as np

class SheetGroup:
    def __init__(self, columns, rows, filename, table_vals):
        self.columns = columns
        self.rows = rows
        self.shape = table_vals.shape

        self.table_vals = {}
        self.drug_names = np.full(self.shape, None, dtype=object)
        self.cuboids_count = np.zeros(self.shape, dtype=int)
        self.is_background = np.zeros(self.shape, dtype=bool)

        self.table_vals[filename] = table_vals

    def add_new_sheet(self, filename, table_vals):
        self.table_vals[filename] = table_vals

    def set_drug_name(self, row, col, drug_name):
        """
        Sets the drug name of a given cell.
        """
        self.drug_names[row, col] = drug_name

    def set_cuboids_count(self, row, col, cuboids_count):
        self.cuboids_count[row, col] = cuboids_count

    def set_is_background(self, row, col, is_background):
        self.is_background[row, col] = is_background

    def get_file_names(self):
      return self.table_vals.keys()