import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.game.board import Difficulty
from src.game.game_state import GameState, GameStatus
from src.gui.styles import BG_MAIN, BG_PANEL, FG_TEXT, style
from src.gui.menu_frame import MainMenuFrame
from src.gui.game_frame import GameFrame
from src.gui.stats_frame import StatsFrame


class MinesweeperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minesweeper")
        self.resizable(False, False)
        self.styles = style(self)

        # set window icon
        try:
            icon_path = os.path.join(project_root, "image", "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not load icon: {e}")

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
        
        #collect stats about current game
        gs = self.current_game
        diff_name = gs.difficulty["name"]
        won = gs.status == GameStatus.WON

        #update total stats this session
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

        #win/lose message
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

if __name__ == "__main__":
    app = MinesweeperApp()
    app.mainloop()
