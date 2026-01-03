import pandas as pd
import numpy as np

def find_table_in_sheet(sheet_df):
    """
    Find the cell that contains "<>" and return ONLY the table below/right of it.
    If "<>" is not found, return None.
    """
    rows, cols = sheet_df.shape

    anchor_row = None
    anchor_col = None

    # Search every cell until we find "<>"
    for i in range(rows):
        for j in range(cols):
            value = sheet_df.iat[i, j]
            if str(value) == "<>":
                anchor_row = i
                anchor_col = j
                break
        if anchor_row is not None:
            break

    # If no "<>" was found, no table
    if anchor_row is None:
        return None

    # Crop: table is below and to the right of "<>"
    table = sheet_df.iloc[anchor_row + 1 :, anchor_col + 1 :]

    # Remove empty rows at the bottom
    while len(table) > 0 and table.iloc[-1].isna().all():
        table = table.iloc[:-1]

    # Remove empty columns at the right
    while table.shape[1] > 0 and table.iloc[:, -1].isna().all():
        table = table.iloc[:, :-1]

    # Reset row index
    table = table.reset_index(drop=True)

    return table


def load_excel_file(file_path):
    """
    Loads an Excel file with multiple sheets and returns:
        {sheet_name: cropped_dataframe}
    Cropped dataframe is the table region found using "<>" as the top-left marker.
    Sheets without "<>" are skipped.
    """
    excel_file = pd.ExcelFile(file_path)
    result = {}

    for sheet_name in excel_file.sheet_names:
        sheet_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        table_df = find_table_in_sheet(sheet_df)

        if table_df is not None and not table_df.empty:
            result[sheet_name] = table_df

    return result


def convert_sheet_to_numpy(sheet_dataframe):
    """
    Converts a pandas dataframe to:
      - data_array: 2D numpy array of values
      - col_labels: numpy array of column labels (0,1,2,... if no headers)
      - row_labels: numpy array of row labels (0,1,2,...)
    
    NOTE: Since we read Excel with header=None, columns are numbers by default.
    """
    data_array = sheet_dataframe.to_numpy()

    # Column labels (these will usually be 0,1,2,... unless you set them later)
    col_labels = np.array(sheet_dataframe.columns)

    # Row labels (0,1,2,... after reset_index)
    row_labels = np.array(sheet_dataframe.index)

    return data_array, row_labels, col_labels
