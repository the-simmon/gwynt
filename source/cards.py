from source.core.card import Card, Ability, LeaderCard
from source.core.cards.flatten import flatten
from source.core.comabt_row import CombatRow
from source.core.player import Faction

deck = [
    Card(CombatRow.CLOSE, 8) * 4,
    Card(CombatRow.CLOSE, 3, Ability.TIGHT_BOND) * 4,
    Card(CombatRow.RANGE, 4, hero=True),
    Card(CombatRow.CLOSE, 5) * 8
]

deck = flatten(deck)

leader = LeaderCard(CombatRow.RANGE, 0, Ability.SPECIAL_COMMANDERS_HORN)

faction = Faction.NILFGAARD
