from source.core.card import Card, Ability, LeaderCard, LeaderAbility
from source.core.cards.flatten import flatten
from source.core.comabt_row import CombatRow

cards = [
    Card(CombatRow.RANGE, 2),
    Card(CombatRow.RANGE, 6),
    Card(CombatRow.RANGE, 10) * 2,
    Card(CombatRow.CLOSE, 6),
    Card(CombatRow.RANGE, 4),
    Card(CombatRow.RANGE, 1) * 2,
    Card(CombatRow.RANGE, 6),
    Card(CombatRow.SIEGE, 10),
    Card(CombatRow.CLOSE, 3, Ability.TIGHT_BOND) * 5,
    Card(CombatRow.CLOSE, 10, hero=True),
    Card(CombatRow.CLOSE, 10, Ability.MEDIC, hero=True),
    Card(CombatRow.CLOSE, 3),
    Card(CombatRow.SIEGE, 10, hero=True),
    Card(CombatRow.CLOSE, 2, Ability.TIGHT_BOND) * 4,
    Card(CombatRow.RANGE, 3),
    Card(CombatRow.CLOSE, 4),
    Card(CombatRow.RANGE, 5),
    Card(CombatRow.SIEGE, 3),
    Card(CombatRow.CLOSE, 7, Ability.SPY),
    Card(CombatRow.SIEGE, 6),
    Card(CombatRow.SIEGE, 0, Ability.MEDIC),
    Card(CombatRow.RANGE, 2),
    Card(CombatRow.RANGE, 10, hero=True),
    Card(CombatRow.RANGE, 4),
    Card(CombatRow.CLOSE, 2),
    Card(CombatRow.CLOSE, 5, Ability.TIGHT_BOND) * 2,
    Card(CombatRow.SIEGE, 5),
]

cards = flatten(cards)

leaders = [
    LeaderCard(leader_ability=LeaderAbility.RAIN_DECK),
    LeaderCard(leader_ability=LeaderAbility.RANDOM_MEDIC),
    LeaderCard(leader_ability=LeaderAbility.ENEMY_GRAVEYARD2HAND),
    LeaderCard(leader_ability=LeaderAbility.BLOCK_LEADER)
]
