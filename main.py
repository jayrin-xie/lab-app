from core.loader import load_tables_from_excel

if __name__ == "__main__":
    # Use your full filepath here
    excel_path = "/Users/jayrinxie/Desktop/Lab_app/test1.xlsx"

    tables = load_tables_from_excel(excel_path)

    print(f"Loaded tables from: {excel_path}")
    print(f"Sheets with detected tables: {list(tables.keys())}")

    # Print the first few rows of each table so you can see them
    for sheet_name, df in tables.items():
        print("\n==============================")
        print(f"Sheet: {sheet_name}")
        print(df.head())  # show top 5 rows

from core.utils import load_excel_file, convert_sheet_to_numpy

file_path = "/Users/jayrinxie/Desktop/Lab_app/test1.xlsx"
tables = load_excel_file(file_path)

print(tables.keys())  # sheet names that had "<>"

sheet_df = tables[list(tables.keys())[0]]
data, rows, cols = convert_sheet_to_numpy(sheet_df)

print(sheet_df.head())
print(data.shape, rows[:5], cols[:5])