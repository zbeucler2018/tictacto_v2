from game import Game, t_Piece, Piece, Colors

from gymnasium.spaces import Discrete, MultiDiscrete, Box
import gymnasium as gym
import numpy as np


class PePiPoEnv(gym.Env):

    metadata = {
        "name": "pepipo_0v",
    }

    def __init__(self) -> None:
        self.game: Game = Game()
        self.agents = [f"player_{p}" for p in self.game.n_players]
        self.timestep = None

        # action space
        # 3 pieces actions (PE, PI, PO) * 64 possible spots on the board
        self.action_spaces = {i: Discrete(3*64) for i in self.agents}

        # obs space
        # 8x8x4
        self.observation_spaces = {
            i: Box(low=-1, high=len(self.agents), shape=(self.game.board.board_size, self.game.board.board_size, 4)) for i in self.agents
        }

    def parse_piece_from_action(self, action: int) -> tuple[t_Piece, int, int]:
        # this is gross but whatever
        piece_type = -1
        if action > -1 and action < 64: # 0 to 63 inclusively
            piece_type = t_Piece.PI
        elif action > 63 and action <= 127: # 64 to 127 inclusively
            piece_type = t_Piece.PE
        elif action > 127 and action <= 191: # 128 to 192 inclusively
            piece_type = t_Piece.PO
        
        # calc board coords
        indx = action % 64
        x = indx // self.game.board.board_size
        y = indx % self.game.board.board_size
        return piece_type, x, y

    def _get_obs(self):
        # represents type of piece in index 0
        channel_1 = np.zeros((self.game.board.board_size, self.game.board.board_size, 1))
        for x in range(self.game.board.board_size):
            for y in range(self.game.board.board_size):
                cell = self.game.board[x, y]
                channel_1[x, y, 1] = cell[0]._typename.value # 0 EMPTY 1 PI 2 PE 3 PO
        
        # represents type of piece in index 1
        channel_2 = np.zeros((self.game.board.board_size, self.game.board.board_size, 1))
        for x in range(self.game.board.board_size):
            for y in range(self.game.board.board_size):
                cell = self.game.board[x, y]
                channel_2[x, y, 1] = cell[1]._typename.value # 0 EMPTY 1 PI 2 PE 3 PO
                
        # represents owner of piece in index 0
        channel_3 = np.zeros((self.game.board.board_size, self.game.board.board_size, 1))
        for x in range(self.game.board.board_size):
            for y in range(self.game.board.board_size):
                cell = self.game.board[x, y]
                channel_3[x, y, 1] = cell[0].player_indx # -1 = EMPTY
        
        # represents owner of piece in index 1
        channel_4 = np.zeros((self.board.board_size, self.board.board_size, 1))
        for x in range(self.board.board_size):
            for y in range(self.board.board_size):
                cell = self.board[x, y]
                channel_4[x, y, 1] = cell[1].player_indx # -1 = EMPTY
                
        # TODO: WHAT SHOULD THIS RETURN?
        return np.dstack([channel_1, channel_2, channel_3, channel_4])
    
    def observation_space(self, agent):
        return self.observation_space[agent]
    
    def _get_action_mask(self):

        mask = np.zeros(3*64)
        
        # iterate through all possible actions 
        # and mark 1 if legal and 0 if illegal
        for action in range(3*64):
            piece_type, x, y = self.parse_piece_from_action(action)
            move_is_legal = self.game.validate_move(x, y, Piece(piece_type))
            mask[action] = 1 if move_is_legal else 0

        return mask

    def action_space(self, agent):
        return self.action_spaces[agent]
    
    def step(self, actions):

        for player in self.agents:
            
            # parse piece type and coordinates from action
            action = actions[player]
            piece_type, x, y = self.parse_piece_from_action(action)

            # apply action (update the state)
            assert self.game.make_move(x, y, piece_type), f"Got invalid action: {action} | t_piece: {piece_type} | ({x}, {y})"

            # generate observations
            observations = {i: {"observation": self._get_obs(), "action_mask": self._get_action_mask()} for i in self.agents}

            # Calculate reward
            if self.game.check_winner():
                rewards = {i: -1 for i in self.agents} # lose: -1
                rewards[player] = 1                    # win : +1
                truncations = {i: True for i in self.agents}
                terminations = {i: True for i in self.agents}
            elif self.game.check_tie():
                rewards = {i: 0 for i in self.agents} # Tie:  0
                truncations = {i: True for i in self.agents}
                terminations = {i: True for i in self.agents}
            else:
                rewards = {i: 0 for i in self.agents}
                truncations = {i: False for i in self.agents}
                terminations = {i: False for i in self.agents}
            
            self.game.rotate_player()

        infos = {i: {} for i in self.agents}            


        return observations, rewards, terminations, truncations, infos

    def reset(self, seed=None, options=None):
        self.game = Game() # resets board
        self.timestep = 0

        # The same observation and action_mask is passed to every agent
        observations = {
            i: {"observation": self._get_obs(), "action_mask": self._get_action_mask()} for i in self.agents
        }

        # create dummy info's that are required for parallel-to-aec conversion
        infos = {i: {} for i in self.agents}

        return observations, infos
    
    def render(self) -> None:
        self.game.print_board()

# 
# 0   - 63     PI
# 64  - 127    PE
# 128 - 191    PO

def get_piece_from_action(action: int) -> int:
    return action % 8

def get_location_from_action(action: int) -> int:
    return action % 64


# def parse_action(action: int):
#     # this is ugly but whatever
#     piece_type = -1
#     if action > -1 and action < 64: # 0 to 63 inclusively
#         piece_type = t_Piece.PI
#     elif action > 63 and action <= 127: # 64 to 127 inclusively
#         piece_type = t_Piece.PE
#     elif action > 127 and action <= 191: # 128 to 192 inclusively
#         piece_type = t_Piece.PO

#     indx = 
#     return piece_type
def parse_action(action: int):
    # Define piece types and their corresponding ranges
    piece_ranges = {
        t_Piece.PI: range(0, 64),
        t_Piece.PE: range(64, 128),
        t_Piece.PO: range(128, 192)
    }

    # Iterate through piece types and their ranges
    for piece_type, piece_range in piece_ranges.items():
        if action in piece_range:
            return piece_type

    # Default value if action does not match any range
    return -1
    
l = []
for i in range(3*64):
    l.append(parse_action(i))
    print(f"{i}\t", parse_action(i), get_location_from_action(i))

print(l.count(t_Piece.PI), l.count(t_Piece.PE), l.count(t_Piece.PO))
