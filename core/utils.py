import pandas as pd
import numpy as np

# def load_excel_file(file_path):
#     """
#     Loads an Excel file with multiple sheets and returns:
#         {sheet_name: cropped_dataframe}
#     Cropped dataframe is the table region found using "<>" as the top-left marker.
#     Sheets without "<>" are skipped.
#     """
#     excel_file = pd.ExcelFile(file_path)
#     result = {}

#     for sheet_name in excel_file.sheet_names:
#         sheet_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

#         table_df = find_all_tables_in_sheet(sheet_df)

#         if table_df is not None and not table_df.empty:
#             result[sheet_name] = table_df

#     return result

# def find_tables_in_excel(excel_path, anchor="<>", engine=None):
#     xls = pd.ExcelFile(excel_path, engine=engine)
#     all_tables = {}

#     for sheet_name in xls.sheet_names:
#         df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None, engine=engine)
#         tables = find_all_tables_in_sheet(df, anchor=anchor)
#         if tables:
#             all_tables[sheet_name] = tables

#     return all_tables

# def find_all_tables_in_sheet(sheet_df, anchor="<>"):
#     mask = sheet_df.astype(str).applymap(lambda x: x.strip() == anchor)
#     positions = np.argwhere(mask.values)

#     def is_empty(x):
#         return pd.isna(x) or (isinstance(x, str) and x.strip() == "")
#     def clean_header(x):
#         x = str(x).strip()
#         try:
#             x = float(x)
#             return int(x) if x.is_integer() else x
#         except ValueError:
#             return x

#     tables = []

#     for anchor_row, anchor_col in positions:

#         end_col = anchor_col + 1
#         while end_col < sheet_df.shape[1] and not sheet_df.iloc[anchor_row + 1:, end_col].apply(is_empty).all():
#             end_col += 1

#         end_row = anchor_row + 1
#         while end_row < sheet_df.shape[0] and not sheet_df.iloc[end_row, anchor_col + 1:end_col].apply(is_empty).all():
#             end_row += 1

#         extract_header = sheet_df.iloc[anchor_row, anchor_col + 1:end_col]
#         extract_index  = sheet_df.iloc[anchor_row + 1:end_row, anchor_col]

#         cols = [clean_header(x) for x in extract_header]
#         index = extract_index.fillna("").astype(str).str.strip().tolist()

#         table = sheet_df.iloc[anchor_row + 1:end_row, anchor_col + 1:end_col].copy()
#         table.columns = cols
#         table.index = index

#         tables.append(table)

#     return tables

def load_excel_file(file_path, anchor="<>", mode="first"):
    """
    Load an Excel file and extract anchor-marked tables.

    mode:
      - "first": return {sheet_name: df} using first table in each sheet
      - "all":   return {sheet_name: [df1, df2, ...]} for each sheet
    """
    excel_file = pd.ExcelFile(file_path)
    result = {}

    for sheet_name in excel_file.sheet_names:
        sheet_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

        tables = find_all_tables_in_sheet(sheet_df, anchor=anchor)

        if not tables:
            continue

        if mode == "all":
            result[sheet_name] = tables
        else:  # "first"
            result[sheet_name] = tables[0]

    return result


def convert_sheet_to_numpy(sheet_dataframe):
    """
    Converts a pandas dataframe to:
      - data_array: 2D numpy array of values
      - col_labels: numpy array of column labels (0,1,2,... if no headers)
      - row_labels: numpy array of row labels (A,B,C...)

    """
    data_array = sheet_dataframe.to_numpy()

    # Column labels (these will usually be 0,1,2,... unless you set them later)
    col_labels = np.array(sheet_dataframe.columns)

    # Row labels (A,B,C... after reset_index)
    row_labels = np.array(sheet_dataframe.index)

    return data_array, row_labels, col_labels

def find_all_tables_in_sheet(sheet_df, anchor="<>"):
    """
    Find ALL tables in a sheet marked by the anchor string "<>".
    Returns a list of DataFrames (possibly empty).
    """

    # Build a boolean mask for anchor matches without using applymap
    # Convert to string, strip whitespace, compare to anchor
    s = sheet_df.astype(str)
    s = s.apply(lambda col: col.str.strip())
    mask = s.eq(str(anchor))

    positions = np.argwhere(mask.to_numpy())
    if len(positions) == 0:
        return []
    def is_empty(x):
        return pd.isna(x) or (isinstance(x, str) and x.strip() == "")
    def clean_header(x):
        x = str(x).strip()
        try:
            x = float(x)
            return int(x) if x.is_integer() else x
        except ValueError:
            return x

    tables = []

    for anchor_row, anchor_col in positions:
        end_col = anchor_col + 1
        while end_col < sheet_df.shape[1] and not is_empty(sheet_df.iat[anchor_row, end_col]):
            end_col += 1

        end_row = anchor_row + 1
        while end_row < sheet_df.shape[0] and not is_empty(sheet_df.iat[end_row, anchor_col]):
            end_row += 1

        if end_col <= anchor_col + 1 or end_row <= anchor_row + 1:
            continue

        raw_headers = sheet_df.iloc[anchor_row, anchor_col + 1:end_col].tolist()
        raw_index = sheet_df.iloc[anchor_row + 1:end_row, anchor_col].tolist()

        headers = [clean_header(h) for h in raw_headers]
        index = [str(x).strip() if not pd.isna(x) else "" for x in raw_index]

        body = sheet_df.iloc[anchor_row + 1:end_row, anchor_col + 1:end_col].copy()
        body.columns = headers
        body.index = index

        for c in body.columns:
            col = body[c]
            col_num = pd.to_numeric(col, errors="coerce")

            if col_num.notna().sum() == col.notna().sum():
                if (col_num.dropna() % 1 == 0).all():
                    body[c] = col_num.astype("int64")
                else:
                    body[c] = col_num

        tables.append(body)

    return tables


def find_table_in_sheet(sheet_df, anchor="<>"):
    """
    Backwards-compatible helper: returns the first table found, or None.
    """
    tables = find_all_tables_in_sheet(sheet_df, anchor=anchor)
    return tables[0] if len(tables) > 0 else None
