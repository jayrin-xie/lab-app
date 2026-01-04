import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

from core.utils import load_excel_file, convert_sheet_to_numpy
from core.tests.conftest import (
    single_sheet_expected_dataframe,
    multiple_sheets_expected_dataframes,
    SINGLE_SHEET_PATH,
    MULTIPLE_SHEETS_PATH,
)

def test_load_excel_file_single_sheet():
    loaded_df = load_excel_file(SINGLE_SHEET_PATH)
    expected_df = single_sheet_expected_dataframe()
    assert_frame_equal(loaded_df["Sheet1"], expected_df)

def test_load_excel_file_multiple_sheets():
    loaded_df = load_excel_file(MULTIPLE_SHEETS_PATH)
    expected_df = multiple_sheets_expected_dataframes()
    assert_frame_equal(loaded_df["Sheet1"], expected_df[0])
    assert_frame_equal(loaded_df["Sheet2"], expected_df[1])

def test_convert_sheet_to_numpy():
    dataframe = single_sheet_expected_dataframe()

    # to_numpy() returns row-major: 3 rows (B,C,D) x 2 columns (2,3)
    expected_data_array = np.array([[3098, 2991], [2856, 3910], [2162, 2433]])
    expected_row_labels = np.array(["B", "C", "D"])
    # Column labels come from DataFrame.columns which are integers
    expected_column_labels = np.array([2, 3])

    data_array, row_labels, col_labels = convert_sheet_to_numpy(dataframe)
    assert(np.array_equal(data_array, expected_data_array))
    assert(np.array_equal(row_labels, expected_row_labels))
    assert(np.array_equal(col_labels, expected_column_labels))
