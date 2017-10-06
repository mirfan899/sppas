# -*- coding:utf-8 -*-

import unittest
import os.path
import copy
import shutil

from sppas import RESOURCES_PATH, SAMPLES_PATH
from sppas.src.utils.compare import sppasCompare
from sppas.src.utils.fileutils import sppasFileUtils

from ..acm.acmodelhtkio import sppasHtkIO
from ..acm.htktrain import sppasHTKModelTrainer, sppasDataTrainer, \
    sppasPhoneSet, sppasTrainingCorpus, sppasHTKModelInitializer

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

    # -----------------------------------------------------------------------

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------

    def test_datatrainer(self):
        datatrainer = sppasDataTrainer()
        datatrainer.create()
        self.assertEqual(datatrainer.check(), None)
        dire = datatrainer.workdir
        self.assertTrue(os.path.exists(dire))
        datatrainer.delete()
        self.assertFalse(os.path.exists(dire))

    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------

    def test_trainingcorpus(self):
        corpus = sppasTrainingCorpus()

        self.assertEqual(corpus.phonemap.map_entry('#'), "#")

        corpus.fix_resources(dict_file=os.path.join(RESOURCES_PATH, "dict", "nan.dict"))
        self.assertEqual(len(corpus.monophones), 44)

        corpus.fix_resources(dict_file=os.path.join(RESOURCES_PATH, "dict", "nan.dict"),
                             mapping_file=os.path.join(RESOURCES_PATH, "models", "models-nan", "monophones.repl"))
        self.assertEqual(corpus.phonemap.map_entry('#'), "sil")

        self.assertFalse(corpus.add_file("toto", "toto"))
        self.assertTrue(corpus.add_file(os.path.join(DATA, "F_F_B003-P8-palign.TextGrid"), os.path.join(DATA, "F_F_B003-P8.wav")))
        corpus.datatrainer.delete()

    # -----------------------------------------------------------------------

    def test_initializer_without_corpus(self):
        corpus = sppasTrainingCorpus()
        workdir = os.path.join(TEMP, "working")
        os.mkdir(workdir)
        shutil.copy(os.path.join(DATA, "protos", "vFloors"), workdir)

        initial = sppasHTKModelInitializer(corpus, workdir)
        corpus.datatrainer.protodir = os.path.join(DATA, "protos")
        initial.create_model()

    # -----------------------------------------------------------------------

    def test_trainer_without_data(self):
        trainer = sppasHTKModelTrainer()
        model = trainer.training_recipe()
        self.assertEqual(len(model.get_hmms()), 0)

    # def test_trainer_with_data(self):
    #     setup_logging(1, None)
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
    #     self.assertEqual(len(acmodel), 41)

# ---------------------------------------------------------------------------


