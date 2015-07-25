#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import sys
from os.path import dirname, abspath

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.label.label    import Label
from annotationdata.ptime.point    import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation     import Annotation
from annotationdata.io.annotationpro import Antx

SAMPLES = os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")


class TestAntx(unittest.TestCase):
    """
    Represents an antx file, the stand-alone format of annotation pro.
    """

    def test_Read(self):
        tg1 = Antx()
        tg1.read(os.path.join(SAMPLES, "Example_with_TGA.antx"))

# End TestAntx
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAntx)
    unittest.TextTestRunner(verbosity=2).run(suite)
