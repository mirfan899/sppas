#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import shutil
from paths import TEMP


from test_num2letter import TestNum2Letter
from test_tokenize   import TestDictTok
from test_phon       import TestDictPhon, TestDAGPhon, TestSppasPhon, TestPhonUnk

from test_aligners import TestAlignersPackage
from test_aligners import TestBaseAligner
from test_aligners import TestBasicAlign
from test_aligners import TestJuliusAlign
from test_aligners import TestHviteAlign
from test_spkrate  import TestSpeakerRate
from test_tracks   import TestAnchorTier

if os.path.exists( TEMP ) is False:
    os.mkdir( TEMP )

testsuite = unittest.TestSuite()

# # tokenize
# testsuite.addTest(unittest.makeSuite(TestNum2Letter))
# testsuite.addTest(unittest.makeSuite(TestDictTok))
#
# # phonetize
# testsuite.addTest(unittest.makeSuite(TestDictPhon))
# testsuite.addTest(unittest.makeSuite(TestDAGPhon))
# testsuite.addTest(unittest.makeSuite(TestSppasPhon))
# testsuite.addTest(unittest.makeSuite(TestPhonUnk))

# align
testsuite.addTest(unittest.makeSuite(TestAnchorTier))
testsuite.addTest(unittest.makeSuite(TestSpeakerRate))
testsuite.addTest(unittest.makeSuite(TestBaseAligner))
testsuite.addTest(unittest.makeSuite(TestBasicAlign))
testsuite.addTest(unittest.makeSuite(TestJuliusAlign))
testsuite.addTest(unittest.makeSuite(TestHviteAlign))
testsuite.addTest(unittest.makeSuite(TestAlignersPackage))

# run the test...
unittest.TextTestRunner(verbosity=2).run(testsuite)

# clean
shutil.rmtree( TEMP )
