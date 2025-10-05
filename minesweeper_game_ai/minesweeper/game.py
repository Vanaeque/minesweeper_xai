import random
from enum import Enum, auto
import numpy as np

class CellState(Enum):
    HIDDEN = auto()
    REVEALED = auto()
    FLAGGED = auto()

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.state = CellState.HIDDEN
        self.adjacent_mines = 0

    def __repr__(self):
        if self.state == CellState.FLAGGED:
            return "F"
        if self.state == CellState.HIDDEN:
            return "."
        if self.is_mine:
            return "*"
        return str(self.adjacent_mines)

class Board:
    DX = [-1, -1, -1, 0, 0, 1, 1, 1]
    DY = [-1, 0, 1, -1, 1, -1, 0, 1]

    def __init__(self, rows=None, cols=None, num_mines=None, field_array=None):
        if field_array is not None:
            self.rows, self.cols = field_array.shape
            self.grid = [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]
            for r in range(self.rows):
                for c in range(self.cols):
                    self.grid[r][c].is_mine = bool(field_array[r, c])
            # if num_mines is not set, count it here
            if num_mines is None:
                num_mines = np.sum(field_array)
            self.num_mines = num_mines
        else:
            self.rows = rows
            self.cols = cols
            self.num_mines = num_mines
            self.grid = [[Cell(r, c) for c in range(cols)] for r in range(rows)]
            self._place_mines()

        self._compute_adjacency()

    def _place_mines(self):
        locations = random.sample(range(self.rows * self.cols), self.num_mines)
        for loc in locations:
            row = loc // self.cols
            col = loc % self.cols
            self.grid[row][col].is_mine = True

    def _compute_adjacency(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c].is_mine:
                    continue
                mines = 0
                for dx, dy in zip(Board.DX, Board.DY):
                    nr, nc = r + dx, c + dy
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if self.grid[nr][nc].is_mine:
                            mines += 1
                self.grid[r][c].adjacent_mines = mines

    def reveal(self, row, col):
        cell = self.grid[row][col]
        if cell.state == CellState.REVEALED or cell.state == CellState.FLAGGED:
            return
        cell.state = CellState.REVEALED
        if cell.is_mine:
            return "mine"
        if cell.adjacent_mines == 0:
            for dx, dy in zip(Board.DX, Board.DY):
                nr, nc = row + dx, col + dy
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.grid[nr][nc].state == CellState.HIDDEN:
                        self.reveal(nr, nc)
        return "safe"

    def flag(self, row, col):
        cell = self.grid[row][col]
        if cell.state == CellState.HIDDEN:
            cell.state = CellState.FLAGGED

    def unflag(self, row, col):
        cell = self.grid[row][col]
        if cell.state == CellState.FLAGGED:
            cell.state = CellState.HIDDEN

    def print_board(self, reveal_all=False):
        for r in range(self.rows):
            row_repr = ""
            for c in range(self.cols):
                cell = self.grid[r][c]
                if reveal_all:
                    if cell.is_mine:
                        row_repr += "* "
                    else:
                        row_repr += f"{cell.adjacent_mines} "
                else:
                    row_repr += f"{cell} "
            print(row_repr.strip())

    def is_finished(self):
        for row in self.grid:
            for cell in row:
                if not cell.is_mine and cell.state != CellState.REVEALED:
                    return False
        return True
    
    def to_numpy_bombs_safe(self):
        """
        Return a numpy array indicating bomb and safe cells:
        1: bomb
        0: safe (non-mine)
        """
        board_array = np.zeros((self.rows, self.cols), dtype=int)
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.is_mine:
                    board_array[r, c] = 1
                else:
                    board_array[r, c] = 0
        return board_array
    

    def to_numpy(self):
        """
        Return the board as a numpy array encoding current visible cell states:
        -1 : hidden
        -2 : flagged
        -3 : revealed mine
        0..8 : revealed cell with that many adjacent mines
        """
        board_array = np.full((self.rows, self.cols), -1, dtype=int)
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.state == CellState.HIDDEN:
                    board_array[r, c] = -1
                elif cell.state == CellState.FLAGGED:
                    board_array[r, c] = -2
                elif cell.state == CellState.REVEALED:
                    if cell.is_mine:
                        board_array[r, c] = -3
                    else:
                        board_array[r, c] = cell.adjacent_mines
        return board_array

class GameState(Enum):
    IN_PROGRESS = auto()
    WON = auto()
    LOST = auto()

class MinesweeperGame:
    def __init__(self, rows=None, cols=None, num_mines=None, field_array=None):
        """
        Initialization with either:
         - rows, cols, num_mines (random mine placement), or
         - field_array: numpy 2D array with 1=mine, 0=safe
        """
        self.board = Board(rows, cols, num_mines, field_array)
        self.state = GameState.IN_PROGRESS

    def play_move(self, row, col, flag=False):
        if self.state != GameState.IN_PROGRESS:
            return self.state
        if flag:
            self.board.flag(row, col)
        else:
            result = self.board.reveal(row, col)
            if result == "mine":
                self.state = GameState.LOST
            elif self.board.is_finished():
                self.state = GameState.WON
        return self.state

    def hint(self):

        board = self.board
        rows, cols = board.rows, board.cols

        for r in range(rows):
            for c in range(cols):
                cell = board.grid[r][c]
                if cell.state == CellState.REVEALED and cell.adjacent_mines > 0:
                    flagged = 0
                    hidden_neighbors = []
                    for dx, dy in zip(Board.DX, Board.DY):
                        nr, nc = r + dx, c + dy
                        if 0 <= nr < rows and 0 <= nc < cols:
                            neighbor = board.grid[nr][nc]
                            if neighbor.state == CellState.FLAGGED:
                                flagged += 1
                            elif neighbor.state == CellState.HIDDEN:
                                hidden_neighbors.append(neighbor)
                    if flagged == cell.adjacent_mines and hidden_neighbors:
                        safe_cell = hidden_neighbors[0]
                        result = board.reveal(safe_cell.row, safe_cell.col)
                        if result == "mine":
                            self.state = GameState.LOST
                        elif board.is_finished():
                            self.state = GameState.WON
                        return (safe_cell.row, safe_cell.col, result)
                    
        candidates = []
        for r in range(rows):
            for c in range(cols):
                cell = board.grid[r][c]
                if cell.state == CellState.HIDDEN:
                    candidates.append(cell)
        if candidates:
            chosen = random.choice(candidates)
            result = board.reveal(chosen.row, chosen.col)
            if result == "mine":
                self.state = GameState.LOST
            elif board.is_finished():
                self.state = GameState.WON
            return (chosen.row, chosen.col, result)

        return None
    
    def display(self, reveal_all=False):
        self.board.print_board(reveal_all=reveal_all)

