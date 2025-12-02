import tkinter as tk
from tkinter import ttk, messagebox

from src.game.board import Difficulty
from src.gui.styles import BG_MAIN, BG_PANEL, FG_TEXT


class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller

        tk.Label(
            self,
            text="Minesweeper",
            font=("Helvetica", 20, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT,
        ).pack(pady=20)

        tk.Label(
            self,
            text="Select difficulty",
            font=("Helvetica", 12),
            bg=BG_MAIN,
            fg="#cccccc",
        ).pack(pady=(0, 5))

        #take in difficulty as a variable
        self.difficulty_var = tk.StringVar()

        #Create a radiobutton for each difficulty
        for diff in Difficulty.get_all():
            tk.Radiobutton(
                self,
                text=f'{diff["name"]} ({diff["rows"]}x{diff["cols"]}, {diff["mines"]} mines)',
                variable=self.difficulty_var, #assign data to this var
                value=diff["name"], #the data
                anchor="w",
                justify="left",
                bg=BG_MAIN,
                fg=FG_TEXT,
                activebackground=BG_MAIN,
                activeforeground=FG_TEXT,
                selectcolor=BG_PANEL,
            ).pack(fill="x", padx=40, pady=2)

        #Main Menu Buttons
        ttk.Button(
            self,
            text="Start Game",
            width=18,
            command=self._on_start,
            style="Accent.TButton",
        ).pack(pady=15)

        ttk.Button(
            self,
            text="View Stats",
            width=18,
            command=controller.show_stats,
            style="Menu.TButton",
        ).pack(pady=5)

        ttk.Button(
            self,
            text="Quit",
            width=18,
            command=controller.destroy,
            style="Menu.TButton",
        ).pack(pady=5)

    def _on_start(self):
        #Get Var from RadioButton
        selected_name = self.difficulty_var.get()
        
        #Ensure that a difficulty is selected
        selected_diff = None
        for diff in Difficulty.get_all():
            if diff["name"] == selected_name:
                selected_diff = diff
                break
        if selected_diff is None:
            messagebox.showerror("Error", "Please select a difficulty.")
            return
        
        #Handler for custom difficulty
        if selected_name == "Custom":
            custom_diff = self._show_custom_dialog()
            if custom_diff is not None:
                self.controller.start_new_game(custom_diff)
        else:
            self.controller.start_new_game(selected_diff)

    def _show_custom_dialog(self):
        dialog = tk.Toplevel(self.controller)
        dialog.title("Custom Difficulty")
        dialog.transient(self.controller)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=BG_PANEL)

        result = {"cancelled": True}

        tk.Label(
            dialog,
            text="Custom Difficulty Settings",
            font=("Helvetica", 14, "bold"),
            bg=BG_PANEL,
            fg=FG_TEXT,
        ).grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=20)

        tk.Label(dialog, text="Rows (5-30):", bg=BG_PANEL, fg=FG_TEXT).grid(
            row=1, column=0, sticky="e", padx=(20, 5), pady=5
        )
        rows_entry = tk.Entry(dialog, width=10)
        rows_entry.insert(0, "10")
        rows_entry.grid(row=1, column=1, sticky="w", padx=(5, 20), pady=5)

        tk.Label(dialog, text="Columns (5-30):", bg=BG_PANEL, fg=FG_TEXT).grid(
            row=2, column=0, sticky="e", padx=(20, 5), pady=5
        )
        cols_entry = tk.Entry(dialog, width=10)
        cols_entry.insert(0, "10")
        cols_entry.grid(row=2, column=1, sticky="w", padx=(5, 20), pady=5)

        tk.Label(dialog, text="Mines:", bg=BG_PANEL, fg=FG_TEXT).grid(
            row=3, column=0, sticky="e", padx=(20, 5), pady=5
        )
        mines_entry = tk.Entry(dialog, width=10)
        mines_entry.insert(0, "15")
        mines_entry.grid(row=3, column=1, sticky="w", padx=(5, 20), pady=5)

        error_label = tk.Label(dialog, text="", fg="red", bg=BG_PANEL, font=("Helvetica", 9))
        error_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))

        def validate_and_start():
            try:
                rows = int(rows_entry.get())
                cols = int(cols_entry.get())
                mines = int(mines_entry.get())

                if not (5 <= rows <= 30):
                    error_label.config(text="Rows must be between 5 and 30")
                    return
                if not (5 <= cols <= 30):
                    error_label.config(text="Columns must be between 5 and 30")
                    return
                if mines < 1:
                    error_label.config(text="Must have at least 1 mine")
                    return
                if mines >= rows * cols:
                    error_label.config(text="Too many mines! Must be less than total cells")
                    return

                result["cancelled"] = False
                result["difficulty"] = {
                    "rows": rows,
                    "cols": cols,
                    "mines": mines,
                    "name": "Custom",
                }
                dialog.destroy()
            except ValueError:
                error_label.config(text="Please enter valid numbers")

        btn_frame = tk.Frame(dialog, bg=BG_PANEL)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(10, 15))

        ttk.Button(
            btn_frame,
            text="Cancel",
            width=10,
            command=dialog.destroy,
            style="Menu.TButton",
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Start",
            width=10,
            command=validate_and_start,
            style="Accent.TButton",
        ).pack(side="left", padx=5)

        dialog.update_idletasks()
        main_x = self.controller.winfo_x()
        main_y = self.controller.winfo_y()
        main_width = self.controller.winfo_width()
        main_height = self.controller.winfo_height()
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()
        x = main_x + (main_width - dialog_width) // 2
        y = main_y + (main_height - dialog_height) // 2
        dialog.geometry(f"+{x}+{y}")

        dialog.wait_window()

        if result["cancelled"]:
            return None
        return result["difficulty"]
