import random
from typing import List

from source.core.card import Card
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource
from source.core.player import Player


def simulate_random_game(environment: GameEnvironment, current_player: Player, card_source: CardSource) -> Player:
    game_over = environment.game_over()
    while not game_over:
        potential_cards = _get_potential_cards(current_player, card_source)

        if not environment.passed[current_player.id]:
            potential_cards.append(None)  # None == pass

        random_card = random.choice(potential_cards)
        if _should_pass(environment, current_player):
            random_card = None

        if random_card:
            row = random.choice(CombatRow.get_possible_rows(random_card))
        else:
            row = None
        game_over, current_player, card_source = environment.step(current_player, row, random_card)

    return environment.get_winner()


def _get_potential_cards(player: Player, next_card_source: CardSource) -> List[Card]:
    if next_card_source is CardSource.HAND:
        return player.active_cards.get_all_cards()
    return player.graveyard.get_all_cards()


def _should_pass(environment: GameEnvironment, current_player: Player) -> bool:
    enemy = environment.board.get_enemy_player(current_player)
    enemy_passed = environment.passed[enemy.id]
    enemy_damage = environment.board.calculate_damage(enemy)
    own_damage = environment.board.calculate_damage(current_player)

    if enemy_passed and enemy_damage < own_damage:
        return True
    return False
