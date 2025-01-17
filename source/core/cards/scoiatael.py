from source.core.card import Card, Ability, Muster, LeaderCard, LeaderAbility
from source.core.cards.flatten import flatten
from source.core.comabt_row import CombatRow

cards = [
    Card(CombatRow.AGILE, 6),
    Card(CombatRow.AGILE, 3),
    Card(CombatRow.CLOSE, 6),
    Card(CombatRow.CLOSE, 4),
    Card(CombatRow.AGILE, 6) * 3,
    Card(CombatRow.CLOSE, 3, Ability.MUSTER, muster=Muster.DWARVEN_SKIRMISHER) * 3,
    Card(CombatRow.RANGE, 10, hero=True),
    Card(CombatRow.RANGE, 2, Ability.MUSTER, muster=Muster.ELVEN_SKIRMISHER) * 3,
    Card(CombatRow.AGILE, 6),
    Card(CombatRow.RANGE, 0, Ability.MEDIC) * 3,
    Card(CombatRow.CLOSE, 5, Ability.MUSTER, muster=Muster.HAVEKAR_SMUGGLER) * 3,
    Card(CombatRow.RANGE, 6),
    Card(CombatRow.RANGE, 10, hero=True),
    Card(CombatRow.CLOSE, 10, hero=True),
    Card(CombatRow.CLOSE, 5) * 5,
    Card(CombatRow.RANGE, 10, Ability.MORALE_BOOST),
    Card(CombatRow.RANGE, 1),
    Card(CombatRow.RANGE, 10, hero=True),
    Card(CombatRow.SIEGE, 8, Ability.SCORCH),
    Card(CombatRow.RANGE, 2),
    Card(CombatRow.RANGE, 4),
    Card(CombatRow.AGILE, 5) * 2,
    Card(CombatRow.AGILE, 6),
]

cards = flatten(cards)

leaders = [
    LeaderCard(leader_ability=LeaderAbility.EXTRA_CARD),
    LeaderCard(leader_ability=LeaderAbility.OPTIMIZE_AGILE),
    LeaderCard(leader_ability=LeaderAbility.FROST_DECK),
    LeaderCard(CombatRow.CLOSE, ability=Ability.SCORCH),
    LeaderCard(CombatRow.RANGE, ability=Ability.SPECIAL_COMMANDERS_HORN)
]
