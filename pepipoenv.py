from copy import copy

from game import Game, t_Piece, Piece

from gymnasium.spaces import Discrete, Box
import gymnasium as gym
import numpy as np
from pettingzoo import ParallelEnv


class PePiPoEnv(ParallelEnv): # gym.Env

    metadata = {
        "name": "pepipo_0v",
    }

    def __init__(self) -> None:
        self.game: Game = Game()
        self.agents = [f"player_{p}" for p in range(self.game.n_players)]
        self.possible_agents = copy(self.agents) # required for pz.ParallelEnv API

        # action space
        # 3 pieces actions (PE, PI, PO) * 64 possible spots on the board (8x8 board)
        self.action_spaces = {i: Discrete(3*64) for i in self.agents}

        # obs space
        # 8x8x4
        self.observation_spaces = {
            i: Box(low=-1, high=len(self.agents), shape=(self.game.board.board_size, self.game.board.board_size, 4)) for i in self.agents
        }

    def parse_piece_from_action(self, action: int) -> tuple[t_Piece, int, int]:
        # this is gross but whatever
        # TODO: unit test
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
        n_channels = 4
        base = np.zeros(shape=(self.game.board.board_size, self.game.board.board_size, n_channels), dtype=np.int8)
        for x in range(self.game.board.board_size):
            for y in range(self.game.board.board_size):
                cell = self.game.board[x, y]

                # 1st channel represents type of piece in index 0
                base[x, y, 0] = cell[0]._typename.value

                # 2nd channel represents type of piece in index 1
                base[x, y, 1] = cell[1]._typename.value

                # 3rd channel represents owner of piece in index 0
                base[x, y, 2] = cell[0].player_indx

                # 4th channel represents owner of piece in index 1
                base[x, y, 3] = cell[1].player_indx
        return base

    def observation_space(self, agent) -> np.ndarray:
        return self.observation_spaces[agent]
    
    def _get_action_mask(self) -> np.ndarray:
        mask = np.zeros(shape=(3*64), dtype=np.int8)
        # iterate through all possible actions 
        # and mark 1 if legal and 0 if illegal
        for action in range(3*64):
            piece_type, x, y = self.parse_piece_from_action(action)
            move_is_legal, _ = self.game.validate_move(x, y, piece_type)
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
            move_is_valid, reason = self.game.validate_move(x, y, piece_type)
            assert move_is_valid, f"Got invalid action for agent {player}: {action} {piece_type} ({x}, {y}) {reason}"
            self.game.make_move(x, y, piece_type)

            # generate observations
            observations = {i: {"observation": self._get_obs(), "action_mask": self._get_action_mask()} for i in self.agents}

            # Calculate reward
            if self.game.check_winner():
                print('won')
                rewards = {i: -1 for i in self.agents} # lose: -1
                rewards[player] = 1                    # win : +1
                truncations = {i: True for i in self.agents}
                terminations = {i: True for i in self.agents}
                self.agents = []
            elif self.game.check_tie():
                print('tie')
                rewards = {i: 0 for i in self.agents} # Tie:  0
                truncations = {i: True for i in self.agents}
                terminations = {i: True for i in self.agents}
                self.agents = [] # NOTE: required for pz?
            else:
                print('none')
                rewards = {i: 0 for i in self.agents}
                truncations = {i: False for i in self.agents}
                terminations = {i: False for i in self.agents}
            
            self.game.rotate_player()

        infos = {i: {} for i in self.agents}            
        return observations, rewards, terminations, truncations, infos

    def reset(self, seed=None, options=None):
        self.game = Game() # resets board

        # The same observation and action_mask is passed to every agent
        observations = {
            i: {"observation": self._get_obs(), "action_mask": self._get_action_mask()} for i in self.agents
        }

        # create dummy info's that are required for parallel-to-aec conversion
        infos = {i: {} for i in self.agents}

        return observations, infos
    
    def render(self) -> None:
        self.game.print_board()

    def close(self):
        return super().close()


if __name__ == "__main__":

    # TODO: Seeing errors for invalid actions. Mask isn't providing good options I think
    # TODO: Seems like sometimes the game doesn't term or trunc when it should (ex: game won)

    env = PePiPoEnv()

    observations, infos = env.reset()


    steps = 0

    while env.agents:
        # get action mask (the mask is the same for every player)
        mask = observations["player_0"]["action_mask"]

        print("********************* BEFORE *************************************")

        env.render()

        # generate random policy
        actions = {agent: env.action_space(agent).sample(observations[agent]["action_mask"]) for agent in env.agents}

        try:
            observations, rewards, terminations, truncations, infos = env.step(actions)
        except Exception as e:
            print(e)
            print("Action : ", actions, "player_0: ", env.parse_piece_from_action(actions["player_0"]), "player_1: ", env.parse_piece_from_action(actions["player_1"]))
            print("Steps  : ", steps+1)
            print("Rewards: ", rewards)
            print("Terms  : ", terminations)
            print("Truncs : ", truncations)
            idk = 0
            break

        steps += 1
        print("Action : ", actions, "player_0: ", env.parse_piece_from_action(actions["player_0"]), "player_1: ", env.parse_piece_from_action(actions["player_1"]))
        print("Steps  : ", steps)
        print("Rewards: ", rewards)
        print("Terms  : ", terminations)
        print("Truncs : ", truncations)
        idk = 0

        env.render()

        print("************************ END *************************************")

        # input()

        if terminations["player_0"] or terminations["player_1"]: break
        if truncations["player_0"] or truncations["player_1"]: break


    env.close()


    print("********************** END")
    print("Steps  : ", steps)
    print("Rewards: ", rewards)
    print("Terms  : ", terminations)
    print("Truncs : ", truncations)