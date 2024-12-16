from game import Game, PIECES
import utils

import numpy as np

from copy import deepcopy
from typing import Tuple
import random

"""
The 'maximizing' player is minimax.      They're always trying to pick the tree path with the MAXIMUM score. 
The 'minimizing' player is the opponent. They're always trying to pick the tree path with the MINIMUM score.
"""

# TODO: Create a web vizualization (with graphviz) of game tree to help evaluation debugging

def evaluate2(game: Game, is_maximizing_player: bool, player: int) -> float:
    other_player = 1 if player == 2 else 2
    player_score, other_player_score = 0, 0

    # Check for immediate win
    WIN_SCORE = 10
    if game.check_win(player):
        return WIN_SCORE if is_maximizing_player else -WIN_SCORE
    elif game.check_win(other_player):
        return -WIN_SCORE if is_maximizing_player else WIN_SCORE
    
    player_score += utils.get_max_sequence(game, player)
    other_player_score += utils.get_max_sequence(game, other_player)

    if is_maximizing_player:
        return player_score - other_player_score
    else:
        return other_player_score - player_score


def evaluate(game: Game, is_maximizing_player: bool, player: int) -> float:
    other_player = 1 if player == 2 else 2
    WIN_REWARD = 1000  # Extra reward for winning

    player_score = utils.get_max_sequence(game, player)
    opponent_score = utils.get_max_sequence(game, other_player)
    
    if game.check_win(player):  # Check if it's a winning state for player
        return WIN_REWARD
    elif game.check_win(other_player):  # Check if the opponent won
        return -WIN_REWARD
    
    # Base evaluation with added incentives
    return player_score - opponent_score if is_maximizing_player else opponent_score - player_score    
    

def minimax_ab(game: Game, depth: int, is_maximizing_player: bool, player: int, ab: bool=True, alpha=float('-inf'), beta=float('inf'), viz=None) -> float:
    other_player = 1 if player == 2 else 2

    if depth == 0 or game.check_game_over():
        return evaluate2(game, is_maximizing_player, player)
    
    if is_maximizing_player:
        max_eval = float('-inf')
        for (row, col, piece) in utils.get_valid_moves(game, player):
            game_copy = deepcopy(game)
            assert game_copy.make_move(row, col, piece, player)
            evaluation = minimax_ab(game_copy, depth-1, False, other_player, alpha, beta)
            max_eval = max(max_eval, evaluation)
            if ab:
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float('inf')
        for (row, col, piece) in utils.get_valid_moves(game, player):
            game_copy = deepcopy(game)
            assert game_copy.make_move(row, col, piece, player)
            evaluation = minimax_ab(game_copy, depth-1, True, other_player, alpha, beta)
            min_eval = min(min_eval, evaluation)
            if ab:
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
        return min_eval
        

def find_best_move(game: Game, player: int, depth: int, display: bool=False) -> Tuple[int, int, PIECES]:
    best_score = float('-inf')
    best_move = None
    b = np.zeros((8, 8))

    for (row, col, piece) in utils.get_valid_moves(game, player):
        game_copy = deepcopy(game)
        assert game_copy.make_move(row, col, piece, player)
        score = minimax_ab(game_copy, depth-1, True, player)
        b[row][col] = score
        if score > best_score:
            best_score = score
            best_move = (row, col, piece)
    if display: print(b, best_score)
    return best_move


def mm_sanity_test(interactive:bool=False, mm_depth:int=5, chance:float=0.1):
    g = Game()
    g.display()
    print(utils.colorize("Start!", "cyan"))

    while not g.check_game_over():
        utils.p1_print("player 1")
        if interactive:
            bad = True
            while bad:
                _, row = utils.p1_print("Enter row (0-7): ", end=""), int(input())
                _, col = utils.p1_print("Enter col (0-7): ", end=""), int(input())
                _, piece = utils.p1_print("Enter the piece (PE=0, PI=1, PO=2): ", end=""), int(input())
                if not g.validate_move(row, col, piece, 1):
                    utils.p1_print(f"Invalid move ({row}, {col}) {piece}. Try again.")
                else:
                    bad = False
            assert g.make_move(row, col, piece, 1)
        else:
            import time
            before = time.perf_counter()
            row, col, piece = find_best_move(g, 1, mm_depth) if random.random() < chance else random.choice(utils.get_valid_moves(g, 1))
            print(f"Total time to calc move: {time.perf_counter() - before}s")
            utils.p1_print(f"Enter row (0-7): {row}")
            utils.p1_print(f"Enter col (0-7): {col}")
            utils.p1_print(f"Enter the piece (PE=0, PI=1, PO=2): {piece}")
            assert g.make_move(row, col, piece, 1)
        
        g.display()
        
        utils.p2_print("player 2")
        before = time.perf_counter()
        row, col, piece = find_best_move(g, 2, mm_depth) if random.random() < chance else random.choice(utils.get_valid_moves(g, 2))
        print(f"Total time to calc move: {time.perf_counter() - before}s")
        utils.p2_print(f"Enter row (0-7): {row}")
        utils.p2_print(f"Enter col (0-7): {col}")
        utils.p2_print(f"Enter the piece (PE=0, PI=1, PO=2): {piece}")
        assert g.make_move(row, col, piece, 2)

        g.display()

    print(f"Tie={g.check_tie()}")
    utils.p1_print(f"player 1 | win={g.check_win(1)}")
    utils.p2_print(f"player 2 | win={g.check_win(2)}")


def mm_vs_random():
    g = Game()
    g.display()
    while not g.check_game_over():
        g.display()
        # player 1 is random
        player=1
        r, c, p = random.choice(utils.get_valid_moves(g, player))
        print(f"Player{player} | {(r,c)} {p}")
        assert g.make_move(r, c, p, player)

        if g.check_game_over(): break
        g.display()

        player=2
        r, c, p = random.choice(utils.get_valid_moves(g, player))
        print(f"Player{player} | {(r,c)} {p}")
        assert g.make_move(r, c, p, player)
    g.display()
    print(f"Tie={g.check_tie()}")
    print(f"player1 (mm) | win={g.check_win(1)}")
    print(f"player2 (rd) | win={g.check_win(2)}")


# mm_vs_random()