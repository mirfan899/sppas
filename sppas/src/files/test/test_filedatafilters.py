import unittest
import os

import sppas
from ..filedata import FileData
from ..filedatacompare import *
from ..filedatafilters import sppasFileDataFilters


class TestsFileDataFilter (unittest.TestCase):

    def setUp(self):
        self.files = FileData()
        self.files.add_file(__file__)
        self.files.add_file(os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.PitchTier'))
        self.files.add_file(os.path.join(sppas.paths.samples, 'samples-jpn', 'JPA_M16_JPA_T02.TextGrid'))
        self.files.add_file(os.path.join(sppas.paths.samples, 'samples-cat', 'TB-FE1-H1_phrase1.TextGrid'))

        spk1 = FileReference('spk1')
        spk1.set_type('SPEAKER')
        spk1.append(sppasAttribute('age', '20', "int"))
        spk1.append(sppasAttribute('name', 'toto'))

        ref2 = FileReference('record')
        ref2.append(sppasAttribute('age', '50', "int"))
        ref2.append(sppasAttribute('name', 'toto'))

        fr1 = self.files.get_object(
            os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379'))
        fr1.add_ref(spk1)

        fr2 = self.files.get_object(
            os.path.join(sppas.paths.samples, 'samples-cat', 'TB-FE1-H1_phrase1'))
        fr2.add_ref(ref2)

        self.data_filter = sppasFileDataFilters(self.files)

    def test_path(self):
        self.assertEqual(3, len(self.data_filter.path(contains='samples-')))

    def test_root(self):
        self.assertEqual(4, len(self.data_filter.root(contains='_')))

    def test_filename(self):
        self.assertEqual(1, len(self.data_filter.name(iexact='jpa_m16_jpa_t02')))

    def test_filename_extension(self):
        self.assertEqual(3, len(self.data_filter.extension(not_exact='.PY')))

    def test_filename_state(self):
        self.assertEqual(4, len(self.data_filter.file(state=States().UNUSED)))

    def test_ref_id(self):
        self.assertEqual(1, len(self.data_filter.ref(startswith='rec')))
        self.assertEqual(0, len(self.data_filter.ref(startswith='aa')))

    def test_att(self):
        self.assertEqual(1, len(self.data_filter.att(iequal=('age', '20'))))
        self.assertEqual(1, len(self.data_filter.att(gt=('age', '30'))))
        self.assertEqual(2, len(self.data_filter.att(le=('age', '60'))))
        self.assertEqual(2, len(self.data_filter.att(exact=('name', 'toto'))))
        self.assertEqual(2, len(self.data_filter.att(exact=('name', 'toto'), lt=('age', '60'), logic_bool="and")))
        self.assertEqual(1, len(self.data_filter.att(exact=('name', 'toto'), equal=('age', '20'), logic_bool="and")))
        self.assertEqual(2, len(self.data_filter.att(exact=('name', 'toto'), equal=('age', '20'), logic_bool="or")))

    def test_mixed_filter_sets_way(self):
        self.assertEqual(1, len(self.data_filter.extension(not_exact='.PY') &
                                self.data_filter.name(iexact='jpa_m16_jpa_t02')))

    def test_mixed_filter_argument_way(self):
        self.assertEqual(2, len(self.data_filter.extension(not_exact='.PY', startswith='.TEXT', logic_bool='and')))
