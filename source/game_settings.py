class GameSettings:
    SIMULATE_BOTH_PLAYERS = False
    PLAY_AGAINST_WITCHER = True

    @staticmethod
    def disable_scoiatael_ability() -> bool:
        return not GameSettings.SIMULATE_BOTH_PLAYERS and not GameSettings.PLAY_AGAINST_WITCHER
