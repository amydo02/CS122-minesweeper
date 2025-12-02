import tkinter as tk
from tkinter import ttk

from src.gui.styles import BG_MAIN

class StatsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller

        tk.Label(self, text="Statistics", font=("Helvetica", 18, "bold")).pack(pady=15)

        self.summary_label = tk.Label(self, text="", justify="left", font=("Courier", 10))
        self.summary_label.pack(padx=20, pady=10)

        button_bar = tk.Frame(self, bg=BG_MAIN)
        button_bar.pack(pady=10)

        ttk.Button(
            button_bar,
            text="Back to Main Menu",
            command=self._back_to_menu,
            style="Menu.TButton",
        ).pack(side="left", padx=10)

        ttk.Button(
            button_bar,
            text="Play Again",
            command=self._play_again,
            style="Menu.TButton",
        ).pack(side="left", padx=10)

    #update the stats frame
    def refresh(self):
        s = self.controller.stats
        lines: list[str] = []

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
            self.controller.show_frame("menu")
            return

        diff_name = last["difficulty"]
        from src.game.board import Difficulty

        chosen = None
        for diff in Difficulty.get_all():
            if diff["name"] == diff_name:
                chosen = diff
                break

        if chosen is None:
            self.controller.show_frame("menu")
            return

        self.controller.start_new_game(chosen)
