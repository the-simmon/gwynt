import abc

from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


class AbstractAI(abc.ABC):

    def __init__(self):
        super().__init__()
        self.reward_list = []

    @abc.abstractmethod
    def step(self, environment: GameEnvironment, player: Player) -> bool:
        pass

    def _log_reward(self, reward: int):
        self.reward_list.append(reward)
