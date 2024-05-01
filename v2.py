# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import pytest



class Colors:
  BLACK = '\033[30m'
  RED = '\033[31m'
  GREEN = '\033[32m'
  YELLOW = '\033[33m'
  BLUE = '\033[34m'
  MAGENTA = '\033[35m'
  CYAN = '\033[36m'
  WHITE = '\033[37m'
  UNDERLINE = '\033[4m'
  RESET = '\033[0m'


class t_Piece(Enum):
  EMPTY = 0
  PI = 1
  PE = 2
  PO = 3


@dataclass
class Piece:
  _typename: t_Piece
  player_indx: Optional[int] = -1
  color: Optional[Colors] = ""

  def to_str(self) -> str:
    match self._typename:
      case t_Piece.EMPTY:
        return self.color + "E" + Colors.RESET
      case t_Piece.PI:
        return self.color + "." + Colors.RESET
      case t_Piece.PE:
        return self.color + "O" + Colors.RESET
      case t_Piece.PO:
        return self.color + "0" + Colors.RESET
      case _:
        return self.color + "?" + Colors.RESET


class Board:
  def __init__(self, n_players: int = 2):  
    self.n_players = n_players
    self.board_size = 8
    self.board = []  
    self.empty_board()
  
  def empty_board(self) -> None:
    self.board = [ [Piece(t_Piece.EMPTY) for _ in range(self.n_players)] for _ in range(self.board_size**self.n_players) ]
  
  def convert_xy_to_indx(self, x: int, y: int) -> int:
    """Converts (x,y) cordinates to an index on the board"""
    return x + y * self.board_size
  
  def __setitem__(self, key, value):
    x, y = key
    indx = self.convert_xy_to_indx(x, y)
    if isinstance(value, list):
      self.board[indx] = value
    elif isinstance(value, Piece):
      # pi's go on the left and everything else
      # on the right for rendering purposes
      if value._typename == t_Piece.PI:
        self.board[indx][0] = value
      else:
        self.board[indx][1] = value
  
  def __getitem__(self, key):
    x, y = key
    index = self.convert_xy_to_indx(x, y)
    return self.board[index]
  
  def __repr__(self) -> str:
    """Renders the board to the console"""
    tmp = "   |0 ||1 ||2 ||3 ||4 ||5 ||6 || 7|\n\n"
    for y in reversed(range(self.board_size)):  # Iterate in reverse for correct orientation
        tmp += f"{y}| "
        for x in range(self.board_size):
          indx = self.convert_xy_to_indx(x, y)
          l, r = self.board[indx]
          tmp += f"|{l.to_str()}{r.to_str()}|"
        tmp += "\n"
    tmp += "\n"
    return tmp


