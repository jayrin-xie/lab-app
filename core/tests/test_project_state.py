import pytest
import numpy as np
from core.project_state import ProjectState
from core.tests.test_utils import _single_sheet_expected_dataframe, _multiple_sheets_expected_dataframes

SINGLE_SHEET_PATH = "core/tests/example_data/single_sheet.xlsx"
MULTIPLE_SHEETS_PATH = "core/tests/example_data/double_sheet.xlsx"

def test_load_excel_file_single_sheet():
    # Create a project state
    project_state = ProjectState()
    
    # Load the single sheet Excel file
    project_state.load_excel_file(SINGLE_SHEET_PATH)
    
    # Get the expected dataframe and convert to expected numpy arrays
    expected_df = _single_sheet_expected_dataframe()
    expected_table_vals = expected_df.to_numpy()
    expected_columns = np.array(expected_df.columns)
    expected_rows = np.array(expected_df.index)
    
    # Check that the sheet group exists and has the expected structure
    assert "Sheet1" in project_state.sheet_groups
    sheet_group = project_state.sheet_groups["Sheet1"]
    
    # Check columns, rows, and shape
    assert np.array_equal(sheet_group.columns, expected_columns)
    assert np.array_equal(sheet_group.rows, expected_rows)
    assert sheet_group.shape == expected_table_vals.shape
    
    # Check table_vals
    assert len(sheet_group.table_vals) == 1
    assert np.array_equal(sheet_group.table_vals[0], expected_table_vals)

def test_load_excel_file_double_sheet():
    # Create a project state
    project_state = ProjectState()
    
    # Load the double sheet Excel file
    project_state.load_excel_file(MULTIPLE_SHEETS_PATH)
    
    # Get the expected dataframes and convert to expected numpy arrays
    expected_df1, expected_df2 = _multiple_sheets_expected_dataframes()
    
    # Convert first sheet to numpy arrays
    expected_table_vals1 = expected_df1.to_numpy()
    expected_columns1 = np.array(expected_df1.columns)
    expected_rows1 = np.array(expected_df1.index)
    
    # Convert second sheet to numpy arrays
    expected_table_vals2 = expected_df2.to_numpy()
    expected_columns2 = np.array(expected_df2.columns)
    expected_rows2 = np.array(expected_df2.index)
    
    # Check that both sheet groups exist
    assert "Sheet1" in project_state.sheet_groups
    assert "Sheet2" in project_state.sheet_groups
    
    # Check Sheet1
    sheet_group1 = project_state.sheet_groups["Sheet1"]
    assert np.array_equal(sheet_group1.columns, expected_columns1)
    assert np.array_equal(sheet_group1.rows, expected_rows1)
    assert sheet_group1.shape == expected_table_vals1.shape
    assert len(sheet_group1.table_vals) == 1
    assert np.array_equal(sheet_group1.table_vals[0], expected_table_vals1)
    
    # Check Sheet2
    sheet_group2 = project_state.sheet_groups["Sheet2"]
    assert np.array_equal(sheet_group2.columns, expected_columns2)
    assert np.array_equal(sheet_group2.rows, expected_rows2)
    assert sheet_group2.shape == expected_table_vals2.shape
    assert len(sheet_group2.table_vals) == 1
    assert np.array_equal(sheet_group2.table_vals[0], expected_table_vals2)

