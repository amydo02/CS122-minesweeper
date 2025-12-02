import tkinter as tk
from tkinter import ttk

#colors
BG_MAIN     = '#1e1e1e'
BG_PANEL    = '#2b2b2b'
FG_TEXT     = '#f5f5f5'
ACCENT      = '#4caf50'
BTN_BG      = '#3a3a3a'
BTN_BG_HOVER = '#4a4a4a'

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

TILE_FONT = ('Arial', 11, 'bold')

#streamline styles
class style:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style(root)

        self._setup_theme()
        self._setup_common_styles()
        self._setup_tile_styles()

    def _setup_theme(self):
        self.style.theme_use('clam')

        self.root.configure(bg=BG_MAIN)
        self.root.option_add('*Font', "Helvetica 11")
        self.root.option_add('*Label.foreground', FG_TEXT)
        self.root.option_add('*Label.background', BG_MAIN)

    def _setup_common_styles(self):
        # Menu Buttons
        self.style.configure(
            'Menu.TButton',
            background=BTN_BG,
            foreground=FG_TEXT,
            padding=(8, 4),
            borderwidth=0,
            focusthickness=0,
        )
        self.style.map(
            'Menu.TButton',
            background=[('active', BTN_BG_HOVER)],
        )

        # Green Buttons
        self.style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground=FG_TEXT,
            padding=(8, 4),
            borderwidth=0,
            focusthickness=0,
        )
        self.style.map(
            'Accent.TButton',
            background=[('active', ACCENT)],
        )

    def _setup_tile_styles(self):
        # Tiles
        self.style.configure(
            'Tile.TButton',
            background=BTN_BG,
            foreground=FG_TEXT,
            padding=0,
            borderwidth=1,
            relief='raised',
            font = TILE_FONT
        )
        self.style.map(
            'Tile.TButton',
            background=[('active', BTN_BG_HOVER)],
            foreground=[('active', FG_TEXT)]
        )

        # Revealed Tiles
        self.style.configure(
            'TileRevealed.TButton',
            background='white',
            foreground=FG_TEXT,
            padding=0,
            borderwidth=1,
            relief="sunken",
            font= TILE_FONT
        )
        self.style.map(
            'TileRevealed.TButton',
            background=[('active', 'white')],
            foreground=[('active', 'black')],
        )

        # Mines
        self.style.configure(
            'TileMine.TButton',
            background = 'white',
            foreground='red',
            padding=0,
            borderwidth=1,
            relief='sunken',
            font = TILE_FONT
        )
        self.style.map(
            'TileMine.TButton',
            background=[('active','white')],
            foreground=[('active','red')],
        )

        # Flags
        self.style.configure(
            'TileFlagged.TButton',
            background=BTN_BG,
            foreground='yellow',
            padding=0,
            borderwidth=1,
            relief='raised',
            font = TILE_FONT
        )
        self.style.map(
            'TileFlagged.TButton',
            background=[('active', BTN_BG_HOVER)],
        )

        for n, color in NUMBER_COLORS.items():
            style_name = f"TileNum{n}.TButton"
            self.style.configure(
                style_name,
                background='white',    
                foreground=color,
                padding=0,
                borderwidth=1,
                relief='sunken',
                font=TILE_FONT,
            )
            self.style.map(
                style_name,
                background=[('active', 'white')], 
                foreground=[('active', color)],
            )