import abc

from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


class AbstractAI(abc.ABC):

    @abc.abstractmethod
    def choose_revive(self, environment: GameEnvironment, player: Player):
        pass
