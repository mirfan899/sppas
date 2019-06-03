import os
import unittest

import sppas
from ..dictionary import Dictionary
from ..sppasNumConstructor import sppasNumConstructor


class sppasNum2TextTest(unittest.TestCase):

    def setUp(self):

        class Hello(object):
            def __init__(self):
                pass
        self.hello = Hello()

        # Dictionaries actually created in normalize.py
        self.dictionaryFra = Dictionary('fra')
        self.dictionaryEng = Dictionary('eng')

        self.sppasConverteurFrench = sppasNumConstructor().construct('fra', self.dictionaryFra)
        self.sppasConverteurEnglish = sppasNumConstructor().construct('eng', self.dictionaryEng)

    def test_convert(self):
        res_fra = self.sppasConverteurFrench.convert(123456789)
        res_eng = self.sppasConverteurEnglish.convert(123456789)

        self.assertEqual('cent_vingt_trois_million_quatre_cent_cinquante_six_mille_sept_cent_quatre_vingt_neuf', res_fra)
        self.assertEqual('hundred_twenty_three_million_four_hundred_fifty_six_thousand_seven_hundred_eighty_nine', res_eng)