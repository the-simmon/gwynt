from __future__ import annotations

import enum
from copy import deepcopy

from source.core.comabt_row import CombatRow


class Ability(enum.Enum):
    NONE = 0
    DECOY = 1
    MEDIC = 2
    MORALE_BOOST = 3
    MUSTER = 4
    SPY = 5
    TIGHT_BOND = 6
    SCORCH = 7
    COMMANDERS_HORN = 8
    SPECIAL_COMMANDERS_HORN = 9
    CLEAR_WEATHER = 10
    FROST = 11
    FOG = 12
    RAIN = 13
    PASS = 14

    @staticmethod
    def is_weather(ability: Ability) -> bool:
        return ability is Ability.CLEAR_WEATHER or ability is Ability.FROST or ability is Ability.FOG or \
               ability is Ability.RAIN

    def __lt__(self, other):
        return self.value < other.value


class Muster(enum.Enum):
    NONE = 0
    ARACHAS = 1
    CRONE = 2
    DWARVEN_SKIRMISHER = 3
    ELVEN_SKIRMISHER = 4
    GHOUL = 5
    HAVEKAR_SMUGGLER = 6
    NEKKER = 7
    VAMPIRE = 8


class Card:

    def __init__(self, combat_row: CombatRow, damage: int, ability: Ability = Ability.NONE, hero: bool = False,
                 muster: Muster = Muster.NONE):
        self.combat_row = combat_row
        self.damage = damage
        self.ability = ability
        self.hero = hero
        self.muster = muster

    def __eq__(self, other):
        return other is not None and self.combat_row is other.combat_row and self.damage == other.damage and \
               self.ability is other.ability and self.muster is other.muster and self.hero is other.hero

    def __hash__(self):
        return hash(self.combat_row) + self.damage + hash(self.ability) + hash(self.muster)

    def __mul__(self, count: int):
        return [deepcopy(self) for _ in range(count)]

    def __str__(self):
        return str(self.combat_row) + ' ' + str(self.damage) + ' ' + str(self.ability) + ' ' + str(
            self.hero) + ' ' + str(self.muster)


class LeaderAbility(enum.Enum):
    NONE = 0
    SPY_DAMAGE = 1
    GRAVEYARD2HAND = 2
    SWAP_CARDS = 3
    PICK_WEATHER = 4
    RAIN_DECK = 5
    RANDOM_MEDIC = 6
    ENEMY_GRAVEYARD2HAND = 7
    BLOCK_LEADER = 8
    FOG_DECK = 9
    EXTRA_CARD = 10
    OPTIMIZE_AGILE = 11
    FROST_DECK = 12


class LeaderCard(Card):

    def __init__(self, combat_row: CombatRow = CombatRow.NONE, damage: int = 0, ability: Ability = Ability.NONE,
                 hero: bool = False, muster: Muster = Muster.NONE,
                 leader_ability: LeaderAbility = LeaderAbility.NONE):
        super(LeaderCard, self).__init__(combat_row, damage, ability, hero, muster)
        self.leader_ability = leader_ability

    def is_passive(self):
        return self.leader_ability is LeaderAbility.SPY_DAMAGE or self.leader_ability is LeaderAbility.RANDOM_MEDIC or \
               self.leader_ability is LeaderAbility.BLOCK_LEADER or self.leader_ability is LeaderAbility.EXTRA_CARD
