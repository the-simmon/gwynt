from enum import Enum
from typing import List


class OneHotEnum(Enum):

    def one_hot(self) -> List[int]:
        one_hot = [0] * len(self.__class__)
        one_hot[self.value] = 1
        return one_hot
