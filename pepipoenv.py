from copy import copy

from game import Game, t_Piece, Piece, Colors

from gymnasium.spaces import Discrete, Box
import gymnasium as gym
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector


class PePiPoEnv(AECEnv):

    metadata = {
        "name": "pepipo_0v",
        "is_parallelizable": False,
        "render_fps": 1,
    }

    def __init__(self) -> None:
        self.game: Game = Game()
        
        # AEC API
        self.agents = [f"player_{p}" for p in range(self.game.n_players)]
        self.num_agents = len(self.agents)
        self.possible_agents = copy(self.agents)
        self.max_num_agents = len(self.possible_agents)
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()

        # action space
        # 3 pieces actions (PE, PI, PO) * 64 possible spots on the board (8x8 board)
        self.action_spaces = {i: Discrete(3*64) for i in self.agents}

        # obs space
        # 8x8x4
        self.observation_spaces = {
            i: Box(low=-1, high=len(self.agents), shape=(self.game.board.board_size, self.game.board.board_size, 4)) for i in self.agents
        }


    



    def observe(self, agent):
        self.game.current_player_indx = self.agents.index(agent)
        return {"observation": self._get_obs(), "action_mask": self._get_action_mask()}

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

    def _get_obs(self) -> np.ndarray:
        """Generates the observation from the state (board)"""
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
    
    def _get_action_mask(self, agent) -> np.ndarray:
        # NOTE: T
        mask = np.zeros(shape=(3*64), dtype=np.int8)
        # iterate through all possible actions 
        # and mark 1 if legal and 0 if illegal
        for action in range(3*64):
            piece_type, x, y = self.parse_piece_from_action(action)
            move_is_legal, _ = self.game.validate_move(x, y, piece_type, agent)
            mask[action] = 1 if move_is_legal else 0
        return mask

    def action_space(self, agent):
        return self.action_spaces[agent]
    


    def step(self, actions):

        p0_action = actions["player_0"]
        p1_action = actions["player_1"]

        # execute actions
        self.game.current_player_indx = 0
        p0_piece_type, x, y = self.parse_piece_from_action(p0_action)
        move_is_valid, reason = self.game.validate_move(x, y, p0_piece_type)
        try:
            assert move_is_valid, f"Invalid player_0 move: {reason} ({x}, {y}) {p0_piece_type}"
        except Exception:
            breakpoint
        self.game.make_move(x, y, p0_piece_type)

        # action nask needs to be updated. 
        # NOTE: BOTH AGENTS ARE GENERATING THE SAME ACTION AND SO PLAYER_1's ACTION 
        # WILL ALWAYS BE INVALID BECAUSE PLAYER_1's PIECE IS THERE

        self.game.current_player_indx = 1
        p1_piece_type, x, y = self.parse_piece_from_action(p1_action)
        move_is_valid, reason = self.game.validate_move(x, y, p1_piece_type)
        try:
            assert move_is_valid, f"Invalid player_1 move: {reason} ({x}, {y}) {p1_piece_type}"
        except Exception:
            breakpoint
        self.game.make_move(x, y, p1_piece_type)

        # generate action masks
        self.game.current_player_indx = 0
        p0_mask = self._get_action_mask()

        self.game.current_player_indx = 1
        p1_mask = self._get_action_mask()


        # check termination conditions
        terminations = {i: False for i in self.agents}
        rewards = {i: 0 for i in self.agents}
        self.game.current_player_indx = 0
        if self.game.check_winner():
            rewards = {"player_0": 1, "player_1": -1}
            terminations = {i: True for i in self.agents}
            self.agents = []

        self.game.current_player_indx = 1
        if self.game.check_winner():
            print(self.game.current_player_indx)
            rewards = {"player_0": -1, "player_1": 1}
            terminations = {i: True for i in self.agents}
            self.agents = []

        # check truncation conditions
        truncations = {i: False for i in self.agents}
        self.game.current_player_indx = 0
        if self.game.check_tie():
            rewards = {"player_0": 0, "player_1": 0}
            truncations = {i: True for i in self.agents}
            self.agents = []

        self.game.current_player_indx = 1
        if self.game.check_tie():
            rewards = {"player_0": 0, "player_1": 0}
            truncations = {i: True for i in self.agents}
            self.agents = []

        # get observations
        observations = {
            "player_0": {"observation": self._get_obs(), "action_mask": p0_mask},
            "player_1": {"observation": self._get_obs(), "action_mask": p1_mask}
        }

        # generate dummy infos
        infos = {"player_0": {}, "player_1": {}}

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

    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
        else:
            # invalid action masking is optional and environment-dependent
            if "action_mask" in info:
                mask = info["action_mask"]
            elif isinstance(observation, dict) and "action_mask" in observation:
                mask = observation["action_mask"]
            else:
                mask = None
            action = env.action_space(agent).sample(mask) # this is where you would insert your policy

        env.step(action)
    env.close()











    # observations, infos = env.reset()

    # steps = 0

    # while env.agents:

    #     env.render()

    #     # generate random policy
    #     actions = {agent: env.action_space(agent).sample(observations[agent]["action_mask"]) for agent in env.agents}

    #     observations, rewards, terminations, truncations, infos = env.step(actions)


    # env.close()

    # env.render()

    # print("********************** END")
    # print("Steps  : ", steps)
    # print("Rewards: ", rewards)
    # print("Terms  : ", terminations)
    # print("Truncs : ", truncations)