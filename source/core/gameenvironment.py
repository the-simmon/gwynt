from __future__ import annotations

import enum
import random
from copy import deepcopy
from typing import Tuple, Dict, Optional, List

from source.core.board import Board
from source.core.card import Ability, LeaderCard, LeaderAbility
from source.core.card import Card
from source.core.comabt_row import CombatRow
from source.core.faction_abililty import nilfgaard_check_draw, northern_realms_check_extra_card, \
    scoiatael_decide_starting_player
from source.core.player import Player
from source.core.weather import Weather


class CardSource(enum.Enum):
    HAND = 0
    GRAVEYARD = 1


class GameEnvironment:

    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.current_player = None
        self.current_card_source = CardSource.HAND

        # Leader card 'Emhyr var Emreis: The White Flame'
        self.block_leader = False
        passive_leaders = self._check_passive_leaders()
        self.board = Board(player1, player2, passive_leaders)

        self.current_round = 0
        self.passed: Dict[int, bool] = {player1.id: False, player2.id: False}

    def _check_passive_leaders(self) -> List[LeaderCard]:
        result = []
        for player in [self.player1, self.player2]:
            if player.leader.is_passive() and not self.block_leader:
                result.append(player.leader)
                if player.leader.ability is LeaderAbility.BLOCK_LEADER:
                    self.block_leader = True
                    result = [player.leader]
        return result

    def init(self):
        self.current_player = scoiatael_decide_starting_player(self)
        self._chose_hand()

    def _chose_hand(self):
        for player in [self.player1, self.player2]:

            #  random.choices not applicable, because it can return the same object multiple times
            deck_cards = player.deck.get_all_cards()
            random.shuffle(deck_cards)
            chosen_cards = deck_cards[:10]

            for card in chosen_cards:
                player.deck.remove(card.combat_row, card)
                player.hand.add(card.combat_row, card)

    def step(self, player: Player, row: Optional[CombatRow], card: Optional[Card]) -> Tuple[bool, Player, CardSource]:
        # card == None => player passes
        if card:
            if self.current_card_source is CardSource.HAND:
                player.hand.remove(card.combat_row, card)
            else:
                player.graveyard.remove(card.combat_row, card)
            self.board.add(player, row, card)

        self._end_of_step(player, card)
        return self.game_over(), self.current_player, self.current_card_source

    def step_decoy(self, player: Player, row: CombatRow, decoy: Card, replace_card: Card) \
            -> Tuple[bool, Player, CardSource]:
        player.hand.remove(decoy.combat_row, decoy)
        player.hand.add(replace_card.combat_row, replace_card)
        self.board.add(player, row, decoy)

        self.board.remove(player, row, replace_card, ignore_graveyard=True)
        self._end_of_step(player, decoy)
        return self.game_over(), self.current_player, self.current_card_source

    def _end_of_step(self, player: Player, card: Card):
        if len(player.hand.get_all_cards()) == 0 or not card:
            self.passed[player.id] = True

        self.current_player, self.current_card_source = self._determine_current_player(card, player)

        if self.round_over():
            self.current_player, self.current_card_source = self._end_of_round()

    def round_over(self):
        return all(self.passed.values())

    def game_over(self):
        return self._player_won() or self.current_round == 3

    def get_winner(self) -> Player:
        winner = None
        if self.player1.rounds_won == 2 and self.player2.rounds_won != 2:
            winner = self.player1
        elif self.player2.rounds_won == 2 and self.player1.rounds_won != 2:
            winner = self.player2
        return winner

    def _player_won(self):
        return self.player1.rounds_won >= 2 or self.player2.rounds_won >= 2

    def _end_of_round(self) -> Tuple[Player, CardSource]:
        self.current_round += 1

        player1_damage = self.board.calculate_damage(self.player1)
        player2_damage = self.board.calculate_damage(self.player2)

        current_player = self.current_player
        if player1_damage > player2_damage:
            self.player1.rounds_won += 1
            current_player = self.player1
            northern_realms_check_extra_card(self.player1)
        elif player1_damage < player2_damage:
            self.player2.rounds_won += 1
            current_player = self.player2
            northern_realms_check_extra_card(self.player2)
        else:
            nilfgaard_check_draw(self)
        card_source = CardSource.HAND

        self.board.all_cards_to_graveyard(self.player1)
        self.board.all_cards_to_graveyard(self.player2)
        self.passed = {self.player1.id: False, self.player2.id: False}

        self.board.weather = [Weather.CLEAR]

        return current_player, card_source

    def _determine_current_player(self, played_card: Card, player: Player) -> Tuple[Player, CardSource]:
        if played_card and played_card.ability is Ability.MEDIC and len(player.graveyard.get_all_cards()):
            result = self.current_player, CardSource.GRAVEYARD
        else:
            enemy = self.board.get_enemy_player(self.current_player)
            if self.passed[enemy.id]:
                result = self.current_player, CardSource.HAND
            else:
                result = enemy, CardSource.HAND

        return result

    def __deepcopy__(self, memodict={}):
        copy = GameEnvironment(deepcopy(self.player1), deepcopy(self.player2))

        board = copy.board
        board.player1 = copy.player1
        board.player2 = copy.player2
        board.cards = deepcopy(self.board.cards)
        board.weather = deepcopy(self.board.weather)

        copy.current_player = copy.board.get_player(self.current_player)
        copy.passed = deepcopy(self.passed)
        copy.current_card_source = deepcopy(self.current_card_source)
        copy.current_round = deepcopy(self.current_round)
        return copy
