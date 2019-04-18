# ---------------------------------------------------------------------------
# Unittests
# ---------------------------------------------------------------------------
import unittest
from sppas.src.files.filedata import FileBase, FileName, FileRoot, FilePath
from sppas.src.files.fileexc import FileOSError


class TestFileBase(unittest.TestCase):

    def test_init(self):
        f = FileBase(__file__)
        self.assertEqual(__file__, f.get_id())

    def test_overloads(self):
        f = FileBase(__file__)
        self.assertEqual(__file__, str(f))
        self.assertEqual(__file__, "{!s:s}".format(f))


# ---------------------------------------------------------------------------


class TestFileName(unittest.TestCase):

    def test_init(self):
        # Attempt to instantiate with an unexisting file
        with self.assertRaises(FileOSError):
            FileName("toto")

        # Attempt to instantiate with a directory
        with self.assertRaises(FileTypeError):
            FileName(dirname(__file__))

        # Normal situation
        fn = FileName(__file__)
        self.assertEqual(__file__, fn.get_id())
        self.assertFalse(fn.check)

    def test_extension(self):
        fn = FileName(__file__)
        self.assertEqual(".PY", fn.get_extension())
        self.assertEqual("text/plain", fn.get_mime())


# ---------------------------------------------------------------------------


class TestFileRoot(unittest.TestCase):

    def test_init(self):
        fr = FileRoot(__file__)
        root = __file__.replace('.py', '')
        self.assertEqual(root, fr.id)
        fr = FileRoot("toto")
        self.assertEqual("toto", fr.id)

    def test_pattern(self):
        self.assertEqual('', FileRoot.pattern('filename.wav'))
        self.assertEqual('', FileRoot.pattern('filename-unk.xra'))
        self.assertEqual('-phon', FileRoot.pattern('filename-phon.xra'))

    def test_root(self):
        self.assertEqual('filename', FileRoot.root('filename.wav'))
        self.assertEqual('filename', FileRoot.root('filename-phon.xra'))
        self.assertEqual('filename-unk', FileRoot.root('filename-unk.xra'))
        self.assertEqual('filename-unk-unk', FileRoot.root('filename-unk-unk.xra'))
        self.assertEqual('filename.unk-unk', FileRoot.root('filename.unk-unk.xra'))
        self.assertEqual(
            'e:\\bigi\\__pycache__\\filedata.cpython-37',
            FileRoot.root('e:\\bigi\\__pycache__\\filedata.cpython-37.pyc'))


# ---------------------------------------------------------------------------


class TestFilePath(unittest.TestCase):

    def test_init(self):
        # Attempt to instantiate with an unexisting file
        with self.assertRaises(FileOSError):
            FilePath("toto")

        # Attempt to instantiate with a file
        with self.assertRaises(PathTypeError):
            FilePath(__file__)

        # Normal situation
        d = dirname(__file__)
        fp = FilePath(d)
        self.assertEqual(d, fp.id)
        self.assertFalse(fp.check)
        self.assertEqual(fp.id, fp.get_id())

        # Property is only defined for 'get' (set is not implemented).
        with self.assertRaises(AttributeError):
            fp.id = "toto"

    def test_append_remove(self):
        d = dirname(__file__)
        fp = FilePath(d)

        # Attempt to append an unexisting file
        with self.assertRaises(FileOSError):
            fp.append("toto")

        # Normal situation
        fn = fp.append(__file__)
        self.assertIsNotNone(fn)
        self.assertIsInstance(fn, FileName)
        self.assertEqual(__file__, fn.id)

        fr = fp.get_root(FileRoot.root(fn.id))
        self.assertIsNotNone(fr)
        self.assertIsInstance(fr, FileRoot)
        self.assertEqual(FileRoot.root(__file__), fr.id)

        self.assertEqual(1, len(fp))
        self.assertEqual(1, len(fr))

        # Attempt to add again the same file
        fn2 = fp.append(__file__)
        self.assertEqual(1, len(fp))
        self.assertEqual(fn, fn2)
        fn3 = fp.append(FileName(__file__))
        self.assertEqual(1, len(fp))
        self.assertEqual(fn, fn3)

        # Remove the file from its name
        fp.remove(fp.get_root(FileRoot.root(__file__)))
        self.assertEqual(0, len(fp))

        # Append an instance of FileName
        fn = FileName(__file__)
        rfn = fp.append(fn)
        self.assertIsNotNone(rfn)
        self.assertEqual(fn, rfn)
        self.assertEqual(1, len(fp))

        # Attempt to add again the same file
        fp.append(FileName(__file__))
        self.assertEqual(1, len(fp))

        # Remove the file from its instance
        i = fp.remove(fp.get_root(fn.id))
        self.assertEqual(0, len(fp))
        self.assertEqual(i, 0)

        # Remove an un-existing file
        self.assertEqual(-1, fp.remove("toto"))

        # Remove a file not in the list!
        i = fp.remove(FileName(__file__))
        self.assertEqual(-1, i)


# ---------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
