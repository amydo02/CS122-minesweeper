import random
from typing import List, Tuple, Set
from .cell import Cell, CellState

class Difficulty:
    """Difficulty configurations."""
    BEGINNER = {"rows": 9, "cols": 9, "mines": 10, "name": "Beginner"}
    INTERMEDIATE = {"rows": 16, "cols": 16, "mines": 40, "name": "Intermediate"}
    ADVANCED = {"rows": 25, "cols": 25, "mines": 99, "name": "Advanced"}
    CUSTOM = {"rows": 10, "cols": 10, "mines": 15, "name": "Custom"}  # Default custom settings

    @staticmethod
    def get_all():
        return [Difficulty.BEGINNER, Difficulty.INTERMEDIATE, Difficulty.ADVANCED, Difficulty.CUSTOM]

class Board:
    """Manages the game board logic."""
    
    def __init__(self, difficulty: dict):
        self.rows = difficulty["rows"]
        self.cols = difficulty["cols"]
        self.num_mines = difficulty["mines"]
        self.difficulty_name = difficulty["name"]
        
        self.grid: List[List[Cell]] = []
        self.mines_positions: Set[Tuple[int, int]] = set()
        self.first_click = True
        self.flags_placed = 0
        
        self._initialize_grid()
    
    def _initialize_grid(self):
        """Creates an empty grid."""
        self.grid = [[Cell(r, c) for c in range(self.cols)] 
                     for r in range(self.rows)]
    
    def place_mines(self, safe_row: int, safe_col: int):
        """Places mines after first click to ensure first click is safe."""
        available_positions = [(r, c) for r in range(self.rows) 
                               for c in range(self.cols)
                               if (r, c) != (safe_row, safe_col)]
        
        self.mines_positions = set(random.sample(available_positions, self.num_mines))
        
        for row, col in self.mines_positions:
            self.grid[row][col].is_mine = True
        
        self._calculate_adjacent_mines()
        self.first_click = False
    
    def _calculate_adjacent_mines(self):
        """Calculates adjacent mine counts for all cells."""
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.grid[row][col].is_mine:
                    count = sum(1 for r, c in self._get_neighbors(row, col)
                               if self.grid[r][c].is_mine)
                    self.grid[row][col].adjacent_mines = count
    
    def _get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Returns valid neighbor coordinates."""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbors.append((nr, nc))
        return neighbors
    
    def reveal_cell(self, row: int, col: int) -> bool:
        """
        Reveals a cell and recursively reveals empty neighbors.
        Returns True if a mine was hit.
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        
        cell = self.grid[row][col]
        
        if cell.is_revealed() or cell.is_flagged():
            return False
        
        # First click safety
        if self.first_click:
            self.place_mines(row, col)
        
        # Reveal the cell
        is_mine = cell.reveal()
        
        if is_mine:
            return True
        
        # Recursive reveal for empty cells (DFS)
        if cell.adjacent_mines == 0:
            neighbors = self._get_neighbors(row, col)
            for neighbor_row, neighbor_col in neighbors:
                self.reveal_cell(neighbor_row, neighbor_col)
        return False
    
    def toggle_flag(self, row: int, col: int) -> bool:
        """Toggles flag on a cell. Returns True if flagged."""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        
        cell = self.grid[row][col]
        was_flagged = cell.is_flagged()
        flagged = cell.toggle_flag()
        
        if flagged and not was_flagged:
            self.flags_placed += 1
        elif not flagged and was_flagged:
            self.flags_placed -= 1
        
        return flagged
    
    def get_safe_unrevealed_cells(self) -> List[Tuple[int, int]]:
        """Returns list of safe, unrevealed cells for hints."""
        safe_cells = []
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.grid[row][col]
                if not cell.is_mine and not cell.is_revealed() and not cell.is_flagged():
                    safe_cells.append((row, col))
        return safe_cells
    
    def check_win(self) -> bool:
        """
        Checks if the player has won.
        Win conditions:
        1. All non-mine cells are revealed, OR
        2. All mines are correctly flagged and no safe cells are incorrectly flagged
        """
        all_safe_revealed = True
        all_mines_flagged = True
        no_incorrect_flags = True

        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.grid[row][col]

                # Check if all non-mine cells are revealed
                if not cell.is_mine and not cell.is_revealed():
                    all_safe_revealed = False

                # Check if all mines are flagged
                if cell.is_mine and not cell.is_flagged():
                    all_mines_flagged = False

                # Check for incorrect flags (flagged but not a mine)
                if cell.is_flagged() and not cell.is_mine:
                    no_incorrect_flags = False

        # Win if either: all safe cells revealed, OR all mines correctly flagged
        return all_safe_revealed or (all_mines_flagged and no_incorrect_flags)
    
    def reveal_all_mines(self):
        """Reveals all mines (for game over)."""
        for row, col in self.mines_positions:
            self.grid[row][col].state = CellState.REVEALED
    
    def print_board(self, reveal_all=False):
        """
        Prints the board to terminal for debugging.
        
        Args:
            reveal_all: If True, shows all cells (including hidden mines)
        
        Legend:
            . = Hidden cell
            F = Flagged cell
            * = Mine (revealed or reveal_all=True)
            0-8 = Number of adjacent mines
            _ = Empty revealed cell (0 adjacent mines)
        """
        print("\n" + "=" * (self.cols * 2 + 3))
        print(f"  Board: {self.difficulty_name} ({self.rows}x{self.cols}, {self.num_mines} mines)")
        print("=" * (self.cols * 2 + 3))
        
        # Column numbers
        print("   ", end="")
        for col in range(self.cols):
            print(f"{col % 10}", end=" ")
        print()
        
        # Print each row
        for row in range(self.rows):
            print(f"{row:2} ", end="")
            for col in range(self.cols):
                cell = self.grid[row][col]
                
                if reveal_all:
                    # Show everything (debug mode)
                    if cell.is_mine:
                        print("*", end=" ")
                    elif cell.adjacent_mines == 0:
                        print("_", end=" ")
                    else:
                        print(cell.adjacent_mines, end=" ")
                else:
                    # Show only what player can see
                    if cell.is_revealed():
                        if cell.is_mine:
                            print("*", end=" ")
                        elif cell.adjacent_mines == 0:
                            print("_", end=" ")
                        else:
                            print(cell.adjacent_mines, end=" ")
                    elif cell.is_flagged():
                        print("F", end=" ")
                    else:
                        print(".", end=" ")
            print(f" {row}")
        
        # Column numbers again at bottom
        print("   ", end="")
        for col in range(self.cols):
            print(f"{col % 10}", end=" ")
        print()
        print("=" * (self.cols * 2 + 3))
        print(f"Flags placed: {self.flags_placed}/{self.num_mines}")
        print()
    
    def print_board_colorized(self, reveal_all=False):
        """
        Prints a colorized board to terminal (requires ANSI color support).
        
        Args:
            reveal_all: If True, shows all cells (including hidden mines)
        """
        # ANSI color codes
        RESET = '\033[0m'
        BOLD = '\033[1m'
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        GRAY = '\033[90m'
        
        number_colors = {
            1: BLUE,
            2: GREEN,
            3: RED,
            4: MAGENTA,
            5: '\033[31m',  # Dark red
            6: CYAN,
            7: BOLD,
            8: GRAY
        }
        
        print("\n" + "=" * (self.cols * 2 + 3))
        print(f"  {BOLD}Board: {self.difficulty_name}{RESET} ({self.rows}x{self.cols}, {self.num_mines} mines)")
        print("=" * (self.cols * 2 + 3))
        
        # Column numbers
        print("   ", end="")
        for col in range(self.cols):
            print(f"{GRAY}{col % 10}{RESET}", end=" ")
        print()
        
        # Print each row
        for row in range(self.rows):
            print(f"{GRAY}{row:2}{RESET} ", end="")
            for col in range(self.cols):
                cell = self.grid[row][col]
                
                if reveal_all:
                    # Show everything (debug mode)
                    if cell.is_mine:
                        print(f"{RED}*{RESET}", end=" ")
                    elif cell.adjacent_mines == 0:
                        print(f"{GRAY}_{RESET}", end=" ")
                    else:
                        color = number_colors.get(cell.adjacent_mines, RESET)
                        print(f"{color}{cell.adjacent_mines}{RESET}", end=" ")
                else:
                    # Show only what player can see
                    if cell.is_revealed():
                        if cell.is_mine:
                            print(f"{RED}{BOLD}*{RESET}", end=" ")
                        elif cell.adjacent_mines == 0:
                            print(f"{GRAY}_{RESET}", end=" ")
                        else:
                            color = number_colors.get(cell.adjacent_mines, RESET)
                            print(f"{color}{cell.adjacent_mines}{RESET}", end=" ")
                    elif cell.is_flagged():
                        print(f"{YELLOW}F{RESET}", end=" ")
                    else:
                        print(f"{GRAY}.{RESET}", end=" ")
            print(f" {GRAY}{row}{RESET}")
        
        # Column numbers again at bottom
        print("   ", end="")
        for col in range(self.cols):
            print(f"{GRAY}{col % 10}{RESET}", end=" ")
        print()
        print("=" * (self.cols * 2 + 3))
        print(f"Flags placed: {self.flags_placed}/{self.num_mines}")
        print()
