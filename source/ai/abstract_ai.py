import abc
from typing import Tuple

from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


class AbstractAI(abc.ABC):

    def __init__(self):
        super().__init__()
        self.reward_list = []

    @abc.abstractmethod
    def step(self, environment: GameEnvironment, player: Player) -> Tuple[bool, int]:
        pass

    def chose_revive(self, environment: GameEnvironment, player: Player):
        pass

    def _log_reward(self, reward: int):
        self.reward_list.append(reward)
