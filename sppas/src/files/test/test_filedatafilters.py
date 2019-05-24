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

        age = FileReference('age')
        age.append(sppasAttribute('age1', '14', 'int', 'age of the first interviewee'))
        age.append(sppasAttribute('age2', '11', 'int', 'age of the second interviewee'))
        age.append(sppasAttribute('age3', '12', 'int', 'age of the third interviewee'))

        # for fp in self.files:
        #     for fr in fp:
        #         fr.categories.append(age)

        fr = FileRoot(os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.PitchTier'))
        fr.add_ref(age)
        self.data_filter = sppasFileDataFilters(self.files)

    def test_path(self):
        self.assertEqual(3, len(self.data_filter.path(contains='samples-')))

    def test_root(self):
        self.assertEqual(4, len(self.data_filter.root(contains='_')))

    def test_fileName(self):
        self.assertEqual(1, len(self.data_filter.name(iexact='jpa_m16_jpa_t02')))

    def test_fileNameExtension(self):
        self.assertEqual(3, len(self.data_filter.extension(not_exact='.PY')))

    def test_fileNameState(self):
        self.assertEqual(4, len(self.data_filter.file(state=States().UNUSED)))

    def test_ref_id(self):
        self.assertEqual(0, len(self.data_filter.ref(startswith='a')))
        self.assertEqual(1, len(self.data_filter.att(equal=('age1', '14'))))

    # def test_attValue(self):
    #     self.assertTrue(
    #         len(self.data_filter.att(age_ge='12')) == 1
    #     )

    def test_mixed_filter_sets_way(self):
        self.assertEqual(1, len(self.data_filter.extension(not_exact='.PY') &
                                self.data_filter.name(iexact='jpa_m16_jpa_t02')))

    def test_mixed_filter_argument_way(self):
        self.assertEqual(2, len(self.data_filter.extension(not_exact='.PY', startswith='.TEXT', logic_bool='and')))
