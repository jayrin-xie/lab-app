import os
# from core import sheet_group
from sheet_group import SheetGroup
import pandas as pd
import numpy as np
import re
from utils import load_excel_file as load_excel_tables
from utils import convert_sheet_to_numpy


class ProjectState:
    def __init__(self):
        self.sheet_groups = {}
        self.raw_tables = {}
        self.norm_control_by_plate = {}  

    def load_workbook(self, file_path, mode="first"):
        filename = os.path.basename(file_path)
        dataframes = load_excel_tables(file_path, mode=mode)

        for sheet_name in dataframes:
            obj = dataframes[sheet_name]

            # Make everything a list so we have ONE code path
            tables = obj if isinstance(obj, list) else [obj]

            for i, df in enumerate(tables, start=1):
                # unique id per table
                table_id = f"{filename} | table{i}" if len(tables) > 1 else filename

                # store the raw DataFrame (keeps row/col labels + variable shapes)
                self.raw_tables[(sheet_name, table_id)] = df

                # Create SheetGroup only ONCE per sheet_name (for UI metadata grid)
                # We use the FIRST table’s rows/cols as the starting grid (can expand later if you want)
                if sheet_name not in self.sheet_groups:
                    self.sheet_groups[sheet_name] = SheetGroup(
                        columns=df.columns.tolist(),
                        rows=df.index.tolist(),
                        first_table_id=table_id,
                        first_table_vals=df.to_numpy()
                    )
                else:
                    self.sheet_groups[sheet_name].add_new_sheet(
                        table_id,
                        df.to_numpy(),
                        df.index.tolist(),
                        df.columns.tolist()
                    )


    # def load_workbook(self, file_path, mode="first"):
    #   """
    #   Loads an excel file and adds sheets to corresponding sheet groups.
    #   """
    #   filename = os.path.basename(file_path)
    #   dataframes = load_excel_tables(file_path, mode=mode)

    #   for sheet_name, dataframe in dataframes.items():
    #       table_vals, rows, columns = convert_sheet_to_numpy(dataframe)
    #       if sheet_name in self.sheet_groups:
    #           self.sheet_groups[sheet_name].add_new_sheet(filename, table_vals)
    #       else:
    #           self.sheet_groups[sheet_name] = SheetGroup(columns, rows, filename, table_vals)

    def set_condition_name(self, sheet, row, col, condition_name):
      self.sheet_groups[sheet].set_condition_name(row, col, condition_name)

    def set_cuboids_count(self, sheet, row, col, cuboids_count):
      self.sheet_groups[sheet].set_cuboids_count(row, col, cuboids_count)

    def set_is_background(self, sheet, row, col, is_background):
      self.sheet_groups[sheet].set_is_background(row, col, is_background)

    def set_norm_control(self, plate_name: str, control_condition: str):
        self.norm_control_by_plate[str(plate_name)] = str(control_condition)

    def get_sheet_group_names(self):
        return self.sheet_groups.keys()

    def get_all_files_from_same_sheet_group(self, sheet_name):
        return self.sheet_groups[sheet_name].get_file_names()

    def get_columns(self, sheet_name):
        """
        Returns the columns for a given sheet group.
        """
        return self.sheet_groups[sheet_name].columns

    def get_rows(self, sheet_name):
        """
        Returns the rows for a given sheet group.
        """
        return self.sheet_groups[sheet_name].rows

    def get_table_vals(self, sheet_name):
        """
        Returns the table_vals dictionary for a given sheet group.
        """
        return self.sheet_groups[sheet_name].table_vals

    def get_condition_names(self, sheet_name, row=None, col=None):
        """
        Returns the condition_names array for a given sheet group.
        If row and col are provided, returns the value at that specific cell.
        """
        if row is not None and col is not None:
            return self.sheet_groups[sheet_name].condition_names[row, col]
        return self.sheet_groups[sheet_name].condition_names

    def get_cuboids_count(self, sheet_name, row=None, col=None):
        """
        Returns the cuboids_count array for a given sheet group.
        If row and col are provided, returns the value at that specific cell.
        """
        if row is not None and col is not None:
            return self.sheet_groups[sheet_name].cuboids_count[row, col]
        return self.sheet_groups[sheet_name].cuboids_count

    def get_is_background(self, sheet_name, row=None, col=None):
        """
        Returns the is_background array for a given sheet group.
        If row and col are provided, returns the value at that specific cell.
        """
        if row is not None and col is not None:
            return self.sheet_groups[sheet_name].is_background[row, col]
        return self.sheet_groups[sheet_name].is_background
    
    def on_clear_selected_wells(self):
        selected = self.plate_table.selectedIndexes()
        if not selected:
            return

        for idx in selected:
            r_i, c_i = idx.row(), idx.column()
            self.state.set_condition_name(self.current_sheet, r_i, c_i, "")
            self.state.set_cuboids_count(self.current_sheet, r_i, c_i, 0)
            self.state.set_is_background(self.current_sheet, r_i, c_i, False)
            self._refresh_one_plate_cell(self.current_sheet, r_i, c_i)

    # def export_to_excel(self, output_path):
    #     """
    #     Export everything to one Excel file.
    #     Creates one sheet per sheet_group (plate1, plate2, etc.)
    #     in a long-table format that's easy to analyze later.
    #     """
    #     with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    #         for sheet_name, group in self.sheet_groups.items():
    #             rows = []
    #             row_labels = list(group.rows)
    #             col_labels = list(group.columns)

    #             # group.table_vals: dict of file/table_id -> 2D numpy array
    #             for table_id, values in group.table_vals.items():
    #                 for r_i, r_label in enumerate(row_labels):
    #                     for c_i, c_label in enumerate(col_labels):
    #                         rows.append({
    #                             "Sheet": sheet_name,
    #                             "Table": table_id,
    #                             "Row": r_label,
    #                             "Column": c_label,
    #                             "Value": values[r_i, c_i],
    #                             "Condition": group.condition_names[r_i, c_i],
    #                             "Cuboids": group.cuboids_count[r_i, c_i],
    #                             "IsBackground": group.is_background[r_i, c_i],
    #                         })

    #             df_out = pd.DataFrame(rows)
    #             df_out.to_excel(writer, sheet_name=sheet_name[:31], index=False)



    # def export_to_excel(self, output_path: str):
    #     """
    #     Export everything to one Excel file.
    #     Creates one sheet per plate (sheet group).
    #     Each exported sheet is a long table contains columns:
    #     Plate | Table | Row | Column | Value | Condition | Cuboids | IsBackground

    #     Pulls numeric Value from raw_tables (per file/day),
    #     and pulls metadata from SheetGroup (shared template per plate).
    #     """
    #     def extract_day(table_id: str) -> str:
    #             # Finds days like d1, d2, d4, d5, d10, etc anywhere in table_id
    #             m = re.search(r"\b(d\d+)\b", str(table_id).lower())
    #             return m.group(1) if m else "unknown"

    #     with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    #         # loop each plate group (plate1, plate2, ...)
    #         for plate_name, group in self.sheet_groups.items():
    #             out_rows = []

    #             # collect all tables belonging to this plate from raw_tables
    #             plate_tables = [
    #                 (table_id, df)
    #                 for (sheet_key, table_id), df in self.raw_tables.items()
    #                 if sheet_key == plate_name
    #             ]

    #             # build label->index maps for metadata lookup
    #             row_to_i = {str(r): i for i, r in enumerate(group.rows)}
    #             col_to_j = {str(c): j for j, c in enumerate(group.columns)}

    #             for table_id, df in plate_tables:
    #                 day = extract_day(table_id)

    #                 # df index/columns are the extracted table's labels
    #                 for r_label in df.index:
    #                     for c_label in df.columns:
    #                         val = df.loc[r_label, c_label]

    #                         # map df labels -> master grid indices (for metadata)
    #                         ri = row_to_i.get(str(r_label))
    #                         cj = col_to_j.get(str(c_label))

    #                         if ri is None or cj is None:
    #                             # metadata not found (table has labels outside master grid)
    #                             cond = ""
    #                             cub = np.nan
    #                             bg = False
    #                         else:
    #                             cond = group.condition_names[ri, cj]
    #                             cub = group.cuboids_count[ri, cj]
    #                             bg = bool(group.is_background[ri, cj])

    #                         out_rows.append({
    #                             "Plate": plate_name,
    #                             "Table": table_id,
    #                             "Row": str(r_label),
    #                             "Column": int(float(c_label)) if str(c_label).replace(".", "", 1).isdigit() else c_label,
    #                             "Condition": cond,
    #                             "Cuboids": cub,
    #                             "Background": bg,
    #                             "Day": day,
    #                             "Value": val,
    #                         })

    #             df_long = pd.DataFrame(out_rows)

    #             if df_long.empty:
    #                 df_long.to_excel(writer, sheet_name=str(plate_name)[:31], index=False)
    #                 continue

    #             # Pivot so each Day becomes its own column (d1, d2, d4, d5, ...)
    #             meta_cols = ["Plate", "Table", "Row", "Column", "Condition", "Cuboids", "Background"]

    #             df_wide = (
    #                 df_long
    #                 .pivot_table(
    #                     index=meta_cols,
    #                     columns="Day",
    #                     values="Value",
    #                     aggfunc="first"   # if duplicates exist, keep first
    #                 )
    #                 .reset_index()
    #             )

    #             # Optional: sort day columns numerically (d1, d2, d4, d5, d10...)
    #             day_cols = [c for c in df_wide.columns if isinstance(c, str) and c.startswith("d") and c[1:].isdigit()]
    #             day_cols_sorted = sorted(day_cols, key=lambda x: int(x[1:]))

    #             # Reorder columns: metadata first, then days
    #             df_wide = df_wide[meta_cols + day_cols_sorted + [c for c in df_wide.columns if c not in meta_cols + day_cols_sorted]]

    #             # Optional sorting
    #             df_wide = df_wide.sort_values(["Table", "Row", "Column"]).reset_index(drop=True)

    #             # Write
    #             df_wide.to_excel(writer, sheet_name=str(plate_name)[:31], index=False)

    def export_to_excel(self, output_path: str):
        """
        One sheet per plate (plate1, plate2, ...)

        Columns:
        Plate | Table | Row | Column | Condition | Cuboids | Background | d1 | d2 | d4 | d5 | ...| ratio d2/d1 | ratio d4/d1 | ...

        - Table is a BASE experiment name (e.g., "MC38") so days align in one row.
        - Day columns are created dynamically from whatever days exist.
        """

        def extract_day(table_id: str) -> str:
            # finds d1, d2, d4, d5, d10, etc
            m = re.search(r"\b(d\d+)\b", str(table_id).lower())
            return m.group(1) if m else "unknown"

        def extract_base_table_name(table_id: str) -> str:
            """
            Convert something like:
            "MC38-d1.xlsx | table1"  -> "MC38"
            "MC38-d2.xlsx"           -> "MC38"
            If pattern not found, returns the filename stem.
            """
            file_part = str(table_id).split("|")[0].strip()      # "MC38-d1.xlsx"
            stem = re.sub(r"\.xlsx$", "", file_part, flags=re.I) # "MC38-d1"
            # remove "-d<number>" if present
            base = re.sub(r"-d\d+\b", "", stem, flags=re.I)
            return base

        wrote_any_sheet = False

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for plate_name, group in self.sheet_groups.items():
                out_rows = []

                # pull all raw tables for this plate
                plate_tables = [
                    (table_id, df)
                    for (sheet_key, table_id), df in self.raw_tables.items()
                    if sheet_key == plate_name
                ]

                # metadata lookup maps (string matching is safest)
                row_to_i = {str(r): i for i, r in enumerate(group.rows)}
                col_to_j = {str(c): j for j, c in enumerate(group.columns)}

                for table_id, df in plate_tables:
                    day = extract_day(table_id)
                    base_table = extract_base_table_name(table_id)

                    for r_label in df.index:
                        for c_label in df.columns:
                            val = df.loc[r_label, c_label]

                            ri = row_to_i.get(str(r_label))
                            cj = col_to_j.get(str(c_label))

                            if ri is None or cj is None:
                                cond = ""
                                cub = np.nan
                                bg = False
                            else:
                                cond = group.condition_names[ri, cj]
                                cub = group.cuboids_count[ri, cj]
                                bg = bool(group.is_background[ri, cj])

                            # keep Column numeric if possible
                            try:
                                col_value = int(float(c_label))
                            except (ValueError, TypeError):
                                col_value = c_label

                            out_rows.append({
                                "Plate": plate_name,
                                "Table": base_table,      
                                "Row": str(r_label),
                                "Column": col_value, 
                                "Condition": cond,
                                "Cuboids": cub,
                                "Background": bg,
                                "Day": day,
                                "Value": val,
                            })

                df_long = pd.DataFrame(out_rows)

                # If nothing for this plate, still write an empty sheet (prevents "no visible sheet" error)
                if df_long.empty:
                    pd.DataFrame(columns=["Plate","Table","Row","Column","Condition","Cuboids","Background"]).to_excel(
                        writer, sheet_name=str(plate_name)[:31], index=False
                    )
                    wrote_any_sheet = True
                    continue

                meta_cols = ["Plate", "Table", "Row", "Column", "Condition", "Cuboids", "Background"]

                df_wide = (
                    df_long
                    .pivot_table(
                        index=meta_cols,
                        columns="Day",
                        values="Value",
                        aggfunc="first"
                    )
                    .reset_index()
                )

                # sort day columns nicely: d1,d2,d4,d5,d10,...
                day_cols = [c for c in df_wide.columns if isinstance(c, str) and re.fullmatch(r"d\d+", c)]
                day_cols_sorted = sorted(day_cols, key=lambda x: int(x[1:]))

                # final column order (metadata + day columns first)
                df_wide = df_wide[meta_cols + day_cols_sorted]

                # --- Add ratio columns: (each day)/(d1) for all days after d1 ---
                if "d1" in df_wide.columns:
                    d1 = df_wide["d1"].replace(0, np.nan)  # avoid inf

                    for day in day_cols_sorted:
                        if day == "d1":
                            continue
                        ratio_name = f"ratio {day}/d1"
                        df_wide[ratio_name] = df_wide[day] / d1

                # now collect ratio columns that exist
                ratio_cols = [c for c in df_wide.columns if isinstance(c, str) and c.startswith("ratio d")]

                # reorder to: meta + days + ratios
                df_wide = df_wide[meta_cols + day_cols_sorted + ratio_cols]
                

                # --- Add ratio columns: (each day)/(d1) for all days after d1 ---
                if "d1" in df_wide.columns:
                    # avoid division by 0 producing inf
                    d1 = df_wide["d1"].replace(0, np.nan)

                    for day in day_cols_sorted:
                        if day == "d1":
                            continue

                        ratio_name = f"ratio {day}/d1"   # e.g. "ratio d2/d1"
                        df_wide[ratio_name] = df_wide[day] / d1


                # optional: sort rows
                df_wide = df_wide.sort_values(["Table", "Row", "Column"]).reset_index(drop=True)

                df_wide.to_excel(writer, sheet_name=str(plate_name)[:31], index=False)

                
            # Write ratio tables sheet
                ratio_sheet_name = f"{plate_name}_ratios"[:31]
            # no background columns in ratio tables
                cond_order = [
                    c for c in df_wide["Condition"].dropna().unique().tolist()
                    if str(c).strip().lower() != "BG" and str(c).strip() != ""
                ]

                start_row = 0

                control_cond = self.norm_control_by_plate.get(plate_name, None)

                for ratio in ratio_cols:
                    # Use ONLY Condition + ratio
                    tmp = df_wide[["Condition", ratio]].copy()
                    tmp = tmp.dropna(subset=["Condition", ratio])

                    # Build dict: condition -> list of ratio values
                    cond_to_vals = {
                        cond: tmp.loc[tmp["Condition"] == cond, ratio].tolist()
                        for cond in cond_order
                    }

                    # Create a DataFrame with uneven-length columns (pandas will pad with NaN)
                    block = pd.DataFrame({cond: pd.Series(vals) for cond, vals in cond_to_vals.items()})

                    # 1) Title row
                    pd.DataFrame([[ratio]]).to_excel(
                        writer,
                        sheet_name=ratio_sheet_name,
                        index=False,
                        header=False,
                        startrow=start_row,
                        startcol=0
                    )

                    # 2) Block table underneath (NO index => no "rep" column)
                    block.to_excel(
                        writer,
                        sheet_name=ratio_sheet_name,
                        index=False,          #removes rep/index column
                        startrow=start_row + 1,
                        startcol=0
                    )

                    # spacing between blocks
                    start_row += (len(block) + 1 + 3)

                control_cond = self.norm_control_by_plate.get(plate_name, None)

                start_row = 0
                for ratio in ratio_cols:
                    # block = your original ratio table (columns = conditions)
                    # example: block = pd.DataFrame({...})

                    # ---- NORMALIZE ----
                    normalized = block.copy()
                    if control_cond and control_cond in block.columns:
                        control_mean = pd.to_numeric(block[control_cond], errors="coerce").mean(skipna=True)
                        if pd.notna(control_mean) and control_mean != 0:
                            normalized = block.apply(pd.to_numeric, errors="coerce") / control_mean
                        else:
                            normalized.iloc[:, :] = np.nan
                    else:
                        normalized.iloc[:, :] = np.nan

                    # ---- WRITE ORIGINAL + NORMALIZED SIDE BY SIDE ----
                    pd.DataFrame([[ratio, f"normalized (control={control_cond})"]]).to_excel(
                        writer, sheet_name=ratio_sheet_name,
                        index=False, header=False,
                        startrow=start_row, startcol=0
                    )

                    block.to_excel(
                        writer, sheet_name=ratio_sheet_name,
                        index=False,
                        startrow=start_row + 1, startcol=0
                    )

                    startcol_norm = block.shape[1] + 2  # gap of 2 columns
                    normalized.to_excel(
                        writer, sheet_name=ratio_sheet_name,
                        index=False,
                        startrow=start_row + 1, startcol=startcol_norm
                    )

                    start_row += (len(block) + 1 + 3)

                    wrote_any_sheet = True

            # absolute safety fallback (should never trigger now)
            if not wrote_any_sheet:
                pd.DataFrame({"Note": ["No tables found."]}).to_excel(writer, sheet_name="Name?", index=False)

