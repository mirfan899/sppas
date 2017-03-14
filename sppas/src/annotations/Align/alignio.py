#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: alignio.py
# ----------------------------------------------------------------------------

import os
import codecs

from sppas import encoding
from sppas.src.resources.mapping import Mapping
from sppas.src.resources.rutils import to_strip

from .aligntrack import AlignTrack
from .tracks import TracksReader, TrackSplitter, TrackNamesGenerator

# ------------------------------------------------------------------
# Main class
# ------------------------------------------------------------------


class AlignIO(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Read/Write segments from/to Tiers.

    ??? HOW TO DO: READ ALL ALTERNATIVE LABELS AND MERGE ALTERNATIVE RESULTS ???

    """
    def __init__(self, mapping, model):
        """
        Creates a new AlignIO instance.

        @param mapping (Mapping) a mapping table to convert the phone set

        """
        # Mapping system for the phonemes
        if mapping is None:
            mapping = Mapping()
        if isinstance(mapping, Mapping) is False:
            raise TypeError('Aligner expected a Mapping as argument.')
        self._mapping = mapping

        # The automatic alignment system
        self.aligntrack = AlignTrack( model )

        # The list of units file generator
        self._listio = ListIO()

        # The file names of tracks generator
        self._tracknames = TrackNamesGenerator()

    # ------------------------------------------------------------------------

    def set_aligner(self, alignername):
        """
        Fix the name of the aligner.
        The list of accepted aligner names is available in:
        >>> aligners.aligner_names()

        @param alignername (str - IN) Case-insensitive name of the aligner.

        """
        self.aligntrack.set_aligner(alignername)

    # -----------------------------------------------------------------------

    def get_aligner(self):
        """
        Return the aligner name identifier.

        """
        return self.aligntrack.get_aligner()

    # ----------------------------------------------------------------------

    def set_infersp(self, infersp):
        """
        Fix the infersp option.

        @param infersp (bool - IN) If infersp is set to True, the aligner
        will add an optional short pause at the end of each token, and the
        will infer if it is relevant.

        """
        self.aligntrack.set_infersp( infersp )

    # ------------------------------------------------------------------------

    def segment_track(self, track, diralign, segment=True):
        """
        Perform the speech segmentation of a track in a directory.

        @param track (str - int)
        @param diralign (str - IN)
        @param segment (bool - IN) If True, call an aligner to segment speech,
        else create a file with an empty alignment.

        @return A message of the aligner in case of any problem, or
        an empty string if success.

        """
        audiofilename = self._tracknames.audiofilename(diralign, track)
        phonname      = self._tracknames.phonesfilename(diralign,track)
        tokenname     = self._tracknames.tokensfilename(diralign,track)
        alignname     = self._tracknames.alignfilename(diralign,track)

        if segment is True:
            msg = self.aligntrack.segmenter(audiofilename, phonname, tokenname, alignname)
        else:
            msg = self.aligntrack.segmenter(audiofilename, None, None, alignname)

        return msg

    # ------------------------------------------------------------------------

    def read(self, dirname):
        """
        Read time-aligned tracks in a directory and return a Transcription.

        @param diralign (str - IN) Input directory to get files.
        @return Transcription

        """
        units = self._listio.read( dirname )

        trsin = TracksReader()
        trsin.set_tracksnames( self._tracknames )
        trsin.read(dirname, units)

        # map-back phonemes
        self._mapping.set_keep_miss(True)
        self._mapping.set_reverse(False)

        # Map time-aligned phonemes (even the alternatives)
        tier = trsin.Find("PhonAlign")
        for ann in tier:
            for text in ann.GetLabel().GetLabels():
                text.SetValue( self._mapping.map_entry(text.GetValue()) )

        return trsin

    # ------------------------------------------------------------------------

    def split(self, inputaudio, phontier, toktier, diralign):
        """
        Write tracks from a Transcription.
        If the given phontier is not already time-aligned in intervals,
        an automatic track-segmenter will be applied first and the TimeAligned
        version of the tokenization is returned.

        @param audioname (str - IN) Audio file name.
        @param phontier (Tier - IN) The phonetization.
        @param toktier  (Tier - IN) The tokenization, or None.
        @param diralign  (str - IN) Output directory to store files.

        @return Transcription

        """
        # Map phonemes from SAMPA to the expected ones.
        self._mapping.set_keep_miss(True)
        self._mapping.set_reverse(True)

        # Map phonetizations (even the alternatives)
        for ann in phontier:
            for text in ann.GetLabel().GetLabels():
                text.SetValue( self._mapping.map( text.GetValue() ) )

        sgmt = TrackSplitter()
        sgmt.set_tracksnames( self._tracknames )
        sgmt.set_trackalign( self.aligntrack )
        units = sgmt.split(inputaudio, phontier, toktier, diralign)
        self._listio.write(diralign, units)

        return sgmt

# ------------------------------------------------------------------
# ----------------------------------------------------------------------

class ListIO():

    DEFAULT_FILENAME="tracks_index.list"

    # ------------------------------------------------------------------

    def __init__(self):
        pass

    # ------------------------------------------------------------------

    def read(self, dirname):
        """
        Read a list file (start-time end-time).

        @param filename is the list file name.
        @raise IOError

        """
        filename = os.path.join( dirname, ListIO.DEFAULT_FILENAME )
        with codecs.open(filename, 'r', encoding) as fp:
            lines = fp.readlines()

        _units = []
        # Each line corresponds to a track,
        # with a couple 'start end' of float values.
        for line in lines:
            line = to_strip(line)
            _tab = line.split()
            if len(_tab) >= 2:
                _units.append( (float(_tab[0]),float(_tab[1])) )

        return _units

    # ------------------------------------------------------------------

    def write(self, dirname, units):
        """
        """
        filename = os.path.join( dirname, ListIO.DEFAULT_FILENAME )
        with codecs.open(filename ,'w', encoding) as fp:
            for start,end in units:
                fp.write( "%.6f %.6f " %(start,end))
                fp.write( "\n" )

    # ------------------------------------------------------------------
