from dataclass import dataclass
from enum import enum

class PieceTypes(enum):
	PE = 0 # small
	PI = 1 # medium
	PO = 2 # large


@dataclass
class Piece:
	color: str
	position: tuple(int, int)
	type: PieceTypes



@dataclass
class BoardSpace:
	position: tuple(int, int)
	contains: list|list(Piece)



class Player:
	def __init__(self, color: string):
		self._color = color
		self._amount_of_po = 8

	@property
	def can_place_po(self) -> bool:
		return self._amount_of_po <= 8







def make_board(size: int = 8):
	_board = [ [] for _ in range(size) ]
	for x_indx,row in _board:
		for y_index,y in row:
			_space = BoardSpace(position=(x_index, y_index))
			_board[x_index][y_index] = _space



def can_place_in_space(board, piece: Piece, location: tuple(int, int), player: Player) -> bool:
	"""
	yes if:
		within board
		empty
		placing a small piece in a empty medium piece
	"""

	board_size = len(board)

	_x, _y = location

	if _x > board_size or _y > board_size:
		return False

	space = board[_x][_y]

	if not space.contains:
		return True

	# decrement PO amount
	if piece.type == PieceTypes.PO and player.can_place_po:
		player._amount_of_po -= 1
		return True

	if space.contains == PieceTypes.PI and piece.type == PieceTypes.PE:
		return True
	else:
		return False




def check_win(board, color) -> str:
	"""
    hard-coded to check for 5 in a row
    """
    rows = len(board)
    cols = rows
    
    # Check horizontally
    for row in range(rows):
        for col in range(cols - 4):
            if all(grid[row][col+i].contains == color for i in range(5)):
                return True
    
    # Check vertically
    for col in range(cols):
        for row in range(rows - 4):
            if all(grid[row+i][col].contains == color for i in range(5)):
                return True
    
    # Check diagonally (top-left to bottom-right)
    for row in range(rows - 4):
        for col in range(cols - 4):
            if all(grid[row+i][col+i].contains == color for i in range(5)):
                return True
    
    # Check diagonally (top-right to bottom-left)
    for row in range(rows - 4):
        for col in range(4, cols):
            if all(grid[row+i][col-i].contains == color for i in range(5)):
                return True
    return False



	


p1 = Player("green")
p2 = Player("red")



def play(player_1: Player, player_2: Player):

	board = make_board()

	current_player = random.choices([player_1, player_2])

	game_ended = False

	while not game_ended:

		# if board full
			# tie game

		# ask for piece and placement
    	while True:
			x = int(input(f"{current_player.color}: Enter the x-coordinate: "))
			y = int(input(f"{current_player.color}: Enter the y-coordinate: "))
	    	location = (x, y)
	    	piece = int(input(f"{current_player.color}: Enter PieceType (0,1,2 -> PE,PI,PO): "))

	    	if can_place_in_space(board, piece, location, current_player) and piece in [0, 1, 2]:
	    		break

	    # place piece
	    board[x][y] = Piece(current_player.color, location, PieceTypes[piece])
		
		# check win
		if check_win(board):
			print(f"{current_player.color} won!")
			return


		# change player
		if current_player == player_1:
			current_player == player_2
		else:
			current_player == player_1



"""

[ '   ', '   ', '   ' ],
[ '   ', '   ', '   ' ],
[ '   ', '   ', '   ' ]



[ '   ', '   ', '   ' ],
[ '   ', ' . ', '   ' ],
[ '   ', '   ', '   ' ]

[ ' . ', ' . ', ' . ' ],
[ ' . ', '   ', ' . ' ],
[ ' . ', ' . ', ' . ' ]

[ ' . ', ' . ', ' . ' ],
[ ' . ', ' . ', ' . ' ],
[ ' . ', ' . ', ' . ' ]




[ '   ', '   ', '   ' ],
[ '   ', ' * ', '   ' ],
[ '   ', '   ', '   ' ]

[ ' * ', ' * ', ' * ' ],
[ ' * ', '   ', ' * ' ],
[ ' * ', ' * ', ' * ' ]

[ ' * ', ' * ', ' * ' ],
[ ' * ', ' * ', ' * ' ],
[ ' * ', ' * ', ' * ' ]

"""



