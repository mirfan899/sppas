from os import *
from random import randint
from unittest import *
from sppas.src.files.filedatacompare import *


class TestRootCompare (unittest.TestCase):

    def setUp(self):
        self.cmp = sppasRootCompare

    def test_exact (self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp exactly equals d
        self.assertTrue(fp.match([(self.cmp.exact, d, False)]))

    def test_iexact (self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp matches with upper case d
        self.assertFalse(fp.match([(self.cmp.iexact, d.upper(), True)]))

    def test_startswith (self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp begins with d's first character
        self.assertTrue(fp.match([(self.cmp.startswith, d[0], False)]))

    def test_istartswith (self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp starts with d's first character in any case
        self.assertTrue(fp.match([(self.cmp.istartswith, d[0].upper(), False)]))

    def test_endswith (self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp finishes with d's last character
        self.assertFalse(fp.match([(self.cmp.endswith, d[-1], True)]))

    def test_iendswith (self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp finishes with d's last character in any case
        self.assertFalse(fp.match([(self.cmp.iendswith, d[-1].upper(), True)]))

    def test_contains (self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp contains any d's character
        self.assertTrue(fp.match([(self.cmp.contains, d[randint(0, len(d) -1)], False)]))

    def test_regexp (self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp looks like the regex
        self.assertFalse(fp.match([(self.cmp.regexp, "[^a-z]", True)]))

    def test_check (self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp isn't checked
        self.assertTrue(fp.match([(self.cmp.check, False, False)]))

    def test_expand (self):
        d = path.splitext(__file__)[0]
        fp = FileRoot(d)
        #fp isn't expanded
        self.assertFalse(fp.match([(self.cmp.expand, True, True)]))