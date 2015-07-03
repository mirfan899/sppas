#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_timepoint      import TestTimePoint
from test_timeinterval   import TestTimeInterval
from test_timedisjoint   import TestTimeDisjoint
from test_framepoint     import TestFramePoint
from test_frameinterval  import TestFrameInterval
from test_framedisjoint  import TestFrameDisjoint
from test_localization   import TestLocalization

from test_text          import TestText
from test_silence       import TestSilence
from test_label         import TestLabel
from test_annotation    import TestAnnotation
from test_tier          import TestTier
from test_transcription import TestTranscription
from test_ctrlvocab     import TestCtrlVocab
from test_hierarchy     import TestHierarchy

from test_tiermapping   import TestTierMapping


testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestTimePoint))
testsuite.addTest(unittest.makeSuite(TestTimeInterval))
testsuite.addTest(unittest.makeSuite(TestTimeDisjoint))
testsuite.addTest(unittest.makeSuite(TestText))
testsuite.addTest(unittest.makeSuite(TestSilence))
testsuite.addTest(unittest.makeSuite(TestLabel))
testsuite.addTest(unittest.makeSuite(TestAnnotation))
testsuite.addTest(unittest.makeSuite(TestTier))
testsuite.addTest(unittest.makeSuite(TestTranscription))
testsuite.addTest(unittest.makeSuite(TestCtrlVocab))
testsuite.addTest(unittest.makeSuite(TestHierarchy))
testsuite.addTest(unittest.makeSuite(TestTierMapping))

unittest.TextTestRunner(verbosity=2).run(testsuite)

