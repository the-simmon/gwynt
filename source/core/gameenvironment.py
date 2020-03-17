from __future__ import annotations

import enum
import random
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
from source.game_settings import GameSettings


class CardSource(enum.Enum):
    HAND = 0
    GRAVEYARD = 1
    ENEMY_GRAVEYARD = 2
    LEADER = 3
    WEATHER_DECK = 4
    WEATHER_RAIN = 5
    WEATHER_FOG = 6
    WEATHER_FROST = 7
    EXCHANGE_HAND_4_DECK2 = 8
    EXCHANGE_HAND_4_DECK1 = 9
    DECK = 10
    AGILE_2_BEST_ROW = 11
    BOARD = 12

    # only for witcher mode
    SPY2 = 13
    SPY1 = 14

    @staticmethod
    def is_weather(source: CardSource) -> bool:
        return source is CardSource.WEATHER_DECK or source is CardSource.WEATHER_RAIN or \
               source is CardSource.WEATHER_FOG or source is CardSource.WEATHER_FROST

    @staticmethod
    def is_exchange_hand_4_deck(source: CardSource) -> bool:
        return source is CardSource.EXCHANGE_HAND_4_DECK1 or source is CardSource.EXCHANGE_HAND_4_DECK2

    @staticmethod
    def is_deck(source: CardSource) -> bool:
        return CardSource.is_weather(source) or source is CardSource.DECK or CardSource.is_spy(
            source) or CardSource.is_exchange_hand_4_deck(source)

    @staticmethod
    def is_spy(source: CardSource) -> bool:
        return source is CardSource.SPY2 or source is CardSource.SPY1


class CardDestination(enum.Enum):
    BOARD = 0
    HAND = 1
    GRAVEYARD = 2


class PassiveLeaderState:

    def __init__(self):
        # Leader card 'Emhyr var Emreis: The White Flame'
        self.block_leader = False
        # Emhyr var Emreis: Invader of the North
        self.random_medic = False
        # Francesca Findabair: Daisy of the Valley
        self.extra_card = False
        self.extra_card_player = None

        self.leaders_ability: List[LeaderAbility] = []

    def check_leader(self, player: Player, leader: LeaderCard):
        if leader and leader.is_passive() and not self.block_leader:
            self.leaders_ability.append(leader.leader_ability)
            if leader.leader_ability is LeaderAbility.BLOCK_LEADER:
                self._set_block_leader()
            elif leader.leader_ability is LeaderAbility.RANDOM_MEDIC:
                self._set_random_medic()
            elif leader.leader_ability is LeaderAbility.EXTRA_CARD:
                self._set_extra_card(player)

    def _set_block_leader(self):
        self.block_leader = True
        self.random_medic = False
        self.extra_card = False
        self.leaders_ability = [LeaderAbility.BLOCK_LEADER]

    def _set_random_medic(self):
        self.random_medic = True

    def _set_extra_card(self, player: Player):
        self.extra_card = True
        self.extra_card_player = player


