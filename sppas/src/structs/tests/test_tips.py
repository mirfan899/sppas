# -*- coding:utf-8 -*-

import unittest

from ..tips import sppasTips

# ---------------------------------------------------------------------------


class TestTips(unittest.TestCase):

    def test_tips(self):
        self.tips = sppasTips()
        self.assertGreater(len(self.tips), 8)

        t = self.tips.get_message()
        self.assertGreater(len(t), 8)
