from enum import Enum

class CellState(Enum):
    HIDDEN = 0
    REVEALED = 1
    FLAGGED = 2

class Cell:
    """Represents a single cell in the Minesweeper grid."""
    
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.is_mine = False
        self.adjacent_mines = 0
        self.state = CellState.HIDDEN
        
    def reveal(self) -> bool:
        """Reveals the cell. Returns True if it was a mine."""
        if self.state == CellState.FLAGGED:
            return False
        self.state = CellState.REVEALED
        return self.is_mine
    
    def toggle_flag(self) -> bool:
        """Toggles flag state. Returns True if flagged."""
        if self.state == CellState.REVEALED:
            return False
        
        if self.state == CellState.HIDDEN:
            self.state = CellState.FLAGGED
            return True
        else:
            self.state = CellState.HIDDEN
            return False
    
    def is_revealed(self) -> bool:
        return self.state == CellState.REVEALED
    
    def is_flagged(self) -> bool:
        return self.state == CellState.FLAGGED
    
    def __repr__(self):
        return f"Cell({self.row},{self.col},mine={self.is_mine},adj={self.adjacent_mines})"