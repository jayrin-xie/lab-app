import pytest
import numpy as np
from core.sheet_group import SheetGroup

def test_sheet_group():
  """
  Test the creation of a sheet group. Make sure that each of the fields are correct.
  Try updating fields and make sure that the updates run correctly
  """
  # Create test data
  columns = np.array([2, 3])
  rows = np.array(["B", "C", "D"])
  table_vals = np.array([[3098, 2856, 2162], [2991, 3910, 2433]]).T  # 3x2 array
  filename1 = "test_file1.xlsx"

  # Create sheet group, assert all fields are correct
  sheet_group = SheetGroup(columns, rows, filename1, table_vals)
  
  assert np.array_equal(sheet_group.columns, columns)
  assert np.array_equal(sheet_group.rows, rows)
  assert sheet_group.shape == table_vals.shape
  assert len(sheet_group.table_vals) == 1
  assert filename1 in sheet_group.table_vals
  assert np.array_equal(sheet_group.table_vals[filename1], table_vals)
  assert sheet_group.drug_names.shape == table_vals.shape
  assert np.all(sheet_group.drug_names == None)
  assert sheet_group.cuboids_count.shape == table_vals.shape
  assert np.all(sheet_group.cuboids_count == 0)
  assert sheet_group.is_background.shape == table_vals.shape
  assert np.all(sheet_group.is_background == False)

  # Add a new sheet. Verify state
  filename2 = "test_file2.xlsx"
  new_table_vals = np.array([[3100, 2900, 2200], [3000, 4000, 2500]]).T
  sheet_group.add_new_sheet(filename2, new_table_vals)
  
  assert len(sheet_group.table_vals) == 2
  assert filename2 in sheet_group.table_vals
  assert np.array_equal(sheet_group.table_vals[filename2], new_table_vals)
  # Shape and other fields should remain unchanged
  assert sheet_group.shape == table_vals.shape

  # Update the drug name, verify state
  sheet_group.set_drug_name(0, 0, "Aspirin")
  assert sheet_group.drug_names[0, 0] == "Aspirin"
  # Other cells should still be None
  assert sheet_group.drug_names[0, 1] == None
  assert sheet_group.drug_names[1, 0] == None

  # Set cuboid count. Verify state
  sheet_group.set_cuboids_count(1, 1, 5)
  assert sheet_group.cuboids_count[1, 1] == 5
  # Other cells should still be 0
  assert sheet_group.cuboids_count[0, 0] == 0
  assert sheet_group.cuboids_count[1, 0] == 0

  # Set is_background, verify state
  sheet_group.set_is_background(2, 0, True)
  assert sheet_group.is_background[2, 0] == True
  # Other cells should still be False
  assert sheet_group.is_background[0, 0] == False
  assert sheet_group.is_background[2, 1] == False