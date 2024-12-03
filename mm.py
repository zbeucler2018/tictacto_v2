from game import Game, PIECES
import utils

import numpy as np

import copy
from typing import Tuple



def evaluate(game: Game, is_maximizing_player: bool, player: int) -> float:
    #return 1 if is_maximizing_player and game.check_win(player) else -1
    other_player = 1 if player == 2 else 2
    player_score = utils.get_max_sequence(game, player)
    opponent_score = utils.get_max_sequence(game, other_player)
    
    if is_maximizing_player:
        return player_score - opponent_score
    else:
        return opponent_score - player_score

def minimax(game: Game, depth: int, is_maximizing_player: bool, player: int):
    other_player = 1 if player == 2 else 2

    if depth == 0 or game.check_game_over():
        return evaluate(game, is_maximizing_player, player)
    
    if is_maximizing_player: # the ai
        max_eval = float('-inf')
        for (row, col, piece) in utils.get_valid_moves(game, player):
            game_copy = copy.deepcopy(game)
            assert game_copy.make_move(row, col, piece, player)
            evaluation = minimax(game, depth-1, False, other_player)
            return max(max_eval, evaluation)
    else: # the opponent (playijng optimially)
        min_eval = float('+inf')
        for (row, col, piece) in utils.get_valid_moves(game, player):
            game_copy = copy.deepcopy(game)
            assert game_copy.make_move(row, col, piece, player)
            evaluation = minimax(game, depth-1, True, other_player)
            return min(min_eval, evaluation)
        

def find_best_move(game: Game, player: int, depth: int) -> Tuple[int, int, int]:
    best_score = float('-inf')
    best_move = None
    other_player = 1 if player == 2 else 2

    for (row, col, piece) in utils.get_valid_moves(game, player):
        game_copy = copy.deepcopy(game)
        assert game_copy.make_move(row, col, piece, player)
        score = minimax(game_copy, depth-1, False, other_player)
        if score > best_score:
            best_score = score
            best_move = (row, col, piece)

    return best_move

"""
- make a board for testing that only has a couple of valid moves and a win close by
"""

g = Game()

for r in range(g.board_size):
    for c in range(g.board_size):
        if r == 3 and c > 2: continue
        g.make_move(r, c, PIECES.PE, 3)
        g.make_move(r, c, PIECES.PI, 3)

g.make_move(3, 3, PIECES.PE, 1)
g.make_move(3, 3, PIECES.PI, 1)
g.make_move(3, 4, PIECES.PE, 1)
g.make_move(3, 4, PIECES.PI, 1)
g.make_move(3, 5, PIECES.PE, 1)
g.make_move(3, 5, PIECES.PI, 1)

g.display()

print(
    find_best_move(g, 1, 4)
)


test = Game()

while not test.check_game_over():
    print("\n", "-"*10)
    test.display()
    print("Player 1")
    row, col = int(input("Enter row (0-7): ")), int(input("Enter col (0-7): "))
    piece = int(input("Enter the piece (PE=0, PI=1, PO=2): "))

    if not test.validate_move(row, col, piece, 1):
        print(f"r:{row} c:{col} p:{piece} is not valid, try again...")
        continue
    
    assert test.make_move(row, col, piece, 1)

    mm_row, mm_col, mm_piece = find_best_move(test, 2, 4)
    print(f"Player 2 | r:{mm_row} c:{mm_col} p:{mm_piece}")

    assert test.make_move(mm_row, mm_col, mm_piece, 2)


