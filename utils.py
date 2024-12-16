import numpy as np
from game import Game, PIECES, PIECE_STR, PLAYER_COLORS, COLORS
from typing import Tuple
from copy import deepcopy


def check_sequence(game: Game, player: int, length: int) -> bool:
    """Returns true if the player has a sequence of pieces the given length"""
    sb = np.logical_or.reduce([
        game.board[:, :, PIECES.PE] == player,
        game.board[:, :, PIECES.PI] == player,
        game.board[:, :, PIECES.PO] == player,
    ]).astype(bool)

    for r in range(game.board_size):
        for c in range(game.board_size-(length-1)):
            if np.all(sb[r, c:c+length]):
                return True
    for c in range(game.board_size):
        for r in range(game.board_size-(length-1)):
            if np.all(sb[r, c:c+length]):
                return True
    for r in range(game.board_size-(length-1)):
        for c in range(game.board_size-(length-1)):
            if np.all([sb[r + i, c + i] for i in range(length)]):
                return True
    for r in range(game.board_size-(length-1)):
        for c in range(length-1, game.board_size):
            if np.all([sb[r + i, c - i] for i in range(length)]):
                return True
    return False



def get_max_sequence(game: Game, player: int) -> int:
    """
    Finds the longest sequence of pieces for a given player and returns the length
    """
    board = game.board
    # Combine PE, PI, and PO layers for the player
    seq_board = np.logical_or.reduce([
        board[:, :, PIECES.PE] == player, 
        board[:, :, PIECES.PI] == player,
        board[:, :, PIECES.PO] == player
    ]).astype(int)

    max_sequence = 0

    # Check horizontal sequences
    for row in range(game.board_size):
        current_sequence = 0
        for col in range(game.board_size):
            if seq_board[row, col] == 1:
                current_sequence += 1
                max_sequence = max(max_sequence, current_sequence)
            else:
                current_sequence = 0

    # Check vertical sequences
    for col in range(game.board_size):
        current_sequence = 0
        for row in range(game.board_size):
            if seq_board[row, col] == 1:
                current_sequence += 1
                max_sequence = max(max_sequence, current_sequence)
            else:
                current_sequence = 0

    # Check diagonal sequences (both directions)
    # Down-right diagonals
    for start_row in range(game.board_size):
        for start_col in range(game.board_size):
            current_sequence = 0
            row, col = start_row, start_col
            while row < game.board_size and col < game.board_size:
                if seq_board[row, col] == 1:
                    current_sequence += 1
                    max_sequence = max(max_sequence, current_sequence)
                else:
                    current_sequence = 0
                row += 1
                col += 1

    # Up-right diagonals
    for start_row in range(game.board_size):
        for start_col in range(game.board_size):
            current_sequence = 0
            row, col = start_row, start_col
            while row >= 0 and col < game.board_size:
                if seq_board[row, col] == 1:
                    current_sequence += 1
                    max_sequence = max(max_sequence, current_sequence)
                else:
                    current_sequence = 0
                row -= 1
                col += 1

    return max_sequence


def does_spot_contain_player(game: Game, row: int, col: int, player: int) -> bool:
    """returns true if the spot contains a piece owned by the given player"""
    return player in [game.board[row, col, PIECES.PE], game.board[row, col, PIECES.PI], game.board[row, col, PIECES.PO]] 


def is_spot_empty(game: Game, row: int, col: int) -> bool:
    """returns true if the spot is empty"""
    return all(game.board[row, col, :] == PIECES.EMPTY)


def get_valid_moves(game: Game, player: int) -> list[int, int, PIECES]:
    """list of valid moves [(row, col, piece), ...]"""
    valid_moves = []
    for r in range(game.board_size):
        for c in range(game.board_size):
            for p in [PIECES.PE, PIECES.PI, PIECES.PO]:
                if game.validate_move(r, c, p, player):
                    valid_moves.append((r, c, p))
    return valid_moves


def count_sequences(game: Game, player: int, length: int) -> int:
    def check_sequence(row, col, dr, dc):
        count = 0
        for i in range(length):
            r, c = row + i*dr, col + i*dc
            if not (0 <= r < game.board_size and 0 <= c < game.board_size):
                return False
            if game.board[r, c, PIECES.PE] == player or game.board[r, c, PIECES.PI] or game.board[r, c, PIECES.PO]:
                count += 1
        return count == length
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    sequence_count = 0

    for row in range(game.board_size):
        for col in range(game.board_size):
            for dr, dc in directions:
                if check_sequence(row, col, dr, dc):
                    sequence_count += 1

    return sequence_count


def colorize(msg: str, color: str = "green") -> str:
    """green, red, blue, cyan, white"""
    s = ""
    match color.lower():
        case "green":
            s = "\033[32m" + msg
        case "red":
            s = "\033[31m" + msg
        case "blue":
            s = "\033[34m" + msg
        case "cyan":
            s = "\033[96m" + msg
        case "white":
            s = "\033[97m" + msg
        case _:
            raise ValueError(f"{color} is not a supported color")
    s += "\033[0m"
    return s


p1_print = lambda msg, **print_args: print(colorize(msg, "green"), **print_args)
p2_print = lambda msg, **print_args: print(colorize(msg, "blue"), **print_args)


def is_winning_move(game: Game, row: int, col: int, piece: PIECES, player: int) -> bool:
    g = deepcopy(game)
    g.make_move(row, col, piece, player)
    return g.check_win(player)

def is_blocking_move(game: Game, row: int, col: int, piece: PIECES, player: int) -> bool:
    other_player = 1 if player == 2 else 2
    # if other player places any valid piece there and wins then this is a blocking move (if )
    ...