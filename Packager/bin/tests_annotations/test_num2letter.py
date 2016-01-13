#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotations.Token.num2letter import sppasNum

ref_es = [
u"cero",
u"uno",
u"dos",
u"tres",
u"cuatro",
u"cinco",
u"seis",
u"siete",
u"ocho",
u"nueve",
u"diez",
u"once",
u"doce",
u"trece",
u"catorce",
u"quince",
u"dieciséis",
u"diecisiete",
u"dieciocho",
u"diecinueve",
u"veinte",
u"veintiuno",
u"veintidós",
u"veintitrés",
u"veinticuatro",
u"veinticinco",
u"veintiséis",
u"veintisiete",
u"veintiocho",
u"veintinueve",
u"treinta",
u"treinta y uno",
u"treinta y dos",
u"treinta y tres",
u"treinta y cuatro",
u"treinta y cinco",
u"treinta y seis",
u"treinta y siete",
u"treinta y ocho",
u"treinta y nueve",
u"cuarenta",
u"cuarenta y uno",
u"cuarenta y dos",
u"cuarenta y tres",
u"cuarenta y cuatro",
u"cuarenta y cinco",
u"cuarenta y seis",
u"cuarenta y siete",
u"cuarenta y ocho",
u"cuarenta y nueve",
u"cincuenta",
u"cincuenta y uno",
u"cincuenta y dos",
u"cincuenta y tres",
u"cincuenta y cuatro",
u"cincuenta y cinco",
u"cincuenta y seis",
u"cincuenta y siete",
u"cincuenta y ocho",
u"cincuenta y nueve",
u"sesenta",
u"sesenta y uno",
u"sesenta y dos",
u"sesenta y tres",
u"sesenta y cuatro",
u"sesenta y cinco",
u"sesenta y seis",
u"sesenta y siete",
u"sesenta y ocho",
u"sesenta y nueve",
u"setenta",
u"setenta y uno",
u"setenta y dos",
u"setenta y tres",
u"setenta y cuatro",
u"setenta y cinco",
u"setenta y seis",
u"setenta y siete",
u"setenta y ocho",
u"setenta y nueve",
u"ochenta",
u"ochenta y uno",
u"ochenta y dos",
u"ochenta y tres",
u"ochenta y cuatro",
u"ochenta y cinco",
u"ochenta y seis",
u"ochenta y siete",
u"ochenta y ocho",
u"ochenta y nueve",
u"noventa",
u"noventa y uno",
u"noventa y dos",
u"noventa y tres",
u"noventa y cuatro",
u"noventa y cinco",
u"noventa y seis",
u"noventa y siete",
u"noventa y ocho",
u"noventa y nueve",
u"cien"
]

class TestNum2Letter(unittest.TestCase):

    def test_num2letterFR(self):
        num = sppasNum('fra')
        s =  num.convert("123")
        self.assertEquals(s, u"cent-vingt-trois")

    def test_num2letterES(self):
        num = sppasNum('spa')
        ret = [num.convert(i) for i in range(101)]
        self.assertEquals(ret, ref_es)

        s = num.convert(1241)
        self.assertEquals(s, u"mil doscientos cuarenta y uno")

        s = num.convert(2346022)
        self.assertEquals(s, u"dos millones trescientos cuarenta y seis mil veintidós")

        s = num.convert(382121)
        self.assertEquals(s, u"trescientos ochenta y dos mil ciento veintiuno")

        s = num.convert(739499)
        self.assertEquals(s, u"setecientos treinta y nueve mil cuatrocientos noventa y nueve")

# End TestNum2Letter
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNum2Letter)
    unittest.TextTestRunner(verbosity=2).run(suite)
