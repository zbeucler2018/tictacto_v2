import numpy as np
from game import Game, PIECES, PIECE_STR, PLAYER_COLORS, COLORS


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



def get_valid_moves(game: Game, player: int):
    """list of valid moves [(row, col, piece), ...]"""
    valid_moves = []
    for r in range(game.board_size):
        for c in range(game.board_size):
            for p in [PIECES.PE, PIECES.PI, PIECES.PO]:
                if game.validate_move(r, c, p, player):
                    valid_moves.append((r, c, p))
    return valid_moves


def colorize_spot(piece: PIECES, player: int, other_player: int=-1, other_piece: PIECES=PIECES.EMPTY):
    # NOTE: Not tested, just psydocode
    tmplt = PLAYER_COLORS[player] + PIECE_STR[piece]
    tmplt += " " if other_player != -1 and other_piece != PIECES.EMPTY else PLAYER_COLORS[other_player] + PIECE_STR[other_piece]
    return tmplt + COLORS.RESET
