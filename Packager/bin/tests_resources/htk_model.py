#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from resources.acmodel import AcModel

MODEL_PATH = os.path.join(SPPAS, "resources", "models")

def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return added, removed, modified, same

def compare_dictionaries(dict1, dict2):
    if dict1 == None or dict2 == None:
        return False

    if type(dict1) is not dict or type(dict2) is not dict:
        return False

    shared_keys = set(dict2.keys()) & set(dict2.keys())

    if not ( len(shared_keys) == len(dict1.keys()) and len(shared_keys) == len(dict2.keys())):
        return False


    dicts_are_equal = True
    for key in dict1.keys():
        if type(dict1[key]) is dict:
            dicts_are_equal = dicts_are_equal and compare_dictionaries(dict1[key],dict2[key])
        else:
            dicts_are_equal = dicts_are_equal and (dict1[key] == dict2[key])

    return dicts_are_equal


# ---------------------------------------------------------------------------
class TestAcModel(unittest.TestCase):

    def test_load_save(self):
        # Load an existing model in SPPAS
        hmmdefs = os.path.join(MODEL_PATH,"models-cat","hmmdefs")
        acmodel = AcModel( hmmdefs )

        # Save temporarilly the loaded model into a file
        tmpfile = os.path.join(dirname(abspath(__file__)),"hmmdefs")
        acmodel.save_model(tmpfile)

        # Load the temporary file
        acmodelcopy = AcModel( tmpfile )
        added, removed, modified, same = dict_compare(acmodel.model,
                                                      acmodelcopy.model)

        print "added:",added
        print "removed:",removed
        print "modified",modified
        print "same",same
        # Compare original and copy
        os.remove(tmpfile)

# End TestAcModel
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAcModel)
    unittest.TextTestRunner(verbosity=2).run(suite)
