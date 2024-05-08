import pytest
from game import Game, Piece, t_Piece, Colors


"""
board representation is right and its getter/setters are correct too

I want to make sure that:

-  [x] a player can win in any direction
    - [ ] a player can cross over another player with a pi and win
- [x] pis can only be placed in a spot with a empty pe
- [x] pes can only be placed in empty spots
- [x] pos can only be placed in empty spots
- [x] only 8 pos per player
- [ ] game ends in a tie when there are no more valid spots left
"""


@pytest.fixture
def game():
    return Game()


def test_convert_xy_to_indx(game: Game):
    assert game.board.convert_xy_to_indx(0, 0) == 0
    assert game.board.convert_xy_to_indx(1, 1) == 9
    assert game.board.convert_xy_to_indx(7, 7) == 63


def test_validate_move(game: Game) -> None:
    assert game.validate_move(3, 4, Piece(t_Piece.PE)), "Could not place pe on empty valid spot"
    assert game.validate_move(2, 2, Piece(t_Piece.PO)), "Could not place po on empty valid spot"
    assert not game.validate_move(0, 0, Piece(t_Piece.PI)), "Was able to place a pi in an valid empty spot"
    assert not game.validate_move(-1, 0, Piece(t_Piece.PE)), "Was able to place piece (pe) outside of board (-1,0)"
    assert not game.validate_move(8, 5, Piece(t_Piece.PE)), "Was able to place piece (pe) outside of board (8,5)"


def test_rotate_player(game: Game):
    initial_player_indx = game.current_player_indx
    game.rotate_player()
    assert initial_player_indx != game.current_player_indx


def test_check_winner(game: Game):
    game.current_player_indx = 1
    assert not game.check_winner(), "Detected win when the board was empty"

    # Test horizontal wins
    for y in range(game.board.board_size):
        for x in range(game.board.board_size - game.n_pieces_in_a_row_to_win + 1):
            for i in range(game.n_pieces_in_a_row_to_win):
                game.make_move(x + i, y, t_Piece.PE)
            assert game.check_winner(), f"Could not detect horizontal win at ({x}, {y})"
            game.board.empty_board()

    # Test vertical wins
    for x in range(game.board.board_size):
        for y in range(game.board.board_size - game.n_pieces_in_a_row_to_win + 1):
            for i in range(game.n_pieces_in_a_row_to_win):
                game.make_move(x, y + i, t_Piece.PE)
            assert game.check_winner(), f"Could not detect vertical win at ({x}, {y})"
            game.board.empty_board()

    # Test diagonal (top-left to bottom-right) wins
    for y in range(game.board.board_size - game.n_pieces_in_a_row_to_win + 1):
        for x in range(game.board.board_size - game.n_pieces_in_a_row_to_win + 1):
            for i in range(game.n_pieces_in_a_row_to_win):
                game.make_move(x + i, y + i, t_Piece.PE)
            assert game.check_winner(), f"Could not detect diagonal (top-left to bottom-right) win at ({x}, {y})"
            game.board.empty_board()

    # Test diagonal (top-right to bottom-left) wins
    for y in range(game.n_pieces_in_a_row_to_win - 1, game.board.board_size):
        for x in range(game.board.board_size - game.n_pieces_in_a_row_to_win + 1):
            for i in range(game.n_pieces_in_a_row_to_win):
                game.make_move(x + i, y - i, t_Piece.PE)
            assert game.check_winner(), f"Could not detect diagonal (top-right to bottom-left) win at ({x}, {y})"
            game.board.empty_board()


def test_po_rules(game: Game):
    game.current_player_indx = 1
    assert game.po_per_player[game.current_player_indx] == game.max_pos_per_player, "Started the game with the wrong amount of POs"
    game.make_move(0, 0, t_Piece.PO)
    assert game.po_per_player[game.current_player_indx] == game.max_pos_per_player - 1, "PO placement not reflected in record"
    game.po_per_player[game.current_player_indx] = 0
    assert not game.make_move(0, 1, t_Piece.PO), "Was able to place a PO when none are left"


def test_piece_rules(game: Game):

    def is_board_spot_completely_empty(x: int, y: int, g: Game) -> bool:
        return g.board[x, y][0]._typename == t_Piece.EMPTY and g.board[x, y][1]._typename == t_Piece.EMPTY

    # pes can only be placed in empty spots
    assert is_board_spot_completely_empty(0, 0, game), f"The test spot is not completely empty ({game.board[0, 0]})"
    assert game.make_move(0, 0, t_Piece.PE), "Was not able to place a PE in a empty spot"

    # pos can only be placed in empty spots
    assert is_board_spot_completely_empty(1, 1, game), f"The test spot is not completely empty ({game.board[1, 1]})"
    assert game.make_move(1, 1, t_Piece.PO), "Was not able to place a PO in a empty spot"

    # pis can only be placed in a spot with a empty pe
    assert is_board_spot_completely_empty(2, 2, game) and not game.make_move(2, 2, t_Piece.PI), "Was able to place a PI in a empty spot"
    assert not game.make_move(1, 1, t_Piece.PI), "Was able to place a PI spot with a PO"

    # pis can only be placed in a spot with a empty pe
    assert game.board[0, 0][0]._typename == t_Piece.EMPTY and game.board[0, 0][1]._typename == t_Piece.PE
    assert game.make_move(0, 0, t_Piece.PI), "Was not able to place a PI in a PE"
