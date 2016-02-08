#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *
import glob
import collections
import copy

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from resources.acmodel import AcModel
from utils.type import compare_dictionaries


MODEL_PATH = os.path.join(SPPAS, "resources", "models")

# ---------------------------------------------------------------------------

class TestAcModel(unittest.TestCase):

    def setUp(self):
        self.hmmdefs = os.path.join(MODEL_PATH,"models-jpn","hmmdefs")
        self.acmodel = AcModel( self.hmmdefs )

#     def test_load_all_models(self):
#         models = glob.glob(os.path.join(MODEL_PATH,"models-*","hmmdefs"))
#         for hmmdefs in models:
#             acmodel = AcModel( hmmdefs )
#             self._test_load_save( acmodel )

    def test_load_save(self):
        self._test_load_save( self.hmmdefs )


    def _test_load_save(self, acmodel):

        # Save temporarilly the loaded model into a file
        tmpfile = self.hmmdefs+".copy"
        self.acmodel.save_model( tmpfile )

        # Load the temporary file into a new model
        acmodelcopy = AcModel( tmpfile )

        # Compare original and copy
        self.assertTrue(compare_dictionaries(self.acmodel.model,acmodelcopy.model))
        os.remove(tmpfile)


    def test_get_hmm(self):

        # get an hmm not in the model
        with self.assertRaises(ValueError):
            self.acmodel.get_hmm('Q')

        Nhmm = self.acmodel.get_hmm('N')
        definition = Nhmm['definition']

        states = definition['states']
        for item in states: # a dict
            state = item['state']
            streams = state['streams']
            for s in streams: # a list
                mixtures = s['mixtures']
                for mixture in mixtures: # a list of dict
                    self.assertEqual(type(mixture['weight']),float)
                    pdf = mixture['pdf']
                    self.assertEqual(pdf['mean']['dim'], 25)
                    self.assertEqual(len(pdf['mean']['vector']),25)
                    self.assertEqual(pdf['covariance']['variance']['dim'], 25)
                    self.assertEqual(len(pdf['covariance']['variance']['vector']), 25)
                    self.assertEqual(type(pdf['gconst']),float)

        transition = definition['transition']
        self.assertEqual(transition['dim'], 5)
        matrix = transition['matrix']
        for i in range(len(matrix)-1):
            # the last vector is always 0.!
            vector=matrix[i]
            self.assertEqual(1.0, sum(vector))


    def test_append_hmm(self):
        with self.assertRaises(TypeError):
            self.acmodel.append_hmm({'toto':None})
        hmm = collections.OrderedDict()

        with self.assertRaises(TypeError):
            self.acmodel.append_hmm(hmm)

        Nhmm = self.acmodel.get_hmm('N')
        with self.assertRaises(ValueError):
            self.acmodel.append_hmm(Nhmm)

        Newhmm = copy.deepcopy(Nhmm)
        Newhmm['name'] = "NewN"
        self.acmodel.append_hmm(Newhmm)


    def test_pop_hmm(self):
        self.acmodel.pop_hmm("N")
        with self.assertRaises(ValueError):
            self.acmodel.get_hmm( "N" )

# End TestAcModel
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAcModel)
    unittest.TextTestRunner(verbosity=2).run(suite)
