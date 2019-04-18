from sppas.src.files.filedata import FileData
from sppas.src.files.filedatacompare import *
from sppas.src.files.filedatafilters import sppasFileDataFilters


class TestsFileDataFilter (unittest.TestCase):

    def setUp(self):
        self.files = FileData()
        self.files.add_file(__file__)
        #change here C:\Users\drabczuk by where you installed sppas file
        self.files.add_file('C:\\Users\\drabczuk\\sppas\\samples\\samples-fra\\AC track_0379.PitchTier')
        self.files.add_file('C:\\Users\\drabczuk\\sppas\\samples\\samples-jpn\\JPA_M16_JPA_T02.TextGrid')
        self.files.add_file('C:\\Users\\drabczuk\\sppas\\samples\\samples-cat\\TB-FE1-H1_phrase1.TextGrid')

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

    def test_fileNameProperties (self):
        self.assertTrue(
            len(self.data_filter.file(not_lock='true')) == 4
        )

    def test_mixed_filter_sets_way (self):
        self.assertTrue(
            len(self.data_filter.extension(not_exact='.PY') & self.data_filter.name(iexact='jpa_m16_jpa_t02')) == 1
        )

    def test_mixed_filter_argument_way (self):
        self.assertTrue(
            len(self.data_filter.extension(not_exact='.PY', startswith='.TEXT', logic_bool='and')) == 2
        )