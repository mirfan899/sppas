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

from resources.acmodel import AcModel, HMM, HMMInterpolation
from utils.type import compare_dictionaries, compare_lists

MODEL_PATH = os.path.join(SPPAS, "resources", "models")

# ---------------------------------------------------------------------------

class TestAcModel(unittest.TestCase):

# This one takes too much time
#     def test_load_all_models(self):
#         models = glob.glob(os.path.join(MODEL_PATH,"models-*","hmmdefs"))
#         for hmmdefs in models:
#             acmodel = AcModel( hmmdefs )
#             self._test_load_save( acmodel )


    def test_interpolate_simple(self):
        vec1 = [0,0.2,0.8,0]
        vec2 = [0,0.4,0.6,0]
        lin = HMMInterpolation()
        v = lin._linear_interpolate_vectors( [vec1,vec2], [1,0] )
        self.assertEqual(v, vec1)
        v = lin._linear_interpolate_vectors( [vec1,vec2], [0,1] )
        self.assertEqual(v, vec2)
        v = lin._linear_interpolate_vectors( [vec1,vec2], [0.5,0.5] )
        v = [round(value,1) for value in v]
        self.assertEqual(v, [0,0.3,0.7,0])

        mat1 = [vec1,vec1]
        mat2 = [vec2,vec2]
        m = lin._linear_interpolate_matrix( [mat1,mat2], [1,0] )
        self.assertEqual(m, mat1)
        m = lin._linear_interpolate_matrix( [mat1,mat2], [0,1] )
        self.assertEqual(m, mat2)
        m = lin._linear_interpolate_matrix( [mat1,mat2], [0.5,0.5] )
        m[0] = [round(value,1) for value in m[0]]
        m[1] = [round(value,1) for value in m[1]]
        self.assertEqual(m, [[0,0.3,0.7,0],[0,0.3,0.7,0]])


    def test_interpolate_hmm(self):
        lin = HMMInterpolation()
        acmodel1 = AcModel()
        acmodel1.load_htk( "1-hmmdefs" )
        acmodel2 = AcModel()
        acmodel2.load_htk( "2-hmmdefs" )
        ahmm1=acmodel1.get_hmm('a')
        ahmm2=acmodel2.get_hmm('a')

        # transitions
        transitions = [ ahmm1.definition['transition'],ahmm2.definition['transition'] ]
        trs = lin.linear_transitions( transitions, [1,0])
        self.assertTrue(compare_dictionaries(trs,ahmm1.definition['transition']))
        trs = lin.linear_transitions( transitions, [0,1])
        self.assertTrue(compare_dictionaries(trs,ahmm2.definition['transition']))

        # states
        states = [ ahmm1.definition['states'],ahmm2.definition['states'] ]
        sts = lin.linear_states( states, [1,0])
        #self.assertTrue(compare_dictionaries(sts,ahmm1.definition['states']))

        sts = lin.linear_states( states, [0,1])
        #self.assertTrue(compare_dictionaries(sts,ahmm2.definition['states']))


    def setUp(self):
        self.hmmdefs = os.path.join(MODEL_PATH,"models-jpn","hmmdefs")
        self.acmodel = AcModel()
        self.acmodel.load_htk( self.hmmdefs )


    def test_load_save(self):
        self._test_load_save( self.hmmdefs )


    def _test_load_save(self, acmodel):

        # Save temporary the loaded model into a file
        tmpfile = self.hmmdefs+".copy"
        self.acmodel.save_htk( tmpfile )

        # Load the temporary file into a new model
        acmodelcopy = AcModel()
        acmodelcopy.load_htk(tmpfile)

        # Compare original and copy
        self.assertEqual(len(self.acmodel.hmms),len(acmodelcopy.hmms))
        for hmm,hmmcopy in zip(self.acmodel.hmms,acmodelcopy.hmms):
            self.assertEqual(hmm.name,hmmcopy.name)
            self.assertTrue(compare_dictionaries(hmm.definition,hmmcopy.definition))
        self.assertTrue(compare_lists(self.acmodel.macros,acmodelcopy.macros))

        os.remove(tmpfile)


    def test_get_hmm(self):
        with self.assertRaises(ValueError):
            self.acmodel.get_hmm('Q')
        Nhmm = self.acmodel.get_hmm('N')
        self.__test_states( Nhmm.definition['states'] )
        self.__test_transition( Nhmm.definition['transition'] )


    def test_append_hmm(self):
        with self.assertRaises(TypeError):
            self.acmodel.append_hmm({'toto':None})
        hmm = HMM()

        with self.assertRaises(TypeError):
            self.acmodel.append_hmm(hmm)

        Nhmm = self.acmodel.get_hmm('N')
        with self.assertRaises(ValueError):
            self.acmodel.append_hmm(Nhmm)

        Newhmm = copy.deepcopy(Nhmm)
        Newhmm.name = "NewN"
        self.acmodel.append_hmm(Newhmm)


    def test_pop_hmm(self):
        self.acmodel.pop_hmm("N")
        with self.assertRaises(ValueError):
            self.acmodel.get_hmm( "N" )


    def test_no_merge(self):
        nbhmms = len(self.acmodel.hmms)

        # Try to merge with the same model!
        acmodel2 = AcModel()
        acmodel2.load_htk(self.hmmdefs)

        (appended,interpolated,keeped,changed) = acmodel2.merge_model(self.acmodel,gamma=1.)
        self.assertEqual(interpolated, 0)
        self.assertEqual(appended, 0)
        self.assertEqual(keeped, nbhmms)
        self.assertEqual(changed, 0)

        (appended,interpolated,keeped,changed) = acmodel2.merge_model(self.acmodel,gamma=0.5)
        self.assertEqual(interpolated, nbhmms)
        self.assertEqual(appended, 0)
        self.assertEqual(keeped, 0)
        self.assertEqual(changed, 0)

        (appended,interpolated,keeped,changed) = acmodel2.merge_model(self.acmodel,gamma=0.)
        self.assertEqual(interpolated, 0)
        self.assertEqual(appended, 0)
        self.assertEqual(keeped, 0)
        self.assertEqual(changed, nbhmms)


    def test_merge(self):
        acmodel1 = AcModel()
        acmodel1.load_htk( "1-hmmdefs" )
        acmodel2 = AcModel()
        acmodel2.load_htk( "2-hmmdefs" )

        (appended,interpolated,keeped,changed) = acmodel2.merge_model(acmodel1,gamma=0.5)
        self.assertEqual(interpolated, 1)
        self.assertEqual(appended, 1)
        self.assertEqual(keeped, 1)
        self.assertEqual(changed, 0)

        self.__test_states( acmodel2.get_hmm('a').definition['states'] )
        self.__test_transition( acmodel2.get_hmm('a').definition['transition'] )


    def test_load_hmm(self):
        hmm = HMM()
        hmm.load( "N-hmm" )
        self.__test_states( hmm.definition['states'] )
        self.__test_transition( hmm.definition['transition'] )


    def test_save_hmm(self):
        hmm = HMM()
        hmm.load( "N-hmm" )
        hmm.save("N-hmm-copy")
        newhmm = HMM()
        newhmm.load("N-hmm-copy")
        self.assertEqual(hmm.name,newhmm.name)
        self.assertTrue(compare_dictionaries(hmm.definition,newhmm.definition))
        os.remove('N-hmm-copy')


    def __test_transition(self, transition):
        self.assertEqual(transition['dim'], 5)
        matrix = transition['matrix']
        for i in range(len(matrix)-1):
            # the last vector is always 0.!
            vector=matrix[i]
            self.assertEqual(1.0, round(sum(vector),4))

    def __test_states(self, states):
        for item in states: # a dict
            state = item['state']
            streams = state['streams']
            for s in streams: # a list
                mixtures = s['mixtures']
                for mixture in mixtures: # a list of dict
                    #self.assertEqual(type(mixture['weight']),float)
                    pdf = mixture['pdf']
                    self.assertEqual(pdf['mean']['dim'], 25)
                    self.assertEqual(len(pdf['mean']['vector']),25)
                    self.assertEqual(pdf['covariance']['variance']['dim'], 25)
                    self.assertEqual(len(pdf['covariance']['variance']['vector']), 25)
                    self.assertEqual(type(pdf['gconst']),float)

# End TestAcModel
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAcModel)
    unittest.TextTestRunner(verbosity=2).run(suite)
