# ---------------------------------------------------------------------------
# Unittests
# ---------------------------------------------------------------------------


import unittest
from os.path import dirname

import sppas
from sppas import sppasTypeError
from ..fileref import AttValue, Reference
from ..filedata import FileData
from ..filebase import FileBase, States
from ..filestructure import FileName, FileRoot, FilePath
from ..fileexc import FileOSError, FileTypeError, PathTypeError


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
        self.assertFalse(fn.statefn == States().CHECKED)

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
        self.assertFalse(fp.statefp is States().ALL_CHECKED)
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

class TestAttValue(unittest.TestCase):

    def setUp(self):
        self.valint = AttValue('12', 'int', 'speaker\'s age')
        self.valfloat = AttValue('0.002', 'float', 'word appearance frequency')
        self.valbool = AttValue('false', 'bool', 'speaker is minor')
        self.valstr = AttValue('Hi everyone !', None, 'первый токен')

    def testInt(self):
        self.assertTrue(isinstance(self.valint.get_typed_value(), int))
        self.assertTrue(self.valint.get_value() == '12')

    def testFloat(self):
        self.assertTrue(isinstance(self.valfloat.get_typed_value(), float))
        self.assertFalse(self.valfloat.get_value() == 0.002)

    def testBool(self):
        self.assertFalse(self.valbool.get_typed_value())

    def testStr(self):
        self.assertTrue(self.valstr.get_typed_value() == 'Hi everyone !')
        self.assertTrue(self.valstr.get_value() == 'Hi everyone !')

    def testRepr(self):
        self.assertTrue(str(self.valint) == '12, speaker\'s age')

    def testSetTypeValue(self):
        with self.assertRaises(sppasTypeError) as error:
            self.valbool.set_value_type('AttValue')

        self.assertTrue(isinstance(error.exception, sppasTypeError))

    def testGetValuetype(self):
        self.assertTrue(self.valstr.get_value_type() == 'str')

# ---------------------------------------------------------------------------


class TestCategories(unittest.TestCase):

    def setUp(self):
        self.micros = Reference('microphone')
        self.micros.add('mic1', AttValue('Bird UM1', None, '最初のインタビューで使えていましたマイク'))
        self.micros.add('mic2', 'AKG D5')

    def testGetItem(self):
        self.assertTrue(
            self.micros['mic1'].description == '最初のインタビューで使えていましたマイク'
        )

    def testAttValue(self):
        self.assertFalse(
            isinstance(self.micros['mic2'].get_typed_value(), int)
        )

    def testAddKey(self):
        with self.assertRaises(ValueError) as AsciiError:
            self.micros.add('i*asaà', 'Blue Yeti')

        self.assertTrue(
            isinstance(AsciiError.exception, ValueError)
        )

    def testPopKey(self):
        self.micros.pop('mic1')

        self.assertFalse(
            len(self.micros) == 2
        )

# ---------------------------------------------------------------------------


class TestFileData(unittest.TestCase):

    def setUp(self):
        self.files = FileData()
        self.files.add_file(__file__)
        self.files.add_file(sppas.paths.samples + '\\samples-fra\\AC track_0379.PitchTier')
        self.files.add_file(sppas.paths.samples + '\\samples-fra\\AC track_0379.TextGrid')
        self.files.add_file(sppas.paths.samples + '\\samples-jpn\\JPA_M16_JPA_T02.TextGrid')
        self.files.add_file(sppas.paths.samples + '\\samples-cat\\TB-FE1-H1_phrase1.TextGrid')

        self.age = Reference('age')
        self.age.add('age1', AttValue('14', 'int', 'age of the first interviwee'))
        self.age.add('age2', AttValue('11', 'int', 'age of the second interviewee'))
        self.age.add('age3', AttValue('12', 'int', 'age of the third interviewee'))

    def testSave(self):
        current_file_list = list()
        saved_file_list = list()
        self.files.save(sppas.paths.sppas + '\\src\\files\\test\\save.json')
        for fp in self.files:
            for fr in fp:
                for fn in fr:
                    current_file_list.append(fn)
        self.files.load(sppas.paths.sppas + '\\src\\files\\test\\save.json')
        for fp in self.files:
            for fr in fp:
                for fn in fr:
                    saved_file_list.append(fn)

        for i in range(len(current_file_list)):
            self.assertTrue(
                current_file_list[i] == saved_file_list[i]
            )

        # self.files.set_state(FilePath.States.ALL_LOCKED)
        # self.files.load(sppas.paths.sppas + '\\src\\files\\test\\save.json')

    def testState(self):
        self.files.set_state(States().ALL_LOCKED)

        self.assertTrue(
            self.files.get_state(self.files[0]) == States().ALL_LOCKED
        )

    def testRef(self):
        self.files.add_ref(self.age)

        self.assertTrue(
            len(self.files.get_refs()) == 1
        )

    def testAssocations(self):
        self.files.add_ref(self.age)

        for ref in self.files.get_refs():
            ref.state = States().CHECKED

        self.files.set_state(States().ALL_CHECKED)

        self.files.associate()

        for fp in self.files:
            for fr in fp:
                self.assertTrue(
                    fr.references.contains(self.age)
                )

# ---------------------------------------------------------------------------
