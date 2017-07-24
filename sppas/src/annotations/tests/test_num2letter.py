# -*- coding:utf-8 -*-

import unittest

from sppas.src.utils.makeunicode import u
from ..TextNorm.num2letter import sppasNum

ref_es = [
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


class TestNum2Letter(unittest.TestCase):

    def test_init(self):
        # Unknown language
        num = sppasNum('zzz')
        with self.assertRaises(ValueError):
            num.convert('3')
        # Known language
        num = sppasNum('fra')
        num.convert("03")
        num.convert("3")
        with self.assertRaises(ValueError):
            num.convert('3.0')

    def test_num2letterFR(self):
        num = sppasNum('fra')
        s = num.convert("123")
        self.assertEquals(s, u("cent-vingt-trois"))

    def test_num2letterES(self):
        num = sppasNum('spa')
        ret = [num.convert(i) for i in range(41)]
        self.assertEquals(ret, ref_es)

        s = num.convert(1241)
        self.assertEquals(s, u("mil-doscientos-cuarenta-y-uno"))

        s = num.convert(2346022)
        self.assertEquals(s, u("dos-millones-trescientos-cuarenta-y-seis-mil-veintidós"))

        s = num.convert(382121)
        self.assertEquals(s, u("trescientos-ochenta-y-dos-mil-ciento-veintiuno"))

        s = num.convert(739499)
        self.assertEquals(s, u("setecientos-treinta-y-nueve-mil-cuatrocientos-noventa-y-nueve"))
