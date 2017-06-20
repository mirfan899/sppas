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

    src.annotations.Align.alignio.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import os
import codecs

from sppas import encoding
from sppas.src.resources.mapping import Mapping
from sppas.src.utils.makeunicode import sppasUnicode

from .aligntrack import AlignTrack
from .tracks import TracksReader, TrackSplitter, TrackNamesGenerator

# ------------------------------------------------------------------


class ListIO(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Manage the file with a list of tracks.

    """
    DEFAULT_FILENAME = "tracks_index.list"

    # ------------------------------------------------------------------

    def __init__(self):
        pass

    # ------------------------------------------------------------------

    @staticmethod
    def read(dirname):
        """ Read a list file (start-time end-time).

        :param dirname: Name of the directory with the file to read.

        """
        filename = os.path.join(dirname, ListIO.DEFAULT_FILENAME)
        with codecs.open(filename, 'r', encoding) as fp:
            lines = fp.readlines()

        _units = []
        # Each line corresponds to a track,
        # with a couple 'start end' of float values.
        for line in lines:
            s = sppasUnicode(line)
            line = s.to_strip()
            _tab = line.split()
            if len(_tab) >= 2:
                _units.append((float(_tab[0]), float(_tab[1])))

        return _units

    # ------------------------------------------------------------------

    @staticmethod
    def write(dirname, units):
        """ Write a list file (start-time end-time).

        :param dirname: Name of the directory with the file to read.
        :param units: List of units to write.

        """
        filename = os.path.join(dirname, ListIO.DEFAULT_FILENAME)
        with codecs.open(filename, 'w', encoding) as fp:
            for start, end in units:
                fp.write("%.6f %.6f " % (start, end))
                fp.write("\n")

# ------------------------------------------------------------------


class AlignIO(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Read/Write segments from/to Tiers.

    ??? HOW TO DO: READ ALL ALTERNATIVE LABELS AND MERGE ALTERNATIVE RESULTS ???

    """
    def __init__(self, mapping, model):
        """ Creates a new AlignIO instance.

        :param mapping: (Mapping) a mapping table to convert the phone set

        """
        # Mapping system for the phonemes
        if mapping is None:
            mapping = Mapping()
        if isinstance(mapping, Mapping) is False:
            raise TypeError('Aligner expected a Mapping() as argument.')
        self._mapping = mapping

        # The automatic alignment system
        self.aligntrack = AlignTrack(model)

        # The file names of tracks generator
        self._tracknames = TrackNamesGenerator()

    # ------------------------------------------------------------------------

    def set_aligner(self, alignername):
        """ Fix the name of the aligner.

        :param alignername: (str) Case-insensitive name of the aligner.

        """
        self.aligntrack.set_aligner(alignername)

    # -----------------------------------------------------------------------

    def get_aligner(self):
        """ Return the name used as identifier of the aligner. """

        return self.aligntrack.get_aligner()

    # ----------------------------------------------------------------------

    def set_infersp(self, infersp):
        """ Fix the infersp option.

        :param infersp (bool) If infersp is set to True, the aligner
        will add an optional short pause at the end of each token, and the
        will infer if it is relevant.

        """
        self.aligntrack.set_infersp(infersp)

    # ------------------------------------------------------------------------

    def segment_track(self, track, diralign, segment=True):
        """ Perform the speech segmentation of a track in a directory.

        :param track: (str - int)
        :param diralign: (str)
        :param segment: (bool) If True, call an aligner to segment speech,
        else create a file with an empty alignment.

        :returns: A message of the aligner in case of any problem, or
        an empty string if success.

        """
        audio_filename = self._tracknames.audio_filename(diralign, track)
        phonname = self._tracknames.phones_filename(diralign, track)
        tokenname = self._tracknames.tokens_filename(diralign, track)
        alignname = self._tracknames.align_filename(diralign, track)

        if segment is True:
            msg = self.aligntrack.segmenter(audio_filename, phonname, tokenname, alignname)
        else:
            msg = self.aligntrack.segmenter(audio_filename, None, None, alignname)

        return msg

    # ------------------------------------------------------------------------

    def read(self, dirname):
        """ Read time-aligned tracks in a directory and return a Transcription.

        :param dirname: (str) Input directory to get files.
        :returns: Transcription

        """
        units = ListIO().read(dirname)

        trsin = TracksReader()
        trsin.set_tracksnames(self._tracknames)
        trsin.read(dirname, units)

        # map-back phonemes
        self._mapping.set_keep_miss(True)
        self._mapping.set_reverse(False)

        # Map time-aligned phonemes (even the alternatives)
        tier = trsin.Find("PhonAlign")
        for ann in tier:
            for text in ann.GetLabel().GetLabels():
                text.SetValue(self._mapping.map_entry(text.GetValue()))

        return trsin

    # ------------------------------------------------------------------------

    def split(self, inputaudio, phontier, toktier, diralign):
        """ Write tracks of a Transcription.
        If the given phontier is not already time-aligned in intervals,
        an automatic track-segmenter will be applied first and the TimeAligned
        version of the tokenization is returned.

        :param inputaudio: (str) Audio file name.
        :param phontier: (Tier) The phonetization tier.
        :param toktier: (Tier) The tokenization tier, or None.
        :param diralign: (str) Output directory to store files.

        :returns: Transcription

        """
        # Map phonemes from SAMPA to the expected ones.
        self._mapping.set_keep_miss(True)
        self._mapping.set_reverse(True)

        # Map phonetizations (even the alternatives)
        for ann in phontier:
            for text in ann.GetLabel().GetLabels():
                text.SetValue(self._mapping.map(text.GetValue()))

        sgmt = TrackSplitter()
        sgmt.set_tracksnames(self._tracknames)
        sgmt.set_trackalign(self.aligntrack)
        units = sgmt.split(inputaudio, phontier, toktier, diralign)
        ListIO().write(diralign, units)

        return sgmt
