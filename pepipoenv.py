from game import Game, t_Piece, Piece, Colors

from gymnasium import spaces
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
        self.possible_agents = self.agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()
        self.terminations = {i: False for i in self.agents}
        self.truncations = {i: False for i in self.agents}
        self.rewards = {i: 0 for i in self.agents}
        self.infos = {i: {} for i in self.agents}

        self._cumulative_rewards = {agent: 0 for agent in self.agents}

        valid_piece_types = [t_Piece.PE, t_Piece.PI, t_Piece.PO]
        total_spots_on_board = self.game.board.board_size * self.game.board.board_size

        # action space
        # 3 pieces actions (PE, PI, PO) * 64 possible spots on the board (8x8 board)
        self.action_spaces = {i: spaces.Discrete(valid_piece_types*total_spots_on_board) for i in self.agents}

        # obs space
        # 8x8x4
        # Not sure why I have to make the obs space a dict, this was how the connect_four env is (and other classic pz envs)
        self.observation_spaces = {
            i: spaces.Dict({
                "observation": spaces.Box(low=-1, high=valid_piece_types, shape=(self.game.board.board_size, self.game.board.board_size, 4), dtype=np.int8),
                "action_mask": spaces.Box(low=0, high=1, shape=(valid_piece_types*total_spots_on_board,), dtype=np.int8)
            }) for i in self.agents
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

    def observe(self, agent):
        return {"observation": self._get_obs(), "action_mask": self._get_action_mask(agent)}

    def _get_obs(self) -> np.ndarray:
        """Generates the observation from the state (board). All agents have the same observation space."""
        player_to_obs = {"": -1, "player_0": 0, "player_1": 1}
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
                # -1 if t_Piece.EMPTY, else use the index of the player in self.agents
                base[x, y, 2] = player_to_obs[cell[0].player_id]

                # 4th channel represents owner of piece in index 1
                # -1 if t_Piece.EMPTY, else use the index of the player in self.agents
                base[x, y, 3] = player_to_obs[cell[1].player_id]
        return base

    def observation_space(self, agent) -> np.ndarray:
        return self.observation_spaces[agent]
    
    def _get_action_mask(self, agent) -> np.ndarray:
        mask = np.zeros(shape=(3*64), dtype=np.int8)
        # iterate through all possible actions 
        # and mark 1 if legal and 0 if illegal
        for action in range(3*64):
            piece_type, x, y = self.parse_piece_from_action(action)
            mask[action] = 1 if self.game.validate_move(x, y, piece_type, agent) else 0
        return mask

    def action_space(self, agent):
        return self.action_spaces[agent]

    def step(self, action):
        if (self.terminations[self.agent_selection] or self.truncations[self.agent_selection]):
            # handles stepping an agent which is already dead
            # accepts a None action for the one agent, and moves the agent_selection to
            # the next dead agent,  or if there are no more dead agents, to the next live agent
            return self._was_dead_step(action)
        
        agent = self.agent_selection
        
        # NOTE: I don't understand self._cumulative_rewards
        # the agent which stepped last had its _cumulative_rewards accounted for
        # (because it was returned by last()), so the _cumulative_rewards for this
        # agent should start again at 0
        self._cumulative_rewards[agent] = 0
        
        
        # decode action
        piece_type, x, y = self.parse_piece_from_action(action)

        # print(agent, piece_type, x, y)

        # validate move
        assert self.game.validate_move(x, y, piece_type, agent)

        # make move
        self.game.make_move(x, y, piece_type, agent)

        # check winner
        if self.game.check_winner(agent):
            print(f"{agent} won!")
            self.rewards = {i: -1 for i in self.agents}
            self.rewards[self.agent_selection] = 1  # winner gets +1 reward, loser gets -1
            self.terminations = {i: True for i in self.agents}
            self.truncations = {i: True for i in self.agents}
        elif self.game.check_tie(agent):
            print('Tie!')
            self.rewards = {i: 0 for i in self.agents} # 0 reward for all agents in a tie
            self.terminations = {i: True for i in self.agents}
            self.truncations = {i: True for i in self.agents}

        # # selects the next agent.
        # # Adds .rewards to ._cumulative_rewards
        # self._accumulate_rewards()

        # Switch selection to next agents
        self._cumulative_rewards[self.agent_selection] = 0
        self.agent_selection = self._agent_selector.next()

        self._accumulate_rewards()
    
    def reset(self, seed=None, options=None):
        self.game = Game() # resets board
        self.agents = self.possible_agents[:]
        self.terminations = {i: False for i in self.agents}
        self.truncations = {i: False for i in self.agents}
        self.rewards = {i: 0 for i in self.agents}
        self.infos = {i: {} for i in self.agents}
        self._cumulative_rewards = {i: 0 for i in self.agents}

    def render(self) -> None:
        self.game.print_board()

    def close(self):
        return super().close()


if __name__ == "__main__":

    pass