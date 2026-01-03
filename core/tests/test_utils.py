import pytest
import pandas as pd
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
    # First DataFrame
    df1 = pd.DataFrame(
        {
            2: [3092, 2835, 3000],
            3: [3333, 4350, 833]
        },
        index=["B", "C", "D"]
    )

    # Second DataFrame
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
    print(expected_df)
    print()
    print(loaded_df["Sheet1"])
    assert_frame_equal(loaded_df["Sheet1"], expected_df)

def test_load_excel_file_multiple_sheets():
    loaded_df = load_excel_file(MULTIPLE_SHEETS_PATH)
    expected_df = _multiple_sheets_expected_dataframes()
    assert_frame_equal(loaded_df["Sheet1"], expected_df[0])
    assert_frame_equal(loaded_df["Sheet2"], expected_df[1])