class Game:

  def __init__(self, n_players: int = 2):
    self.n_players = 2
    self.current_player_indx = 0 # TODO: Should be random
    self.board = Board(self.n_players)
    self.max_pos_per_player = 8
    self.po_per_player = [self.max_pos_per_player] * self.n_players
    self.n_pieces_in_a_row_to_win = 5 # Need to get 5 in a row to win

  def play(self) -> None:
    return
  
  def validate_move(self, x: int, y: int, piece: Piece) -> bool:
    """Returns true if the move is valid.
    1. PE's and PO's can only be placed in empty spaces.
    2. PI's can only be placed within PE's.
    3. Player has not used all 8 of their PO's.
    4. Move is within the board.
    """
    is_valid = False
    # 1. PEs and POs can only be placed in empty spaces
    if (piece._typename == t_Piece.PE or piece._typename == t_Piece.PO) and self.board[x, y][1]._typename == t_Piece.EMPTY:
      is_valid = True
    # 2. PIs can only be placed within PEs
    if piece._typename == t_Piece.PI and self.board[x, y][1]._typename == t_Piece.PE:
      is_valid = True
    # 3. Player has not used all 8 of their PO's
    if piece._typename == t_Piece.PO and self.po_per_player[self.current_player_indx] > 0:
      is_valid = True
    # 4. Move is within the board
    if x < 0 or x >= self.board.board_size or y < 0 or y >= self.board.board_size:
      is_valid = False
    return is_valid

  def make_move(self, x: int, y: int, piece: Piece) -> bool:
    """Places a piece on the board."""
    if not self.validate_move(x, y, piece): return False
    self.board[x, y] = piece
    return True
    
  def rotate_player(self) -> None:
    """Rotates to the next player's turn."""
    self.current_player_indx = (self.current_player_indx + 1) % self.n_players

  def check_tie(self) -> bool:
    """Returns True if there is no more valid moves, False if not.
    There is a tie game if there are no more valid moves left on the board.
    """
    for x in range(self.board.board_size):
        for y in range(self.board.board_size):
            for p in (t_Piece.PE, t_Piece.PI, t_Piece.PO):
                if self.validate_move(x, y, Piece(p, player_indx=self.current_player_indx)):
                    return False
    return True
    
    
  def check_winner(self) -> bool:
    """Returns True if the current player has won, False if not.
    To win, the player must have 5 pieces in a row diagonally, horizontally, or vertically.
    Also, a space with a PE and a PI count for both players.
    """
    def check_current_player_in_space(space: list[Piece, Piece]):
        return space[0].player_indx == self.current_player_indx or space[1].player_indx == self.current_player_indx
  
    def check_diagonal(start_x: int, start_y: int, dx: int, dy: int) -> bool:
        """Checks a diagonal starting from (start_x, start_y) in direction (dx, dy)."""
        diagonal_pieces = [self.board[start_x + i*dx, start_y + i*dy] for i in range(self.n_pieces_in_a_row_to_win)]
        return all(check_current_player_in_space(dp) for dp in diagonal_pieces)
  
    # Check horizontal
    for y in range(self.board.board_size):
        for x in range(self.board.board_size - self.n_pieces_in_a_row_to_win + 1):
            board_spaces = [self.board[x+w, y] for w in range(self.n_pieces_in_a_row_to_win)]
            if all(check_current_player_in_space(bs) for bs in board_spaces):
                return True
  
    # Check vertical
    for x in range(self.board.board_size):
        for y in range(self.board.board_size - self.n_pieces_in_a_row_to_win + 1):
            board_spaces = [self.board[x, y+w] for w in range(self.n_pieces_in_a_row_to_win)]
            if all(check_current_player_in_space(bs) for bs in board_spaces):
                return True
  
    # Check diagonals (top-left to bottom-right)
    for y in range(self.board.board_size - self.n_pieces_in_a_row_to_win + 1):
        for x in range(self.board.board_size - self.n_pieces_in_a_row_to_win + 1):
            if check_diagonal(x, y, 1, 1):
                return True
  
    # Check diagonals (top-right to bottom-left)
    for y in range(self.n_pieces_in_a_row_to_win - 1, self.board.board_size):
        for x in range(self.board.board_size - self.n_pieces_in_a_row_to_win + 1):
            if check_diagonal(x, y, 1, -1):
                return True
    return False



@pytest.fixture
def game():
    return Game()

# mark: game
def test_check_winner(game: Game):
    game.current_player_indx = 1

    print()

    assert not game.check_winner(), "Detected win when the board was empty"

    # Test horizontal
    for y in range(game.board.board_size):
        for x in range(game.board.board_size - game.n_pieces_in_a_row_to_win):
            for w in range(game.n_pieces_in_a_row_to_win+1):
                game.make_move(x+w, y, Piece(t_Piece.PE, player_indx=game.current_player_indx, color=Colors.BLUE))

            assert game.check_winner(), "Could not detect horizontal win"
            game.board.empty_board()

    # Test vertical
    for x in range(game.board.board_size):
        for y in range(game.board.board_size - game.n_pieces_in_a_row_to_win):
            for w in range(game.n_pieces_in_a_row_to_win+1):
                game.make_move(x, y+w, Piece(t_Piece.PE, player_indx=game.current_player_indx, color=Colors.BLUE))

            assert game.check_winner(), "Could not detect horizontal win"
            game.board.empty_board()


    # Test diagonal (top-left to bottom-right)
    for y in range(game.board.board_size - game.n_pieces_in_a_row_to_win + 1):
        for x in range(game.board.board_size - game.n_pieces_in_a_row_to_win + 1):
            for i in range(game.n_pieces_in_a_row_to_win):
                game.make_move(i, i, Piece(t_Piece.PE, player_indx=game.current_player_indx, color=Colors.MAGENTA))

            print(game.board)
            assert game.check_winner(), "Could not detect diagonal (top-left to bottom-right) win"
            game.board.empty_board()


#     # Test diagonal (top-right to bottom-left)
#     for i in range(game.n_pieces_in_a_row_to_win):
#         game.make_move(game.n_pieces_in_a_row_to_win - 1 - i, i, Piece(t_Piece.PE, player_indx=game.current_player_indx, color=Colors.GREEN))

#     assert game.check_winner(), "Could not detect diagonal (top-right to bottom-left) win"
#     print(game.board)



# """
# # mark: Game logic / rules

# -  [x] a player can win in any direction
#     - [ ] a player can cross over another player with a pi and win
# - [ ] pis can only be placed in a spot with a empty pe
# - [ ] pes can only be placed in empty spots
# - [ ] pos can only be placed in empty spots
# - [ ] only 8 pos per player
# - [ ] game ends in a tie when there are no more valid spots left
# """

