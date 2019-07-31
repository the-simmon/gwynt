import unittest

from source.core.one_hot_enum import OneHotEnum


class OneHotEnumTest(unittest.TestCase):

    def test_one_hot_enum(self):
        class TestEnum(OneHotEnum):
            ONE = 0
            TWO = 1
            THREE = 2

        self.assertEqual([0, 1, 0], TestEnum.TWO.one_hot())
