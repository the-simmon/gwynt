from source.core.card import Card, Ability, Muster, LeaderCard, LeaderAbility
from source.core.cards.flatten import flatten
from source.core.comabt_row import CombatRow

cards = [
    Card(CombatRow.CLOSE, 4, Ability.MUSTER, muster=Muster.ARACHAS) * 3,
    Card(CombatRow.SIEGE, 6, Ability.MUSTER, muster=Muster.ARACHAS),
    Card(CombatRow.CLOSE, 4),
    Card(CombatRow.AGILE, 2, Ability.NONE),
    Card(CombatRow.RANGE, 2),
    Card(CombatRow.CLOSE, 6, Ability.MUSTER, muster=Muster.CRONE) * 3,
    Card(CombatRow.CLOSE, 10, hero=True),
    Card(CombatRow.SIEGE, 6),
    Card(CombatRow.RANGE, 2),
    Card(CombatRow.CLOSE, 6),
    Card(CombatRow.SIEGE, 6),
    Card(CombatRow.CLOSE, 2),
    Card(CombatRow.CLOSE, 5),
    Card(CombatRow.CLOSE, 5),
    Card(CombatRow.RANGE, 2),
    Card(CombatRow.CLOSE, 1, Ability.MUSTER, muster=Muster.GHOUL) * 3,
    Card(CombatRow.RANGE, 5),
    Card(CombatRow.CLOSE, 5),
    Card(CombatRow.AGILE, 2, Ability.NONE),
    Card(CombatRow.SIEGE, 5),
    Card(CombatRow.CLOSE, 10, hero=True),
    Card(CombatRow.AGILE, 8, hero=True),
    Card(CombatRow.RANGE, 10, hero=True),
    Card(CombatRow.CLOSE, 2, Ability.MUSTER, muster=Muster.NEKKER) * 3,
    Card(CombatRow.CLOSE, 5),
    Card(CombatRow.CLOSE, 4, Ability.MUSTER, muster=Muster.VAMPIRE) * 5,
    Card(CombatRow.CLOSE, 5),
    Card(CombatRow.RANGE, 2)
]

cards = flatten(cards)

leaders = [
    LeaderCard(leader_ability=LeaderAbility.SPY_DAMAGE),
    LeaderCard(leader_ability=LeaderAbility.GRAVEYARD2HAND),
    LeaderCard(CombatRow.CLOSE, 0, ability=Ability.SPECIAL_COMMANDERS_HORN),
    LeaderCard(leader_ability=LeaderAbility.SWAP_CARDS),
    LeaderCard(leader_ability=LeaderAbility.PICK_WEATHER),
]
