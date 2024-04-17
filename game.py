# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


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
  TOTAL = auto()

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


class Game:

  def __init__(self):
    self.board_size = 8
    self.board = [ [Piece(t_Piece.EMPTY) for _ in range(2)] for _ in range(self.board_size**2) ]
    self.n_players = 2
    self.current_player_indx = 0
    self.po_per_player = [8] * self.n_players

  def convert_xy_to_indx(self, x: int, y: int) -> int:
    """Converts (x,y) cordinates to an index on the board"""
    return x + y * self.board_size

  def print_board(self) -> None:
    """Renders the board to the console"""
    for i in range(self.board_size):
      for j in range(self.board_size):
        l,r = self.board[i * self.board_size + j]
        print(f"|{l.to_str()}{r.to_str()}|", end="")
      print()
    print()

  def check_valid_move(self, x: int, y: int, piece: Piece) -> bool:
    """I might want to invert the logic to make this more intuitive. is_valid starts as True and then is false if certain rules fail"""
    is_valid = False
    index = self.convert_xy_to_indx(x, y)
    # 1. move is within board
    if x < 0 or x >= self.board_size or y < 0 or y >= self.board_size:
      is_valid = True
    # 2. PEs and POs can only be placed in empty spaces
    if piece._typename != t_Piece.PI and self.board[index][1]._typename == t_Piece.EMPTY:
      is_valid = True
    # 3. PIs can only be placed within PEs
    if piece._typename == t_Piece.PI and self.board[index][1]._typename == t_Piece.PE:
      is_valid = True
    # 4. Player has PO's left to use
      # 4.1 Ensure piece is PO
      # 4.2 Ensure the PO space is empty
      # 4.3 Ensure the player has POs left to use
    if piece._typename == t_Piece.PO and self.board[index][1]._typename == t_Piece.EMPTY and self.po_per_player[self.current_player_indx] > 0:
      is_valid = True
    return is_valid

  def make_move(self, x: int, y: int, piece: Piece) -> None:
    """Places a piece on the board at the given x,y"""
    if not self.check_valid_move(x, y, piece): raise Exception(f"The move {piece._typename.name} to ({x},{y}) is not a valid move")
    index = self.convert_xy_to_indx(x, y)
    if piece._typename == t_Piece.PI:
      self.board[index][0] = piece
    else:
      self.board[index][1] = piece

  def rotate_player(self) -> None:
    """Rotates to the next player's turn"""
    self.current_player_indx = (self.current_player_indx + 1) % self.n_players

  def check_winner(self) -> bool:
    """Returns True if the current player has won, False otherwise.
    To win, the player must have 5 pieces in a row diagnolly, horizontally, or vertically.
    Also, a space with a PE and a PI count for both players
    TODO: UNIT TESTS!!!!
    """
    
    def check_current_player_in_space(space: list[Piece, Piece]):
      return space[0].player_indx == self.current_player_indx or space[1].player_indx == self.current_player_indx
      
    magic_number = 5

    # check horizontal
    for y in range(self.board_size):
      for x in range(magic_number-1): # TODO: update to self.board_size - magin_number + 1
        index = self.convert_xy_to_indx(x, y)
        board_spaces = [self.board[index+w] for w in range(magic_number)]
        if all(check_current_player_in_space(bs) for bs in board_spaces):
          return True
    # check vertical
    for x in range(self.board_size):
      for y in range(magic_number-1): # TODO: update to self.board_size - magin_number + 1
        index = self.convert_xy_to_indx(x, y)
        board_spaces = [self.board[index + self.board_size * w] for w in range(magic_number)]
        if all(check_current_player_in_space(bs) for bs in board_spaces):
          return True
    # check tl-br diagonal
    for y in range(self.board_size - magic_number + 1):
      for x in range(self.board_size - magic_number + 1):
        index = self.convert_xy_to_indx(x, y)
        board_spaces = [self.board[index + (self.board_size + 1) * w] for w in range(magic_number)]
        if all(check_current_player_in_space(bs) for bs in board_spaces):
          return True
    # check tr-bl diagonal
    for y in range(magic_number - 1, self.board_size):
      for x in range(self.board_size - magic_number + 1):
        index = self.convert_xy_to_indx(x, y)
        board_spaces = [self.board[index - (self.board_size - 1) * w] for w in range(magic_number)]
        if all(check_current_player_in_space(bs) for bs in board_spaces):
          return True
    return False



if __name__ == "__main__":

  g = Game()
  g.print_board()
  while True:
    print(f"Player {g.current_player_indx}'s turn")
    # get player input
    y, x = tuple(map(int, input(f"Enter the row and column seperated by a space (EX: 1 4): ").split(" ")))
    piece_type = int(input("Enter piece type (0=PI, 1=PE, 2=PO): "))
    # place piece on board
    g.make_move(
      int(x), int(y), 
      Piece(t_Piece(piece_type+1), 
            player_indx=g.current_player_indx, 
            color=Colors.MAGENTA if g.current_player_indx == 0 else Colors.GREEN))
    g.print_board()
    # check for winner
    if g.check_winner():
      print(f"Player {g.current_player_indx} wins!")
      break
    # rotate to next player
    g.rotate_player()

