#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os.path
import shutil

from sppas import RESOURCES_PATH

from sppas.src.models.acm.acmodel import sppasAcModel
from sppas.src.models.acm.hmm import sppasHMM
from sppas.src.models.acm.modelmixer import sppasModelMixer

# ---------------------------------------------------------------------------

MODELDIR = os.path.join(RESOURCES_PATH, "models")

# ---------------------------------------------------------------------------


class TestModelMixer(unittest.TestCase):

    def setUp(self):
        # a French speaker reading an English text...
        self._model_L2dir = os.path.join(MODELDIR, "models-eng")
        self._model_L1dir = os.path.join(MODELDIR, "models-fra")

    def testMix(self):
        acmodel1 = sppasAcModel()
        hmm1 = sppasHMM()
        hmm1.create_proto(25)
        hmm1.name = "y"
        acmodel1.append_hmm(hmm1)
        acmodel1.repllist.add("y", "j")

        acmodel2 = sppasAcModel()
        hmm2 = sppasHMM()
        hmm2.create_proto(25)
        hmm2.name = "j"
        hmm3 = sppasHMM()
        hmm3.create_proto(25)
        hmm3.name = "y"
        acmodel2.hmms.append(hmm2)
        acmodel2.hmms.append(hmm3)
        acmodel2.repllist.add("y", "y")
        acmodel2.repllist.add("j", "j")

        modelmixer = sppasModelMixer()
        modelmixer.set_models(acmodel1, acmodel2)

        outputdir = os.path.join(MODELDIR, "models-test")
        modelmixer.mix(outputdir, gamma=1.)
        mixedh1 = sppasAcModel()
        mixedh1.load(outputdir)
        shutil.rmtree(outputdir)

    def testMixData(self):
        modelmixer = sppasModelMixer()
        modelmixer.load(self._model_L2dir, self._model_L1dir)
        outputdir = os.path.join(MODELDIR, "models-eng-fra")
        modelmixer.mix(outputdir, gamma=0.5)
        self.assertTrue(os.path.exists(outputdir))
        acmodel1 = sppasAcModel()
        acmodel1.load_htk(os.path.join(self._model_L2dir, "hmmdefs"))
        acmodel1 = acmodel1.extract_monophones()
        acmodel2 = sppasAcModel()
        acmodel2.load_htk(os.path.join(os.path.join(MODELDIR, "models-eng-fra"), "hmmdefs"))
        shutil.rmtree(outputdir)
