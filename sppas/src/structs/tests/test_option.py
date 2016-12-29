# -*- coding:utf-8 -*-

import unittest
from structs.baseoption import sppasBaseOption, Option

# ---------------------------------------------------------------------------


class TestOption(unittest.TestCase):

    def test_init_(self):
        opt = sppasBaseOption("int", 3)
        opt = Option("three", "int", 3)
