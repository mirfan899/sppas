#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os.path
import shutil

from sp_glob import RESOURCES_PATH

from resources.acm.acmodel import AcModel
from resources.acm.hmm import HMM
from resources.acm.modelmixer import ModelMixer

# ---------------------------------------------------------------------------

MODELDIR = os.path.join(RESOURCES_PATH, "models")

# ---------------------------------------------------------------------------


class TestModelMixer(unittest.TestCase):

    def setUp(self):
        # a French speaker reading an English text...
        self._modelL2dir = os.path.join(MODELDIR, "models-eng")
        self._modelL1dir = os.path.join(MODELDIR, "models-fra")

    def testMix(self):
        acmodel1 = AcModel()
        hmm1 = HMM()
        hmm1.create_proto(25)
        hmm1.name = "y"
        acmodel1.append_hmm(hmm1)
        acmodel1.repllist.add("y", "j")

        acmodel2 = AcModel()
        hmm2 = HMM()
        hmm2.create_proto(25)
        hmm2.name = "j"
        hmm3 = HMM()
        hmm3.create_proto(25)
        hmm3.name = "y"
        acmodel2.hmms.append(hmm2)
        acmodel2.hmms.append(hmm3)
        acmodel2.repllist.add("y","y")
        acmodel2.repllist.add("j","j")

        modelmixer = ModelMixer()
        modelmixer.set_models(acmodel1,acmodel2)

        outputdir = os.path.join(MODELDIR, "models-test")
        modelmixer.mix(outputdir, gamma=1.)
        mixedh1 = AcModel()
        mixedh1.load(outputdir)
        shutil.rmtree(outputdir)

    def testMixData(self):
        modelmixer = ModelMixer()
        modelmixer.load(self._modelL2dir, self._modelL1dir)
        outputdir = os.path.join(MODELDIR, "models-eng-fra")
        modelmixer.mix(outputdir, gamma=0.5)
        self.assertTrue(os.path.exists(outputdir))
        acmodel1 = AcModel()
        acmodel1.load_htk(os.path.join(self._modelL2dir, "hmmdefs"))
        acmodel1 = acmodel1.extract_monophones()
        acmodel2 = AcModel()
        acmodel2.load_htk(os.path.join(os.path.join(MODELDIR, "models-eng-fra"), "hmmdefs"))
        shutil.rmtree(outputdir)
