from unittest import *
from sppas.src.files.filedatacompare import *


class TestPathCompare(unittest.TestCase):

    def setUp(self):
        self.cmp = sppasPathCompare()

    def test_match(self):
        d = dirname(__file__)
        fp = FilePath(d)

        # fp.id is matching dirname
        self.assertTrue(fp.match([(self.cmp.exact, d, False)]))

        # fp.id is not matching dirname
        self.assertFalse(fp.match([(self.cmp.exact, d, True)]))

        # fp.id is matching dirname and path is checked
        self.assertTrue(fp.match(
            [(self.cmp.exact, d, False),
             (self.cmp.check, False, False)]))

        #fp is checked
        self.assertFalse(fp.match([(self.cmp.check, True, False)]))

        # fp.id ends with 'files' (the name of the package)!
        self.assertTrue(fp.match([(self.cmp.endswith, "test", False)]))

        if __name__ == '__main__':
            unittest.main()

# ---------------------------------------------------------------------------
