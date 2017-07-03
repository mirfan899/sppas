# -*- coding:utf-8 -*-

import unittest
import os.path
import copy
import shutil

from sppas import RESOURCES_PATH, SAMPLES_PATH
from sppas.src.models.acm.acmodel import sppasAcModel, sppasHtkIO
from sppas.src.models.acm.hmm import sppasHMM, HMMInterpolation
from sppas.src.models.acm.htktrain import sppasHTKModelTrainer, sppasDataTrainer, sppasPhoneSet, sppasTrainingCorpus, sppasHTKModelInitializer
from sppas.src.utils.compare import sppasCompare
from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
MODEL_PATH = os.path.join(RESOURCES_PATH, "models")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestTrainer(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is True:
            shutil.rmtree(TEMP)
        os.mkdir(TEMP)
        shutil.copytree(os.path.join(DATA, "protos"), os.path.join(TEMP, "protos"))

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_add_corpus(self):
        corpus = sppasTrainingCorpus()
        corpus1 = os.path.join(SAMPLES_PATH, "samples-eng")
        corpus2 = os.path.join(SAMPLES_PATH, "samples-ita")
        nb = corpus.add_corpus(corpus1)
        self.assertEqual(nb, 0)
        nb = corpus.add_corpus(corpus2)
        self.assertEqual(nb, 4)
        corpus.add_corpus(SAMPLES_PATH)
        self.assertGreater(len(corpus.transfiles), 10)
        self.assertEqual(len(corpus.phonfiles), 0)
        self.assertEqual(len(corpus.alignfiles), 0)

    def test_datatrainer(self):
        datatrainer = sppasDataTrainer()
        datatrainer.create()
        self.assertEqual(datatrainer.check(), None)
        dire = datatrainer.workdir
        self.assertTrue(os.path.exists(dire))
        datatrainer.delete()
        self.assertFalse(os.path.exists(dire))

    def test_phoneset(self):
        pho = sppasPhoneSet()
        self.assertEqual(len(pho), 4)
        pho.add_from_dict(os.path.join(RESOURCES_PATH, "dict", "nan.dict"))
        self.assertEqual(len(pho), 44)
        pho.save(os.path.join(TEMP, "monophones"))

        pho2 = sppasPhoneSet(os.path.join(TEMP, "monophones"))
        for phone in pho.get_list():
            self.assertTrue(pho2.is_in(phone))
        for phone in pho2.get_list():
            self.assertTrue(pho.is_in(phone))

        os.remove(os.path.join(TEMP, "monophones"))

    def test_trainingcorpus(self):
        corpus = sppasTrainingCorpus()

        self.assertEqual(corpus.phonemap.map_entry('#'), "#")

        corpus.fix_resources(dictfile=os.path.join(RESOURCES_PATH, "dict", "nan.dict"))
        self.assertEqual(len(corpus.monophones), 44)

        corpus.fix_resources(dictfile=os.path.join(RESOURCES_PATH, "dict", "nan.dict"),
                             mappingfile=os.path.join(RESOURCES_PATH, "models", "models-nan", "monophones.repl"))
        self.assertEqual(corpus.phonemap.map_entry('#'), "sil")

        self.assertFalse(corpus.add_file("toto", "toto"))
        self.assertTrue(corpus.add_file(os.path.join(DATA, "F_F_B003-P8-palign.TextGrid"), os.path.join(DATA, "F_F_B003-P8.wav")))
        corpus.datatrainer.delete()

    def test_initializer_without_corpus(self):
        corpus = sppasTrainingCorpus()
        workdir = os.path.join(TEMP, "working")
        os.mkdir(workdir)
        shutil.copy(os.path.join(DATA, "protos", "vFloors"), workdir)

        initial = sppasHTKModelInitializer(corpus, workdir)

        corpus.datatrainer.protodir = os.path.join(DATA, "protos")
        initial.create_model()

        hmm1 = sppasHMM()
        hmm2 = sppasHMM()
        sp = sppasCompare()

        hmm1.load(os.path.join(workdir, "@@.hmm"))
        hmm2.load(os.path.join(DATA, "protos", "@@.hmm"))
        self.assertTrue(sp.equals(hmm1.definition, hmm2.definition))

        hmm1.load(os.path.join(workdir, "sil.hmm"))
        hmm2.load(os.path.join(DATA, "protos", "sil.hmm"))

        corpus.datatrainer.fix_proto(proto_filename=os.path.join(DATA, "protos", "proto.hmm"))
        hmm2.load(os.path.join(DATA, "protos", "proto.hmm"))

        hmm1.load(os.path.join(workdir, "gb.hmm"))
        self.assertTrue(sp.equals(hmm1.definition, hmm2.definition))

        hmm1.load(os.path.join(workdir, "dummy.hmm"))
        self.assertTrue(sp.equals(hmm1.definition, hmm2.definition))

        acmodel = sppasAcModel()
        acmodel.load_htk(os.path.join(workdir, "hmmdefs"))

    def test_trainer_without_data(self):
        trainer = sppasHTKModelTrainer()
        model = trainer.training_recipe()
        self.assertEqual(len(model.hmms), 0)

        trainer.corpus = sppasTrainingCorpus()
        model = trainer.training_recipe()
        self.assertEqual(len(model.hmms), 4)

    # def test_trainer_with_data(self):
    # TODO: Test the model
    #     #from utils.fileutils import setup_logging
    #     #setup_logging(1,None)
    #     corpus = sppasTrainingCorpus()
    #     corpus.fix_resources(dictfile=os.path.join(RESOURCES_PATH, "dict", "fra.dict"),
    #                          mappingfile=os.path.join(RESOURCES_PATH, "models", "models-fra", "monophones.repl"))
    #     corpus.lang = "fra"
    #     corpus.datatrainer.protodir = os.path.join(DATA, "protos")
    #     corpus.add_file(os.path.join(DATA, "F_F_B003-P8-palign.TextGrid"), os.path.join(DATA, "F_F_B003-P8.wav"))
    #     corpus.add_file(os.path.join(DATA, "track_0001-phon.xra"), os.path.join(DATA, "track_0001.wav"))
    #     corpus.add_corpus(os.path.join(SAMPLES_PATH, "samples-fra"))
    #
    #     trainer = sppasHTKModelTrainer(corpus)
    #     acmodel = trainer.training_recipe(delete=True)


# ---------------------------------------------------------------------------


class TestInterpolate(unittest.TestCase):
    def setUp(self):
        self.vec1 = [0, 0.2, 0.8, 0]
        self.vec2 = [0, 0.4, 0.6, 0]
        self.lin = HMMInterpolation()

    def test_interpolate_vector(self):
        v = self.lin.linear_interpolate_vectors([self.vec1, self.vec2], [1, 0])
        self.assertEqual(v, self.vec1)
        v = self.lin.linear_interpolate_vectors([self.vec1, self.vec2], [0, 1])
        self.assertEqual(v, self.vec2)
        v = self.lin.linear_interpolate_vectors([self.vec1, self.vec2], [0.5, 0.5])
        v = [round(value, 1) for value in v]
        self.assertEqual(v, [0, 0.3, 0.7, 0])

    def test_interpolate_matrix(self):
        mat1 = [self.vec1, self.vec1]
        mat2 = [self.vec2, self.vec2]
        m = self.lin.linear_interpolate_matrix([mat1, mat2], [1, 0])
        self.assertEqual(m, mat1)
        m = self.lin.linear_interpolate_matrix([mat1, mat2], [0, 1])
        self.assertEqual(m, mat2)
        m = self.lin.linear_interpolate_matrix([mat1, mat2], [0.5, 0.5])
        m[0] = [round(value, 1) for value in m[0]]
        m[1] = [round(value, 1) for value in m[1]]
        self.assertEqual(m, [[0, 0.3, 0.7, 0], [0, 0.3, 0.7, 0]])

    def test_interpolate_hmm(self):
        acmodel1 = sppasAcModel()
        acmodel1.load_htk(os.path.join(DATA, "1-hmmdefs"))
        acmodel2 = sppasAcModel()
        acmodel2.load_htk(os.path.join(DATA, "2-hmmdefs"))
        ahmm1 = acmodel1.get_hmm('a')
        ahmm2 = acmodel2.get_hmm('a')
        sp = sppasCompare()

        # transitions
        # (notice that the transition of 'a' in acmodel1 is in a macro.)
        a1transition = [macro["transition"] for macro in acmodel1.macros if macro.get('transition', None)][0]
        transitions = [a1transition['definition'], ahmm2.definition['transition']]
        trs = self.lin.linear_transitions(transitions, [1, 0])
        sp.equals(trs, a1transition['definition'])
        self.assertTrue(sp.equals(trs, a1transition['definition']))

        acmodel1.fill_hmms()

        transitions = [ahmm1.definition['transition'], ahmm2.definition['transition']]
        trs = self.lin.linear_transitions(transitions, [1, 0])
        self.assertTrue(sp.equals(trs, ahmm1.definition['transition']))

        trs = self.lin.linear_transitions(transitions, [0, 1])
        self.assertTrue(sp.equals(trs, ahmm2.definition['transition']))

        # states
        # (notice that the state 2 of 'a' in acmodel1 is in a macro.)
        states = [ahmm1.definition['states'], ahmm2.definition['states']]
        sts = self.lin.linear_states(states, [1, 0])
        self.assertTrue(sp.equals(sts, ahmm1.definition['states']))
        sts = self.lin.linear_states(states, [0, 1])
        self.assertTrue(sp.equals(sts, ahmm2.definition['states']))

# ---------------------------------------------------------------------------


class TestsppasAcModel(unittest.TestCase):

# This one takes too much time to be tested each time....
#     def test_load_all_models(self):
#         models = glob.glob(os.path.join(MODEL_PATH,"models-*","hmmdefs"))
#         for hmmdefs in models:
#             acmodel = sppasAcModel(hmmdefs)
#             self._test_load_save(acmodel)

    def setUp(self):
        self.hmmdefs = os.path.join(MODEL_PATH, "models-jpn", "hmmdefs")
        self.acmodel = sppasAcModel()
        self.acmodel.load_htk(self.hmmdefs)
        if os.path.exists(TEMP) is True:
            shutil.rmtree(TEMP)
        os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_load_save(self):
        self._test_load_save(self.hmmdefs)

    def _test_load_save(self, acmodel):

        # Save temporary the loaded model into a file
        tmpfile = os.path.join(TEMP, "hmmdefs.copy")
        self.acmodel.save_htk(tmpfile)

        # Load the temporary file into a new model
        acmodelcopy = sppasAcModel()
        acmodelcopy.load_htk(tmpfile)
        sp = sppasCompare()

        # Compare original and copy
        self.assertEqual(len(self.acmodel.hmms),len(acmodelcopy.hmms))
        for hmm, hmmcopy in zip(self.acmodel.hmms, acmodelcopy.hmms):
            self.assertEqual(hmm.name, hmmcopy.name)
            self.assertTrue(sp.equals(hmm.definition, hmmcopy.definition))
        self.assertTrue(sp.equals(self.acmodel.macros, acmodelcopy.macros))

    def test_get_hmm(self):
        with self.assertRaises(ValueError):
            self.acmodel.get_hmm('Q')
        Nhmm = self.acmodel.get_hmm('N')
        self.__test_states(Nhmm.definition['states'])
        self.__test_transition(Nhmm.definition['transition'])

    def test_append_hmm(self):
        with self.assertRaises(TypeError):
            self.acmodel.append_hmm({'toto': None})
        hmm = sppasHMM()

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
            self.acmodel.get_hmm("N")

    def test_load_hmm(self):
        hmm = sppasHMM()
        hmm.load(os.path.join(DATA, "N-hmm"))
        self.__test_states(hmm.definition['states'])
        self.__test_transition(hmm.definition['transition'])

    def test_save_hmm(self):
        sp = sppasCompare()
        hmm = sppasHMM()
        hmm.load(os.path.join(DATA, "N-hmm"))
        hmm.save(os.path.join(TEMP, "N-hmm-copy"))
        newhmm = sppasHMM()
        newhmm.load(os.path.join(TEMP, "N-hmm-copy"))
        self.assertEqual(hmm.name, newhmm.name)
        self.assertTrue(sp.equals(hmm.definition, newhmm.definition))

    def test_fill(self):
        sp = sppasCompare()
        acmodel1 = sppasAcModel()
        acmodel1.load_htk(os.path.join(DATA, "1-hmmdefs"))
        ahmm1 = acmodel1.get_hmm('a')
        a1transition = [macro["transition"] for macro in acmodel1.macros if macro.get('transition', None)][0]

        acmodel1.fill_hmms()
        self.assertTrue(sp.equals(ahmm1.definition['transition'], a1transition['definition']))

    def test_no_merge(self):
        nbhmms = len(self.acmodel.hmms)

        # Try to merge with the same model!
        acmodel2 = sppasAcModel()
        acmodel2.load_htk(self.hmmdefs)

        (appended, interpolated, keeped, changed) = acmodel2.merge_model(self.acmodel, gamma=1.)
        self.assertEqual(interpolated, 0)
        self.assertEqual(appended, 0)
        self.assertEqual(keeped, nbhmms)
        self.assertEqual(changed, 0)

        (appended, interpolated, keeped, changed) = acmodel2.merge_model(self.acmodel, gamma=0.5)
        self.assertEqual(interpolated, nbhmms)
        self.assertEqual(appended, 0)
        self.assertEqual(keeped, 0)
        self.assertEqual(changed, 0)

        (appended, interpolated, keeped, changed) = acmodel2.merge_model(self.acmodel, gamma=0.)
        self.assertEqual(interpolated, 0)
        self.assertEqual(appended, 0)
        self.assertEqual(keeped, 0)
        self.assertEqual(changed, nbhmms)

        # Try to merge with a different MFCC parameter kind model...
        acmodel2 = sppasAcModel()
        acmodel2.load_htk(os.path.join(MODEL_PATH, "models-cat", "hmmdefs"))
        with self.assertRaises(TypeError):
            acmodel2.merge_model(self.acmodel, gamma=1.)

    def test_merge(self):
        acmodel1 = sppasAcModel()
        acmodel1.load_htk(os.path.join(DATA, "1-hmmdefs"))
        acmodel2 = sppasAcModel()
        acmodel2.load_htk(os.path.join(DATA, "2-hmmdefs"))

        (appended, interpolated, keeped, changed) = acmodel2.merge_model(acmodel1, gamma=0.5)
        self.assertEqual(interpolated, 2)  # acopy, a
        self.assertEqual(appended, 1)      # i
        self.assertEqual(keeped, 1)        # e
        self.assertEqual(changed, 0)

        self.__test_states(acmodel2.get_hmm('a').definition['states'])
        self.__test_transition(acmodel2.get_hmm('a').definition['transition'])

    def test_replace_phones(self):
        sp = sppasCompare()
        acmodel1 = sppasAcModel()
        acmodel1.load(os.path.join(MODEL_PATH, "models-fra"))
        acmodel1.replace_phones(reverse=False)
        acmodel1.replace_phones(reverse=True)

        acmodel2 = sppasAcModel()
        acmodel2.load(os.path.join(MODEL_PATH, "models-fra"))

        for h1 in acmodel1.hmms:
            h2 = acmodel2.get_hmm(h1.name)
            self.assertTrue(sp.equals(h1.definition['transition'], h2.definition['transition']))
            self.assertTrue(sp.equals(h1.definition['states'], h2.definition['states']))

    def test_monophones(self):
        acmodel1 = sppasAcModel()
        acmodel1.load(os.path.join(MODEL_PATH, "models-fra"))

        acmodel2 = acmodel1.extract_monophones()
        acmodel2.save(os.path.join(TEMP, 'fra-mono'))
        self.assertTrue(os.path.isfile(os.path.join(TEMP, 'fra-mono', 'hmmdefs')))
        self.assertTrue(os.path.isfile(os.path.join(TEMP, 'fra-mono', 'monophones.repl')))
        self.assertFalse(os.path.isfile(os.path.join(TEMP, 'fra-mono', 'tiedlist')))

        self.assertEqual(len(acmodel2.hmms), 38)

    def test_proto(self):
        sp = sppasCompare()
        h1 = sppasHtkIO()
        h1.write_hmm_proto(25, os.path.join(TEMP, "proto_from_htkio"))

        h2 = sppasHMM()
        h2.create_proto(25)
        h2.save(os.path.join(TEMP, "proto_from_hmm"))

        m1 = sppasHMM()
        m1.load(os.path.join(TEMP, "proto_from_htkio"))

        m2 = sppasHMM()
        m2.load(os.path.join(TEMP, "proto_from_hmm"))

        self.assertTrue(sp.equals(m1.definition['transition'], m2.definition['transition']))
        self.assertTrue(sp.equals(m1.definition['states'], m2.definition['states']))

    def __test_transition(self, transition):
        self.assertEqual(transition['dim'], 5)
        matrix = transition['matrix']
        for i in range(len(matrix)-1):
            # the last vector is always 0.!
            vector = matrix[i]
            self.assertEqual(1.0, round(sum(vector), 4))

    def __test_states(self, states):
        for item in states:  # a dict
            state = item['state']
            streams = state['streams']
            for s in streams:  # a list
                mixtures = s['mixtures']
                for mixture in mixtures:  # a list of dict
                    # self.assertEqual(type(mixture['weight']),float)
                    pdf = mixture['pdf']
                    self.assertEqual(pdf['mean']['dim'], 25)
                    self.assertEqual(len(pdf['mean']['vector']), 25)
                    self.assertEqual(pdf['covariance']['variance']['dim'], 25)
                    self.assertEqual(len(pdf['covariance']['variance']['vector']), 25)
                    self.assertEqual(type(pdf['gconst']), float)
