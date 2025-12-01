import os
import sys
import tkinter as tk
from tkinter import messagebox

# Add project root to path (go up two levels from src/gui/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.game.board import Difficulty
from src.game.game_state import GameState, GameStatus

# Colors
BG_MAIN = "#1e1e1e"
BG_PANEL = "#2b2b2b"
FG_TEXT = "#f5f5f5"
ACCENT = "#4caf50"
BTN_BG = "#3a3a3a"
BTN_BG_HOVER = "#4a4a4a"
BTN_DANGER = "#c62828"

# Cell colors
CELL_UNREVEALED = "#7b7b7b"
CELL_REVEALED = "#c0c0c0"
CELL_FLAG = "#ffa726"

# Number colors (classic Minesweeper style)
NUMBER_COLORS = {
    1: "#0000ff",  # Blue
    2: "#008000",  # Green
    3: "#ff0000",  # Red
    4: "#000080",  # Dark Blue
    5: "#800000",  # Maroon
    6: "#008080",  # Cyan
    7: "#000000",  # Black
    8: "#808080",  # Gray
}


class MinesweeperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minesweeper")
        self.resizable(False, False)

        #themeing
        self.configure(bg=BG_MAIN)

        # Set window icon
        try:
            icon_path = os.path.join(project_root, "image", "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not load icon: {e}")

        self.option_add("*Font", "Helvetica 11")
        self.option_add("*Label.foreground", FG_TEXT)
        self.option_add("*Label.background", BG_MAIN)
        self.option_add("*Button.background", BTN_BG)
        self.option_add("*Button.foreground", FG_TEXT)
        self.option_add("*Button.activeBackground", BTN_BG_HOVER)
        self.option_add("*Button.activeForeground", FG_TEXT)

        #all frames will go here
        container = tk.Frame(self, bg=BG_MAIN)
        container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.container = container
        self.frames = {} #dictionary to store frames

        #initialize gamestate var 
        self.current_game: GameState = None

        #store stats across session
        self.stats = {
            "games_played": 0,
            "games_won": 0,
            "per_difficulty": {},
            "last_game": None,
        }
        
        #initialize per-difficulty stat
        for diff in Difficulty.get_all():
            name = diff["name"]
            self.stats["per_difficulty"][name] = {
                "played": 0,
                "won": 0,
                "best_time": None,
                "best_score": None,
            }

        #create fixed frames
        self.frames["menu"] = MainMenuFrame(parent=container, controller=self)
        self.frames["menu"].grid(row=0, column=0, sticky="nsew")

        self.frames["stats"] = StatsFrame(parent=container, controller=self)
        self.frames["stats"].grid(row=0, column=0, sticky="nsew")

        #create game frame
        self.frames["game"] = None

        #open with main menu
        self.show_frame("menu")



    #helper function to raise specified frame to front
    def show_frame(self, name: str):
        frame = self.frames.get(name)
        if frame is not None:
            frame.tkraise()

    #explicit function to show the stats frame
    #since we need to refresh the stats specifically
    def show_stats(self):
        stats_frame: StatsFrame = self.frames["stats"]
        stats_frame.refresh()
        self.show_frame("stats")


    def start_new_game(self, difficulty: dict):
        self.current_game = GameState(difficulty)

        #destroy all previous games
        old = self.frames.get("game")
        if old is not None:
            old.destroy()

        
        game_frame = GameFrame(parent=self.container, controller=self, game_state=self.current_game)
        self.frames["game"] = game_frame
        game_frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("game")

    def on_game_finished(self):
        if self.current_game is None:
            return

        gs = self.current_game
        diff_name = gs.difficulty["name"]
        won = gs.status == GameStatus.WON

        #update the total stats
        self.stats["games_played"] += 1
        self.stats["per_difficulty"][diff_name]["played"] += 1
        if won:
            self.stats["games_won"] += 1
            self.stats["per_difficulty"][diff_name]["won"] += 1

            #update best time and best score
            best_time = self.stats["per_difficulty"][diff_name]["best_time"]
            if best_time is None or gs.elapsed_time < best_time:
                self.stats["per_difficulty"][diff_name]["best_time"] = gs.elapsed_time

            best_score = self.stats["per_difficulty"][diff_name]["best_score"]
            if best_score is None or gs.score > best_score:
                self.stats["per_difficulty"][diff_name]["best_score"] = gs.score

        #store last game summary
        self.stats["last_game"] = {
            "difficulty": diff_name,
            "won": won,
            "time": gs.elapsed_time,
            "score": gs.score,
            "hints_used": gs.hints_used,
        }

        # show win/lose message
        if won:
            message = f"You won!\n\nTime: {gs.elapsed_time:.1f} s\nScore: {gs.score}"
        else:
            message = "Boom! You hit a mine.\n\nBetter luck next time."
        self._show_game_over_message(message)
    
    def _show_game_over_message(self, message):
        popup = tk.Toplevel(self)
        popup.title("Game Over")
        popup.transient(self)
        popup.grab_set()
        popup.resizable(False, False)
        popup.configure(bg=BG_PANEL)

        tk.Label(
            popup,
            text=message,
            padx=20,
            pady=20,
            justify="left",
            bg=BG_PANEL,
            fg=FG_TEXT,
        ).pack()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        #exit
        tk.Button(btn_frame, text="OK", width=12,
                command=popup.destroy, fg="black").pack(side="left", padx=8)

        #view stats
        tk.Button(btn_frame, text="View Stats", width=12,
                command=lambda: (popup.destroy(), self.show_stats()),
                fg="black"
        ).pack(side="left", padx=8)

        # Center the popup on the main window
        popup.update_idletasks()

        # Get main window position and size
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()

        # Get popup size
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()

        # Calculate center position relative to main window
        x = main_x + (main_width - popup_width) // 2
        y = main_y + (main_height - popup_height) // 2

        popup.geometry(f"+{x}+{y}")

