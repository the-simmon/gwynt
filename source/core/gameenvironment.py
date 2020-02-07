from __future__ import annotations

import enum
import random
from copy import deepcopy
from typing import Tuple, Dict, Optional, List

from source.core.board import Board
from source.core.card import Ability, LeaderCard, LeaderAbility
from source.core.card import Card
from source.core.cards.util import get_cards
from source.core.comabt_row import CombatRow
from source.core.faction_abililty import nilfgaard_check_draw, northern_realms_check_extra_card, \
    scoiatael_decide_starting_player
from source.core.player import Player
from source.core.weather import Weather


class CardSource(enum.Enum):
    HAND = 0
    GRAVEYARD = 1


class PassiveLeaderState:

    def __init__(self):
        # Leader card 'Emhyr var Emreis: The White Flame'
        self.block_leader = False
        # Emhyr var Emreis: Invader of the North
        self.random_medic = False
        self.leaders_ability: List[LeaderAbility] = []

    def check_leader(self, leader: LeaderCard):
        if leader.is_passive() and not self.block_leader:
            self.leaders_ability.append(leader.leader_ability)
            if leader.leader_ability is LeaderAbility.BLOCK_LEADER:
                self._set_block_leader()
            elif leader.leader_ability is LeaderAbility.RANDOM_MEDIC:
                self._set_random_medic()

    def _set_block_leader(self):
        self.block_leader = True
        self.random_medic = False
        self.leaders_ability = [LeaderAbility.BLOCK_LEADER]

    def _set_random_medic(self):
        self.random_medic = True


class GameEnvironment:

    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.next_player = None
        self.next_card_source = CardSource.HAND

        self.passive_leader_state = PassiveLeaderState()
        passive_leaders = self._check_passive_leaders()
        self.board = Board(player1, player2, passive_leaders)

        self.card_tracker = _PossibleCardsTracker(self)

        self.current_round = 0
        self.passed: Dict[int, bool] = {player1.id: False, player2.id: False}
        self.played_cards: Dict[int, List[Card]] = {player1.id: [], player2.id: []}

    def _check_passive_leaders(self) -> List[LeaderAbility]:
        for player in [self.player1, self.player2]:
            self.passive_leader_state.check_leader(player.leader)
        return self.passive_leader_state.leaders_ability

    def init(self):
        self.next_player = scoiatael_decide_starting_player(self)
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
            if self.next_card_source is CardSource.HAND:
                player.hand.remove(card.combat_row, card)
            else:
                player.graveyard.remove(card.combat_row, card)
            self.board.add(player, row, card)
            self.played_cards[player.id].append(card)

        self._end_of_step(player, card)
        return self.game_over(), self.next_player, self.next_card_source

    def step_decoy(self, player: Player, row: CombatRow, decoy: Card, replace_card: Card) \
            -> Tuple[bool, Player, CardSource]:
        player.hand.remove(decoy.combat_row, decoy)
        player.hand.add(replace_card.combat_row, replace_card)
        self.board.add(player, row, decoy)

        self.board.remove(player, row, replace_card, ignore_graveyard=True)
        if replace_card in self.played_cards[player.id]:
            self.played_cards[player.id].remove(replace_card)

        self._end_of_step(player, decoy)
        return self.game_over(), self.next_player, self.next_card_source

    def _end_of_step(self, player: Player, card: Card):
        if len(player.hand.get_all_cards()) == 0 or not card:
            self.passed[player.id] = True

        self.next_player, self.next_card_source = self._determine_current_player(card, player)

        if self.round_over():
            self.next_player, self.next_card_source = self._end_of_round()

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

        current_player = self.next_player
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
            result = self.next_player, CardSource.GRAVEYARD
        else:
            enemy = self.board.get_enemy_player(self.next_player)
            if self.passed[enemy.id]:
                result = self.next_player, CardSource.HAND
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

        copy.next_player = copy.board.get_player(self.next_player)
        copy.passed = deepcopy(self.passed)
        copy.next_card_source = deepcopy(self.next_card_source)
        copy.current_round = deepcopy(self.current_round)
        return copy


class _PossibleCardsTracker:

    def __init__(self, environment: GameEnvironment):
        self.environment = environment

    def get_possible_cards(self, obfuscate: bool) -> List[Card]:
        """Returns all cards current player can play. If obfuscate is true, the hand is ignored and only not played
        cards are returned """
        if self.environment.next_card_source is CardSource.HAND:
            if not obfuscate:
                result = self.environment.next_player.hand.get_all_cards()
            else:
                not_played_cards = self.get_available_cards()
                result = list(set(not_played_cards))
        else:
            # leader ability
            result = self.environment.next_player.graveyard.get_all_cards()
            if self.environment.passive_leader_state.random_medic:
                result = [random.choice(result)]

        return result

    def get_available_cards(self) -> List[Card]:
        environment = self.environment
        all_cards = get_cards(environment.next_player.faction)
        played_cards = environment.played_cards[environment.next_player.id]
        played_cards.extend(environment.next_player.graveyard.get_all_cards())

        for card in played_cards:
            if card in all_cards:
                all_cards.remove(card)

        return all_cards
