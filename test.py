import pytest
from game import GameBoard, PieceType
"""
# Functional tests
    - Piece placement
        - PI cant be placed on spot by itself
        - PO cant be placed on occupied space
        - PO cannot be placed more than 8 times
        - PE cant be placed on occupied space
    - Win validation
        - 




"""
import pytest
from typing import List, Tuple

@pytest.fixture
def board():
    """Fixture to create a fresh board for each test"""
    return GameBoard(size=8, num_players=2)

def place_sequence(board: GameBoard, positions: List[Tuple[int, int]], piece_type: PieceType, player: int):
    """Helper function to place multiple pieces"""
    for row, col in positions:
        board.place_piece(row, col, piece_type, player)

def test_tie_all_po(board):
    """Test tie condition when all empty spaces are blocked by PO pieces"""
    # Fill first half of board with PO from player 1 (their max 8 POs)
    for i in range(2):
        for j in range(4):
            assert board.place_piece(i, j, PieceType.PO, player=1)
    
    # Fill remaining spaces with PO from player 2
    remaining_spaces = [(i, j) for i in range(8) for j in range(8) 
                       if not (i < 2 and j < 4)]
    
    # Use only 8 POs from player 2
    for i, (row, col) in enumerate(remaining_spaces):
        if i < 8:
            assert board.place_piece(row, col, PieceType.PO, player=2)
            
    # Fill rest with PE and PI to block all moves
    for i, (row, col) in enumerate(remaining_spaces[8:]):
        player = (i % 2) + 1
        other_player = 2 if player == 1 else 1
        assert board.place_piece(row, col, PieceType.PE, player)
        assert board.place_piece(row, col, PieceType.PI, other_player)
    
    assert board.is_tie()

def test_tie_all_pi(board):
    """Test tie condition when all PE pieces have PI pieces on them"""
    # Fill board with PE pieces alternating between players
    for i in range(8):
        for j in range(8):
            player = ((i + j) % 2) + 1
            assert board.place_piece(i, j, PieceType.PE, player)
    
    # Place PI pieces on all PE pieces
    for i in range(8):
        for j in range(8):
            player = (((i + j) % 2) + 1) % 2 + 1  # Opposite player
            assert board.place_piece(i, j, PieceType.PI, player)
    
    assert board.is_tie()

def test_not_tie_with_valid_moves(board):
    """Test that game is not tied when valid moves exist"""
    # Fill most of the board but leave some valid moves
    for i in range(7):  # Leave last row empty
        for j in range(8):
            assert board.place_piece(i, j, PieceType.PE, player=1)
    
    assert not board.is_tie()

def test_tie_partial_board(board):
    """Test tie condition with partially filled board but no valid moves"""
    # Create a pattern where no winning sequence is possible
    # Use alternating PO pieces to block any potential 5-in-a-row
    for i in range(8):
        for j in range(8):
            if (i + j) % 2 == 0:
                player = 1 if (i * j) % 2 == 0 else 2
                if player == 1 and board.po_count[1] < 8:
                    assert board.place_piece(i, j, PieceType.PO, player)
                elif player == 2 and board.po_count[2] < 8:
                    assert board.place_piece(i, j, PieceType.PO, player)
                else:
                    # Fill with PE+PI combination when out of POs
                    assert board.place_piece(i, j, PieceType.PE, 1)
                    assert board.place_piece(i, j, PieceType.PI, 2)
            else:
                # Fill remaining spaces with PE+PI combinations
                assert board.place_piece(i, j, PieceType.PE, 2)
                assert board.place_piece(i, j, PieceType.PI, 1)
    
    assert board.is_tie()

def test_not_tie_with_winning_possibility(board):
    """Test that game is not tied when a winning sequence is still possible"""
    # Fill board with alternating PE pieces but leave a potential winning sequence
    for i in range(8):
        for j in range(8):
            if not (i == 0 and j < 5):  # Leave top row first 5 spaces empty
                player = ((i + j) % 2) + 1
                assert board.place_piece(i, j, PieceType.PE, player)
    
    assert not board.is_tie()
    
    # Fill potential winning sequence
    for j in range(5):
        assert board.place_piece(0, j, PieceType.PE, player=1)
    
    assert board.check_win(0, 4, player=1)
    assert not board.is_tie()

def test_tie_after_blocked_win(board):
    """Test tie condition after blocking all possible winning sequences"""
    # Create a scenario where both players have used their POs to block 
    # each other's winning opportunities
    
    # Player 1 creates potential winning sequence
    for i in range(4):
        assert board.place_piece(0, i, PieceType.PE, player=1)
    
    # Player 2 blocks with PO
    assert board.place_piece(0, 4, PieceType.PO, player=2)
    
    # Fill rest of the board with alternating PE+PI combinations
    for i in range(1, 8):
        for j in range(8):
            if not board.has_piece(i, j):
                assert board.place_piece(i, j, PieceType.PE, player=1)
                assert board.place_piece(i, j, PieceType.PI, player=2)
    
    assert board.is_tie()

def test_get_valid_moves(board):
    """Test getting valid moves for current player"""
    # Place some pieces
    board.place_piece(0, 0, PieceType.PE, player=1)
    board.place_piece(0, 1, PieceType.PO, player=2)
    board.place_piece(0, 2, PieceType.PE, player=1)
    board.place_piece(0, 2, PieceType.PI, player=2)
    
    valid_moves = board.get_valid_moves(player=1)
    
    # Should include:
    # - Empty spaces for PE
    # - PE spaces without PI for PI placement
    # - Should not include PO spaces or PE+PI combinations
    
    assert (0, 0) in valid_moves  # Can place PI on existing PE
    assert (0, 1) not in valid_moves  # Cannot place on PO
    assert (0, 2) not in valid_moves  # Cannot place on PE+PI
    assert (1, 0) in valid_moves  # Can place PE on empty space

if __name__ == '__main__':
    pytest.main([__file__])