#=== MAIN MENU ===#
class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller: MinesweeperApp):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller

        tk.Label(
            self, 
            text="Minesweeper", 
            font=("Helvetica", 20, "bold"), 
            bg=BG_MAIN,
            fg=FG_TEXT).pack(pady=20)

        tk.Label(
            self, 
            text="Select difficulty", 
            font=("Helvetica", 12),
            bg=BG_MAIN,
            fg="#cccccc").pack(pady=(0, 5))

        self.difficulty_var = tk.StringVar()

        for diff in Difficulty.get_all():
            tk.Radiobutton(
                self,
                text=f'{diff["name"]} ({diff["rows"]}x{diff["cols"]}, {diff["mines"]} mines)',
                variable=self.difficulty_var,
                value=diff["name"],
                anchor="w",
                justify="left",
                bg=BG_MAIN,
                fg=FG_TEXT,
                activebackground=BG_MAIN,
                activeforeground=FG_TEXT,
                selectcolor=BG_PANEL,
            ).pack(fill="x", padx=40, pady=2)

        tk.Button(self, text="Start Game", width=18, command=self._on_start, fg="black", bg=BTN_BG).pack(pady=15)
        tk.Button(self, text="View Stats", width=18, command=controller.show_stats, fg="black").pack(pady=5)
        tk.Button(self, text="Quit", width=18, command=controller.destroy, fg="red").pack(pady=5)

    #starts the game with selected difficulty
    def _on_start(self):
        selected_name = self.difficulty_var.get()
        selected_diff = None
        for diff in Difficulty.get_all():
            if diff["name"] == selected_name:
                selected_diff = diff
                break
        if selected_diff is None:
            messagebox.showerror("Error", "Please select a difficulty.")
            return

        # If custom difficulty is selected, show custom dialog
        if selected_name == "Custom":
            custom_diff = self._show_custom_dialog()
            if custom_diff is not None:
                self.controller.start_new_game(custom_diff)
        else:
            self.controller.start_new_game(selected_diff)

    def _show_custom_dialog(self):
        """Show dialog to get custom difficulty settings."""
        dialog = tk.Toplevel(self.controller)
        dialog.title("Custom Difficulty")
        dialog.transient(self.controller)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=BG_PANEL)

        result = {"cancelled": True}

        # Title
        tk.Label(
            dialog,
            text="Custom Difficulty Settings",
            font=("Helvetica", 14, "bold"),
            bg=BG_PANEL,
            fg=FG_TEXT
        ).grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=20)

        # Rows input
        tk.Label(dialog, text="Rows (5-30):", bg=BG_PANEL, fg=FG_TEXT).grid(
            row=1, column=0, sticky="e", padx=(20, 5), pady=5
        )
        rows_entry = tk.Entry(dialog, width=10)
        rows_entry.insert(0, "10")
        rows_entry.grid(row=1, column=1, sticky="w", padx=(5, 20), pady=5)

        # Columns input
        tk.Label(dialog, text="Columns (5-30):", bg=BG_PANEL, fg=FG_TEXT).grid(
            row=2, column=0, sticky="e", padx=(20, 5), pady=5
        )
        cols_entry = tk.Entry(dialog, width=10)
        cols_entry.insert(0, "10")
        cols_entry.grid(row=2, column=1, sticky="w", padx=(5, 20), pady=5)

        # Mines input
        tk.Label(dialog, text="Mines:", bg=BG_PANEL, fg=FG_TEXT).grid(
            row=3, column=0, sticky="e", padx=(20, 5), pady=5
        )
        mines_entry = tk.Entry(dialog, width=10)
        mines_entry.insert(0, "15")
        mines_entry.grid(row=3, column=1, sticky="w", padx=(5, 20), pady=5)

        # Error label
        error_label = tk.Label(dialog, text="", fg="red", bg=BG_PANEL, font=("Helvetica", 9))
        error_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))

        def validate_and_start():
            try:
                rows = int(rows_entry.get())
                cols = int(cols_entry.get())
                mines = int(mines_entry.get())

                # Validation
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

                # Valid settings
                result["cancelled"] = False
                result["difficulty"] = {
                    "rows": rows,
                    "cols": cols,
                    "mines": mines,
                    "name": "Custom"
                }
                dialog.destroy()

            except ValueError:
                error_label.config(text="Please enter valid numbers")

        # Buttons
        btn_frame = tk.Frame(dialog, bg=BG_PANEL)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(10, 15))

        tk.Button(
            btn_frame,
            text="Cancel",
            width=10,
            command=dialog.destroy,
            bg=BTN_BG,
            fg="red"
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Start",
            width=10,
            command=validate_and_start,
            bg=ACCENT,
            fg="black"
        ).pack(side="left", padx=5)

        # Center the dialog
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


