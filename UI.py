import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.project_state import ProjectState

class UI:
    def __init__(self, root):
        self.root = root
        self.root.title("Project State UI")
        self.project_state = ProjectState()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File loading section
        file_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(file_frame, text="Load Excel File(s)", command=self.load_excel_file).grid(row=0, column=0, padx=5)
        
        # Sheet selection section
        sheet_frame = ttk.LabelFrame(main_frame, text="Sheet Groups", padding="10")
        sheet_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        ttk.Label(sheet_frame, text="Select Sheet Group:").grid(row=0, column=0, padx=5)
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(sheet_frame, textvariable=self.sheet_var, state="readonly")
        self.sheet_combo.grid(row=0, column=1, padx=5)
        self.sheet_combo.bind("<<ComboboxSelected>>", self.on_sheet_selected)
        
        # Table display section
        table_frame = ttk.LabelFrame(main_frame, text="Data Table", padding="10")
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbars for table
        table_scroll_y = ttk.Scrollbar(table_frame)
        table_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        table_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        table_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.tree = ttk.Treeview(
            table_frame,
            yscrollcommand=table_scroll_y.set,
            xscrollcommand=table_scroll_x.set,
            selectmode="none"  # <-- IMPORTANT: disable row selection
        )
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Our cell selection state
        self.selected_cells = set()   # set of (item_id, col_id like '#1')
        self.last_clicked_cell = None # for optional shift-range later (not required)

        # Click to select/toggle cells, double-click (or Enter) to edit selection
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.open_editor_for_selection)
        self.root.bind("<Return>", self.open_editor_for_selection)  # press Enter to edit selected cells
        self.root.bind("<Escape>", self.clear_cell_selection)       # Esc clears selection
        
        # Store current sheet name for cell selection
        self.current_sheet_name = None
        
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Cell editing section
        edit_frame = ttk.LabelFrame(main_frame, text="Edit Cell", padding="10")
        edit_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(edit_frame, text="Selected Row:").grid(row=0, column=0, padx=5)
        self.row_var = tk.StringVar()
        self.row_entry = ttk.Entry(edit_frame, textvariable=self.row_var, width=10, state="readonly")
        self.row_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(edit_frame, text="Selected Column:").grid(row=0, column=2, padx=5)
        self.col_var = tk.StringVar()
        self.col_entry = ttk.Entry(edit_frame, textvariable=self.col_var, width=10, state="readonly")
        self.col_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(edit_frame, text="Drug Name:").grid(row=1, column=0, padx=5, pady=5)
        self.drug_name_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.drug_name_var, width=20).grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        
        ttk.Label(edit_frame, text="Cuboids Count:").grid(row=2, column=0, padx=5)
        self.cuboids_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.cuboids_var, width=20).grid(row=2, column=1, columnspan=2, padx=5)
        
        self.background_var = tk.BooleanVar()
        ttk.Checkbutton(edit_frame, text="Is Background", variable=self.background_var).grid(row=2, column=3, padx=5)
        
        ttk.Button(edit_frame, text="Update Cell", command=self.update_cell).grid(row=3, column=0, columnspan=4, pady=10)
        
        # Information section
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.info_text = tk.Text(info_frame, height=5, width=50)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        info_scroll = ttk.Scrollbar(info_frame, command=self.info_text.yview)
        info_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.config(yscrollcommand=info_scroll.set)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def load_excel_file(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Excel Files",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_paths:
            loaded_files = []
            failed_files = []
            
            for file_path in file_paths:
                try:
                    self.project_state.load_excel_file(file_path)
                    loaded_files.append(file_path)
                except Exception as e:
                    failed_files.append((file_path, str(e)))
            
            self.update_sheet_combo()
            
            info_message = f"Loaded {len(loaded_files)} file(s):\n"
            for file_path in loaded_files:
                info_message += f"  - {file_path}\n"
            
            if failed_files:
                info_message += f"\nFailed to load {len(failed_files)} file(s):\n"
                for file_path, error in failed_files:
                    info_message += f"  - {file_path}: {error}\n"
            
            self.update_info(info_message)
            
            if failed_files:
                error_details = "\n".join([f"{path}: {error}" for path, error in failed_files])
                messagebox.showwarning("Partial Load", f"Some files failed to load:\n{error_details}")
            elif loaded_files:
                messagebox.showinfo("Success", f"Successfully loaded {len(loaded_files)} file(s)")
                
    def update_sheet_combo(self):
        sheet_groups = list(self.project_state.sheet_groups.keys())
        self.sheet_combo['values'] = sheet_groups
        if sheet_groups:
            self.sheet_var.set(sheet_groups[0])
            self.on_sheet_selected()
            
    def on_sheet_selected(self, event=None):
        sheet_name = self.sheet_var.get()
        if sheet_name:
            self.display_table(sheet_name)
            self.update_sheet_info(sheet_name)
            
    def display_table(self, sheet_name):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree["columns"] = []
        
        # Store current sheet name for cell selection
        self.current_sheet_name = sheet_name
        
        try:
            columns = self.project_state.get_columns(sheet_name)
            rows = self.project_state.get_rows(sheet_name)
            table_vals = self.project_state.get_table_vals(sheet_name)
            drug_names = self.project_state.get_drug_names(sheet_name)
            cuboids_count = self.project_state.get_cuboids_count(sheet_name)
            is_background = self.project_state.get_is_background(sheet_name)
            
            # Set up columns
            self.tree["columns"] = [str(col) for col in columns]
            self.tree.heading("#0", text="Row")
            
            for col in columns:
                self.tree.heading(str(col), text=str(col))
                self.tree.column(str(col), width=100)
            
            # Get first file's data for display
            first_file = list(table_vals.keys())[0] if table_vals else None
            if first_file:
                data = table_vals[first_file]
                
                # Populate rows
                for i, row_label in enumerate(rows):
                    values = []
                    for j, col_label in enumerate(columns):
                        val = data[i, j] if i < data.shape[0] and j < data.shape[1] else ""
                        drug = drug_names[i, j] if drug_names is not None and i < drug_names.shape[0] and j < drug_names.shape[1] else None
                        cuboids = cuboids_count[i, j] if cuboids_count is not None and i < cuboids_count.shape[0] and j < cuboids_count.shape[1] else 0
                        bg = is_background[i, j] if is_background is not None and i < is_background.shape[0] and j < is_background.shape[1] else False
                        
                        display_val = str(val)
                        if drug:
                            display_val += f" [D:{drug}]"
                        if cuboids > 0:
                            display_val += f" [C:{cuboids}]"
                        if bg:
                            display_val += " [BG]"
                        
                        values.append(display_val)
                    
                    self.tree.insert("", tk.END, text=str(row_label), values=values)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display table: {str(e)}")
            
    def update_sheet_info(self, sheet_name):
        try:
            files = list(self.project_state.get_all_files_from_same_sheet_group(sheet_name))
            columns = self.project_state.get_columns(sheet_name)
            rows = self.project_state.get_rows(sheet_name)
            drug_names = self.project_state.get_drug_names(sheet_name)
            cuboids_count = self.project_state.get_cuboids_count(sheet_name)
            
            info = f"Sheet Group: {sheet_name}\n"
            info += f"Files: {', '.join(files)}\n"
            info += f"Rows: {len(rows)}, Columns: {len(columns)}\n"
            
            unique_drugs = set()
            for i in range(drug_names.shape[0]):
                for j in range(drug_names.shape[1]):
                    if drug_names[i, j] is not None:
                        unique_drugs.add(drug_names[i, j])
            
            info += f"Unique Drug Names: {', '.join(map(str, unique_drugs)) if unique_drugs else 'None'}\n"
            
            total_cuboids = int(cuboids_count.sum())
            info += f"Total Cuboids: {total_cuboids}"
            
            self.update_info(info)
        except Exception as e:
            self.update_info(f"Error getting sheet info: {str(e)}")
            
    def update_cell(self):
        sheet_name = self.sheet_var.get()
        if not sheet_name:
            messagebox.showwarning("Warning", "Please select a sheet group first")
            return
            
        try:
            row_str = self.row_var.get().strip()
            col_str = self.col_var.get().strip()
            
            if not row_str or not col_str:
                messagebox.showwarning("Warning", "Please select a cell in the table first")
                return
            
            rows = self.project_state.get_rows(sheet_name)
            columns = self.project_state.get_columns(sheet_name)
            
            # Find row and column indices
            try:
                row_idx = list(rows).index(row_str)
            except ValueError:
                # Try numeric conversion
                row_idx = int(row_str)
                
            try:
                col_idx = list(columns).index(col_str)
            except (ValueError, TypeError):
                # Try numeric conversion
                col_idx = int(col_str)
            
            # Update values
            drug_name = self.drug_name_var.get().strip()
            if drug_name:
                self.project_state.set_drug_name(sheet_name, row_idx, col_idx, drug_name)
            
            cuboids = self.cuboids_var.get().strip()
            if cuboids:
                self.project_state.set_cuboid_count(sheet_name, row_idx, col_idx, int(cuboids))
            
            self.project_state.set_is_background(sheet_name, row_idx, col_idx, self.background_var.get())
            
            # Refresh display
            self.display_table(sheet_name)
            self.update_sheet_info(sheet_name)
            
            messagebox.showinfo("Success", "Cell updated successfully")
            
            # Clear input fields
            self.drug_name_var.set("")
            self.cuboids_var.set("")
            self.background_var.set(False)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update cell: {str(e)}")
    
    def clear_cell_selection(self, event=None):
        """Clear selected cell set and remove any visual markers."""
        self.selected_cells.clear()
        self.refresh_cell_markers()
    
    def refresh_cell_markers(self):
        """Re-render the table to restore clean display, then re-apply markers"""
        if not self.current_sheet_name:
            return

        # Re-render the table to restore clean display, then re-apply markers
        # (This is simplest; if performance becomes an issue we can optimize.)
        sheet_name = self.current_sheet_name
        self.display_table(sheet_name)

        # Now add a visual marker to selected cells
        # We do it by editing the cell's displayed value (prefixing "▶ ")
        for (item_id, col_id) in self.selected_cells:
            try:
                col_index = int(col_id.replace("#", "")) - 1
                vals = list(self.tree.item(item_id, "values"))
                if 0 <= col_index < len(vals):
                    v = vals[col_index]
                    if not str(v).startswith("▶ "):
                        vals[col_index] = "▶ " + str(v)
                        self.tree.item(item_id, values=vals)
            except Exception:
                pass

    def on_tree_click(self, event):
        """Click selects a single cell. Ctrl-click toggles. Shift-click optional (not implemented here)."""
        region = self.tree.identify_region(event.x, event.y)

        # Only act on actual cells (not headers/empty)
        if region != "cell":
            return

        item_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)  # '#1', '#2', ... ; '#0' is row label
        if not item_id or not col_id or col_id == "#0":
            return

        # Ctrl pressed? (Windows/Linux: 0x0004; macOS Command is different in Tk, but Ctrl works reliably.)
        ctrl_pressed = (event.state & 0x0004) != 0

        cell = (item_id, col_id)

        if not ctrl_pressed:
            # Normal click: replace selection with this single cell
            self.selected_cells = {cell}
        else:
            # Ctrl-click: toggle this cell
            if cell in self.selected_cells:
                self.selected_cells.remove(cell)
            else:
                self.selected_cells.add(cell)

        self.last_clicked_cell = cell
        self.refresh_cell_markers()

    def open_editor_for_selection(self, event=None):
        """Open a popup editor for all currently selected cells."""
        if not self.current_sheet_name:
            return

        if not self.selected_cells:
            messagebox.showinfo("No selection", "Click a cell (Ctrl-click to multi-select), then press Enter or double-click to edit.")
            return

        # Popup window
        win = tk.Toplevel(self.root)
        win.title("Edit Selected Cells")
        win.transient(self.root)
        win.grab_set()

        frm = ttk.Frame(win, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text=f"Selected cells: {len(self.selected_cells)}").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(frm, text="Drug Name (leave blank = don't change):").grid(row=1, column=0, sticky="w")
        drug_var = tk.StringVar()
        ttk.Entry(frm, textvariable=drug_var, width=30).grid(row=1, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(frm, text="Cuboids Count (leave blank = don't change):").grid(row=2, column=0, sticky="w", pady=(8, 0))
        cuboids_var = tk.StringVar()
        ttk.Entry(frm, textvariable=cuboids_var, width=30).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))

        bg_var = tk.BooleanVar(value=False)
        bg_change_var = tk.BooleanVar(value=False)  # checkbox to indicate if user wants to update bg
        bg_row = ttk.Frame(frm)
        bg_row.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Checkbutton(bg_row, text="Set/clear Is Background", variable=bg_change_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(bg_row, text="Is Background = True", variable=bg_var).grid(row=0, column=1, sticky="w", padx=(12, 0))

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(14, 0))

        def apply_changes():
            sheet_name = self.current_sheet_name
            rows = self.project_state.get_rows(sheet_name)
            cols = self.project_state.get_columns(sheet_name)

            drug = drug_var.get().strip()
            cuboids_str = cuboids_var.get().strip()

            # Validate cuboids if provided
            cuboids_val = None
            if cuboids_str:
                try:
                    cuboids_val = int(cuboids_str)
                except ValueError:
                    messagebox.showerror("Invalid input", "Cuboids Count must be an integer.")
                    return

            bg_change = bg_change_var.get()
            bg_value = bg_var.get()

            # Apply to every selected cell
            for (item_id, col_id) in list(self.selected_cells):
                try:
                    row_label = self.tree.item(item_id, "text")
                    col_index = int(col_id.replace("#", "")) - 1
                    if col_index < 0 or col_index >= len(cols):
                        continue

                    col_label = cols[col_index]

                    # Resolve row index
                    try:
                        row_idx = list(rows).index(row_label)
                    except ValueError:
                        try:
                            row_idx = int(row_label)
                        except ValueError:
                            continue

                    col_idx = col_index

                    if drug:
                        self.project_state.set_drug_name(sheet_name, row_idx, col_idx, drug)
                    if cuboids_val is not None:
                        self.project_state.set_cuboid_count(sheet_name, row_idx, col_idx, cuboids_val)
                    if bg_change:
                        self.project_state.set_is_background(sheet_name, row_idx, col_idx, bool(bg_value))

                except Exception:
                    continue

            # Refresh table + info
            self.display_table(sheet_name)
            self.update_sheet_info(sheet_name)

            win.destroy()

        ttk.Button(btns, text="Apply to Selected", command=apply_changes).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Cancel", command=win.destroy).grid(row=0, column=1)

        frm.columnconfigure(1, weight=1)
        win.resizable(False, False)
            
    def update_info(self, text):
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)


def main():
    root = tk.Tk()
    app = UI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
