import unittest
from unittest.mock import patch

from source.core.card import Card, LeaderCard, LeaderAbility, Ability
from source.core.cardcollection import CardCollection
from source.core.cards.util import get_cards
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource, PassiveLeaderState, _PossibleCardsTracker, \
    CardDestination
from source.core.player import Player, Faction


class GameEnvironmentTest(unittest.TestCase):

    def setUp(self):
        self.player1 = Player(1, Faction.NOTHERN_REALMS, Card(CombatRow.CLOSE, 6) * 22, LeaderCard())
        self.player2 = Player(2, Faction.NILFGAARD, Card(CombatRow.RANGE, 10) * 22, LeaderCard())
        self.environment = GameEnvironment(self.player1, self.player2)
        self.environment.init()

    def test_active_card_choice(self):
        self.assertEqual(10, len(self.player1.hand.get_all_cards()))
        self.assertEqual(10, len(self.player2.hand.get_all_cards()))

    def test_step(self):
        card = self.player1.hand[CombatRow.CLOSE][0]
        self.environment.next_player = self.player1
        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual(False, actual)
        self.assertEqual(self.player2, self.environment.next_player)
        self.assertEqual(CardSource.HAND, self.environment.next_card_source)
        self.assertEqual(CardDestination.BOARD, self.environment.next_card_destination)

    def test_pass(self):
        card = self.player1.hand[CombatRow.CLOSE][0]
        self.environment.step(self.player1, card.combat_row, card)

        self.environment.next_player = self.player1
        actual = self.environment.step(self.player1, None, None)
        self.assertEqual(False, actual)
        self.assertEqual(self.player2, self.environment.next_player)
        self.assertEqual(CardSource.HAND, self.environment.next_card_source)
        self.assertEqual(CardDestination.BOARD, self.environment.next_card_destination)

        actual = self.environment.step(self.player2, None, None)
        self.assertEqual(False, actual)
        self.assertEqual(self.player1, self.environment.next_player)
        self.assertEqual(CardSource.HAND, self.environment.next_card_source)
        self.assertEqual(CardDestination.BOARD, self.environment.next_card_destination)

    def test_end_of_game(self):
        card = Card(CombatRow.CLOSE, 3)
        self.environment.current_round = 2

        self.player1.hand = CardCollection([card])
        self.player2.hand = CardCollection([card])

        self.environment.next_player = self.player1
        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertEqual(False, actual)
        self.assertEqual(self.player2, self.environment.next_player)
        self.assertEqual(CardSource.HAND, self.environment.next_card_source)
        self.assertEqual(CardDestination.BOARD, self.environment.next_card_destination)

        actual = self.environment.step(self.player2, card.combat_row, card)
        self.assertEqual(True, actual)
        self.assertEqual(self.player2, self.environment.next_player)
        self.assertEqual(CardSource.HAND, self.environment.next_card_source)
        self.assertEqual(CardDestination.BOARD, self.environment.next_card_destination)

    def test_step_decoy(self):
        card_to_replace = Card(CombatRow.CLOSE, 3)
        decoy = Card(CombatRow.SPECIAL, 0, Ability.DECOY)
        expected = self.player1.hand.get_all_cards() + [card_to_replace]
        self.player1.hand.add(CombatRow.SPECIAL, decoy)
        self.environment.board.cards[self.player1.id].add(card_to_replace.combat_row, card_to_replace)
        self.environment.next_player = self.player1

        self.environment.step_decoy(self.player1, CombatRow.CLOSE, decoy, card_to_replace)
        self.assertCountEqual(expected, self.player1.hand.get_all_cards())
        self.assertCountEqual([decoy], self.environment.board.cards[self.player1.id].get_all_cards())
        self.assertEqual(CardDestination.BOARD, self.environment.next_card_destination)

    def test_normal_leader(self):
        leader = LeaderCard(CombatRow.CLOSE, 1)
        self.environment.step_leader(self.player1, leader)

        self.assertCountEqual([leader], self.environment.board.cards[self.player1.id].get_all_cards())
        self.assertEqual(CardSource.HAND, self.environment.next_card_source)
        self.assertEqual(CardDestination.BOARD, self.environment.next_card_destination)

    def test_blocked_leader(self):
        leader = LeaderCard(CombatRow.CLOSE, 1)
        self.environment.passive_leader_state.block_leader = True
        self.environment.step_leader(self.player1, leader)

        self.assertCountEqual([], self.environment.board.cards[self.player1.id].get_all_cards())
        self.assertEqual(CardSource.HAND, self.environment.next_card_source)
        self.assertEqual(CardDestination.BOARD, self.environment.next_card_destination)

    def test_graveyard2hand_leader(self):
        self.environment.step_leader(self.player1, LeaderCard(leader_ability=LeaderAbility.GRAVEYARD2HAND))
        self.assertEqual(CardSource.GRAVEYARD, self.environment.next_card_source)
        self.assertEqual(CardDestination.HAND, self.environment.next_card_destination)


