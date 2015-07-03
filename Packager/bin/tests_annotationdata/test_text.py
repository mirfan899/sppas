#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.label.text import Text

class TestText(unittest.TestCase):

    def test_decode(self):
        text = Text("\têtre   \r   être être  \n  ")
        self.assertTrue(isinstance(text.GetTypedValue(), unicode))


    def test_value(self):
        # string value
        text = Text(" test ", score=0.5)
        self.assertEquals(text.GetValue(), u"test")
        self.assertEqual(text.GetScore(), 0.5)
        text = Text("test", score=1)
        self.assertTrue(isinstance(text.GetScore(), float))

        # int value
        text = Text( 2, data_type="int")
        textstr = Text( "2" )
        self.assertEquals(text.GetTypedValue(), 2)
        self.assertEquals(text.GetValue(), u"2")
        self.assertNotEquals(text.GetTypedValue(), textstr.GetTypedValue())
        self.assertEquals(text.GetValue(), textstr.GetValue())

        # float value
        text = Text( 2.10, data_type="float")
        textstr = Text( "2.1" )
        self.assertEquals(text.GetTypedValue(), 2.1)
        self.assertEquals(text.GetValue(), u"2.1")
        self.assertNotEquals(text.GetTypedValue(), textstr.GetTypedValue())
        self.assertEquals(text.GetValue(), textstr.GetValue())

        # boolean value
        text = Text( "1", data_type="bool")
        textstr = Text( "True" )
        self.assertEquals(text.GetTypedValue(), True)
        self.assertEquals(text.GetValue(), u"True")
        self.assertNotEquals(text.GetTypedValue(), textstr.GetTypedValue())
        self.assertEquals(text.GetValue(), textstr.GetValue())



    def test_set(self):
        text = Text("test", score=1)
        text.SetValue( "toto" )
        text.SetScore( 0.4 )

    def test__eq__(self):
        text1 = Text(" test ", score=0.5)
        text2 = Text("test\n", score=1)
        self.assertEqual(text1, text2)
        self.assertTrue(text1.Equal(text2))
        self.assertFalse(text1.StrictEqual(text2))

# End TestText
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestText)
    unittest.TextTestRunner(verbosity=2).run(suite)

