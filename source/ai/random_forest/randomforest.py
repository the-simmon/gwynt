from sklearn.ensemble import RandomForestRegressor

from source.ai.abstract_ai import AbstractAI
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


class RandomForest(AbstractAI):

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.rf = RandomForestRegressor(n_estimators=1000)

    def step(self, environment: GameEnvironment, player: Player) -> bool:
        pass
