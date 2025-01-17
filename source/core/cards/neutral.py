from source.core.card import Card, Ability
from source.core.cards.flatten import flatten
from source.core.comabt_row import CombatRow

cards = [
    Card(CombatRow.NONE, 0, Ability.FROST) * 3,
    Card(CombatRow.CLOSE, 15, hero=True),
    Card(CombatRow.NONE, 0, Ability.CLEAR_WEATHER) * 2,
    Card(CombatRow.SPECIAL, 0, Ability.SPECIAL_COMMANDERS_HORN) * 4,
    Card(CombatRow.CLOSE, 2, Ability.COMMANDERS_HORN),
    Card(CombatRow.SPECIAL, 0, Ability.DECOY) * 3,
    Card(CombatRow.CLOSE, 5),
    Card(CombatRow.CLOSE, 15, hero=True),
    Card(CombatRow.NONE, 0, Ability.FOG),
    Card(CombatRow.CLOSE, 0, Ability.SPY, hero=True),
    Card(CombatRow.NONE, 0, Ability.SCORCH) * 3,
    Card(CombatRow.NONE, 0, Ability.RAIN),
    Card(CombatRow.CLOSE, 7, hero=True),
    Card(CombatRow.CLOSE, 6),
    Card(CombatRow.CLOSE, 7, Ability.SCORCH),
    Card(CombatRow.RANGE, 7, Ability.MEDIC, hero=True),
    Card(CombatRow.CLOSE, 5),
]

cards = flatten(cards)
