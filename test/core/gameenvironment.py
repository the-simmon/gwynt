import unittest
from unittest.mock import patch

from source.core.card import Card, LeaderCard, LeaderAbility, Ability
from source.core.cardcollection import CardCollection
from source.core.cards.util import get_cards
from source.core.comabt_row import CombatRow
from source.core.gameenvironment import GameEnvironment, CardSource, PassiveLeaderState, _PossibleCardsTracker
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
        expected = (False, self.player2, CardSource.HAND)
        card = self.player1.hand[CombatRow.CLOSE][0]
        self.environment.current_player = self.player1
        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertCountEqual(expected, actual)

    def test_pass(self):
        card = self.player1.hand[CombatRow.CLOSE][0]
        self.environment.step(self.player1, card.combat_row, card)

        self.environment.current_player = self.player1
        actual = self.environment.step(self.player1, None, None)
        self.assertCountEqual((False, self.player2, CardSource.HAND), actual)

        actual = self.environment.step(self.player2, None, None)
        self.assertEqual((False, self.player1, CardSource.HAND), actual)

    def test_end_of_game(self):
        card = Card(CombatRow.CLOSE, 3)
        self.environment.current_round = 2

        self.player1.hand = CardCollection([card])
        self.player2.hand = CardCollection([card])

        self.environment.current_player = self.player1
        actual = self.environment.step(self.player1, card.combat_row, card)
        self.assertCountEqual((False, self.player2, CardSource.HAND), actual)

        actual = self.environment.step(self.player2, card.combat_row, card)
        self.assertCountEqual((True, self.player2, CardSource.HAND), actual)


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
        self.environment.current_player = self.player1

        self.environment.step(self.player1, self.player1_cards[0].combat_row, self.player1_cards[0])
        self.environment.current_player = self.player1
        self.environment.step(self.player1, self.player1_cards[1].combat_row, self.player1_cards[1])
        self.environment.current_player = self.player1

    def test_get_available_cards(self):
        self.player1_cards.pop(0)
        self.player1_cards.pop(1)
        actual = self.tracker.get_available_cards()
        self.assertCountEqual(self.player1_cards, actual)

    def test_get_available_cards_spy(self):
        self.environment.step(self.player1, self.player1_cards[2].combat_row, self.player1_cards[2])
        self.environment.current_player = self.player1
        self.player1_cards.pop(0)
        self.player1_cards.pop(1)
        self.player1_cards.pop(2)
        actual = self.tracker.get_available_cards()
        self.assertCountEqual(self.player1_cards, actual)

    def test_get_hand_count(self):
        actual = self.tracker.get_hand_count()
        self.assertEqual(8, actual)

    def test_get_possible_cards(self):
        actual = self.tracker.get_possible_cards(False)
        self.assertCountEqual(self.player1_cards[2:10], actual)

    def test_get_possible_cards_obfuscate(self):
        actual = self.tracker.get_possible_cards(True)
        self.assertCountEqual(set(self.player1_cards[2:]), actual)

    def test_get_possible_cards_medic(self):
        self.environment.current_card_source = CardSource.GRAVEYARD
        self.player1.graveyard = CardCollection(
            [Card(CombatRow.CLOSE, 6), Card(CombatRow.SIEGE, 6), Card(CombatRow.CLOSE, 2)])

        expected = self.player1.graveyard.get_all_cards()
        actual = self.tracker.get_possible_cards(False)
        self.assertCountEqual(expected, actual)

    @patch('random.choice', lambda x: x[0])
    def test_get_possible_cards_random_medic_leader(self):
        self.environment.current_card_source = CardSource.GRAVEYARD
        self.environment.passive_leader_state.random_medic = True
        self.player1.graveyard = CardCollection(
            [Card(CombatRow.CLOSE, 6), Card(CombatRow.SIEGE, 6), Card(CombatRow.CLOSE, 2)])

        expected = self.player1.graveyard.get_all_cards()[0]
        actual = self.tracker.get_possible_cards(False)
        self.assertCountEqual([expected], actual)
