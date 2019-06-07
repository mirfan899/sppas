# -*- coding: UTF-8 -*-

import os
import unittest

from sppas import sppasTypeError, sppasValueError, sppasDictRepl, paths
from sppas.src.annotations.TextNorm.num2text.construct import sppasNumConstructor
from sppas.src.utils.makeunicode import u

# ---------------------------------------------------------------------------


ref_spa = [
    u("cero"),
    u("uno"),
    u("dos"),
    u("tres"),
    u("cuatro"),
    u("cinco"),
    u("seis"),
    u("siete"),
    u("ocho"),
    u("nueve"),
    u("diez"),
    u("once"),
    u("doce"),
    u("trece"),
    u("catorce"),
    u("quince"),
    u("dieciséis"),
    u("diecisiete"),
    u("dieciocho"),
    u("diecinueve"),
    u("veinte"),
    u("veintiuno"),
    u("veintidós"),
    u("veintitrés"),
    u("veinticuatro"),
    u("veinticinco"),
    u("veintiséis"),
    u("veintisiete"),
    u("veintiocho"),
    u("veintinueve"),
    u("treinta"),
    u("treinta-y-uno"),
    u("treinta-y-dos"),
    u("treinta-y-tres"),
    u("treinta-y-cuatro"),
    u("treinta-y-cinco"),
    u("treinta-y-seis"),
    u("treinta-y-siete"),
    u("treinta-y-ocho"),
    u("treinta-y-nueve"),
    u("cuarenta")
]

# ---------------------------------------------------------------------------


class sppasNum2TextTest(unittest.TestCase):

    def setUp(self):

        class Hello(object):
            def __init__(self):
                pass
        self.hello = Hello()

        # Dictionaries actually created in normalize.py
        self.dict_fra = sppasDictRepl(os.path.join(paths.resources, 'num', 'fra_num.repl'), nodump=True)
        self.dict_eng = sppasDictRepl(os.path.join(paths.resources, 'num', 'eng_num.repl'), nodump=True)
        self.dict_jpn = sppasDictRepl(os.path.join(paths.resources, 'num', 'jpn_num.repl'), nodump=True)
        self.dict_spa = sppasDictRepl(os.path.join(paths.resources, 'num', 'spa_num.repl'), nodump=True)

        self.num_fra = sppasNumConstructor.construct('fra', self.dict_fra)
        self.num_eng = sppasNumConstructor.construct('eng', self.dict_eng)
        self.num_jpn = sppasNumConstructor.construct('jpn', self.dict_jpn)
        self.num_spa = sppasNumConstructor.construct('spa', self.dict_spa)

    def test_init(self):
        # Known language
        self.num_fra.convert("03")
        self.num_fra.convert("3")
        with self.assertRaises(ValueError):
            self.num_fra.convert('3.0')

    def test_convert(self):
        res_million_fra = self.num_fra.convert(1000000)
        res_eng = self.num_eng.convert(123456789)
        res_zero_english = self.num_eng.convert('00000123')
        res_jpn = self.num_jpn.convert(123456789)
        res_jpn_twenty = self.num_jpn.convert(22)

        self.assertEqual('un_million', res_million_fra)
        self.assertEqual('hundred_twenty_three_million_four_hundred_fifty_six_thousand_seven_hundred_eighty_nine', res_eng)
        self.assertEqual('zero_zero_zero_zero_zero_hundred_twenty_three', res_zero_english)
        self.assertEqual('一億二千三百四十五万六千七百八十九', res_jpn)
        self.assertEqual('二十二', res_jpn_twenty)

        with self.assertRaises(sppasTypeError) as error:
            sppasNumConstructor.construct(18, self.dict_eng)
            self.assertTrue(isinstance(error.exception, sppasTypeError))

        with self.assertRaises(sppasTypeError) as error:
            sppasNumConstructor.construct('fra', 18)
            self.assertTrue(isinstance(error.exception, sppasTypeError))

        with self.assertRaises(sppasValueError) as error:
            sppasNumConstructor.construct('ger')
            self.assertTrue(isinstance(error.exception, sppasValueError))

    # -----------------------------------------------------------------------

    def test_fra(self):
        """... number to letter in French """
        self.assertEqual(u("douze"),
                         self.num_fra.convert("12"))
        self.assertEqual(u("cent_vingt_trois"),
                         self.num_fra.convert("123"))
        self.assertEqual(u("cent_vingt-et-un"),
                         self.num_fra.convert("121"))
        self.assertEqual('cent_vingt_trois_million_quatre_cent_cinquante_six_mille_sept_cent_quatre-vingt_neuf',
                         self.num_fra.convert(123456789))

    # -----------------------------------------------------------------------

    def test_spa(self):
        """... number to letter in Spanish  """

        ret = [self.num_spa.convert(i) for i in range(41)]
        self.assertEquals(ref_spa, ret)

        self.assertEqual(u("mil-doscientos-cuarenta-y-uno"),
                         self.num_spa.convert(1241))

        self.assertEqual(u("dos-millones-trescientos-cuarenta-y-seis-mil-veintidós"),
                         self.num_spa.convert(2346022))

        self.assertEqual(u("trescientos-ochenta-y-dos-mil-ciento-veintiuno"),
                         self.num_spa.convert(382121))

        self.assertEqual(u("setecientos-treinta-y-nueve-mil-cuatrocientos-noventa-y-nueve"),
                         self.num_spa.convert(739499))
