# -*- coding: utf8 -*-
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

    src.annotations.tests.test_align.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os
import shutil
import codecs

from sppas.src.config import sg
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasTier

from ..Align.tracksio import TrackNamesGenerator
from ..Align.tracksio import TracksWriter
from ..Align.tracksio import ListIO
from sppas.src.utils.fileutils import sppasFileUtils
from ..annotationsexc import BadInputError
from ..annotationsexc import SizeInputsError
from ..annotationsexc import NoDirectoryError

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestTrackNamesGenerator(unittest.TestCase):
    """Manage names of the files for a given track number."""

    def test_names(self):
        """Test all generators: audio, phones, tokens, align."""
        # audio
        self.assertEqual("track_000001.wav",
                         TrackNamesGenerator.audio_filename("", 1))
        # phones
        self.assertEqual("track_000001.phn",
                         TrackNamesGenerator.phones_filename("", 1))
        # tokens
        self.assertEqual("track_000001.tok",
                         TrackNamesGenerator.tokens_filename("", 1))
        # aligned file
        self.assertEqual("track_000001",
                         TrackNamesGenerator.align_filename("", 1))
        self.assertEqual("track_000001.palign",
                         TrackNamesGenerator.align_filename("", 1, "palign"))

# ---------------------------------------------------------------------------


