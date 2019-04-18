from os import *
from random import randint
from unittest import *
from sppas.src.files.filedatacompare import *

class TestFileNameCompare (unittest.TestCase):

    def setUp(self):
        self.cmp = sppasFileNameCompare()
        self.fileName = 'testFileNameCompare'

    def test_exact(self):
        d = __file__
        fp = FileName(d)
        # fp exactly equals d
        self.assertTrue(fp.match([(self.cmp.exact, self.fileName, False)]))

    def test_iexact(self):
        d = __file__
        fp = FileName(d)
        # fp matches with upper case d
        self.assertFalse(fp.match([(self.cmp.iexact, self.fileName.upper(), True)]))

    def test_startswith(self):
        d = __file__
        fp = FileName(d)
        # fp begins with d's first character
        self.assertTrue(fp.match([(self.cmp.startswith, self.fileName[0], False)]))

    def test_istartswith(self):
        d = __file__
        fp = FileName(d)
        # fp starts with d's first character in any case
        self.assertTrue(fp.match([(self.cmp.istartswith, self.fileName[0].upper(), False)]))

    def test_endswith(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character
        self.assertFalse(fp.match([(self.cmp.endswith, self.fileName[-1], True)]))

    def test_iendswith(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character in any case
        self.assertFalse(fp.match([(self.cmp.iendswith, self.fileName[-1].upper(), True)]))

    def test_contains(self):
        d = __file__
        fp = FileName(d)
        # fp contains any d's character
        self.assertTrue(fp.match([(self.cmp.contains, self.fileName[randint(0, len(self.fileName) - 1)], False)]))

    def test_regexp(self):
        d = __file__
        fp = FileName(d)
        # fp looks like the regex
        self.assertFalse(fp.match([(self.cmp.regexp, "^[a-z]", True)]))