class GameEnvironment:

    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.next_player = None
        self.next_card_source = CardSource.HAND
        self.next_card_destination = CardDestination.BOARD

        self.passive_leader_state = PassiveLeaderState()
        passive_leaders = self._check_passive_leaders()
        self.board = Board(player1, player2, passive_leaders)

        self.card_tracker = _PossibleCardsTracker(self)

        self.current_round = 0
        self.passed: Dict[int, bool] = {player1.id: False, player2.id: False}
        self.played_cards: Dict[int, List[Card]] = {player1.id: [], player2.id: []}

    def _check_passive_leaders(self) -> List[LeaderAbility]:
        for player in [self.player1, self.player2]:
            self.passive_leader_state.check_leader(player, player.leader)
        return self.passive_leader_state.leaders_ability

    def init(self):
        self.next_player = scoiatael_decide_starting_player(self)
        self._chose_hand()

    def _chose_hand(self):
        for player in [self.player1, self.player2]:

            #  random.choices not applicable, because it can return the same object multiple times
            deck_cards = player.deck.get_all_cards()
            random.shuffle(deck_cards)

            card_count = 10
            if self.passive_leader_state.extra_card and self.passive_leader_state.extra_card_player is player:
                card_count += 1
            chosen_cards = deck_cards[:card_count]

            for card in chosen_cards:
                player.deck.remove(card.combat_row, card)
                player.hand.add(card.combat_row, card)

    def step(self, player: Player, row: Optional[CombatRow], card: Optional[Card]) -> bool:
        # card == None => player passes
        if card:
            self._remove_card_from_source(player, card)
            self._add_card_to_destination(player, row, card)

        self._end_of_step(player, card)
        return self.game_over()

    def _remove_card_from_source(self, player: Player, card: Card):
        if self.next_card_source is CardSource.HAND or CardSource.is_exchange_hand_4_deck(self.next_card_source):
            player.hand.remove(card.combat_row, card)
        elif self.next_card_source is CardSource.GRAVEYARD:
            player.graveyard.remove(card.combat_row, card)
        elif CardSource.is_deck(self.next_card_source):
            player.deck.remove(card.combat_row, card)

    def add_card_to_source(self, player: Player, card: Card):
        if self.next_card_source is CardSource.HAND or CardSource.is_exchange_hand_4_deck(self.next_card_source):
            player.hand.add(card.combat_row, card)
        elif self.next_card_source is CardSource.GRAVEYARD:
            player.graveyard.add(card.combat_row, card)
        elif CardSource.is_deck(self.next_card_source):
            player.deck.add(card.combat_row, card)

    def _add_card_to_destination(self, player: Player, row: CombatRow, card: Card):
        if self.next_card_destination is CardDestination.BOARD:
            self.board.add(player, row, card)
            if self.next_card_source is CardSource.HAND:
                self.played_cards[player.id].append(card)
        elif self.next_card_destination is CardDestination.HAND:
            player.hand.add(card.combat_row, card)
        elif self.next_card_destination is CardDestination.GRAVEYARD:
            player.graveyard.add(card.combat_row, card)

    def step_decoy(self, player: Player, row: CombatRow, decoy: Card, replace_card: Card) -> bool:
        player.hand.remove(decoy.combat_row, decoy)
        player.hand.add(replace_card.combat_row, replace_card)
        self.board.add(player, row, decoy)

        self.board.remove(player, row, replace_card, ignore_graveyard=True)
        if replace_card in self.played_cards[player.id]:
            self.played_cards[player.id].remove(replace_card)

        self._end_of_step(player, decoy)
        return self.game_over()

    def step_leader(self, player: Player, card: LeaderCard) -> bool:
        player.leader = None
        if not self.passive_leader_state.block_leader:
            if card.leader_ability is LeaderAbility.NONE:
                self.next_card_source = CardSource.LEADER
                result = self.step(player, card.combat_row, card)
            else:
                self.next_player = player
                self._handle_leader_ability(card)
                result = self.game_over()
        else:
            result = self.game_over()
        return result

    def _handle_leader_ability(self, card: LeaderCard):
        if card.leader_ability is LeaderAbility.GRAVEYARD2HAND:
            self.next_card_source = CardSource.GRAVEYARD
            self.next_card_destination = CardDestination.HAND
        elif card.leader_ability is LeaderAbility.ENEMY_GRAVEYARD2HAND:
            self.next_card_source = CardSource.ENEMY_GRAVEYARD
            self.next_card_destination = CardDestination.HAND
        elif card.leader_ability is LeaderAbility.PICK_WEATHER:
            self.next_card_source = CardSource.WEATHER_DECK
            self.next_card_destination = CardDestination.BOARD
        elif card.leader_ability is LeaderAbility.RAIN_DECK:
            self.next_card_source = CardSource.WEATHER_RAIN
            self.next_card_destination = CardDestination.BOARD
        elif card.leader_ability is LeaderAbility.FOG_DECK:
            self.next_card_source = CardSource.WEATHER_FOG
            self.next_card_destination = CardDestination.BOARD
        elif card.leader_ability is LeaderAbility.FROST_DECK:
            self.next_card_source = CardSource.WEATHER_FROST
            self.next_card_destination = CardDestination.BOARD
        elif card.leader_ability is LeaderAbility.SWAP_CARDS:
            self.next_card_source = CardSource.EXCHANGE_HAND_4_DECK2
            self.next_card_destination = CardDestination.GRAVEYARD
        elif card.leader_ability is LeaderAbility.OPTIMIZE_AGILE:
            self.board.agile_to_best_row_leader(self.next_player)
            # source and destination will be reverted by the if block below, as this leader does not play a card
            self.next_card_source = CardSource.AGILE_2_BEST_ROW

        # revert leader ability if no cards can be placed on the board, to avoid blocking
        if not self.card_tracker.get_possible_cards(False):
            self.next_card_source = CardSource.HAND
            self.next_card_destination = CardDestination.BOARD
            enemy = self.board.get_enemy_player(self.next_player)
            if not self.passed[enemy.id]:
                self.next_player = enemy

    def _end_of_step(self, player: Player, card: Card):
        if len(player.hand.get_all_cards()) == 0 or not card:
            self.passed[player.id] = True

        self.next_player, self.next_card_source, self.next_card_destination = self._determine_current_player(card,
                                                                                                             player)

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

    def _determine_current_player(self, played_card: Card, player: Player) -> Tuple[
        Player, CardSource, CardDestination]:
        if played_card and played_card.ability is Ability.MEDIC and len(player.graveyard.get_all_cards()):
            result = self.next_player, CardSource.GRAVEYARD, CardDestination.BOARD

        # pick cards obtained by spy manually when playing in witcher mode
        elif played_card and played_card.ability is Ability.SPY and player.id == 0 and \
                GameSettings.PLAY_AGAINST_WITCHER and self.next_card_source is CardSource.HAND:
            result = player, CardSource.SPY2, CardDestination.HAND

        elif self.next_card_source is CardSource.SPY2:
            result = player, CardSource.SPY1, CardDestination.HAND

        elif CardSource.is_exchange_hand_4_deck(self.next_card_source):
            if self.next_card_source is CardSource.EXCHANGE_HAND_4_DECK2:
                result = player, CardSource.EXCHANGE_HAND_4_DECK1, CardDestination.GRAVEYARD
            else:
                result = player, CardSource.DECK, CardDestination.HAND

        else:
            enemy = self.board.get_enemy_player(self.next_player)
            if self.passed[enemy.id]:
                result = self.next_player, CardSource.HAND, CardDestination.BOARD
            else:
                result = enemy, CardSource.HAND, CardDestination.BOARD

        return result


