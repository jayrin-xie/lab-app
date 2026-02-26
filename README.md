# lab-app
# utils
- find all <> in a excel sheet
- extract multiple tables per sheet
- Returns clean pandas DataFrames

- load_excel_file: Iterates through all sheets, mode="first" → one table per sheet, mode="all" → list of tables per sheet
- Works once pass a correct file path

# project state
- hold loaded tables, loads an excel file and adds sheets to corresponding sheet groups (one table per sheet or multiple tables per sheet)
- load work book has problem, it requires all table to have same shape
- manage current file / sheet / plate
- apply processing steps (subtract, ratio, mask)
- expose clean data to the GUI

