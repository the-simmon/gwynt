import random
from copy import deepcopy
from typing import Tuple, List

from sklearn.ensemble import RandomForestRegressor

from source.ai.abstract_ai import AbstractAI
from source.core.card import CombatRow, Card, Ability
from source.core.gameenvironment import GameEnvironment
from source.core.player import Player


class RandomForest(AbstractAI):

    def __init__(self, filename: str = None):
        super().__init__()
        self.filename = filename
        self.rf = RandomForestRegressor(n_estimators=1000)
        self.random_factor = 1.0

    def step(self, environment: GameEnvironment, player: Player, ignore_reward=False) -> Tuple[bool, int]:
        card, row = self._get_best_card(environment, player)
        pass_ = card.ability is Ability.PASS
        round_ended = environment.step(player, row, card, pass_)

        game_finished = False
        reward = 0
        if round_ended:
            reward, game_finished = environment.get_round_reward(player)

            if game_finished:
                self.random_factor *= 0.99
                reward += environment.get_game_reward(player)

        if not game_finished and not ignore_reward:
            reward += self._get_future_reward(environment, player)

        if game_finished and not ignore_reward:
            self.rf.fit(self.repr_list(environment, player, card, row), [reward])

        return game_finished, reward

    def chose_revive(self, environment: GameEnvironment, player: Player) -> Tuple[Card, CombatRow]:
        revive_card = Card(CombatRow.CLOSE, 0)
        max_damage = 0

        for card in player.graveyard.get_all_cards():
            if card.damage > max_damage:
                max_damage = card.damage
                revive_card = card

        row = random.choice(CombatRow.get_possible_rows(revive_card.combat_row))
        return revive_card, row

    def _get_future_reward(self, environment: GameEnvironment, player: Player) -> int:
        enemy = environment.board.get_enemy_player(player)

        player = deepcopy(player)
        enemy = deepcopy(enemy)
        environment = deepcopy(environment)

        reward = 0
        if not environment.passed[player]:
            if not environment.passed[enemy]:
                self.step(environment, enemy, ignore_reward=True)
            _, reward = self.step(environment, player)
        return reward

    def _get_best_card(self, environment: GameEnvironment, player: Player) -> Tuple[Card, CombatRow]:
        if random.random() < self.random_factor:
            return self._pick_random(environment, player)

        max_reward = float('-inf')
        best_card = None
        best_row = None

        for card in player.active_cards.get_all_cards():
            for row in CombatRow.get_possible_rows(card.combat_row):
                reward = self.rf.predict(self.repr_list(environment, player, card, row))

                if reward > max_reward:
                    max_reward = reward
                    best_card = card
                    best_row = row
        return best_card, best_row

    def _pick_random(self, environment: GameEnvironment, player: Player) -> Tuple[Card, CombatRow]:
        card = random.choice(player.active_cards.get_all_cards())
        row = random.choice(CombatRow.get_possible_rows(card.combat_row))
        return card, row

    def repr_list(self, environment: GameEnvironment, player: Player, card: Card, row: CombatRow) -> List[List[int]]:
        return [environment.repr_list(player, card) + card.repr_list() + row.one_hot()]
