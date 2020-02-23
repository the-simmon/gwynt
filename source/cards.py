from source.core.card import Card, Ability, LeaderCard, LeaderAbility
from source.core.cards.flatten import flatten
from source.core.comabt_row import CombatRow
from source.core.player import Faction

deck = [
    Card(CombatRow.CLOSE, 15, hero=True) * 2,
    Card(CombatRow.RANGE, 7, Ability.MEDIC, hero=True),
    Card(CombatRow.CLOSE, 7, hero=True),
    Card(CombatRow.CLOSE, 7, Ability.SCORCH),
    Card(CombatRow.CLOSE, 6),
    Card(CombatRow.AGILE, 6, Ability.MORALE_BOOST),
    Card(CombatRow.CLOSE, 5) * 2,
    Card(CombatRow.CLOSE, 0, Ability.SPY, hero=True),
    Card(CombatRow.CLOSE, 10, hero=True),
    Card(CombatRow.CLOSE, 10, Ability.MEDIC, hero=True),
    Card(CombatRow.SIEGE, 10, hero=True),
    Card(CombatRow.RANGE, 10, hero=True),
    Card(CombatRow.RANGE, 10) * 2,
    Card(CombatRow.SIEGE, 10),
    Card(CombatRow.RANGE, 6) * 2,
    Card(CombatRow.CLOSE, 6),
    Card(CombatRow.SIEGE, 6),
    Card(CombatRow.CLOSE, 5, Ability.TIGHT_BOND)
]

deck = flatten(deck)

leader = LeaderCard(CombatRow.NONE, 0, Ability.NONE, leader_ability=LeaderAbility.ENEMY_GRAVEYARD2HAND)

faction = Faction.NILFGAARD
