from typing import List
from .one_hot_enum import OneHotEnum


class CombatRow(OneHotEnum):
    CLOSE = 0
    RANGE = 1
    SIEGE = 2
    SPECIAL = 3


class Ability(OneHotEnum):
    NONE = 0
    HERO = 1
    MEDIC = 2
    MORALE_BOOST = 3
    MUSTER = 4
    SPY = 5
    TIGHT_BOND = 6
    SCORCH = 7
    WEATHER = 8
    EMPTY_PLACEHOLDER = 9


class Card:

    def __init__(self, combat_row: CombatRow, damage: int, ability: Ability):
        self.combat_row = combat_row
        self.damage = damage
        self.ability = ability

    def repr_list(self) -> List[int]:
        return [self.damage] + self.ability.one_hot()

    @classmethod
    def empty_card_repr(cls, row) -> List[int]:
        return Card(row, 0, Ability.EMPTY_PLACEHOLDER).repr_list()


class Weather(OneHotEnum):
    CLEAR = 0
    FROST = 1
    FOG = 2
    RAIN = 3


class WeatherCard(Card):

    def __init__(self, weather: Weather):
        super().__init__(damage=0, ability=Ability.WEATHER)
        self.weather = weather

    def repr_list(self) -> List[int]:
        return [self.damage] + self.ability.one_hot() + self.weather.one_hot()

