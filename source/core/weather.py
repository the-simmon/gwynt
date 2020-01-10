from __future__ import annotations

import enum

from source.core.card import Ability


class Weather(enum.Enum):
    CLEAR = 0
    FROST = 1
    FOG = 2
    RAIN = 3

    @classmethod
    def ability_is_weather(cls, ability: Ability):
        if ability is Ability.CLEAR_WEATHER or ability is Ability.FROST or ability is Ability.RAIN or \
                ability is Ability.FOG:
            return True
        return False

    @classmethod
    def ability_to_weather(cls, ability: Ability) -> Weather:
        if ability is Ability.CLEAR_WEATHER:
            return Weather.CLEAR
        elif ability is Ability.FROST:
            return Weather.FROST
        elif ability is Ability.FOG:
            return Weather.FOG
        elif ability is Ability.RAIN:
            return Weather.RAIN

        raise ValueError
