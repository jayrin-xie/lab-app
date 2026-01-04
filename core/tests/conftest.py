"""
Shared test fixtures and helpers for the test suite.
"""
import pandas as pd

# Test data paths
SINGLE_SHEET_PATH = "core/tests/example_data/single_sheet.xlsx"
MULTIPLE_SHEETS_PATH = "core/tests/example_data/double_sheet.xlsx"


def single_sheet_expected_dataframe():
    """Returns the expected dataframe for single_sheet.xlsx."""
    df1 = pd.DataFrame(
        {
            2: [3098, 2856, 2162],
            3: [2991, 3910, 2433]
        },
        index=["B", "C", "D"]
    )
    return df1


def multiple_sheets_expected_dataframes():
    """Returns the expected dataframes for double_sheet.xlsx."""
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

