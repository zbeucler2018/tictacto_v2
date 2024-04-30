from game import Game, t_Piece, Piece

from gymnasium.spaces import Discrete, MultiDiscrete
import gymnasium as gym


class PePiPoEnv(gym.Env):

    metadata = {
        "name": "pepipo_0v",
    }

    def __init__(self) -> None:
        # ? super().__init__()
        self.n_players = 2
        self.game: Game = Game()
        self.agents = [f"player_{p}" for p in self.game.n_players] 

    def render(self) -> None:
        self.game.print_board()

    def step(self, actions):
        self.game = Game()
        pass

    def reset(self, seed=None, options=None):
        pass
    
    def observation_space(self, agent):
        """ 
		For a spot on the board, there are a couple possible states:
			- empty
			- player 1 pe
			- player 2 pe
			- player 1 po
			- player 2 po
			- player 1 pe + player 1 pi
			- player 2 pe + player 2 pi
			- player 1 pe + player 2 pi
			- player 2 pe + player 1 pi
			(9 total)			
		"""
		# NOTE: This is only for 2 players
        return Discrete(2*9) # 64 spots on board * 9 possible states per spot

    def observation_space(self, agent):
        return 

    def action_space(self, agent):
        """Player can only place 1 of the three piece types (pe pi po)"""
        return # Discrete(3) ? # pe, pi, po
