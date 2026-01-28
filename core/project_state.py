import os
from core import sheet_group
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

    def set_cuboids_count(self, sheet, row, col, cuboids_count):
      self.sheet_groups[sheet].set_cuboids_count(row, col, cuboids_count)

    def set_is_background(self, sheet, row, col, is_background):
      self.sheet_groups[sheet].set_is_background(row, col, is_background)

    def export_to_excel(self, sheet):
      """
      Todo: write an in depth overview on how this works
      """
      # File Row Column Drug Cuboids Value

    def get_sheet_group_names(self):
        return self.sheet_group.keys()

    def get_all_files_from_same_sheet_group(self, sheet_name):
        return self.sheet_groups[sheet_name].get_file_names()

    def get_columns(self, sheet_name):
        """
        Returns the columns for a given sheet group.
        """
        return self.sheet_groups[sheet_name].columns

    def get_rows(self, sheet_name):
        """
        Returns the rows for a given sheet group.
        """
        return self.sheet_groups[sheet_name].rows

    def get_table_vals(self, sheet_name):
        """
        Returns the table_vals dictionary for a given sheet group.
        """
        return self.sheet_groups[sheet_name].table_vals

    def get_drug_names(self, sheet_name, row=None, col=None):
        """
        Returns the drug_names array for a given sheet group.
        If row and col are provided, returns the value at that specific cell.
        """
        if row is not None and col is not None:
            return self.sheet_groups[sheet_name].drug_names[row, col]
        return self.sheet_groups[sheet_name].drug_names

    def get_cuboids_count(self, sheet_name, row=None, col=None):
        """
        Returns the cuboids_count array for a given sheet group.
        If row and col are provided, returns the value at that specific cell.
        """
        if row is not None and col is not None:
            return self.sheet_groups[sheet_name].cuboids_count[row, col]
        return self.sheet_groups[sheet_name].cuboids_count

    def get_is_background(self, sheet_name, row=None, col=None):
        """
        Returns the is_background array for a given sheet group.
        If row and col are provided, returns the value at that specific cell.
        """
        if row is not None and col is not None:
            return self.sheet_groups[sheet_name].is_background[row, col]
        return self.sheet_groups[sheet_name].is_background
    