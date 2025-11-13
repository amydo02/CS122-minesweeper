from enum import Enum
import time
from .board import Board, Difficulty

class GameStatus(Enum):
    NOT_STARTED = 0
    PLAYING = 1
    WON = 2
    LOST = 3

class GameState:
    """Manages overall game state."""
    
    def __init__(self, difficulty: dict):
        self.board = Board(difficulty)
        self.status = GameStatus.NOT_STARTED
        self.start_time = None
        self.end_time = None
        self.elapsed_time = 0
        self.hints_used = 0
        self.max_hints = 3
        self.difficulty = difficulty
        self.score = 0
    
    def start_game(self):
        """Starts the game timer."""
        if self.status == GameStatus.NOT_STARTED:
            self.status = GameStatus.PLAYING
            self.start_time = time.time()
    
    def get_elapsed_time(self) -> float:
        """Returns elapsed time in seconds."""
        if self.status == GameStatus.PLAYING and self.start_time:
            return time.time() - self.start_time
        elif self.end_time:
            return self.end_time - self.start_time
        return 0
    
    def use_hint(self) -> bool:
        """Uses a hint. Returns True if successful."""
        if self.hints_used >= self.max_hints:
            return False
        
        safe_cells = self.board.get_safe_unrevealed_cells()
        if not safe_cells:
            return False
        
        # Reveal a random safe cell
        import random
        row, col = random.choice(safe_cells)
        self.board.reveal_cell(row, col)
        self.hints_used += 1
        return True
    
    def click_cell(self, row: int, col: int):
        """Handles left click on a cell."""
        if self.status not in [GameStatus.NOT_STARTED, GameStatus.PLAYING]:
            return
        
        if self.status == GameStatus.NOT_STARTED:
            self.start_game()
        
        hit_mine = self.board.reveal_cell(row, col)
        
        if hit_mine:
            self.end_game(won=False)
        elif self.board.check_win():
            self.end_game(won=True)
    
    def flag_cell(self, row: int, col: int):
        """Handles right click (flag) on a cell."""
        if self.status == GameStatus.PLAYING:
            self.board.toggle_flag(row, col)
    
    def end_game(self, won: bool):
        """Ends the game."""
        self.status = GameStatus.WON if won else GameStatus.LOST
        self.end_time = time.time()
        self.elapsed_time = self.get_elapsed_time()
        
        if not won:
            self.board.reveal_all_mines()
        
        # Calculate score
        self.calculate_score()
    
    def calculate_score(self):
        """Calculates final score based on time and hints."""
        if self.status == GameStatus.WON:
            time_bonus = max(0, 1000 - int(self.elapsed_time))
            hint_penalty = self.hints_used * 50
            difficulty_multiplier = {
                "Beginner": 1,
                "Intermediate": 2,
                "Advanced": 3
            }.get(self.difficulty["name"], 1)
            
            self.score = max(0, (time_bonus - hint_penalty) * difficulty_multiplier)
        else:
            self.score = 0
    
    def reset(self):
        """Resets the game with same difficulty."""
        self.__init__(self.difficulty)