class TestTracksWriter(unittest.TestCase):
    """Write track files."""

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_write_tokens(self):
        """Write the tokenization of a track in a file."""
        # test to write an annotation with complex labels
        l1 = sppasLabel([sppasTag("option1"), sppasTag("alt1")])
        l2 = sppasLabel([sppasTag("option2"), sppasTag("alt2")])
        ann = sppasAnnotation(sppasLocation(sppasPoint(1)), [l1, l2])
        TracksWriter._write_tokens(ann, TEMP, 1)
        fn = os.path.join(TEMP, "track_000001.tok")
        self.assertTrue(os.path.exists(fn))
        with codecs.open(fn, "r", sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(lines))
        self.assertEqual("{option1|alt1} {option2|alt2}", lines[0])

        # test to write an annotation with already serialized labels
        sentence = "A serialized list of {labels|tags}"
        ann = sppasAnnotation(
            sppasLocation(sppasPoint(1)),
            sppasLabel(sppasTag(sentence)))
        TracksWriter._write_tokens(ann, TEMP, 2)
        fn = os.path.join(TEMP, "track_000002.tok")
        self.assertTrue(os.path.exists(fn))
        with codecs.open(fn, "r", sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(lines))
        self.assertEqual(sentence, lines[0])

    # -----------------------------------------------------------------------

    def test_write_phonemes(self):
        """Write the phonetization of a track in a file."""
        # test to write an annotation with complex labels
        l1 = sppasLabel([sppasTag("j"), sppasTag("S")])
        l2 = sppasLabel([sppasTag("e"), sppasTag("E")])
        ann = sppasAnnotation(sppasLocation(sppasPoint(1)), [l1, l2])
        TracksWriter._write_phonemes(ann, TEMP, 1)
        fn = os.path.join(TEMP, "track_000001.phn")
        self.assertTrue(os.path.exists(fn))
        with codecs.open(fn, "r", sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(lines))
        self.assertEqual("{j|S} {e|E}", lines[0])

        # test to write an annotation with already serialized labels
        sentence = "A serialized list of {labels|tags}"
        ann = sppasAnnotation(
            sppasLocation(sppasPoint(1)),
            sppasLabel(sppasTag(sentence)))
        TracksWriter._write_phonemes(ann, TEMP, 2)
        fn = os.path.join(TEMP, "track_000002.phn")
        self.assertTrue(os.path.exists(fn))
        with codecs.open(fn, "r", sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()
        self.assertEqual(1, len(lines))
        self.assertEqual(sentence, lines[0])

    # -----------------------------------------------------------------------

    def test_create_tok_tier(self):
        """Create a tier with tokens like 'w_1 w_2...w_n' from phonemes."""
        l1 = sppasLabel([sppasTag("j"), sppasTag("S")])
        l2 = sppasLabel([sppasTag("e"), sppasTag("E")])
        tier = sppasTier("phonemes")
        tier.create_annotation(sppasLocation(sppasPoint(1)), [l1, l2])
        tier.create_annotation(sppasLocation(sppasPoint(2)), sppasLabel(sppasTag("{j|S} {e|E}")))
        tok_tier = TracksWriter._create_tok_tier(tier)
        self.assertEqual(2, len(tok_tier))
        content_a1 = tok_tier[0].get_best_tag().get_content()
        self.assertEqual("w_1 w_2", content_a1)
        content_a2 = tok_tier[1].get_best_tag().get_content()
        self.assertEqual("w_1 w_2", content_a2)

    # -----------------------------------------------------------------------

    def test_write_text_tracks(self):
        """Write tokenization and phonetization into separated track files."""
        l1 = sppasLabel([sppasTag("j"), sppasTag("S")])
        l2 = sppasLabel([sppasTag("e"), sppasTag("E")])
        tier_phn = sppasTier("phonemes")
        tier_phn.create_annotation(sppasLocation(sppasPoint(1)), [l1, l2])
        tier_phn.create_annotation(sppasLocation(sppasPoint(2)), sppasLabel(sppasTag("j-e s-H-i")))
        tier_tok = sppasTier("tokens")
        tier_tok.create_annotation(sppasLocation(sppasPoint(1)), sppasLabel(sppasTag("j' ai")))
        tier_tok.create_annotation(sppasLocation(sppasPoint(2)), sppasLabel(sppasTag('je suis')))

        with self.assertRaises(SizeInputsError):
            TracksWriter._write_text_tracks(tier_phn, sppasTier('toto'), TEMP)

        dir_tracks = os.path.join(TEMP, "test_write_text_tracks_1")
        os.mkdir(dir_tracks)
        TracksWriter._write_text_tracks(tier_phn, None, dir_tracks)
        created_files = os.listdir(dir_tracks)
        self.assertEqual(4, len(created_files))
        lines = list()
        for fn in created_files:
            with codecs.open(os.path.join(dir_tracks, fn), "r", sg.__encoding__) as fp:
                new_lines = fp.readlines()
                fp.close()
            self.assertEqual(1, len(new_lines))
            lines.append(new_lines[0])
        self.assertTrue("w_1 w_2" in lines)
        self.assertTrue("{j|S} {e|E}" in lines)
        self.assertTrue("j-e s-H-i" in lines)

        dir_tracks = os.path.join(TEMP, "test_write_text_tracks_2")
        os.mkdir(dir_tracks)
        TracksWriter._write_text_tracks(tier_phn, tier_tok, dir_tracks)
        created_files = os.listdir(dir_tracks)
        self.assertEqual(4, len(created_files))
        lines = list()
        for fn in created_files:
            with codecs.open(os.path.join(dir_tracks, fn), "r", sg.__encoding__) as fp:
                new_lines = fp.readlines()
                fp.close()
            self.assertEqual(1, len(new_lines))
            lines.append(new_lines[0])
        self.assertTrue("j' ai" in lines)
        self.assertTrue("je suis" in lines)
        self.assertTrue("{j|S} {e|E}" in lines)
        self.assertTrue("j-e s-H-i" in lines)

    # -----------------------------------------------------------------------

    def test_write_audio_tracks(self):
        """Write the first channel of an audio file into separated track files."""
        pass

    # -----------------------------------------------------------------------

    def test_write_tracks(self):
        """Main method to write tracks from the given data."""
        pass

# ---------------------------------------------------------------------------


class TestListIO(unittest.TestCase):
    """Write track files."""

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_read_write(self):
        """Manage the file with a list of tracks (units, ipus...)."""
        units = [(1., 2.), (2., 3.), (3., 4.)]
        ListIO.write(TEMP, units)
        read_units = ListIO.read(TEMP)
        self.assertEqual(units, read_units)

        with self.assertRaises(BadInputError):
            ListIO.read("toto")

# ---------------------------------------------------------------------------

