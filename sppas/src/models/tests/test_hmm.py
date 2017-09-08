# -*- coding:utf-8 -*-

import unittest
import os.path
import copy
import shutil

from sppas import RESOURCES_PATH, SAMPLES_PATH
from sppas.src.models.acm.hmm import sppasBaseModel, sppasHMM, HMMInterpolation
from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
MODEL_PATH = os.path.join(RESOURCES_PATH, "models")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestBaseModel(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is True:
            shutil.rmtree(TEMP)
        os.mkdir(TEMP)
        shutil.copytree(os.path.join(DATA, "protos"), os.path.join(TEMP, "protos"))

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_init(self):
        model = sppasBaseModel()
        self.assertEqual(model.name, sppasBaseModel.DEFAULT_NAME)
        self.assertEqual(model.definition['state_count'], 0)
        self.assertEqual(len(model.definition['states']), 0)
        self.assertEqual(len(model.definition['transition']), 0)

    def test_name(self):
        model = sppasBaseModel()
        model.name = "test0"
        self.assertEqual(model.name, "test0")
        model.set_name("test1")
        self.assertEqual(model.name, "test1")
        with self.assertRaises(TypeError):
            model.name = 123

    def test_definition(self):
        model = sppasBaseModel()
        model.definition['toto'] = "N'importe quoi"

