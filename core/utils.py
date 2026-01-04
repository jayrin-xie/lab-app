import pandas as pd
import numpy as np

def find_table_in_sheet(sheet_df, anchor="<>"):
    mask = sheet_df.astype(str).eq(str(anchor))
    if not mask.any().any():
        return None

    anchor_row, anchor_col = next(zip(*np.where(mask.values)))

    def is_empty(x):
        return pd.isna(x) or (isinstance(x, str) and x.strip() == "")

    # Headers (right of anchor, same row)
    headers = []
    j = anchor_col + 1
    while j < sheet_df.shape[1] and not is_empty(sheet_df.iat[anchor_row, j]):
        headers.append(sheet_df.iat[anchor_row, j])
        j += 1

    # Index labels (below anchor, same column)
    index = []
    i = anchor_row + 1
    while i < sheet_df.shape[0] and not is_empty(sheet_df.iat[i, anchor_col]):
        index.append(sheet_df.iat[i, anchor_col])
        i += 1

    # Slice body (below-right rectangle)
    body = sheet_df.iloc[
        anchor_row + 1 : anchor_row + 1 + len(index),
        anchor_col + 1 : anchor_col + 1 + len(headers),
    ].copy()

    # Fix column labels like 7.0 -> 7 (labels only)
    fixed_headers = []
    for h in headers:
        if isinstance(h, (float, np.floating)) and float(h).is_integer():
            fixed_headers.append(int(h))
        else:
            fixed_headers.append(h)

    body.index = index
    body.columns = fixed_headers

    # coerce data columns to numeric when possible ---
    for c in body.columns:
        s = body[c]

        # Try numeric conversion (object -> numbers), but only "accept" it if nothing becomes NaN
        s_num = pd.to_numeric(s, errors="coerce")

        # If all non-empty entries became numeric, upgrade dtype
        if s_num.notna().sum() == s.notna().sum():
            # If all numeric values are integers, cast to int64
            if (s_num.dropna() % 1 == 0).all():
                body[c] = s_num.astype("int64")
            else:
                body[c] = s_num  # will be float dtype

    return body


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
