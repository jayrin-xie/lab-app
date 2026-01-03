import numpy as np
import 

class SheetGroup:
    def __init__(self, columns, rows, table_vals):
        self.columns = columns
        self.rows = rows
        self.shape = table_vals.shape

        self.table_vals = []
        self.drug_names = []
        self.cuboids_count = []
        self.is_background = []

        self.table_vals.append(table_vals)
        self.drug_names.append(np.full(self.shape, None, dtype=object))
        self.cuboids_count.append(np.zeros(self.shape, dtype=int))
        self.is_background.append(np.zeros(self.shape, dtype=bool))

    def add_new_sheet(self, table_vals):
        self.table_vals.append(table_vals)
        self.drug_names.append(np.full(self.shape, None, dtype=object))
        self.cuboids_count.append(np.zeros(self.shape, dtype=int))
        self.is_background.append(np.zeros(self.shape, dtype=bool))

    def set_drug_name(self, row, col, drug_name):
        pass

    def set_cuboids_count(self, row, col, cuboids_count):
        pass

    def set_is_background(self, row, col, is_background):
        pass