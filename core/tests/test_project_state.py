import pytest
import numpy as np
import os
from core.project_state import ProjectState
from core.tests.conftest import (
    single_sheet_expected_dataframe,
    multiple_sheets_expected_dataframes,
    SINGLE_SHEET_PATH,
    MULTIPLE_SHEETS_PATH,
)

def test_load_single_excel_file_single_sheet():
    # Create a project state
    project_state = ProjectState()
    
    # Load the single sheet Excel file
    project_state.load_excel_file(SINGLE_SHEET_PATH)
    
    # Get the expected dataframe and convert to expected numpy arrays
    expected_df = single_sheet_expected_dataframe()
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
    filename = os.path.basename(SINGLE_SHEET_PATH)
    assert len(sheet_group.table_vals) == 1
    assert filename in sheet_group.table_vals
    assert np.array_equal(sheet_group.table_vals[filename], expected_table_vals)

def test_load_excel_file_double_sheet():
    # Create a project state
    project_state = ProjectState()
    
    # Load the double sheet Excel file
    project_state.load_excel_file(MULTIPLE_SHEETS_PATH)
    
    # Get the expected dataframes and convert to expected numpy arrays
    expected_df1, expected_df2 = multiple_sheets_expected_dataframes()
    
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
    filename = os.path.basename(MULTIPLE_SHEETS_PATH)
    sheet_group1 = project_state.sheet_groups["Sheet1"]
    assert np.array_equal(sheet_group1.columns, expected_columns1)
    assert np.array_equal(sheet_group1.rows, expected_rows1)
    assert sheet_group1.shape == expected_table_vals1.shape
    assert len(sheet_group1.table_vals) == 1
    assert filename in sheet_group1.table_vals
    assert np.array_equal(sheet_group1.table_vals[filename], expected_table_vals1)
    
    # Check Sheet2
    sheet_group2 = project_state.sheet_groups["Sheet2"]
    assert np.array_equal(sheet_group2.columns, expected_columns2)
    assert np.array_equal(sheet_group2.rows, expected_rows2)
    assert sheet_group2.shape == expected_table_vals2.shape
    assert len(sheet_group2.table_vals) == 1
    assert filename in sheet_group2.table_vals
    assert np.array_equal(sheet_group2.table_vals[filename], expected_table_vals2)

def test_load_both_files_combine_sheet1():
    # Create a project state
    project_state = ProjectState()
    
    # Load the single sheet Excel file first
    project_state.load_excel_file(SINGLE_SHEET_PATH)
    
    # Load the double sheet Excel file (which also contains Sheet1)
    project_state.load_excel_file(MULTIPLE_SHEETS_PATH)
    
    # Get the expected dataframes and convert to expected numpy arrays
    expected_df_single = single_sheet_expected_dataframe()
    expected_df1_double, expected_df2_double = multiple_sheets_expected_dataframes()
    
    # Convert to numpy arrays
    expected_table_vals_single = expected_df_single.to_numpy()
    expected_table_vals1_double = expected_df1_double.to_numpy()
    expected_table_vals2_double = expected_df2_double.to_numpy()
    
    # Check that Sheet1 and Sheet2 exist
    assert "Sheet1" in project_state.sheet_groups
    assert "Sheet2" in project_state.sheet_groups
    
    # Check Sheet1 - should have 2 table_vals (one from each file)
    single_filename = os.path.basename(SINGLE_SHEET_PATH)
    double_filename = os.path.basename(MULTIPLE_SHEETS_PATH)
    sheet_group1 = project_state.sheet_groups["Sheet1"]
    assert len(sheet_group1.table_vals) == 2
    # First table_vals should be from single_sheet.xlsx
    assert single_filename in sheet_group1.table_vals
    assert np.array_equal(sheet_group1.table_vals[single_filename], expected_table_vals_single)
    # Second table_vals should be from double_sheet.xlsx's Sheet1
    assert double_filename in sheet_group1.table_vals
    assert np.array_equal(sheet_group1.table_vals[double_filename], expected_table_vals1_double)
    # Columns and rows should be from the first sheet loaded (single_sheet.xlsx)
    assert np.array_equal(sheet_group1.columns, np.array(expected_df_single.columns))
    assert np.array_equal(sheet_group1.rows, np.array(expected_df_single.index))
    
    # Check Sheet2 - should have 1 table_vals (only from double_sheet.xlsx)
    sheet_group2 = project_state.sheet_groups["Sheet2"]
    assert len(sheet_group2.table_vals) == 1
    assert double_filename in sheet_group2.table_vals
    assert np.array_equal(sheet_group2.table_vals[double_filename], expected_table_vals2_double)
    assert np.array_equal(sheet_group2.columns, np.array(expected_df2_double.columns))
    assert np.array_equal(sheet_group2.rows, np.array(expected_df2_double.index))
    

