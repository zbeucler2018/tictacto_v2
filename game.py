import numpy as np

from enum import IntEnum, StrEnum



class PIECES(IntEnum):
    EMPTY = -1
    PE = 0
    PI = 1
    PO = 2

PIECE_STR = {
    PIECES.EMPTY: "..",
    PIECES.PE: "O",
    PIECES.PI: "*",
    PIECES.PO: "@"
}

class COLORS(StrEnum):
    RESET = "\033[0m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

PLAYER_COLORS = {
    # Mapping of colors to player
    -1: COLORS.WHITE,
    1: COLORS.GREEN,
    2: COLORS.BLUE,
    3: COLORS.CYAN,
    4: COLORS.RED
}



class Game:

    def __init__(self):
        self.n_players = 2
        self.board_size = 8
        self.po_limit = 8
        self.win_length = 5
        self.board = np.full((self.board_size, self.board_size, 3), PIECES.EMPTY, dtype=np.int8)
        self.po_pieces = [self.po_limit] * self.n_players


    def make_move(self, row: int, col: int, piecetype: PIECES, player: int) -> bool:
        if not self.validate_move(row, col, piecetype, player):
            return False
        # Place the piece
        self.board[row, col, piecetype] = player
        # Decrement PO count if applicable
        if piecetype == PIECES.PO:
            self.po_pieces[player-1] -= 1
        return True


    def validate_move(self, row: int, col: int, piecetype: PIECES, player: int) -> bool:
        spot_is_empty = np.all(self.board[row, col, :]==PIECES.EMPTY)
        # PO placement (spot is empty and player has POs left)
        if piecetype == PIECES.PO:
            return (spot_is_empty and self.po_pieces[player-1] > 0)

        # PE placement (spot is empty)
        if piecetype == PIECES.PE:
            return spot_is_empty
        
        # PI placement (there is a PE but no PIs) 
        if piecetype == PIECES.PI:
            return (self.board[row, col, PIECES.PE] != PIECES.EMPTY and 
                    self.board[row, col, PIECES.PI] == PIECES.EMPTY)

        return False
    

    def check_win(self, player: int) -> bool:
        """true if that player has a winning board"""
        # Combine PE, PI, and PO layers for win checking
        win_board = np.logical_or.reduce([
            self.board[:, :, PIECES.PE] == player,
            self.board[:, :, PIECES.PI] == player,
            self.board[:, :, PIECES.PO] == player
        ]).astype(int)

        # Check horizontal
        for row in range(8):
            for col in range(4):
                if np.all(win_board[row, col:col+5] == True):
                    return True
        
        # Check vertical
        for col in range(8):
            for row in range(4):
                if np.all(win_board[row:row+5, col] == True):
                    return True
        
        # Diagonal checks (both directions)
        for row in range(4):
            for col in range(4):
                # Diagonal down-right
                if np.all([win_board[row+i, col+i] for i in range(5)] == True):
                    return True
                
                # Diagonal up-right
                if np.all([win_board[row+4-i, col+i] for i in range(5)] == True):
                    return True
        
        return False

    
    def check_tie(self) -> bool:
        # Check each player
        for player in range(1, self.n_players + 1):
            # Flag to track if the player has any valid moves
            has_valid_moves = False
            
            # Check all board positions for possible moves
            for row in range(self.board_size):
                for col in range(self.board_size):
                    # Check PE placement
                    if self.validate_move(row, col, PIECES.PE, player):
                        has_valid_moves = True
                        break
                    # Check PI placement
                    if self.validate_move(row, col, PIECES.PI, player):
                        has_valid_moves = True
                        break
                    # Check PO placement
                    if self.validate_move(row, col, PIECES.PO, player):
                        has_valid_moves = True
                        break
                # Exit early if valid move found
                if has_valid_moves:
                    break
            
            # If no moves found for this player, continue checking others
            if not has_valid_moves:
                return True
        
        # If all players have moves, no tie
        return False


    def check_game_over(self) -> bool:
        return self.check_win(1) or self.check_win(2) or self.check_tie()


    def display(self) -> None:
        print(" ", *[_ for _ in range(self.board_size)], sep="  ", end="\n")
        for r in range(self.board_size):
            cells = []
            for c in range(self.board_size):
                spot_is_empty = np.all(self.board[r, c, :]==PIECES.EMPTY)
                colorize = lambda r,c,pce: str(PLAYER_COLORS[self.board[r,c,pce]]) + str(PIECE_STR[pce]) + str(COLORS.RESET)

                if spot_is_empty:
                    cells.append(PIECE_STR[PIECES.EMPTY])
                # PE and PI
                elif self.board[r, c, PIECES.PE] != PIECES.EMPTY and self.board[r, c, PIECES.PI] != PIECES.EMPTY:
                    cells.append(PLAYER_COLORS[self.board[r, c, PIECES.PE]] + PIECE_STR[PIECES.PE] + \
                                PLAYER_COLORS[self.board[r, c, PIECES.PI]] + PIECE_STR[PIECES.PI] + COLORS.RESET)
                # PE and no PI
                elif self.board[r, c, PIECES.PE] != PIECES.EMPTY and self.board[r, c, PIECES.PI] == PIECES.EMPTY:
                    cells.append(f"{colorize(r,c,PIECES.PE)} ")
                # PO
                elif self.board[r, c, PIECES.PO] != PIECES.EMPTY:
                    cells.append(f"{colorize(r,c,PIECES.PO)} ")
                # else:
                #     print("B: ", self.board[r, c, :])
            print(f"{r}:", *cells, sep=" ", end="\n")
            cells = []
