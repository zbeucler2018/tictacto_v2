import pytest
from game import Game as Game, PIECES
import utils

@pytest.fixture
def game():
    return Game()

"""
Functional
- validate_move
    - each condition for each piece type
- make_move
    - pieces placed are the expected pieces at the expected stop
    - player index is recorded correctly
- check_win
    - diag
        - with and without opp pieces
    - horiz
        - with and without opp piec
    - vert
        - with and without opp pieces
- check_tie

Integration
- 2 random agents play full game till completion
"""


def test_valid_po_rules(game: Game):
    player = 1
    assert game.make_move(0, 0, PIECES.PO, player), "Could not place PO on empty space"
    assert not game.make_move(0, 0, PIECES.PO, player), "Placed PO ontop of another PO"

    game.make_move(0, 1, PIECES.PE, player)
    assert not game.make_move(0, 1, PIECES.PO, player), "Placed PO ontop of empty PE"

    game.make_move(0, 1, PIECES.PI, player)
    assert not game.make_move(0, 1, PIECES.PO, player), "Placed PO ontop of PE and PI"

    game.po_pieces[player-1] = 0
    assert not game.make_move(1, 1, PIECES.PO, player), f"Was able to place PO even though player {player} has {game.po_pieces[player-1]} POs left"
    

def test_valid_pe_rules(game: Game):
    player = 1
    assert game.make_move(0, 0, PIECES.PE, player), "Could not place PE on empty space"

    assert not game.make_move(0, 0, PIECES.PE, player), "Placed PE ontop of empty PE"

    game.make_move(0, 0, PIECES.PI, player)
    assert not game.make_move(0, 0, PIECES.PE, player), "Placed PE ontop of PE+PI"

    game.make_move(1, 0, PIECES.PO, player)
    assert not game.make_move(1, 0, PIECES.PE, player), "Placed PE+PI ontop of PO"
    


def test_valid_pi_rules(game: Game):
    player = 1
    assert not game.make_move(0, 0, PIECES.PI, player), "Could place PI on empty space"

    game.make_move(0, 1, PIECES.PE, player)
    assert game.make_move(0, 1, PIECES.PI, player), "Could not place PI in PE"

    assert not game.make_move(0, 1, PIECES.PI, player), "Could not place PI on PE+PI"

    game.make_move(1, 0, PIECES.PO, player)
    assert not game.make_move(1, 0, PIECES.PI, player), "Could place PI on PO"


@pytest.mark.parametrize("player", [1, 2])
def test_check_win(game: Game, player: int):
    assert not game.check_win(player), "player {player} won a empty game"

    game.make_move(0, 0, PIECES.PE, player)
    game.make_move(0, 0, PIECES.PI, player)
    game.make_move(0, 1, PIECES.PE, player)
    game.make_move(0, 2, PIECES.PE, player)
    game.make_move(0, 3, PIECES.PO, player)
    game.make_move(0, 4, PIECES.PO, player)

    assert game.check_win(player), "Player {player} didn't win fixed match"


def test_check_tie(game: Game):
    assert not game.check_tie(), "Freshly created game marked as tie"


def test_util_spot_is_empty(game: Game):
    for r in range(game.board_size):
        for c in range(game.board_size):
            assert utils.is_spot_empty(game, r, c)

    r, c = (1, 1)
    game.make_move(r, c, PIECES.PE, player=1)
    assert not utils.is_spot_empty(game, r, c)

    game.make_move(r, c, PIECES.PI, player=2)
    assert not utils.is_spot_empty(game, r, c)

    r, c = (1, 2)
    game.make_move(r, c, PIECES.PO, player=1)
    assert not utils.is_spot_empty(game, r, c)

    r, c = (1, 2)
    game.make_move(r, c, PIECES.PO, player=2)
    assert not utils.is_spot_empty(game, r, c)


def test_util_does_spot_contain_player(game: Game):
    players = [1, 2]
    for player in players:
        for r in range(game.board_size):
            for c in range(game.board_size):
                assert not utils.does_spot_contain_player(game, r, c, player)


def test_util_is_winning_move(game: Game):
    assert not utils.is_winning_move(game, 0, 0, PIECES.PE, 1), "Empty spot marked as winning spot"
    game.make_move(0, 1, PIECES.PE, player=1)
    game.make_move(0, 2, PIECES.PE, player=1)
    game.make_move(0, 3, PIECES.PO, player=1)
    game.make_move(0, 4, PIECES.PO, player=1)
    assert utils.is_winning_move(game, 0, 0, PIECES.PE, 1)