#=== GAME ===#
class GameFrame(tk.Frame):
    def __init__(self, parent, controller: MinesweeperApp, game_state: GameState):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        self.game_state = game_state

        self.board = game_state.board
        self.buttons: dict[tuple[int, int], tk.Button] = {} #dictionary of each button (cell)
        self.top_bar = None
        self.bottom_bar = None
        self.board_frame = None

        self._build_ui()

        #start timer
        self.after(100, self._update_timer)

    #=== UI ===#
    def _build_ui(self):
        ## TOP BAR (Difficulty, Timer, Mines, Flags, Hints) ##
        self.top_bar = tk.Frame(self, bg=BG_PANEL)
        self.top_bar.pack(side="top", fill="x", pady=5)

        tk.Label(
            self.top_bar,
            text=f'Difficulty: {self.board.difficulty_name}',
            font=("Helvetica", 11, "bold"),
            bg=BG_PANEL,
            fg=FG_TEXT
        ).pack(side="left", padx=10)

        self.top_bar.timer_label = tk.Label(self.top_bar, text="Time: 0.0 s", bg=BG_PANEL, fg=FG_TEXT)
        self.top_bar.timer_label.pack(side="left", padx=15)

        self.top_bar.mines_label = tk.Label(
            self.top_bar,
            text=f'Mines: {self.board.num_mines}   Flags: {self.board.flags_placed}',
            bg=BG_PANEL,
            fg=FG_TEXT
        )
        self.top_bar.mines_label.pack(side="left", padx=15)

        self.top_bar.hints_label = tk.Label(
            self.top_bar,
            text=f'Hints: {self.game_state.hints_used}/{self.game_state.max_hints}',
            bg=BG_PANEL,
        )
        self.top_bar.hints_label.pack(side="left", padx=15)

        tk.Button(self.top_bar, text="Hint", command=self._on_hint, bg=ACCENT, fg='black').pack(side="right", padx=10)

        ## BUTTONS (MINE CELLS) ##
        self.board_frame = tk.Frame(self)
        self.board_frame.pack(padx=10, pady=10)

        for r in range(self.board.rows):
            for c in range(self.board.cols):
                btn = tk.Button(
                    self.board_frame,
                    width=2,
                    height=1,
                    relief="raised",
                    text="",
                    font=("Courier", 12, "bold"),
                    bg=CELL_UNREVEALED,
                    activebackground=BTN_BG_HOVER,
                    borderwidth=2,
                )
                btn.grid(row=r, column=c, padx=0, pady=0)

                #button bindings
                btn.bind("<Button-1>", lambda e, row=r, col=c: self._on_left_click(row, col))
                btn.bind("<Button-3>", lambda e, row=r, col=c: self._on_right_click(row, col))

                ### I tested this on my mac and it wasnt working
                ### Because on mac trackpad, right click is Button-2.
                btn.bind("<Button-2>", lambda e, row=r, col=c: self._on_right_click(row, col))
                self.buttons[(r, c)] = btn

        ## BOTTOM BAR (Main Menu/Restart) ##
        self.bottom_bar = tk.Frame(self, bg=BG_PANEL)
        self.bottom_bar.pack(side="bottom", fill="x", pady=5)

        tk.Button(self.bottom_bar, text="Main Menu", command=self._on_main_menu,
                  bg=BTN_BG, fg="black").pack(
            side="left", padx=10
        )
        tk.Button(self.bottom_bar, text="Restart", command=self._on_restart,
                  bg=BTN_BG, fg="black").pack(
            side="right", padx=10
        )

        #render the board
        self._refresh_board()

    #=== EVENT HANDLERS ===#
    def _on_left_click(self, row: int, col: int):
        if self.game_state.status not in (GameStatus.NOT_STARTED, GameStatus.PLAYING):
            return

        self.game_state.click_cell(row, col)
        self._refresh_board()

        if self.game_state.status in (GameStatus.WON, GameStatus.LOST):
            self._refresh_board()
            self.controller.on_game_finished()

    def _on_right_click(self, row: int, col: int):
        if self.game_state.status != GameStatus.PLAYING:
            return
        self.game_state.flag_cell(row, col)
        self._refresh_board()

    def _on_hint(self):
        if self.game_state.status != GameStatus.PLAYING:
            return
        used = self.game_state.use_hint()
        if not used:
            messagebox.showinfo("Hint", "No hints available.")
        self._refresh_board()

        if self.game_state.status is GameStatus.WON: #if you use a hint and it wins the game
            self._refresh_board()
            self.controller.on_game_finished()

    def _on_main_menu(self):
        if self.game_state.status == GameStatus.PLAYING:
            quit = messagebox.askyesno(
                "Quit Game?",
                "Game is still in progress. Are you sure you want to return to the main menu?",
            )
            if not quit:
                return
        self.controller.show_frame("menu")

    def _on_restart(self):
        self.controller.start_new_game(self.game_state.difficulty)

    def _refresh_board(self):
        #update topbar label
        if self.top_bar.mines_label is not None:
            self.top_bar.mines_label.config(
                text=f"Mines: {self.board.num_mines}   Flags: {self.board.flags_placed}"
            )
        if self.top_bar.hints_label is not None:
            self.top_bar.hints_label.config(
                text=f"Hints: {self.game_state.hints_used}/{self.game_state.max_hints}"
            )

        #update each button
        for (r, c), btn in self.buttons.items():
            cell = self.board.grid[r][c]

            if cell.is_flagged():
                btn.config(
                    text="🚩",
                    fg="white",
                    bg=CELL_FLAG,
                    font=("Arial", 11),
                    state="normal",
                    relief="raised"
                )
            elif cell.is_revealed():
                btn.config(relief="sunken", state="disabled", bg=CELL_REVEALED)
                if cell.is_mine:
                    btn.config(
                        text="💣",
                        font=("Arial", 11),
                        disabledforeground="black",
                        bg="#ff6b6b"
                    )
                else:
                    if cell.adjacent_mines > 0:
                        color = NUMBER_COLORS.get(cell.adjacent_mines, "black")
                        btn.config(
                            text=str(cell.adjacent_mines),
                            font=("Arial", 11, "bold"),
                            disabledforeground=color
                        )
                    else:
                        btn.config(text="", font=("Arial", 11))
            else:
                btn.config(
                    text="",
                    bg=CELL_UNREVEALED,
                    state="normal",
                    relief="raised"
                )

    def _update_timer(self):
        if self.top_bar.timer_label is not None:
            elapsed = self.game_state.get_elapsed_time()
            self.top_bar.timer_label.config(text=f"Time: {elapsed:.1f} s")
        # Keep updating while the app is alive; GameState will freeze time after end
        self.after(200, self._update_timer)

