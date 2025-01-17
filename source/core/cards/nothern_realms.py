from source.core.card import Card, Ability, LeaderCard, LeaderAbility
from source.core.cards.flatten import flatten
from source.core.comabt_row import CombatRow

cards = [
    Card(CombatRow.SIEGE, 6),
    Card(CombatRow.CLOSE, 4, Ability.TIGHT_BOND) * 3,
    Card(CombatRow.SIEGE, 8, Ability.TIGHT_BOND) * 2,
    Card(CombatRow.RANGE, 5, Ability.TIGHT_BOND) * 3,
    Card(CombatRow.RANGE, 6),
    Card(CombatRow.SIEGE, 5, Ability.MEDIC),
    Card(CombatRow.CLOSE, 10, hero=True),
    Card(CombatRow.CLOSE, 10, hero=True),
    Card(CombatRow.SIEGE, 1, Ability.MORALE_BOOST),
    Card(CombatRow.RANGE, 5),
    Card(CombatRow.RANGE, 10, hero=True),
    Card(CombatRow.CLOSE, 1, Ability.TIGHT_BOND) * 3,
    Card(CombatRow.CLOSE, 5, Ability.SPY),
    Card(CombatRow.CLOSE, 1),
    Card(CombatRow.RANGE, 4),
    Card(CombatRow.RANGE, 4),
    Card(CombatRow.SIEGE, 6),
    Card(CombatRow.CLOSE, 5),
    Card(CombatRow.CLOSE, 4, Ability.SPY),
    Card(CombatRow.RANGE, 5),
    Card(CombatRow.SIEGE, 1, Ability.SPY),
    Card(CombatRow.SIEGE, 6),
    Card(CombatRow.CLOSE, 10, hero=True),
    Card(CombatRow.CLOSE, 5),
    Card(CombatRow.CLOSE, 2),
]

cards = flatten(cards)

leaders = [
    LeaderCard(leader_ability=LeaderAbility.FOG_DECK),
    LeaderCard(ability=Ability.CLEAR_WEATHER),
    LeaderCard(CombatRow.RANGE, ability=Ability.SCORCH),
    LeaderCard(CombatRow.SIEGE, ability=Ability.SPECIAL_COMMANDERS_HORN),
    LeaderCard(CombatRow.SIEGE, ability=Ability.SCORCH)
]
