import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.game.board import Difficulty
from src.game.game_state import GameState, GameStatus
from src.gui.styles import BG_MAIN, BG_PANEL, FG_TEXT, style
from src.gui.menu_frame import MainMenuFrame
from src.gui.game_frame import GameFrame
from src.gui.stats_frame import StatsFrame
from src.db import SessionLocal, init_db, User, UserDifficultyStat
from src.gui.styles import BG_MAIN, BG_PANEL, FG_TEXT, style

#initialize db
init_db()

class MinesweeperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minesweeper")
        self.resizable(False, False)
        self.styles = style(self)

        #create the session, create current_user var
        self.db = SessionLocal()
        self.current_user: User | None = None

        # set window icon
        try:
            icon_path = os.path.join(project_root, "image", "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not load icon: {e}")

        #prompt user to log in
        self._show_login_dialog()

        container = tk.Frame(self, bg=BG_MAIN)
        container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.container = container
        self.frames: dict[str, tk.Frame] = {}

        self.current_game: GameState | None = None

        self.stats = {
            "games_played": 0,
            "games_won": 0,
            "per_difficulty": {},
            "last_game": None,
        }

        for diff in Difficulty.get_all():
            name = diff["name"]
            self.stats["per_difficulty"][name] = {
                "played": 0,
                "won": 0,
                "best_time": None,
                "best_score": None,
            }

        # fixed frames
        self.frames["menu"] = MainMenuFrame(parent=container, controller=self)
        self.frames["menu"].grid(row=0, column=0, sticky="nsew")

        self.frames["stats"] = StatsFrame(parent=container, controller=self)
        self.frames["stats"].grid(row=0, column=0, sticky="nsew")

        # dynamic game frame
        self.frames["game"] = None

        #open with menu frame
        self.show_frame("menu")
    
    # raises a frame to the top
    def show_frame(self, name: str):
        target = self.frames.get(name)
        if target is None:
            return

        # Hide non active frames so they don't affect resizing
        for key, frame in self.frames.items():
            if frame is None:
                continue
            if frame is target:
                frame.grid()
            else:
                frame.grid_remove()

        target.tkraise()
        self._resize_to_fit()

    # Resizes current raised frame to fit
    # tkinter will automatically size up, but not down
    # this func helps resize down
    def _resize_to_fit(self):
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        self.geometry(f"{w}x{h}")

    # helper function to show stats frame
    def show_stats(self):
        stats_frame: StatsFrame = self.frames["stats"]
        stats_frame.refresh()
        self.show_frame("stats")

    # start game
    def start_new_game(self, difficulty: dict):
        from src.gui.game_frame import GameFrame 

        #initialize gameboard with difficulty
        self.current_game = GameState(difficulty)

        #destroy all old game frames
        old = self.frames.get("game")
        if old is not None:
            old.destroy()

        #create game_frame, add to dict and grid
        game_frame = GameFrame(parent=self.container, controller=self, game_state=self.current_game)
        self.frames["game"] = game_frame
        game_frame.grid(row=0, column=0, sticky="nsew")

        #display game frame
        self.show_frame("game")

    def on_game_finished(self):
        if self.current_game is None:
            return

        gs = self.current_game
        diff_name = gs.difficulty["name"]
        won = gs.status == GameStatus.WON

        # --- update in-memory session stats ---
        self.stats["games_played"] += 1
        self.stats["per_difficulty"][diff_name]["played"] += 1
        if won:
            self.stats["games_won"] += 1
            self.stats["per_difficulty"][diff_name]["won"] += 1

            best_time = self.stats["per_difficulty"][diff_name]["best_time"]
            if best_time is None or gs.elapsed_time < best_time:
                self.stats["per_difficulty"][diff_name]["best_time"] = gs.elapsed_time

            best_score = self.stats["per_difficulty"][diff_name]["best_score"]
            if best_score is None or gs.score > best_score:
                self.stats["per_difficulty"][diff_name]["best_score"] = gs.score

        self.stats["last_game"] = {
            "difficulty": diff_name,
            "won": won,
            "time": gs.elapsed_time,
            "score": gs.score,
            "hints_used": gs.hints_used,
        }

        # --- update persistent "overall" stats in DB ---
        if self.current_user is not None and won:
            # find/create per-difficulty row
            stat = (
                self.db.query(UserDifficultyStat)
                .filter_by(user_id=self.current_user.id, difficulty=diff_name)
                .first()
            )
            if stat is None:
                stat = UserDifficultyStat(
                    user_id=self.current_user.id,
                    difficulty=diff_name,
                    best_time=gs.elapsed_time,
                    best_score=gs.score,
                )
                self.db.add(stat)
            else:
                # update if this run is better
                if stat.best_time is None or gs.elapsed_time < stat.best_time:
                    stat.best_time = gs.elapsed_time
                if stat.best_score is None or gs.score > stat.best_score:
                    stat.best_score = gs.score

            self.db.commit()

        # win/lose message
        if won:
            message = f"You won!\n\nTime: {gs.elapsed_time:.1f} s\nScore: {gs.score}"
        else:
            message = "Boom! You hit a mine.\n\nBetter luck next time."
        self._show_game_over_message(message)


    #Game over message
    def _show_game_over_message(self, message: str):
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

        btn_frame = tk.Frame(popup, bg=BG_PANEL)
        btn_frame.pack(pady=10)

        ttk.Button(
            btn_frame,
            text="OK",
            width=12,
            command=popup.destroy,
            style="Menu.TButton",
        ).pack(side="left", padx=8)

        ttk.Button(
            btn_frame,
            text="View Stats",
            width=12,
            command=lambda: (popup.destroy(), self.show_stats()),
            style="Menu.TButton",
        ).pack(side="left", padx=8)

        #Centers the message
        popup.update_idletasks()
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()
        x = main_x + (main_width - popup_width) // 2
        y = main_y + (main_height - popup_height) // 2
        popup.geometry(f"+{x}+{y}")
    
    #login dialog
    #prompts user for a name/pin
    def _show_login_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Select User")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=BG_PANEL)

        tk.Label(
            dialog,
            text="Minesweeper Profile",
            font=("Helvetica", 14, "bold"),
            bg=BG_PANEL,
            fg=FG_TEXT,
        ).grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=20)

        tk.Label(dialog, text="Name:", bg=BG_PANEL, fg=FG_TEXT).grid(
            row=1, column=0, sticky="e", padx=(20, 5), pady=5
        )
        #name_entry is username
        name_entry = tk.Entry(dialog, width=20)
        name_entry.grid(row=1, column=1, sticky="w", padx=(5, 20), pady=5)

        tk.Label(dialog, text="PIN (4 digits):", bg=BG_PANEL, fg=FG_TEXT).grid(
            row=2, column=0, sticky="e", padx=(20, 5), pady=5
        )
        #pin_entry pin
        pin_entry = tk.Entry(dialog, width=20, show="•")
        pin_entry.grid(row=2, column=1, sticky="w", padx=(5, 20), pady=5)

        error_label = tk.Label(
            dialog, text="", fg="red", bg=BG_PANEL, font=("Helvetica", 9)
        )
        error_label.grid(row=3, column=0, columnspan=2, pady=(5, 0))

        def on_ok():
            name = name_entry.get().strip()
            normal = name.lower()
            pin = pin_entry.get().strip()

            #verify name and pin exists, then verify pin is at least 4 digit number
            if not name or not pin:
                error_label.config(text="Please enter both name and PIN.")
                return
            if not pin.isdigit() or len(pin) < 4:
                error_label.config(text="PIN should be at least 4 digits.")
                return

            # look up existing users
            user = self.db.query(User).filter_by(normalized_name=normal).first()
            #if this user exists
            if user:
                #if the pin is incorrect
                if user.pin != pin:
                    error_label.config(text="Incorrect PIN for this name.")
                    return
                # valid existing user
                self.current_user = user
            #if the user doesn't exist, create a new user, and continue as the new user
            else:
                user = User(name=name, normalized_name=normal, pin=pin)
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                self.current_user = user

            dialog.destroy()

        #close app if user doesn't want to log in
        def on_cancel():
            self.destroy()
        def on_close():
            self.destroy() 
        dialog.protocol("WM_DELETE_WINDOW", on_close)

        btn_frame = tk.Frame(dialog, bg=BG_PANEL)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(10, 15))

        ttk.Button(
            btn_frame, text="Cancel", width=10, command=on_cancel, style="Menu.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame, text="OK", width=10, command=on_ok, style="Accent.TButton"
        ).pack(side="left", padx=5)

        # center the dialog
        dialog.update_idletasks()
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width() or 400
        main_height = self.winfo_height() or 300
        dw = dialog.winfo_width()
        dh = dialog.winfo_height()
        x = main_x + (main_width - dw) // 2
        y = main_y + (main_height - dh) // 2
        dialog.geometry(f"+{x}+{y}")

        name_entry.focus_set()
        dialog.wait_window()

        # in case somehow no user is logged in after waiting for dialog to destroy
        if self.current_user is None and not dialog:
            self.destroy()

if __name__ == "__main__":
    app = MinesweeperApp()
    app.mainloop()
