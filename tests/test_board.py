import unittest
from src.game.board import Board, Difficulty
from src.game.cell import CellState

class TestBoard(unittest.TestCase):
    """Tests for Board class."""
    
    def setUp(self):
        """Set up test board."""
        self.board = Board(Difficulty.BEGINNER)
    
    def test_board_initialization(self):
        """Test board is initialized correctly."""
        self.assertEqual(self.board.rows, 9)
        self.assertEqual(self.board.cols, 9)
        self.assertEqual(self.board.num_mines, 10)
        self.assertTrue(self.board.first_click)
    
    def test_mine_placement(self):
        """Test mines are placed correctly."""
        self.board.place_mines(0, 0)
        
        # Should have exactly num_mines mines
        mine_count = sum(1 for row in self.board.grid 
                        for cell in row if cell.is_mine)
        self.assertEqual(mine_count, self.board.num_mines)
        
        # First click position should be safe
        self.assertFalse(self.board.grid[0][0].is_mine)
    
    def test_adjacent_mine_calculation(self):
        """Test adjacent mine counts are correct."""
        self.board.place_mines(0, 0)
        
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                cell = self.board.grid[row][col]
                if not cell.is_mine:
                    # Manually count adjacent mines
                    neighbors = self.board._get_neighbors(row, col)
                    actual_count = sum(1 for r, c in neighbors 
                                     if self.board.grid[r][c].is_mine)
                    self.assertEqual(cell.adjacent_mines, actual_count)
    
    def test_reveal_cell(self):
        """Test cell revealing."""
        self.board.place_mines(4, 4)
        
        # Reveal a safe cell
        hit_mine = self.board.reveal_cell(0, 0)
        self.assertFalse(hit_mine)
        self.assertTrue(self.board.grid[0][0].is_revealed())
    
    def test_recursive_reveal(self):
        """Test empty cells reveal recursively."""
        # Create a small custom board where we control mine placement
        small_board = Board({"rows": 5, "cols": 5, "mines": 1, "name": "Small"})
    
        # Manually place mine in corner, far from center
        small_board.grid[0][0].is_mine = True
        small_board.mines_positions.add((0, 0))
        small_board._calculate_adjacent_mines()
        small_board.first_click = False
    
        # Reveal cell at (4, 4) - should trigger recursive reveal
        small_board.reveal_cell(4, 4)
    
        # Many cells should be revealed due to recursion
        revealed_count = sum(1 for row in small_board.grid 
                        for cell in row if cell.is_revealed())
    
        self.assertGreater(revealed_count, 1, 
                      "Revealing empty cell should trigger recursive reveal")
    
    def test_flag_toggle(self):
        """Test flag toggling."""
        cell = self.board.grid[0][0]
        
        # Flag the cell
        self.board.toggle_flag(0, 0)
        self.assertTrue(cell.is_flagged())
        self.assertEqual(self.board.flags_placed, 1)
        
        # Unflag the cell
        self.board.toggle_flag(0, 0)
        self.assertFalse(cell.is_flagged())
        self.assertEqual(self.board.flags_placed, 0)
    
    def test_win_condition(self):
        """Test win detection."""
        # Create a minimal board for testing
        self.board = Board({"rows": 3, "cols": 3, "mines": 1, "name": "Test"})
        self.board.place_mines(2, 2)
        
        # Reveal all non-mine cells
        for row in range(3):
            for col in range(3):
                if not self.board.grid[row][col].is_mine:
                    self.board.grid[row][col].reveal()
        
        self.assertTrue(self.board.check_win())

if __name__ == '__main__':
    unittest.main()