#=== STATS ===#
class StatsFrame(tk.Frame):
    def __init__(self, parent, controller: MinesweeperApp):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller

        tk.Label(self, text="Statistics", font=("Helvetica", 18, "bold")).pack(pady=15)

        self.summary_label = tk.Label(self, text="", justify="left", font=("Courier", 10))
        self.summary_label.pack(padx=20, pady=10)

        button_bar = tk.Frame(self)
        button_bar.pack(pady=10)

        tk.Button(button_bar, text="Back to Main Menu", command=self._back_to_menu, fg="black", bg=BTN_BG).pack(
            side="left", padx=10,
        )
        tk.Button(button_bar, text="Play Again", command=self._play_again, fg="black", bg=BTN_BG).pack(
            side="left", padx=10,
        )

    #populates the actual stats
    def refresh(self):
        s = self.controller.stats
        lines = []

        lines.append(f"Total games played: {s['games_played']}")
        lines.append(f"Total games won   : {s['games_won']}")
        if s["games_played"] > 0:
            win_rate = 100.0 * s["games_won"] / s["games_played"]
            lines.append(f"Overall win rate  : {win_rate:.1f}%")
        lines.append("")

        lines.append("Per-difficulty stats:")
        for diff_name, d in s["per_difficulty"].items():
            lines.append(f"  {diff_name}:")
            lines.append(f"    Played: {d['played']}, Won: {d['won']}")
            if d["best_time"] is not None:
                lines.append(f"    Best time : {d['best_time']:.1f} s")
            if d["best_score"] is not None:
                lines.append(f"    Best score: {d['best_score']}")
            lines.append("")

        last = s["last_game"]
        if last is not None:
            lines.append("Last game:")
            lines.append(f"  Difficulty : {last['difficulty']}")
            lines.append(f"  Result     : {'WON' if last['won'] else 'LOST'}")
            lines.append(f"  Time       : {last['time']:.1f} s")
            lines.append(f"  Score      : {last['score']}")
            lines.append(f"  Hints used : {last['hints_used']}")
        else:
            lines.append("No games played yet this session.")

        self.summary_label.config(text="\n".join(lines))

    def _back_to_menu(self):
        self.controller.show_frame("menu")

    def _play_again(self):
        last = self.controller.stats.get("last_game")
        if not last:
            #edge case
            self.controller.show_frame("menu")
            return

        #replay previous difficulty
        diff_name = last["difficulty"]
        chosen = None
        for diff in Difficulty.get_all():
            if diff["name"] == diff_name:
                chosen = diff
                break
        if chosen is None:
            self.controller.show_frame("menu")
            return

        self.controller.start_new_game(chosen)


def main():
    app = MinesweeperApp()
    app.mainloop()


if __name__ == "__main__":
    main()