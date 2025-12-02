import tkinter as tk
from tkinter import ttk, messagebox

from src.game.game_state import GameStatus
from src.gui.styles import BG_MAIN, BG_PANEL, FG_TEXT

#The Game
class GameFrame(tk.Frame):
    def __init__(self, parent, controller, game_state):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        self.game_state = game_state

        self.board = game_state.board
        self.buttons: dict[tuple[int, int], ttk.Button] = {} #Buttons dict

        #Bars containing buttons/information
        self.top_bar = None
        self.bottom_bar = None
        self.board_frame = None

        self._build_ui()
        self.after(100, self._update_timer)

    #Game Frame UI
    def _build_ui(self):
        self.top_bar = tk.Frame(self, bg=BG_PANEL)
        self.top_bar.pack(side="top", fill="x", pady=5)

        #Labels for difficulty, Timer, Mines, Flags, Hints
        tk.Label(
            self.top_bar,
            text=f'Difficulty: {self.board.difficulty_name}',
            font=("Helvetica", 11, "bold"),
            bg=BG_PANEL,
            fg=FG_TEXT,
        ).pack(side="left", padx=10)

        self.top_bar.timer_label = tk.Label(self.top_bar, text="Time: 0.0 s", bg=BG_PANEL, fg=FG_TEXT)
        self.top_bar.timer_label.pack(side="left", padx=15)

        self.top_bar.mines_label = tk.Label(
            self.top_bar,
            text=f"Mines: {self.board.num_mines}   Flags: {self.board.flags_placed}",
            bg=BG_PANEL,
            fg=FG_TEXT,
        )
        self.top_bar.mines_label.pack(side="left", padx=15)

        self.top_bar.hints_label = tk.Label(
            self.top_bar,
            text=f"Hints: {self.game_state.hints_used}/{self.game_state.max_hints}",
            bg=BG_PANEL,
            fg=FG_TEXT,
        )
        self.top_bar.hints_label.pack(side="left", padx=15)

        ttk.Button(self.top_bar, text="Hint", command=self._on_hint, style="Accent.TButton").pack(
            side="right", padx=10
        )

        #GAME BOARD
        self.board_frame = tk.Frame(self)
        self.board_frame.pack(padx=10, pady=10)

        for r in range(self.board.rows):
            for c in range(self.board.cols):
                btn = ttk.Button(
                    self.board_frame,
                    width=4,
                    style="Tile.TButton",
                )
                btn.grid(row=r, column=c, ipady=6)

                btn.bind("<Button-1>", lambda e, row=r, col=c: self._on_left_click(row, col))
                btn.bind("<Button-3>", lambda e, row=r, col=c: self._on_right_click(row, col))

                #MacOS registers right click as Button-2 on trackpad
                #Include for cross OS support
                btn.bind("<Button-2>", lambda e, row=r, col=c: self._on_right_click(row, col))
                self.buttons[(r, c)] = btn

        #Bottom Bar
        self.bottom_bar = tk.Frame(self, bg=BG_MAIN)
        self.bottom_bar.pack(side="bottom", fill="x", pady=5)

        ttk.Button(
            self.bottom_bar,
            text="Main Menu",
            command=self._on_main_menu,
            style="Menu.TButton",
        ).pack(side="left", padx=10)

        ttk.Button(
            self.bottom_bar,
            text="Restart",
            command=self._on_restart,
            style="Menu.TButton",
        ).pack(side="right", padx=10)

        self._refresh_board()

    # Event Handlers
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

        if self.game_state.status is GameStatus.WON:
            self._refresh_board()
            self.controller.on_game_finished()

    def _on_main_menu(self):
        if self.game_state.status == GameStatus.PLAYING:
            quit_game = messagebox.askyesno(
                "Quit Game?",
                "Game is still in progress. Are you sure you want to return to the main menu?",
            )
            if not quit_game:
                return
        self.controller.show_frame("menu")

    def _on_restart(self):
        self.controller.start_new_game(self.game_state.difficulty)

    #Fully refresh board on every event
    def _refresh_board(self):
        if self.top_bar.mines_label is not None:
            self.top_bar.mines_label.config(
                text=f"Mines: {self.board.num_mines}   Flags: {self.board.flags_placed}"
            )
        if self.top_bar.hints_label is not None:
            self.top_bar.hints_label.config(
                text=f"Hints: {self.game_state.hints_used}/{self.game_state.max_hints}"
            )

        for (r, c), btn in self.buttons.items():
            cell = self.board.grid[r][c]

            if cell.is_flagged():
                btn.configure(text="🚩", style="TileFlagged.TButton")
            elif cell.is_revealed():
                btn.state(["disabled"]) #disable button on reveal
                if cell.is_mine:
                    btn.configure(text="💣", style="TileMine.TButton")
                #logic for cells with adjacent mines
                else:
                    if cell.adjacent_mines > 0:
                        btn.configure(
                            text=str(cell.adjacent_mines),
                            style=f"TileNum{cell.adjacent_mines}.TButton",
                        )
                    else:
                        btn.configure(text="", style="TileRevealed.TButton")
            #Regular tiles remain blank
            else:
                btn.configure(text="", style="Tile.TButton")

    # Auto Timer update logic
    def _update_timer(self):
        if self.top_bar.timer_label is not None:
            elapsed = self.game_state.get_elapsed_time()
            self.top_bar.timer_label.config(text=f"Time: {elapsed:.1f} s")
        self.after(200, self._update_timer)
