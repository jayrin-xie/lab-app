import os
from core.sheet_group import SheetGroup
from core.utils import load_excel_file, convert_sheet_to_numpy

class ProjectState:
    def __init__(self):
        self.sheet_groups = {}

    def load_excel_file(self, file_path):
      """
      Loads an excel file and adds sheets to corresponding sheet groups.
      """
      filename = os.path.basename(file_path)
      dataframes = load_excel_file(file_path)
      for sheet_name, dataframe in dataframes.items():
          table_vals, rows, columns = convert_sheet_to_numpy(dataframe)
          if sheet_name in self.sheet_groups:
              self.sheet_groups[sheet_name].add_new_sheet(filename, table_vals)
          else:
              self.sheet_groups[sheet_name] = SheetGroup(columns, rows, filename, table_vals)

    def set_drug_name(self, sheet, row, col, drug_name):
      self.sheet_groups[sheet].set_drug_name(row, col, drug_name)

    def set_cuboid_count(self, sheet, row, col, cuboids_count):
      self.sheet_groups[sheet].set_cuboids_count(row, col, cuboids_count)

    def set_is_background(self, sheet, row, col, is_background):
      self.sheet_groups[sheet].set_is_background(row, col, is_background)

    def export_to_excel(self, sheet):
      """
      Todo: write an in depth overview on how this works
      """
      pass