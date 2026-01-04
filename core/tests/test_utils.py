import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

from core.utils import load_excel_file, convert_sheet_to_numpy

SINGLE_SHEET_PATH = "core/tests/example_data/single_sheet.xlsx"
MULTIPLE_SHEETS_PATH = "core/tests/example_data/double_sheet.xlsx"

def _single_sheet_expected_dataframe():
    df1 = pd.DataFrame(
        {
            2: [3098, 2856, 2162],
            3: [2991, 3910, 2433]
        },
        index=["B", "C", "D"]
    )
    return df1


def _multiple_sheets_expected_dataframes():
    df1 = pd.DataFrame(
        {
            2: [3092, 2835, 3000],
            3: [3333, 4350, 833]
        },
        index=["B", "C", "D"]
    )
    df2 = pd.DataFrame(
        {
            7: [3415, 4731],
            8: [822, 780]
        },
        index=["B", "C"]
    )
    return df1, df2

def test_load_excel_file_single_sheet():
    loaded_df = load_excel_file(SINGLE_SHEET_PATH)
    expected_df = _single_sheet_expected_dataframe()
    assert_frame_equal(loaded_df["Sheet1"], expected_df)

def test_load_excel_file_multiple_sheets():
    loaded_df = load_excel_file(MULTIPLE_SHEETS_PATH)
    expected_df = _multiple_sheets_expected_dataframes()
    assert_frame_equal(loaded_df["Sheet1"], expected_df[0])
    assert_frame_equal(loaded_df["Sheet2"], expected_df[1])

def test_convert_sheet_to_numpy():
    dataframe = _single_sheet_expected_dataframe()

    # to_numpy() returns row-major: 3 rows (B,C,D) x 2 columns (2,3)
    expected_data_array = np.array([[3098, 2991], [2856, 3910], [2162, 2433]])
    expected_row_labels = np.array(["B", "C", "D"])
    # Column labels come from DataFrame.columns which are integers
    expected_column_labels = np.array([2, 3])

    data_array, row_labels, col_labels = convert_sheet_to_numpy(dataframe)
    assert(np.array_equal(data_array, expected_data_array))
    assert(np.array_equal(row_labels, expected_row_labels))
    assert(np.array_equal(col_labels, expected_column_labels))
