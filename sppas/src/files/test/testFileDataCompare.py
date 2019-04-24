from os import *
from random import randint

from sppas.src.files.filedata import AttValue
from sppas.src.files.filedatacompare import *


class TestFileDataCompare(unittest.TestCase):

    def setUp(self):
        #for FileNameCompare
        self.cmpFileName = sppasFileNameCompare()
        self.fileName = 'testFileDataCompare'

        #for FileNameExtensionCompare
        self.cmpFileNameExtension = sppasFileNameExtensionCompare()
        self.extenstion = path.splitext(__file__)[1].upper()

        #for FileNamePropertiesCompare
        self.cmpFileNameProperties = sppasFileNamePropertiesCompare()

        #for FilePathCompare
        self.cmpPath = sppasPathCompare()

        #for FileRootComapre
        self.cmpRoot = sppasRootCompare

    def test_exact_fn(self):
        d = __file__
        fp = FileName(d)
        # fp exactly equals d
        self.assertTrue(fp.match([(self.cmpFileName.exact, self.fileName, False)]))

    def test_iexact_fn(self):
        d = __file__
        fp = FileName(d)
        # fp matches with upper case d
        self.assertFalse(fp.match([(self.cmpFileName.iexact, self.fileName.upper(), True)]))

    def test_startswith_fn(self):
        d = __file__
        fp = FileName(d)
        # fp begins with d's first character
        self.assertTrue(fp.match([(self.cmpFileName.startswith, self.fileName[0], False)]))

    def test_istartswith_fn(self):
        d = __file__
        fp = FileName(d)
        # fp starts with d's first character in any case
        self.assertTrue(fp.match([(self.cmpFileName.istartswith, self.fileName[0].upper(), False)]))

    def test_endswith_fn(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character
        self.assertFalse(fp.match([(self.cmpFileName.endswith, self.fileName[-1], True)]))

    def test_iendswith_fn(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character in any case
        self.assertFalse(fp.match([(self.cmpFileName.iendswith, self.fileName[-1].upper(), True)]))

    def test_contains_fn(self):
        d = __file__
        fp = FileName(d)
        # fp contains any d's character
        self.assertTrue(fp.match([(self.cmpFileName.contains, self.fileName[randint(0, len(self.fileName) - 1)], False)]))

    def test_regexp_fn(self):
        d = __file__
        fp = FileName(d)
        # fp looks like the regex
        self.assertFalse(fp.match([(self.cmpFileName.regexp, "^[a-z]", True)]))

    def test_exact_fe(self):
        d = __file__
        fp = FileName(d)
        # fp exactly equals d
        self.assertTrue(fp.match([(self.cmpFileNameExtension.exact, self.extenstion, False)]))

    def test_iexact_fe(self):
        d = __file__
        fp = FileName(d)
        # fp matches with upper case d
        self.assertFalse(fp.match([(self.cmpFileNameExtension.iexact, self.extenstion.lower(), True)]))

    def test_startswith_fe(self):
        d = __file__
        fp = FileName(d)
        # fp begins with d's first character
        self.assertTrue(fp.match([(self.cmpFileNameExtension.startswith, self.extenstion[0], False)]))

    def test_istartswith_fe(self):
        d = __file__
        fp = FileName(d)
        # fp starts with d's first character in any case
        self.assertTrue(fp.match([(self.cmpFileNameExtension.istartswith, self.extenstion[0].lower(), False)]))

    def test_endswith_fe(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character
        self.assertFalse(fp.match([(self.cmpFileNameExtension.endswith, self.extenstion[-1], True)]))

    def test_iendswith_fe(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character in any case
        self.assertFalse(fp.match([(self.cmpFileNameExtension.iendswith, self.extenstion[-1].lower(), True)]))

    def test_contains_fe(self):
        d = __file__
        fp = FileName(d)
        # fp contains any d's character
        self.assertTrue(fp.match([(self.cmpFileNameExtension.contains, self.extenstion[randint(0, len(self.extenstion) - 1)], False)]))

    def test_regexp_fe(self):
        d = __file__
        fp = FileName(d)
        # fp looks like the regex
        self.assertFalse(fp.match([(self.cmpFileNameExtension.regexp, "^\.", True)]))

    def test_lock_fprop (self):
        d = __file__
        fp = FileName(d)

        self.assertTrue(fp.match([(self.cmpFileNameProperties.lock, True, True)]))

    def test_match_fp(self):
        d = dirname(__file__)
        fp = FilePath(d)

        # fp.id is matching dirname
        self.assertTrue(fp.match([(self.cmpPath.exact, d, False)]))

        # fp.id is not matching dirname
        self.assertFalse(fp.match([(self.cmpPath.exact, d, True)]))

        # fp.id is matching dirname and path is checked
        self.assertTrue(fp.match(
            [(self.cmpPath.exact, d, False),
             (self.cmpPath.check, False, False)]))

        #fp is checked
        self.assertFalse(fp.match([(self.cmpPath.check, True, False)]))

        # fp.id ends with 'files' (the name of the package)!
        self.assertTrue(fp.match([(self.cmpPath.endswith, "test", False)]))

    def test_exact_fr(self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp exactly equals d
        self.assertTrue(fp.match([(self.cmpRoot.exact, d, False)]))

    def test_iexact_fr(self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp matches with upper case d
        self.assertFalse(fp.match([(self.cmpRoot.iexact, d.upper(), True)]))

    def test_startswith_fr(self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp begins with d's first character
        self.assertTrue(fp.match([(self.cmpRoot.startswith, d[0], False)]))

    def test_istartswith_fr(self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp starts with d's first character in any case
        self.assertTrue(fp.match([(self.cmpRoot.istartswith, d[0].upper(), False)]))

    def test_endswith_fr(self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp finishes with d's last character
        self.assertFalse(fp.match([(self.cmpRoot.endswith, d[-1], True)]))

    def test_iendswith_fr(self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp finishes with d's last character in any case
        self.assertFalse(fp.match([(self.cmpRoot.iendswith, d[-1].upper(), True)]))

    def test_contains_fr(self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp contains any d's character
        self.assertTrue(fp.match([(self.cmpRoot.contains, d[randint(0, len(d) -1)], False)]))

    def test_regexp_fr(self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp looks like the regex
        self.assertFalse(fp.match([(self.cmpRoot.regexp, "[^a-z]", True)]))

    def test_check_fr(self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp isn't checked
        self.assertTrue(fp.match([(self.cmpRoot.check, False, False)]))

    def test_expand_fr(self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp isn't expanded
        self.assertFalse(fp.match([(self.cmpRoot.expand, True, True)]))


class TestFileDataReferencesCompare(unittest.TestCase):

    def setUp(self):
        self.micros = Category('microphone')
        self.micros.add('mic1', AttValue('Bird UM1', None, '最初のインタビューで使えていましたマイク'))
        self.micros.add('mic2', 'AKG D5')
        self.id_cmp = sppasReferenceCompare()

    def test_exact_id(self):
        self.assertTrue(self.micros.match([(self.id_cmp.exact, 'microphone', False)]))

    def test_iexact_id(self):
        name = 'microphone'
        self.assertFalse(self.micros.match([(self.id_cmp.iexact, name.upper(), True)]))

    def test_startswith_id(self):
        name = 'microphone'
        self.assertTrue(self.micros.match([(self.id_cmp.startswith, name[0], False)]))

    def test_istartswith_id(self):
        name = 'microphone'
        self.assertFalse(self.micros.match([(self.id_cmp.istartswith, name[0].upper(), True)]))

    def test_endswith_id(self):
        name = 'microphone'
        self.assertTrue(self.micros.match([(self.id_cmp.endswith, name[-1], False)]))

    def test_iendswith_id(self):
        name = 'microphone'
        self.assertFalse(self.micros.match([(self.id_cmp.iendswith, name[-1].upper(), True)]))

    def test_contains_id(self):
        name = 'microphone'
        self.assertTrue(self.micros.match([(self.id_cmp.contains, name[randint(0, len(name) - 1)], False)]))

    def test_regexp_id(self):
        regexp = '[^*_ç]'
        self.assertTrue(self.micros.match([(self.id_cmp.regexp, regexp, False)]))
