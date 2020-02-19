class GameSettings:
    SIMULATE_BOTH_PLAYERS = False
    PLAY_AGAINST_WITCHER = True

    @staticmethod
    def disable_scoiatael_ability() -> bool:
        return GameSettings.SIMULATE_BOTH_PLAYERS or GameSettings.PLAY_AGAINST_WITCHER
