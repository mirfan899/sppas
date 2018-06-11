# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.anndata.tests.test_label
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the clases of the label package.

    Includes tests of sppasLabel(), sppasTag().

"""
import unittest

from sppas import ORTHO_SYMBOLS, PHONE_SYMBOLS
from sppas.src.utils.makeunicode import u, b, text_type
from ..annlabel.tag import sppasTag
from ..annlabel.label import sppasLabel

# ---------------------------------------------------------------------------

SIL_PHON = PHONE_SYMBOLS.keys()[PHONE_SYMBOLS.values().index("silence")]
NOISE_PHON = PHONE_SYMBOLS.keys()[PHONE_SYMBOLS.values().index("noise")]
SIL_ORTHO = ORTHO_SYMBOLS.keys()[ORTHO_SYMBOLS.values().index("silence")]
PAUSE_ORTHO = ORTHO_SYMBOLS.keys()[ORTHO_SYMBOLS.values().index("pause")]
NOISE_ORTHO = ORTHO_SYMBOLS.keys()[ORTHO_SYMBOLS.values().index("noise")]

# ---------------------------------------------------------------------------


class TestTag(unittest.TestCase):
    """ Represents a typed content of a label.
    A sppasTag() content can be one of the following types:

        1. string/unicode - (str)
        2. integer - (int)
        3. float - (float)
        4. boolean - (bool)
        5. a list of sppasTag(), all of the same type - (list)

    """
    def test_unicode(self):
        text = sppasTag("\têtre   \r   être être  \n  ")
        self.assertIsInstance(str(text), str)

    # -----------------------------------------------------------------------

    def test_string_content(self):
        """ Test the tag if the content is a unicode/string. """

        text = sppasTag(" test ")
        self.assertEqual(text.get_content(), u("test"))

        text = sppasTag(2)
        self.assertEqual(text.get_typed_content(), "2")
        self.assertEqual(text.get_type(), "str")

        text = sppasTag(2.1)
        self.assertEqual(text.get_typed_content(), "2.1")
        self.assertEqual(text.get_type(), "str")

    # -----------------------------------------------------------------------

    def test_int_content(self):
        """ Test the tag if the content is an integer. """

        # int value
        text = sppasTag(2, tag_type="int")
        textstr = sppasTag("2")
        self.assertEqual(text.get_typed_content(), 2)
        self.assertEqual(text.get_content(), u("2"))
        self.assertNotEqual(text.get_typed_content(), textstr.get_typed_content())
        self.assertEqual(text.get_content(), textstr.get_content())

        with self.assertRaises(TypeError):
            sppasTag("uh uhm", tag_type="int")

    # -----------------------------------------------------------------------

    def test_float_content(self):
        """ Test the tag if the content is a floating point. """

        text = sppasTag(2.10, tag_type="float")
        textstr = sppasTag("2.1")
        self.assertEqual(text.get_typed_content(), 2.1)
        self.assertEqual(text.get_content(), u("2.1"))
        self.assertNotEqual(text.get_typed_content(), textstr.get_typed_content())
        self.assertEqual(text.get_content(), textstr.get_content())

        with self.assertRaises(TypeError):
            sppasTag("uh uhm", tag_type="float")

    # -----------------------------------------------------------------------

    def test_bool_content(self):
        """ Test the tag if the content is a boolean. """

        text = sppasTag("1", tag_type="bool")
        textstr = sppasTag("True")
        self.assertEqual(text.get_typed_content(), True)
        self.assertEqual(text.get_content(), u("True"))
        self.assertNotEqual(text.get_typed_content(), textstr.get_typed_content())
        self.assertEqual(text.get_content(), textstr.get_content())

    # -----------------------------------------------------------------------

    def test_set(self):
        text = sppasTag("test")
        text.set_content("toto")

    # -----------------------------------------------------------------------

    def test__eq__(self):
        text1 = sppasTag(" test    ")
        text2 = sppasTag("test\n")
        self.assertEqual(text1, text2)
        self.assertTrue(text1 == text2)

        text1 = sppasTag("")
        text2 = sppasTag("\n")
        self.assertEqual(text1, text2)
        self.assertTrue(text1 == text2)

# ---------------------------------------------------------------------------


class TestEvents(unittest.TestCase):
    """ Events are labels with a specific text.
    This is a SPPAS convention!
    Test recognized events: silences, pauses, noises, etc.

    """
    def test_is_silence(self):
        label = sppasLabel(sppasTag(SIL_PHON))
        text = label.get_best()
        self.assertTrue(text.is_silence())
        self.assertFalse(text.is_silence() is False)
        label = sppasLabel(sppasTag(SIL_ORTHO))
        text = label.get_best()
        self.assertTrue(text.is_silence())

    def test_IsPause(self):
        label = sppasLabel(sppasTag(PAUSE_ORTHO))
        self.assertTrue(label.get_best().is_pause())

    def test_IsNoise(self):
        label = sppasLabel(sppasTag(NOISE_ORTHO))
        self.assertTrue(label.get_best().is_noise())
        label = sppasLabel(sppasTag(NOISE_PHON))
        self.assertTrue(label.get_best().is_noise())

# ---------------------------------------------------------------------------


class TestLabel(unittest.TestCase):

    def test_unicode(self):
        label = sppasLabel(sppasTag("être"))

    def test_label_type(self):
        label = sppasLabel(sppasTag(2, "int"))
        self.assertIsInstance(str(label.get_best()), str)
        self.assertIsInstance(label.get_best().get_content(), text_type)
        self.assertIsInstance(label.get_best().get_typed_content(), int)

    def test_is_label(self):
        label = sppasLabel(sppasTag(SIL_ORTHO))
        text = label.get_best()
        self.assertFalse(text.is_speech())

    def test_add_tag(self):
        label = sppasLabel(sppasTag("score0.5"), score=0.5)
        self.assertEqual(label.get_best().get_content(), u("score0.5"))

        label.append(sppasTag("score0.8"), score=0.8)
        self.assertEqual(label.get_best().get_content(), u("score0.8"))

        label.append(sppasTag("score1.0"), score=1.0)
        self.assertEqual(label.get_best().get_content(), u("score1.0"))

        # expect error (types inconsistency):
        text1 = sppasTag(2.1)
        self.assertEqual(text1.get_type(), "str")
        text2 = sppasTag(2.10, tag_type="float")
        self.assertEqual(text2.get_type(), "float")
        label.append(text1, score=0.8)
        with self.assertRaises(TypeError):
            label.append(text2, score=0.2)

    def test_is_empty(self):
        label = sppasLabel(sppasTag(""), score=0.5)
        self.assertTrue(label.get_best().is_empty())

        label.append(sppasTag("text"), score=0.8)
        self.assertFalse(label.get_best().is_empty())

    def test_equal(self):
        label = sppasLabel(sppasTag(""), score=0.5)
        self.assertTrue(label == label)
        self.assertEqual(label, label)
        self.assertTrue(label == sppasLabel(sppasTag(""), score=0.5))
        self.assertFalse(label == sppasLabel(sppasTag(""), score=0.7))
        self.assertFalse(label == sppasLabel(sppasTag("a"), score=0.5))

    def test_set_score(self):
        tag = sppasTag("toto")
        label = sppasLabel(tag, score=0.5)
        self.assertEqual(label.get_score(tag), 0.5)
        label.set_score(tag, 0.8)
        self.assertEqual(label.get_score(tag), 0.8)
