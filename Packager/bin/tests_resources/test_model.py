#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *
import copy
import shutil

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from resources.acm.acmodel  import AcModel, HtkIO
from resources.acm.hmm      import HMM, HMMInterpolation
from resources.acm.htktrain import HTKModelTrainer, DataTrainer, PhoneSet, TrainingCorpus, HTKModelInitializer

from utils.type import compare
from utils.fileutils import setup_logging
from sp_glob import RESOURCES_PATH

MODEL_PATH = os.path.join(RESOURCES_PATH, "models")

# ---------------------------------------------------------------------------

class TestTrainer(unittest.TestCase):

    def test_modeltrainer(self):
        trainer = HTKModelTrainer()
        model = trainer.training_recipe()
        self.assertEqual( len(model.hmms),0 )

        trainer.corpus = TrainingCorpus()
        model = trainer.training_recipe()
        self.assertEqual( len(model.hmms),4 )

    def test_datatrainer(self):
        datatrainer = DataTrainer()
        datatrainer.create()
        self.assertEqual( datatrainer.check(), None )
        dire = datatrainer.workdir
        self.assertTrue( os.path.exists( dire ) )
        datatrainer.delete()
        self.assertFalse( os.path.exists( dire ) )

        datatrainer.create( dictfile=os.path.join(RESOURCES_PATH, "dict", "nan.dict") )
        self.assertEqual( datatrainer.monophones.get_size(), 44 )

    def test_phoneset(self):
        pho = PhoneSet( )
        self.assertEqual( pho.get_size(), 4 )
        pho.add_from_dict( os.path.join(RESOURCES_PATH, "dict", "nan.dict") )
        self.assertEqual( pho.get_size(), 44 )
        pho.save( "monophones" )

        pho2 = PhoneSet( "monophones" )
        for phone in pho.get_list():
            self.assertTrue( pho2.is_in( phone ))
        for phone in pho2.get_list():
            self.assertTrue( pho.is_in( phone ))

        os.remove( "monophones" )

    def test_initializer(self):
        #setup_logging(2,None)
        corpus  = TrainingCorpus()

        os.mkdir( "working" )
        shutil.copy( os.path.join("protos","vFloors"), "working" )

        initial = HTKModelInitializer(corpus,"working")

        # Will create a model for all the fillers which are systematically
        # added into the list of monophones: sil, gb, dummy, @@
        # or use the proto if it is available.

        corpus.datatrainer.protodir = "protos"
        initial.create_model()

        hmm1 = HMM()
        hmm2 = HMM()

        hmm1.load( os.path.join("working", "@@.hmm") )
        hmm2.load( os.path.join("protos", "@@.hmm") )
        self.assertTrue(compare(hmm1.definition,hmm2.definition))

        hmm1.load( os.path.join("working", "sil.hmm") )
        hmm2.load( os.path.join("protos", "sil.hmm") )

        corpus.datatrainer.fix_proto(protofilename=os.path.join("proto.hmm"))
        hmm2.load( os.path.join("protos", "proto.hmm") )

        hmm1.load( os.path.join("working", "gb.hmm") )
        self.assertTrue(compare(hmm1.definition,hmm2.definition))

        hmm1.load( os.path.join("working", "dummy.hmm") )
        self.assertTrue(compare(hmm1.definition,hmm2.definition))

        acmodel = AcModel()
        acmodel.load_htk( os.path.join( "working","hmmdefs") )

        # Make some clean
        shutil.rmtree("working")
        os.remove( os.path.join("protos", "proto.hmm") )

# ---------------------------------------------------------------------------

class TestInterpolate(unittest.TestCase):
    def setUp(self):
        self.vec1 = [0,0.2,0.8,0]
        self.vec2 = [0,0.4,0.6,0]
        self.lin = HMMInterpolation()

    def test_interpolate_vector(self):
        v = self.lin._linear_interpolate_vectors( [self.vec1,self.vec2], [1,0] )
        self.assertEqual(v, self.vec1)
        v = self.lin._linear_interpolate_vectors( [self.vec1,self.vec2], [0,1] )
        self.assertEqual(v, self.vec2)
        v = self.lin._linear_interpolate_vectors( [self.vec1,self.vec2], [0.5,0.5] )
        v = [round(value,1) for value in v]
        self.assertEqual(v, [0,0.3,0.7,0])

    def test_interpolate_matrix(self):
        mat1 = [self.vec1,self.vec1]
        mat2 = [self.vec2,self.vec2]
        m = self.lin._linear_interpolate_matrix( [mat1,mat2], [1,0] )
        self.assertEqual(m, mat1)
        m = self.lin._linear_interpolate_matrix( [mat1,mat2], [0,1] )
        self.assertEqual(m, mat2)
        m = self.lin._linear_interpolate_matrix( [mat1,mat2], [0.5,0.5] )
        m[0] = [round(value,1) for value in m[0]]
        m[1] = [round(value,1) for value in m[1]]
        self.assertEqual(m, [[0,0.3,0.7,0],[0,0.3,0.7,0]])

    def test_interpolate_hmm(self):
        acmodel1 = AcModel()
        acmodel1.load_htk( "1-hmmdefs" )
        acmodel2 = AcModel()
        acmodel2.load_htk( "2-hmmdefs" )
        ahmm1=acmodel1.get_hmm('a')
        ahmm2=acmodel2.get_hmm('a')

        # transitions
        # (notice that the transition of 'a' in acmodel1 is in a macro.)
        a1transition = [macro["transition"] for macro in acmodel1.macros if macro.get('transition',None)][0]
        transitions = [ a1transition['definition'],ahmm2.definition['transition'] ]
        trs = self.lin.linear_transitions( transitions, [1,0])
        compare(trs,a1transition['definition'])
        self.assertTrue(compare(trs,a1transition['definition']))

        acmodel1.fill_hmms()

        transitions = [ ahmm1.definition['transition'],ahmm2.definition['transition'] ]
        trs = self.lin.linear_transitions( transitions, [1,0])
        self.assertTrue(compare(trs,ahmm1.definition['transition']))

        trs = self.lin.linear_transitions( transitions, [0,1])
        self.assertTrue(compare(trs,ahmm2.definition['transition']))

        # states
        # (notice that the state 2 of 'a' in acmodel1 is in a macro.)
        states = [ ahmm1.definition['states'],ahmm2.definition['states'] ]
        sts = self.lin.linear_states( states, [1,0])
        compare(sts,ahmm1.definition['states'],verbose=True)
        self.assertTrue(compare(sts,ahmm1.definition['states']))
        sts = self.lin.linear_states( states, [0,1])
        self.assertTrue(compare(sts,ahmm2.definition['states']))

