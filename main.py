"""
Text-Based Minesweeper Game
Play Minesweeper in the terminal without GUI!
"""

import sys
import os
from typing import Optional

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.game.board import Board, Difficulty
from src.game.game_state import GameState, GameStatus


class TextMinesweeper:
    """Text-based Minesweeper game."""
    
    def __init__(self):
        self.game_state: Optional[GameState] = None
        self.running = True
    
    def print_title(self):
        """Print game title."""
        print("\n" + "="*50)
        print(" MINESWEEPER ")
        print("="*50)
    
    def select_difficulty(self) -> dict:
        """Let player select difficulty."""
        print("\nSELECT DIFFICULTY:")
        print("1. Beginner     (9x9,   10 mines) - Easy")
        print("2. Intermediate (16x16, 40 mines) - Medium")
        print("3. Advanced     (25x25, 99 mines) - Hard")
        print("4. Custom       (Your own settings)")
        
        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                return Difficulty.BEGINNER
            elif choice == "2":
                return Difficulty.INTERMEDIATE
            elif choice == "3":
                return Difficulty.ADVANCED
            elif choice == "4":
                try:
                    rows = int(input("Enter rows: "))
                    cols = int(input("Enter columns: "))
                    mines = int(input("Enter number of mines: "))
                    
                    if rows < 3 or cols < 3:
                        print("Board must be at least 3x3!")
                        continue
                    
                    if mines >= rows * cols:
                        print("Too many mines!")
                        continue
                    
                    return {"rows": rows, "cols": cols, "mines": mines, "name": "Custom"}
                except ValueError:
                    print("Invalid input! Please enter numbers.")
            else:
                print("Invalid choice! Please enter 1-4.")
    
    def print_help(self):
        """Print game instructions."""
        print("\n" + "─"*70)
        print("📖 HOW TO PLAY:")
        print("─"*70)
        print("  Commands:")
        print("    r <row> <col>  - Reveal a cell")
        print("    f <row> <col>  - Toggle flag on a cell")
        print("    h              - Use a hint (reveals safe cell)")
        print("    show           - Show the board")
        print("    stats          - Show game statistics")
        print("    help           - Show this help")
        print("    quit           - Quit the game")
        print()
        print("  Legend:")
        print("    .  = Hidden cell")
        print("    F  = Flagged cell (you think there's a mine)")
        print("    *  = Mine (you lose if you see this!)")
        print("    _  = Empty cell (no adjacent mines)")
        print("    1-8 = Number of adjacent mines")
        print()
        print("  Goal: Reveal all safe cells without hitting any mines!")
        print("─"*70 + "\n")
    
    def print_game_stats(self):
        """Print current game statistics."""
        if not self.game_state:
            return
        
        board = self.game_state.board
        
        revealed = sum(1 for row in board.grid 
                      for cell in row if cell.is_revealed())
        total_safe = board.rows * board.cols - board.num_mines
        progress = (revealed / total_safe * 100) if total_safe > 0 else 0
        
        print(f"\nGAME STATISTICS:")
        print(f"   Time: {int(self.game_state.get_elapsed_time())}s")
        print(f"   Mines: {board.num_mines}")
        print(f"   Flags: {board.flags_placed}/{board.num_mines}")
        print(f"   Hints: {self.game_state.hints_used}/{self.game_state.max_hints}")
        print(f"   Progress: {revealed}/{total_safe} cells ({progress:.1f}%)")
        print()
    
    def play_game(self):
        """Main game loop."""
        # Select difficulty
        difficulty = self.select_difficulty()
        
        # Create game state
        self.game_state = GameState(difficulty)
        board = self.game_state.board
        
        print(f"\nGame created! {difficulty['name']} mode")
        print(f"   Board size: {board.rows}x{board.cols}")
        print(f"   Mines: {board.num_mines}")
        
        self.print_help()
        
        # Show initial board
        board.print_board(reveal_all=False)
        
        # Game loop
        while self.running and self.game_state.status in [GameStatus.NOT_STARTED, GameStatus.PLAYING]:
            try:
                # Get command
                command = input(">>> ").strip().lower().split()
                
                if not command:
                    continue
                
                cmd = command[0]
                
                # Process command
                if cmd in ["quit", "q", "exit"]:
                    print("\nThanks for playing! Goodbye!")
                    self.running = False
                    break
                
                elif cmd in ["help", "?"]:
                    self.print_help()
                
                elif cmd in ["show", "s"]:
                    board.print_board(reveal_all=False)
                
                elif cmd == "stats":
                    self.print_game_stats()
                
                elif cmd in ["hint", "h"]:
                    if self.game_state.use_hint():
                        print(f"💡 Hint used! ({self.game_state.hints_used}/{self.game_state.max_hints})")
                        board.print_board(reveal_all=False)
                    else:
                        if self.game_state.hints_used >= self.game_state.max_hints:
                            print("No hints remaining!")
                        else:
                            print("No safe cells to reveal!")
                
                elif cmd in ["r", "reveal", "click"]:
                    if len(command) < 3:
                        print(" Usage: r <row> <col>")
                        print("   Example: r 0 0")
                        continue
                    
                    try:
                        row = int(command[1])
                        col = int(command[2])
                        
                        # Check bounds
                        if not (0 <= row < board.rows and 0 <= col < board.cols):
                            print(f"Invalid position! Row must be 0-{board.rows-1}, Col must be 0-{board.cols-1}")
                            continue
                        
                        # Check if already revealed
                        if board.grid[row][col].is_revealed():
                            print("Cell already revealed!")
                            continue
                        
                        # Check if flagged
                        if board.grid[row][col].is_flagged():
                            print("Cell is flagged! Remove flag first with: f {row} {col}")
                            continue
                        
                        # Reveal the cell
                        self.game_state.click_cell(row, col)
                        
                        # Show board
                        board.print_board(reveal_all=False)
                        
                        # Check game status
                        if self.game_state.status == GameStatus.LOST:
                            self.handle_game_over(won=False)
                            break
                        elif self.game_state.status == GameStatus.WON:
                            self.handle_game_over(won=True)
                            break
                        else:
                            revealed = sum(1 for r in board.grid 
                                         for c in r if c.is_revealed())
                            print(f"Revealed ({row}, {col}) - Total: {revealed} cells")
                    
                    except (ValueError, IndexError):
                        print("Invalid coordinates! Use numbers.")
                        print("   Example: r 0 0")
                
                elif cmd in ["f", "flag"]:
                    if len(command) < 3:
                        print("Usage: f <row> <col>")
                        print("   Example: f 0 0")
                        continue
                    
                    try:
                        row = int(command[1])
                        col = int(command[2])
                        
                        # Check bounds
                        if not (0 <= row < board.rows and 0 <= col < board.cols):
                            print(f"Invalid position! Row must be 0-{board.rows-1}, Col must be 0-{board.cols-1}")
                            continue
                        
                        # Check if already revealed
                        if board.grid[row][col].is_revealed():
                            print(" Cannot flag a revealed cell!")
                            continue
                        
                        # Toggle flag
                        self.game_state.flag_cell(row, col)
                        
                        # Show board
                        board.print_board(reveal_all=False)
                        
                        if board.grid[row][col].is_flagged():
                            print(f"Flagged ({row}, {col}) - Total flags: {board.flags_placed}")
                        else:
                            print(f" Unflagged ({row}, {col}) - Total flags: {board.flags_placed}")
                    
                    except (ValueError, IndexError):
                        print("Invalid coordinates! Use numbers.")
                        print("   Example: f 0 0")
                
                else:
                    print(f"Unknown command: '{cmd}'")
                    print("   Type 'help' for list of commands")
            
            except KeyboardInterrupt:
                print("\n\nGame interrupted! Goodbye!")
                self.running = False
                break
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
    
    def handle_game_over(self, won: bool):
        """Handle game over state."""
        board = self.game_state.board
        
        if won:
            print("\n" + "="*70)
            print("!!! CONGRATULATIONS! YOU WIN! !!!")
            print("="*70)
            print(f" Time: {int(self.game_state.elapsed_time)} seconds")
            print(f"Hints used: {self.game_state.hints_used}")
            print(f"Score: {self.game_state.score}")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("GAME OVER! YOU HIT A MINE! ")
            print("="*70)
            print(f" Time survived: {int(self.game_state.elapsed_time)} seconds")
            print(f" Hints used: {self.game_state.hints_used}")
            print("\nHere's where all the mines were:")
            print("="*70)
            board.print_board(reveal_all=True)
        
        # Ask to play again
        while True:
            choice = input("\nPlay again? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                print("\n" + "="*70 + "\n")
                self.play_game()
                break
            elif choice in ['n', 'no']:
                print("\n👋 Thanks for playing! Goodbye!")
                self.running = False
                break
            else:
                print("Please enter 'y' or 'n'")
    
    def run(self):
        """Start the game."""
        self.print_title()
        self.play_game()


def main():
    """Main entry point."""
    try:
        game = TextMinesweeper()
        game.run()
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted! Goodbye!")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()