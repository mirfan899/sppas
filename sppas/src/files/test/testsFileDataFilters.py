import sppas
from sppas.src.files.filedata import FileData
from sppas.src.files.filedatacompare import *
from sppas.src.files.filedatafilters import sppasFileDataFilters


class TestsFileDataFilter (unittest.TestCase):

    def setUp(self):
        self.files = FileData()
        self.files.add_file(__file__)
        self.files.add_file(sppas.paths.__dict__['samples'] + '\\samples-fra\\AC track_0379.PitchTier')
        self.files.add_file(sppas.paths.__dict__['samples'] + '\\samples-jpn\\JPA_M16_JPA_T02.TextGrid')
        self.files.add_file(sppas.paths.__dict__['samples'] + '\\samples-cat\\TB-FE1-H1_phrase1.TextGrid')

        age = Category('age')
        age.add('age1', AttValue('14', 'int', 'age of the first interviwee'))
        age.add('age2', AttValue('11', 'int', 'age of the second interviewee'))
        age.add('age3', AttValue('12', 'int', 'age of the third interviewee'))

        fr = FileRoot(sppas.paths.__dict__['samples'] + '\\samples-fra\\AC track_0379.PitchTier')
        fr.categories.append(age)

        self.data_filter = sppasFileDataFilters(self.files)

    def test_path(self):
        self.assertTrue(
            len(self.data_filter.path(contains='samples-')) == 3
        )

    def test_root(self):
        self.assertTrue(
            len(self.data_filter.root(contains='_')) == 3
        )

    def test_fileName(self):
        self.assertTrue(
            len(self.data_filter.name(iexact='jpa_m16_jpa_t02')) == 1
        )

    def test_fileNameExtension(self):
        self.assertTrue(
            len(self.data_filter.extension(not_exact='.PY')) == 3
        )

    def test_fileNameProperties(self):
        self.assertTrue(
            len(self.data_filter.fprop(not_lock='true')) == 4
        )

    def test_ref_id(self):
        self.assertTrue(
            len(self.data_filter.ref(startswith='a')) == 0
        )

    def test_attValue(self):
        self.assertTrue(
            len(self.data_filter.att(ge='12')) == 1
        )

    def test_mixed_filter_sets_way(self):
        self.assertTrue(
            len(self.data_filter.extension(not_exact='.PY') & self.data_filter.name(iexact='jpa_m16_jpa_t02')) == 1
        )

    def test_mixed_filter_argument_way(self):
        self.assertTrue(
            len(self.data_filter.extension(not_exact='.PY', startswith='.TEXT', logic_bool='and')) == 2
        )