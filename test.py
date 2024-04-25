import pytest
from game import Game, Piece, t_Piece

@pytest.fixture
def game():
    return Game()

def test_convert_xy_to_indx(game):
    assert game.convert_xy_to_indx(0, 0) == 0
    assert game.convert_xy_to_indx(1, 1) == 9
    assert game.convert_xy_to_indx(7, 7) == 63

@pytest.mark.skip()
def check_rules(game):
    # cannot place pi on empty square
    # pi in pe can win for both plyers
    # po blocks win
    # limit 8 pos max per player
    return

def test_validate_move(game: Game) -> None:
    assert game.validate_move(3, 4, Piece(t_Piece.PE)), f"Could not place 3,4 pe"
    assert game.validate_move(2, 2, Piece(t_Piece.PO)), f"Could not place 3,4 pe"
    assert not game.validate_move(0, 0, Piece(t_Piece.PI)), f"was able to place a pi in an empty spot"
    assert not game.validate_move(-1, 0, Piece(t_Piece.PE)), "was able to place piece outside of board pe -1,0"
    assert not game.validate_move(8, 5, Piece(t_Piece.PE)), "was able to place piece outside of board pe 8,0"

def test_make_move(game: Game):
    game.make_move(0, 0, Piece(t_Piece.PE))
    assert game.board[0][1]._typename == t_Piece.PE

def test_rotate_player(game: Game):
    initial_player_indx = game.current_player_indx
    game.rotate_player()
    assert initial_player_indx != game.current_player_indx

def test_check_winner(game: Game):
    # TODO: Write more specific test cases for check_winner method
    assert not game.check_winner()  # No winner initially
