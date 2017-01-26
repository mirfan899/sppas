# -*- coding:utf-8 -*-

import unittest

from ..baseoption import sppasBaseOption, sppasOption

# ---------------------------------------------------------------------------


class TestOption(unittest.TestCase):

    def test_init_(self):
        opt = sppasBaseOption("int", 3)
        opt = sppasOption("three", "int", 3)

    def test_baseoption_get(self):
        o = sppasBaseOption("integer", "3")
        self.assertEqual(o.get_value(), 3)
        self.assertEqual(o.get_untypedvalue(), "3")
        self.assertEqual(o.get_type(), "int")
        self.assertEqual(o.get_name(), "")
        self.assertEqual(o.get_text(), "")
        self.assertEqual(o.get_description(), "")

        o = sppasBaseOption("toto", "3")
        self.assertEqual(o.get_value(), "3")
        self.assertEqual(o.get_untypedvalue(), "3")
        self.assertEqual(o.get_type(), "str")

    def test_option(self):
        o = sppasBaseOption("opt")
        self.assertEqual(o.get_value(), "")
        self.assertEqual(o.get_untypedvalue(), "")
        self.assertEqual(o.get_type(), "str")
        self.assertEqual(o.get_name(), "")
        self.assertEqual(o.get_text(), "")
        self.assertEqual(o.get_description(), "")

    def test_option_encoding(self):
        o = sppasBaseOption("str", "çéùàï")
        self.assertEqual(o.get_value(), u"çéùàï")
        self.assertEqual(o.get_untypedvalue(), "çéùàï")
        self.assertEqual(o.get_type(), "str")
        self.assertEqual(o.get_name(), "")
        self.assertEqual(o.get_text(), "")
        self.assertEqual(o.get_description(), "")

        o = sppasBaseOption("str", 3)
        self.assertEqual(o.get_value(), "3")