class _PossibleCardsTracker:

    def __init__(self, environment: GameEnvironment):
        self.environment = environment

    def get_possible_cards(self, obfuscate: bool) -> List[Card]:
        """Returns all cards current player can play. If obfuscate is true, the hand is ignored and only not played
        cards are returned """
        result = []
        card_source = self.environment.next_card_source
        if card_source is CardSource.HAND or CardSource.is_deck(card_source):
            if obfuscate:
                result = self._get_available_cards()
                result = list(set(result))
            else:
                if card_source is CardSource.HAND or CardSource.is_exchange_hand_4_deck(card_source):
                    result = self.environment.next_player.hand.get_all_cards()
                elif card_source is CardSource.DECK:
                    result = self.environment.next_player.deck.get_all_cards()
                else:  # card_source is some kind of weather from deck
                    result = self.environment.next_player.deck.get_all_cards()

            if CardSource.is_weather(card_source):
                result = self._filter_weather(result, card_source)

        elif card_source is CardSource.GRAVEYARD or card_source is CardSource.ENEMY_GRAVEYARD:
            if card_source is CardSource.GRAVEYARD:
                result = self.environment.next_player.graveyard.get_all_cards()
            else:  # card_source is CardSource.ENEMY_GRAVEYARD
                enemy = self.environment.board.get_enemy_player(self.environment.next_player)
                result = enemy.graveyard.get_all_cards()
            result = self._filter_non_revivable_cards(result)

            # leader ability
            if self.environment.passive_leader_state.random_medic and result:
                result = [random.choice(result)]
        return result

    def _filter_weather(self, cards: List[Card], card_source: CardSource) -> List[Card]:
        if card_source is CardSource.WEATHER_DECK:
            cards = [card for card in cards if Weather.ability_is_weather(card.ability)]
        elif card_source is CardSource.WEATHER_RAIN:
            cards = [card for card in cards if card.ability is Ability.RAIN]
        elif card_source is CardSource.WEATHER_FOG:
            cards = [card for card in cards if card.ability is Ability.FOG]
        elif card_source is CardSource.WEATHER_FROST:
            cards = [card for card in cards if card.ability is Ability.FROST]

        return cards

    def _filter_non_revivable_cards(self, cards: List[Card]) -> List[Card]:
        # remove cards that cannot be revived
        for card in cards:
            if card.hero or card.combat_row is CombatRow.SPECIAL or card.combat_row is CombatRow.NONE or \
                    type(card) is LeaderCard:
                cards.remove(card)
        return cards

    def _get_available_cards(self) -> List[Card]:
        environment = self.environment
        all_cards = get_cards(environment.next_player.faction)
        played_cards = environment.played_cards[environment.next_player.id]
        played_cards.extend(environment.next_player.graveyard.get_all_cards())

        for card in played_cards:
            if card in all_cards:
                all_cards.remove(card)

        return all_cards
