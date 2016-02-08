#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *
import glob

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from resources.acmodel import AcModel
from utils.type import compare_dictionaries


MODEL_PATH = os.path.join(SPPAS, "resources", "models")

# ---------------------------------------------------------------------------

class TestAcModel(unittest.TestCase):

    def _test(self, hmmdefs):
        # Test to load / save / re-load an hmmdefs file
        acmodel = AcModel( hmmdefs )

        # Save temporarilly the loaded model into a file
        tmpfile = hmmdefs+".copy"
        acmodel.save_model( tmpfile )

        # Load the temporary file into a new model
        acmodelcopy = AcModel( tmpfile )

        # Compare original and copy
        self.assertTrue(compare_dictionaries(acmodel.model,acmodelcopy.model))
        os.remove(tmpfile)


    def test_all_models(self):

        models = glob.glob(os.path.join(MODEL_PATH,"models-*","hmmdefs"))
        for hmmdefs in models:
            self._test( hmmdefs )

# End TestAcModel
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAcModel)
    unittest.TextTestRunner(verbosity=2).run(suite)
