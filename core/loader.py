import pandas as pd

def find_table_in_sheet(sheet_df):
    """
    Given ONE sheet as a pandas DataFrame (sheet_df),
    find the cell that contains "<>" and return ONLY the table
    that is below and to the right of that marker.

    The marker cell itself is NOT part of the table.
    """
    rows, cols = sheet_df.shape

    # 1. Find the position (row, col) of the "<>" marker
    anchor_row = None
    anchor_col = None

    for i in range(rows):
        for j in range(cols):
            value = sheet_df.iat[i, j]  # get cell value
            if str(value) == "<>":      # match exactly "<>"
                anchor_row = i
                anchor_col = j
                break  # stop inner loop
        if anchor_row is not None:
            break  # stop outer loop once we found it

    # If we never found "<>", there is no table on this sheet (by our rule)
    if anchor_row is None:
        return None

    # 2. Take everything BELOW and to the RIGHT of the marker
    #    We skip the marker's row and column themselves.
    table = sheet_df.iloc[anchor_row + 1 :, anchor_col + 1 :]

    # 3. Drop completely empty rows from the bottom
    #    (rows where ALL cells are NaN)
    while len(table) > 0 and table.iloc[-1].isna().all():
        table = table.iloc[:-1]  # keep everything except last row

    # 4. Drop completely empty columns from the right
    while table.shape[1] > 0 and table.iloc[:, -1].isna().all():
        table = table.iloc[:, :-1]  # keep everything except last column

    # 5. Reset row index so it starts at 0 again
    table = table.reset_index(drop=True)

    return table


def load_tables_from_excel(filepath):
    """
    Given an Excel file path, load each sheet, find the "<>" marker,
    and return a dictionary: {sheet_name: table_dataframe}.

    Sheets without "<>" are skipped.
    """
    # Use pandas to look at all sheet names
    excel_file = pd.ExcelFile(filepath)

    result = {}  # this will store: sheet_name -> DataFrame

    for sheet_name in excel_file.sheet_names:
        # Read the entire sheet with no header row (everything as raw data)
        sheet_df = pd.read_excel(filepath, sheet_name=sheet_name, header=None)

        # Find and extract the table in this sheet
        table = find_table_in_sheet(sheet_df)

        # Only add if we found a table and it's not empty
        if table is not None and not table.empty:
            result[sheet_name] = table

    return result
