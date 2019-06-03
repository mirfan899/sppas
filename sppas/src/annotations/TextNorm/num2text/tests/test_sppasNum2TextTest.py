import os
import unittest

from sppas import sppasTypeError, sppasValueError
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

        with self.assertRaises(sppasTypeError) as error:
            dictionaryErrorObj = Dictionary(self.hello)

            self.assertTrue(isinstance(error.exception, sppasTypeError))

        with self.assertRaises(sppasTypeError) as error:
            dictionaryErrorInt = Dictionary(18)

            self.assertTrue(isinstance(error.exception, sppasTypeError))

        with self.assertRaises(sppasTypeError) as error:
            dictionaryErrorBool = Dictionary(True)

            self.assertTrue(isinstance(error.exception, sppasTypeError))

        with self.assertRaises(IOError) as error:
            dictionaryErrorLang = Dictionary('ger')

            self.assertTrue(isinstance(error.exception, IOError))

        with self.assertRaises(sppasTypeError) as error:
            sppasNumConstructor().construct(18, self.dictionaryEng)

            self.assertTrue(isinstance(error.exception, sppasTypeError))

        with self.assertRaises(sppasTypeError) as error:
            sppasNumConstructor().construct('fra', 18)

            self.assertTrue(isinstance(error.exception, sppasTypeError))

        with self.assertRaises(sppasValueError) as error:
            sppasNumConstructor().construct('ger')

            self.assertTrue(isinstance(error.exception, sppasValueError))
