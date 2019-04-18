from os import *
from random import randint
from sppas.src.files.filedatacompare import *

class TestFileNameExtensionCompare (unittest.TestCase):

    def setUp(self):
        self.cmp = sppasFileNameExtensionCompare()
        self.extenstion = path.splitext(__file__)[1].upper()

    def test_exact(self):
        d = __file__
        fp = FileName(d)
        # fp exactly equals d
        self.assertTrue(fp.match([(self.cmp.exact, self.extenstion, False)]))

    def test_iexact(self):
        d = __file__
        fp = FileName(d)
        # fp matches with upper case d
        self.assertFalse(fp.match([(self.cmp.iexact, self.extenstion.lower(), True)]))

    def test_startswith(self):
        d = __file__
        fp = FileName(d)
        # fp begins with d's first character
        self.assertTrue(fp.match([(self.cmp.startswith, self.extenstion[0], False)]))

    def test_istartswith(self):
        d = __file__
        fp = FileName(d)
        # fp starts with d's first character in any case
        self.assertTrue(fp.match([(self.cmp.istartswith, self.extenstion[0].lower(), False)]))

    def test_endswith(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character
        self.assertFalse(fp.match([(self.cmp.endswith, self.extenstion[-1], True)]))

    def test_iendswith(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character in any case
        self.assertFalse(fp.match([(self.cmp.iendswith, self.extenstion[-1].lower(), True)]))

    def test_contains(self):
        d = __file__
        fp = FileName(d)
        # fp contains any d's character
        self.assertTrue(fp.match([(self.cmp.contains, self.extenstion[randint(0, len(self.extenstion) - 1)], False)]))

    def test_regexp(self):
        d = __file__
        fp = FileName(d)
        # fp looks like the regex
        self.assertFalse(fp.match([(self.cmp.regexp, "^\.", True)]))