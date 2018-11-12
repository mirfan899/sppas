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
# annotationdata.aio package
# ----------------------------------------------------------------------------

"""
@author:       Brigitte Bigi, Jibril Saffi
@organization: Laboratoire Parole et Langage, Aix-en-Provence, France
@contact:      develop@sppas.org
@license:      GPL, v3
@copyright:    Copyright (C) 2011-2018  Brigitte Bigi
@summary:      Readers and writers of annotated data.

"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os.path

from sppas.src.anndata.aio.readwrite import sppasRW
from ..transcription import Transcription

from .praat import PitchTier, IntensityTier
from .signaix import HzPitch

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

ext_sppas =       ['.xra', '.[Xx][Rr][Aa]']
ext_praat =       ['.TextGrid', '.PitchTier', '.[Tt][eE][xX][tT][Gg][Rr][Ii][dD]','.[Pp][Ii][tT][cC][hH][Tt][Ii][Ee][rR]']
ext_transcriber = ['.trs','.[tT][rR][sS]']
ext_elan =        ['.eaf', '[eE][aA][fF]']
ext_ascii =       ['.txt','.csv', '.[cC][sS][vV]', '.[tT][xX][Tt]', '.info']
ext_phonedit =    ['.mrk', '.[mM][rR][kK]']
ext_signaix =     ['.hz', '.[Hh][zZ]']
ext_sclite =      ['.stm', '.ctm', '.[sScC][tT][mM]']
ext_htk =         ['.lab', '.mlf']
ext_subtitles =   ['.sub', '.srt', '.[sS][uU][bB]', '.[sS][rR][tT]']
ext_anvil =       ['.anvil', '.[aA][aN][vV][iI][lL]']
ext_annotationpro = ['.antx', '.[aA][aN][tT][xX]']
ext_xtrans        = ['.tdf', '.[tT][dD][fF]']
ext_audacity =    ['.aup']

extensions     = ['.xra', '.textgrid', '.pitchtier', '.hz', '.eaf', '.trs', '.csv', '.mrk', '.txt', '.mrk', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', 'anvil', '.antx', '.tdf' ]
extensionsul   = ext_sppas + ext_praat + ext_transcriber + ext_elan + ext_ascii + ext_phonedit + ext_signaix + ext_sclite + ext_htk + ext_subtitles + ext_anvil + ext_annotationpro + ext_xtrans + ext_audacity
extensions_in  = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.txt', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', '.antx', '.anvil', '.aup', '.trs','.tdf', '.hz', '.PitchTier' ]
extensions_out = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.txt', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', '.antx' ]
extensions_out_multitiers = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.antx', '.mlf' ]

# ----------------------------------------------------------------------------


def get_extension(filename):
    return os.path.splitext(filename)[1][1:]

# ----------------------------------------------------------------------------
# Functions for reading and writing annotated files.
# ----------------------------------------------------------------------------


TRANSCRIPTION_TYPES = {
    "intensitytier": IntensityTier,
    "pitchtier": PitchTier,
    "hz": HzPitch
}


def NewTrs(trs_type):
    """
    Return a new Transcription() according to the format.

    @param trs_type (str) a file extension.
    @return Transcription()

    """
    try:
        return TRANSCRIPTION_TYPES[trs_type.lower()]()
    except KeyError:
        raise KeyError("Unrecognized Transcription type: %s" % trs_type)

# ----------------------------------------------------------------------------


def read(filename):
    """
    Read a transcription file.

    @param filename (string) the file name (including path)
    @raise IOError, UnicodeError, Exception
    @return Transcription

    >>> # Read an annotated file:
    >>> transcription = annotationdata.aio.read('filename')

    >>> # Get a tier of a transcription from its index:
    >>> tier = transcription[0]

    >>> # Get all annotations between 2 time values:
    >>> annotations = tier.Find(0, 200, overlaps=True)

    >>> # Get the first occurrence of a pattern in a tier:
    >>> first_index = tier.Search(['foo', 'bar'],
            function='exact', pos=0, forward=True, reverse=False)

    About encoding of file names:

    Most of the operating systems in common use today support filenames that
    contain arbitrary Unicode characters. Usually this is implemented by
    converting the Unicode string into some encoding that varies depending on
    the system. For example, Mac OS X uses UTF-8 while Windows uses a
    configurable encoding; on Windows, Python uses the name “mbcs” to refer
    to whatever the currently configured encoding is. On Unix systems, there
    will only be a filesystem encoding if you’ve set the LANG or LC_CTYPE
    environment variables; if you haven’t, the default encoding is ASCII.

    When opening a file for reading or writing, you can usually just provide
    the Unicode string as the filename, and it will be automatically converted
    to the right encoding for you!

    """
    ext = get_extension(filename).lower()

    # Use anndata reader
    parser = sppasRW(filename)
    trs = parser.read()

    # Convert anndata.sppasTranscription() into annotationdata.Transcription()
    transcription = Transcription()
    transcription.SetFromAnnData(trs)

    return transcription

# ----------------------------------------------------------------------------


def write(filename, transcription):
    """
    Write a transcription file.

    @param filename: (string) the file name (including path)
    @param transcription: (Transcription) the Transcription to write.

    @raise IOError:

    """
    ext = get_extension(filename).lower()
    if ext in ['intensitytier', 'pitchtier', 'hz']:
        output = NewTrs(ext)
        output.Set(transcription)
        output.SetMinTime(transcription.GetMinTime())
        output.SetMaxTime(transcription.GetMaxTime())
        output.write(unicode(filename))
    else:
        # Convert annotationdata.Transcription() into anndata.sppasTranscription()
        trs = transcription.ExportToAnnData()

        # Use anndata writer
        parser = sppasRW(filename)
        parser.write(trs)