# ---------------------------------------------------------------------------

class TestAcModel(unittest.TestCase):

    #This one takes too much time to be tested each time....
#     def test_load_all_models(self):
#         models = glob.glob(os.path.join(MODEL_PATH,"models-*","hmmdefs"))
#         for hmmdefs in models:
#             acmodel = AcModel( hmmdefs )
#             self._test_load_save( acmodel )

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
            self.assertTrue(compare(hmm.definition,hmmcopy.definition))
        self.assertTrue(compare(self.acmodel.macros,acmodelcopy.macros))

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
        os.remove('N-hmm-copy')
        self.assertEqual(hmm.name,newhmm.name)
        self.assertTrue(compare(hmm.definition,newhmm.definition))


    def test_fill(self):
        acmodel1 = AcModel()
        acmodel1.load_htk( "1-hmmdefs" )
        ahmm1=acmodel1.get_hmm('a')
        a1transition = [macro["transition"] for macro in acmodel1.macros if macro.get('transition',None)][0]

        acmodel1.fill_hmms()
        self.assertTrue(compare(ahmm1.definition['transition'],a1transition['definition']))


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

        # Try to merge with a different MFCC parameter kind model...
        acmodel2 = AcModel()
        acmodel2.load_htk( os.path.join(MODEL_PATH,"models-cat","hmmdefs") )
        with self.assertRaises(TypeError):
            acmodel2.merge_model(self.acmodel,gamma=1.)


    def test_merge(self):
        acmodel1 = AcModel()
        acmodel1.load_htk( "1-hmmdefs" )
        acmodel2 = AcModel()
        acmodel2.load_htk( "2-hmmdefs" )

        (appended,interpolated,keeped,changed) = acmodel2.merge_model(acmodel1,gamma=0.5)
        self.assertEqual(interpolated, 2) # acopy, a
        self.assertEqual(appended, 1)     # i
        self.assertEqual(keeped, 1)       # e
        self.assertEqual(changed, 0)

        self.__test_states( acmodel2.get_hmm('a').definition['states'] )
        self.__test_transition( acmodel2.get_hmm('a').definition['transition'] )


    def test_replace_phones(self):
        acmodel1 = AcModel()
        acmodel1.load( os.path.join(MODEL_PATH,"models-fra") )
        acmodel1.replace_phones( reverse=False )
        acmodel1.replace_phones( reverse=True )

        acmodel2 = AcModel()
        acmodel2.load( os.path.join(MODEL_PATH,"models-fra") )

        for h1 in acmodel1.hmms:
            h2 = acmodel2.get_hmm( h1.name )
            self.assertTrue(compare(h1.definition['transition'],h2.definition['transition']))
            self.assertTrue(compare(h1.definition['states'],h2.definition['states']))


    def test_monophones(self):
        acmodel1 = AcModel()
        acmodel1.load( os.path.join(MODEL_PATH,"models-fra") )

        acmodel2 = acmodel1.extract_monophones()
        acmodel2.save('fra-mono')
        self.assertTrue(  os.path.isfile( os.path.join('fra-mono','hmmdefs')) )
        self.assertTrue(  os.path.isfile( os.path.join('fra-mono','monophones.repl')) )
        self.assertFalse( os.path.isfile( os.path.join('fra-mono','tiedlist')) )
        os.remove( os.path.join('fra-mono','hmmdefs') )
        os.remove( os.path.join('fra-mono','monophones.repl') )
        os.rmdir( 'fra-mono' )
        self.assertEqual( len(acmodel2.hmms), 38 )


    def test_proto(self):
        h1 = HtkIO()
        h1.write_hmm_proto( 25, "proto_from_htkio" )

        h2 = HMM()
        h2.create_proto( 25 )
        h2.save( "proto_from_hmm" )

        m1 = HMM()
        m1.load( "proto_from_htkio" )

        m2 = HMM()
        m2.load( "proto_from_hmm" )

        self.assertTrue(compare(m1.definition['transition'],m2.definition['transition']))
        self.assertTrue(compare(m1.definition['states'],m2.definition['states']))

        os.remove( "proto_from_hmm" )
        os.remove( "proto_from_htkio" )

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


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    testsuite = unittest.TestSuite()
    #testsuite.addTest(unittest.makeSuite(TestInterpolate))
    #testsuite.addTest(unittest.makeSuite(TestAcModel))
    testsuite.addTest(unittest.makeSuite(TestTrainer))
    unittest.TextTestRunner(verbosity=2).run(testsuite)
