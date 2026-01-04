import numpy as np

class SheetGroup:
    def __init__(self, columns, rows, table_vals):
        self.columns = columns
        self.rows = rows
        self.shape = table_vals.shape

        self.table_vals = []
        self.drug_names = np.full(self.shape, None, dtype=object)
        self.cuboids_count = np.zeros(self.shape, dtype=int)
        self.is_background = np.zeros(self.shape, dtype=bool)

        self.table_vals.append(table_vals)

    def add_new_sheet(self, table_vals):
        self.table_vals.append(table_vals)

    def set_drug_name(self, row, col, drug_name):
        """
        Sets the drug name of a given cell.
        """
        pass

    def set_cuboids_count(self, row, col, cuboids_count):
        pass

    def set_is_background(self, row, col, is_background):
        pass