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
    assert game.validate_move(3, 4, Piece(t_Piece.PE)), "Could not place pe on empty valid spot"
    assert game.validate_move(2, 2, Piece(t_Piece.PO)), "Could not place po on empty valid spot"
    assert not game.validate_move(0, 0, Piece(t_Piece.PI)), "Was able to place a pi in an valid empty spot"
    assert not game.validate_move(-1, 0, Piece(t_Piece.PE)), "Was able to place piece (pe) outside of board (-1,0)"
    assert not game.validate_move(8, 5, Piece(t_Piece.PE)), "Was able to place piece (pe) outside of board (8,5)"

def test_make_move(game: Game):
    game.make_move(0, 0, Piece(t_Piece.PE))
    assert game.board[0][1]._typename == t_Piece.PE
    game.make_move(0, 0, Piece(t_Piece.PI))


def test_rotate_player(game: Game):
    initial_player_indx = game.current_player_indx
    game.rotate_player()
    assert initial_player_indx != game.current_player_indx

def test_check_winner(game: Game):
    assert not game.check_winner()  # No winner initially

    n_pieces_in_a_row_to_win = 5

    # horizontal
    for h in range(game.board_size - 3):
        [game.make_move(i, h, Piece(t_Piece.PE, player_indx=game.current_player_indx)) for i in range(game.n_pieces_in_a_row_to_win)]
        assert game.check_winner()
        game.clear_board()

    # vertical
    for v in range(game.board_size - 3):
        [game.make_move(v, i, Piece(t_Piece.PE, player_indx=game.current_player_indx)) for i in range(game.n_pieces_in_a_row_to_win)]
        assert game.check_winner()
        game.clear_board()

"""

board representation is right and its getter/setters are correct too

I want to make sure that:

-  [ ] a player can win in any direction
    - [ ] a player can cross over another player with a pi and win
- [ ] pis can only be placed in a spot with a empty pe
- [ ] pes can only be placed in empty spots
- [ ] pos can only be placed in empty spots
- [ ] only 8 pos per player
- [ ] game ends in a tie when there are no more valid spots left



"""
def is_board_spot_completely_empty(x: int, y: int, g: Game) -> bool:
    indx = g.convert_xy_to_indx(x, y)
    return g.board[indx][0]._typename == t_Piece.EMPTY and g.board[indx][1]._typename == t_Piece.EMPTY

def test_piece_rules(game: Game): # , _piece: Piece):

    # pes can only be placed in empty spots
    assert is_board_spot_completely_empty(0, 0, game), f"The test spot is not completely empty ({game.board[0]})"
    assert game.make_move(0, 0, Piece(t_Piece.PE)), "Was not able to place a PE in a empty spot"

    # pos can only be placed in empty spots
    assert is_board_spot_completely_empty(0, 1, game), f"The test spot is not completely empty ({game.board[1]})"
    assert game.make_move(0, 1, Piece(t_Piece.PO)), "Was not able to place a PO in a empty spot"

    # pis can only be placed in a spot with a empty pe
    assert not game.make_move(0, 0, Piece(t_Piece.PI)), "Was able to place a PI in a empty spot"
    assert not game.make_move(0, 1, Piece(t_Piece.PI)), "Was able to place a PI spot with a PO"



    # pis can only be placed in a spot with a empty pe
    assert game.board[0][0]._typename == t_Piece.EMPTY and game.board[0][1]._typename == t_Piece.PE
    assert game.make_move(0, 0, Piece(t_Piece.PI)), "Was not able to place pi in a pe"
    



"""
0  | 0  1  2  3  4  5  6  7
1  | 8  9  10 11 12 13 14 15
2  | 16 17 18 19 20 21 22 23
3  | 24 25 26 27 28 29 30 31
4  | 32 33 34 35 36 37 38 39
5  | 40 41 42 43 44 45 46 47
6  | 48 49 50 51 52 53 54 55
7  | 56 57 58 59 60 61 62 63
"""