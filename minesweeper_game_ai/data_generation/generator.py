import os
import numpy as np
print(os.getcwd())

from minesweeper_game_ai.minesweeper.game import MinesweeperGame, GameState, CellState

from minesweeper_game_ai.minesweeper.game import MinesweeperGame, GameState, CellState
import numpy as np

def generate_data(num_samples, rows=9, cols=9, num_mines=10, max_hint_steps=10):
    """
    Generate dataset of Minesweeper states by applying hint method steps.
    Saves the board state after each move along with statistics.

    Returns a list of dicts with keys:
     - 'step_allowed': numpy array with ones where stepping is allowed (hidden safe cells)
     - 'bombs': numpy array with ones on bombs
     - 'revealed': numpy array with ones on revealed cells
     - 'observable_state': numpy array showing current visible board state (numbers, hidden cells, flags)
     - 'total_bombs': total bombs on board
     - 'bombs_revealed': bombs revealed (0 or 1 if game ended)
     - 'moves_made': how many hint steps applied
     - 'game_over': whether the game ended
    """
    data = []

    for i in range(num_samples):
        game = MinesweeperGame(rows, cols, num_mines)
        moves = 0
        bombs_revealed = 0
        game_over = False

        while moves < max_hint_steps[i] and not game_over:
            hint_move = game.hint()
            if hint_move is None:
                break
            r, c, result = hint_move
            moves += 1
            if result == "mine":
                bombs_revealed = 1
                game_over = True

            # Generate arrays at current state
            step_allowed = np.zeros((rows, cols), dtype=np.float32)
            bombs = np.zeros((rows, cols), dtype=np.float32)
            revealed = np.zeros((rows, cols), dtype=np.float32)

            for i in range(rows):
                for j in range(cols):
                    cell = game.board.grid[i][j]
                    if cell.is_mine:
                        bombs[i, j] = 1.0
                    if cell.state == CellState.REVEALED:
                        revealed[i, j] = 1.0
                    if cell.state == CellState.HIDDEN and not cell.is_mine:
                        step_allowed[i, j] = 1.0

            # Capture observable board state after this move
            observable_state = game.board.to_numpy()

            data.append({
                'step_allowed': step_allowed.copy(),
                'bombs': bombs.copy(),
                'revealed': revealed.copy(),
                'observable_state': observable_state.copy(),
                'total_bombs': num_mines,
                'bombs_revealed': bombs_revealed,
                'moves_made': moves,
                'game_over': game.state != GameState.IN_PROGRESS
            })

        # Optionally save last state if no moves or incomplete game
        if moves == 0 or (not game_over and moves < max_hint_steps):
            step_allowed = np.zeros((rows, cols), dtype=np.float32)
            bombs = np.zeros((rows, cols), dtype=np.float32)
            revealed = np.zeros((rows, cols), dtype=np.float32)
            for i in range(rows):
                for j in range(cols):
                    cell = game.board.grid[i][j]
                    if cell.is_mine:
                        bombs[i, j] = 1.0
                    if cell.state == CellState.REVEALED:
                        revealed[i, j] = 1.0
                    if cell.state == CellState.HIDDEN and not cell.is_mine:
                        step_allowed[i, j] = 1.0
            observable_state = game.board.to_numpy()
            data.append({
                'step_allowed': step_allowed.copy(),
                'bombs': bombs.copy(),
                'revealed': revealed.copy(),
                'observable_state': observable_state.copy(),
                'total_bombs': num_mines,
                'bombs_revealed': bombs_revealed,
                'moves_made': moves,
                'game_over': game.state != GameState.IN_PROGRESS
            })

    return data