class TestsppasAcModel(unittest.TestCase):

    def setUp(self):
        self.hmmdefs = os.path.join(MODEL_PATH, "models-jpn")
        self.acmodel = sppasHtkIO()
        self.acmodel.read(self.hmmdefs)
        if os.path.exists(TEMP) is True:
            shutil.rmtree(TEMP)
        os.mkdir(TEMP)

    # -----------------------------------------------------------------------

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_get_hmm(self):
        with self.assertRaises(ValueError):
            self.acmodel.get_hmm('Q')
        Nhmm = self.acmodel.get_hmm('N')
        self.__test_states(Nhmm.definition['states'])
        self.__test_transition(Nhmm.definition['transition'])

    # -----------------------------------------------------------------------

    def test_append_hmm(self):
        with self.assertRaises(TypeError):
            self.acmodel.append_hmm({'toto': None})

        n_hmm = self.acmodel.get_hmm('N')
        with self.assertRaises(ValueError):
            self.acmodel.append_hmm(n_hmm)

        new_hmm = copy.deepcopy(n_hmm)
        new_hmm.name = "NewN"
        self.acmodel.append_hmm(new_hmm)

    # -----------------------------------------------------------------------

    def test_pop_hmm(self):
        self.acmodel.pop_hmm("N")
        with self.assertRaises(ValueError):
            self.acmodel.get_hmm("N")
    #
    # def test_load_hmm(self):
    #     hmm = sppasHMM()
    #     hmm.load(os.path.join(DATA, "N-hmm"))
    #     self.__test_states(hmm.definition['states'])
    #     self.__test_transition(hmm.definition['transition'])
    #
    # def test_save_hmm(self):
    #     sp = sppasCompare()
    #     hmm = sppasHMM()
    #     hmm.load(os.path.join(DATA, "N-hmm"))
    #     hmm.save(os.path.join(TEMP, "N-hmm-copy"))
    #     newhmm = sppasHMM()
    #     newhmm.load(os.path.join(TEMP, "N-hmm-copy"))
    #     self.assertEqual(hmm.name, newhmm.name)
    #     self.assertTrue(sp.equals(hmm.definition, newhmm.definition))

    # -----------------------------------------------------------------------

    def test_fill(self):
        sp = sppasCompare()
        acmodel1 = sppasHtkIO()
        acmodel1.read_macros_hmms([os.path.join(DATA, "1-hmmdefs")])
        ahmm1 = acmodel1.get_hmm('a')
        a1transition = [macro["transition"] for macro in acmodel1.get_macros() if macro.get('transition', None)][0]

        acmodel1.fill_hmms()
        self.assertTrue(sp.equals(ahmm1.definition['transition'], a1transition['definition']))

    # -----------------------------------------------------------------------

    def test_no_merge(self):
        nbhmms = len(self.acmodel.get_hmms())

        # Try to merge with the same model!
        acmodel2 = sppasHtkIO()
        acmodel2.read(self.hmmdefs)

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
        acmodel2 = sppasHtkIO()
        acmodel2.read_macros_hmms([os.path.join(MODEL_PATH, "models-cat", "hmmdefs")])
        with self.assertRaises(TypeError):
            acmodel2.merge_model(self.acmodel, gamma=1.)

    # -----------------------------------------------------------------------

    def test_merge(self):
        acmodel1 = sppasHtkIO()
        acmodel1.read_macros_hmms([os.path.join(DATA, "1-hmmdefs")])
        acmodel2 = sppasHtkIO()
        acmodel2.read_macros_hmms([os.path.join(DATA, "2-hmmdefs")])

        (appended, interpolated, keeped, changed) = acmodel2.merge_model(acmodel1, gamma=0.5)
        self.assertEqual(interpolated, 2)  # acopy, a
        self.assertEqual(appended, 1)      # i
        self.assertEqual(keeped, 1)        # e
        self.assertEqual(changed, 0)

        self.__test_states(acmodel2.get_hmm('a').definition['states'])
        self.__test_transition(acmodel2.get_hmm('a').definition['transition'])

    # -----------------------------------------------------------------------

    def test_replace_phones(self):
        sp = sppasCompare()
        acmodel1 = sppasHtkIO()
        acmodel1.read(os.path.join(MODEL_PATH, "models-fra"))
        acmodel1.replace_phones(reverse=False)
        acmodel1.replace_phones(reverse=True)

        acmodel2 = sppasHtkIO()
        acmodel2.read(os.path.join(MODEL_PATH, "models-fra"))

        for h1 in acmodel1.get_hmms():
            h2 = acmodel2.get_hmm(h1.name)
            self.assertTrue(sp.equals(h1.definition['transition'], h2.definition['transition']))
            self.assertTrue(sp.equals(h1.definition['states'], h2.definition['states']))

    # -----------------------------------------------------------------------

    def test_monophones(self):
        acmodel1 = sppasHtkIO()
        acmodel1.read(os.path.join(MODEL_PATH, "models-fra"))
        acmodel2 = acmodel1.extract_monophones()
        parser = sppasHtkIO()
        parser.set(acmodel2)
        parser.write(os.path.join(TEMP, 'fra-mono'))
        self.assertTrue(os.path.isfile(os.path.join(TEMP, 'fra-mono', 'hmmdefs')))
        self.assertTrue(os.path.isfile(os.path.join(TEMP, 'fra-mono', 'monophones.repl')))
        self.assertFalse(os.path.isfile(os.path.join(TEMP, 'fra-mono', 'tiedlist')))

        self.assertEqual(len(acmodel2.get_hmms()), 38)
        self.assertEqual(len(acmodel2), 38)

    # -----------------------------------------------------------------------

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
