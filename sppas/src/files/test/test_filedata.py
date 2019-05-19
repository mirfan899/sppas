
import unittest
import os
import json

import sppas
from sppas import sppasTypeError
from ..fileref import AttValue, FileReference
from ..filedata import FileData
from ..filebase import States
from ..fileexc import FileLockedError

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


class TestReferences(unittest.TestCase):

    def setUp(self):
        self.micros = FileReference('microphone')
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
        self.data = FileData()
        self.data.add_file(__file__)
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.PitchTier'))
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.TextGrid'))
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-jpn', 'JPA_M16_JPA_T02.TextGrid'))
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-cat', 'TB-FE1-H1_phrase1.TextGrid'))

        self.r1 = FileReference('SpeakerAB')
        self.r1.set_type('SPEAKER')
        self.r1.add('initials', AttValue('AB'))
        self.r1.add('sex', AttValue('F'))
        self.r2 = FileReference('SpeakerCM')
        self.r2.set_type('SPEAKER')
        self.r2.add('initials', AttValue('CM'))
        self.r1.add('sex', AttValue('F'))
        self.r3 = FileReference('Dialog1')
        self.r3.set_type('INTERACTION')
        self.r3.add('when', AttValue('2003', 'int', 'Year of recording'))
        self.r3.add('where', AttValue('Aix-en-Provence', att_description='Place of recording'))

    def test_init(self):
        data = FileData()
        self.assertEqual(36, len(data.id))
        self.assertEqual(0, len(data))

    def test_save(self):
        self.data.add_ref(self.r1)
        self.data.add_ref(self.r2)
        self.data.add_ref(self.r3)
        current_file_list = list()
        saved_file_list = list()
        self.data.save(os.path.join(sppas.paths.sppas, 'src', 'files', 'test', 'save.json'))
        for fp in self.data:
            for fr in fp:
                for fn in fr:
                    current_file_list.append(fn)

        data = FileData.load(os.path.join(sppas.paths.sppas, 'src', 'files', 'test', 'save.json'))
        for fp in data:
            for fr in fp:
                for fn in fr:
                    saved_file_list.append(fn)
        self.assertEqual(len(current_file_list), len(saved_file_list))
        for f1, f2 in zip(current_file_list, saved_file_list):
            self.assertEqual(f1, f2)

    def test_state(self):
        self.data.set_object_state(States().LOCKED)
        self.assertEqual(States().LOCKED, self.data.get_object_state(self.data[0]))

    def test_ref(self):
        self.data.add_ref(self.r1)
        self.assertEqual(1, len(self.data.get_refs()))
        self.data.add_ref(self.r2)
        self.assertEqual(2, len(self.data.get_refs()))
        self.r1.set_state(States().CHECKED)
        self.r2.set_state(States().CHECKED)
        self.data.remove_refs(States().CHECKED)
        self.assertEqual(0, len(self.data.get_refs()))

    def test_assocations(self):
        self.data.add_ref(self.age)
        self.data.set_object_state(States().CHECKED)

        for ref in self.data.get_refs():
            self.data.set_object_state(States().CHECKED, ref)

        self.data.associate()

        for fp in self.data:
            for fr in fp:
                self.assertTrue(self.age in fr.get_references())

        self.data.dissociate()

        for fp in self.data:
            for fr in fp:
                self.assertEqual(0, len(fr.get_references()))

    def test_serialize(self):
        d = self.data.serialize()
        jsondata = json.dumps(d, indent=4, separators=(',', ': '))
        jsondict = json.loads(jsondata)
        self.assertEqual(d, jsondict)

    def test_parse(self):
        self.data.add_ref(self.r1)
        self.data.add_ref(self.r2)
        self.data.add_ref(self.r3)
        d = self.data.serialize()
        data = self.data.parse(d)
        self.assertEqual(len(data), len(self.data))
        self.assertEqual(len(data.get_refs()), len(self.data.get_refs()))
        dd = data.serialize()
        self.assertEqual(d, dd)
