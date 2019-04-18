from sppas.src.files.filedatacompare import *

class TestFileNameExtensionCompare (unittest.TestCase):

    def setUp(self):
        self.cmp = sppasFileNamePropertiesCompare()

    def test_lock (self):
        d = __file__
        fp = FileName(d)

        self.assertTrue(fp.match([(self.cmp.lock, True, True)]))