class PassiveLeaderStateTest(unittest.TestCase):

    def setUp(self):
        self.state = PassiveLeaderState()

    def test_no_leader(self):
        self.assertEqual(False, self.state.block_leader)
        self.assertEqual(False, self.state.random_medic)
        self.assertCountEqual([], self.state.leaders_ability)

    def test_active_leader(self):
        self.state.check_leader(LeaderCard())
        self.assertEqual(False, self.state.block_leader)
        self.assertEqual(False, self.state.random_medic)
        self.assertCountEqual([], self.state.leaders_ability)

    def test_block_leader(self):
        self.state.check_leader(LeaderCard(leader_ability=LeaderAbility.BLOCK_LEADER))
        self.assertEqual(True, self.state.block_leader)
        self.assertEqual(False, self.state.random_medic)
        self.assertCountEqual([LeaderAbility.BLOCK_LEADER], self.state.leaders_ability)

    def test_random_medic(self):
        self.state.check_leader(LeaderCard(leader_ability=LeaderAbility.RANDOM_MEDIC))
        self.assertEqual(False, self.state.block_leader)
        self.assertEqual(True, self.state.random_medic)
        self.assertCountEqual([LeaderAbility.RANDOM_MEDIC], self.state.leaders_ability)

    def test_block_leader_with_medic(self):
        self.state.check_leader(LeaderCard(leader_ability=LeaderAbility.RANDOM_MEDIC))
        self.state.check_leader(LeaderCard(leader_ability=LeaderAbility.BLOCK_LEADER))
        self.assertEqual(True, self.state.block_leader)
        self.assertEqual(False, self.state.random_medic)
        self.assertCountEqual([LeaderAbility.BLOCK_LEADER], self.state.leaders_ability)


class PossibleCardsTrackerTest(unittest.TestCase):

    def setUp(self):
        self.player1_cards = get_cards(Faction.NOTHERN_REALMS)

        self.player2_cards = get_cards(Faction.NILFGAARD)

        self.player1 = Player(1, Faction.NOTHERN_REALMS, self.player1_cards, LeaderCard())
        self.player2 = Player(2, Faction.NILFGAARD, self.player2_cards, LeaderCard())
        self.environment = GameEnvironment(self.player1, self.player2)
        self.tracker = _PossibleCardsTracker(self.environment)

        # for some weird reason '@patch('random.shuffle', lambda x: None') is only working once
        # otherwise a mock would be smarter instead of replacing the card in hand manually
        self.player1_cards[0] = Card(CombatRow.CLOSE, 1)
        self.player1_cards[1] = Card(CombatRow.CLOSE, 2)
        self.player1_cards[2] = Card(CombatRow.CLOSE, 2, Ability.SPY)
        self.player1_cards[3] = Card(CombatRow.RANGE, 2)
        self.player1_cards[4] = Card(CombatRow.CLOSE, 6)
        self.player1_cards[5] = Card(CombatRow.SIEGE, 6)
        self.player1_cards[6] = Card(CombatRow.CLOSE, 2)
        self.player1_cards[7] = Card(CombatRow.CLOSE, 5)
        self.player1_cards[8] = Card(CombatRow.CLOSE, 5)
        self.player1_cards[9] = Card(CombatRow.RANGE, 2)

        self.player1.hand = CardCollection(self.player1_cards[:10])
        self.environment.next_player = self.player1

        self.environment.step(self.player1, self.player1_cards[0].combat_row, self.player1_cards[0])
        self.environment.next_player = self.player1
        self.environment.step(self.player1, self.player1_cards[1].combat_row, self.player1_cards[1])
        self.environment.next_player = self.player1

    def test_get_available_cards(self):
        self.player1_cards.pop(0)
        self.player1_cards.pop(1)
        actual = self.tracker.get_available_cards()
        self.assertCountEqual(self.player1_cards, actual)

    def test_get_available_cards_spy(self):
        self.environment.step(self.player1, self.player1_cards[2].combat_row, self.player1_cards[2])
        self.environment.next_player = self.player1
        self.player1_cards.pop(0)
        self.player1_cards.pop(1)
        self.player1_cards.pop(2)
        actual = self.tracker.get_available_cards()
        self.assertCountEqual(self.player1_cards, actual)

    def test_get_possible_cards(self):
        actual = self.tracker.get_possible_cards(False)
        self.assertCountEqual(self.player1_cards[2:10], actual)

    def test_get_possible_cards_obfuscate(self):
        actual = self.tracker.get_possible_cards(True)
        self.assertCountEqual(set(self.player1_cards[2:]), actual)

    def test_get_possible_cards_medic(self):
        self.environment.next_card_source = CardSource.GRAVEYARD
        self.player1.graveyard = CardCollection(
            [Card(CombatRow.CLOSE, 6), Card(CombatRow.SIEGE, 6), Card(CombatRow.CLOSE, 2)])

        expected = self.player1.graveyard.get_all_cards()
        actual = self.tracker.get_possible_cards(False)
        self.assertCountEqual(expected, actual)

    @patch('random.choice', lambda x: x[0])
    def test_get_possible_cards_random_medic_leader(self):
        self.environment.next_card_source = CardSource.GRAVEYARD
        self.environment.passive_leader_state.random_medic = True
        self.player1.graveyard = CardCollection(
            [Card(CombatRow.CLOSE, 6), Card(CombatRow.SIEGE, 6), Card(CombatRow.CLOSE, 2)])

        expected = self.player1.graveyard.get_all_cards()[0]
        actual = self.tracker.get_possible_cards(False)
        self.assertCountEqual([expected], actual)

    def test_get_possible_cards_graveyard2hand_leader(self):
        self.player1.graveyard.add(CombatRow.CLOSE, Card(CombatRow.CLOSE, 8))
        self.player1.graveyard.add(CombatRow.CLOSE, Card(CombatRow.CLOSE, 9))
        expected = self.player1.graveyard.get_all_cards()
        self.environment.step_leader(self.player1, LeaderCard(leader_ability=LeaderAbility.GRAVEYARD2HAND))
        self.assertCountEqual(expected, self.tracker.get_possible_cards(False))
