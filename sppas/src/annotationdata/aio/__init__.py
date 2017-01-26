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
@contact:      brigitte.bigi@gmail.com
@license:      GPL, v3
@copyright:    Copyright (C) 2011-2016  Brigitte Bigi
@summary:      Readers and writers of annotated data.

"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

from os.path import splitext

from .trsfactory import TrsFactory
from .heuristic import HeuristicFactory


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
    return splitext(filename)[1][1:]

# ----------------------------------------------------------------------------
# Functions for reading and writing annotated files.
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
    try:
        transcription = TrsFactory.NewTrs(ext)
    except KeyError:
        transcription = HeuristicFactory.NewTrs(filename)

    try:
        transcription.read(unicode(filename))
    except IOError:
        raise
    except UnicodeError as e:
        raise UnicodeError('Encoding error: the file %r contains non-UTF-8 characters: %s' % (filename,e))

    # Each reader has its own solution to assign min and max, anyway
    # take care, if one missed to assign the values!
    if transcription.GetMinTime() is None:
        transcription.SetMinTime(transcription.GetBegin())
    if transcription.GetMaxTime() is None:
        transcription.SetMaxTime(transcription.GetEnd())

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
    output = TrsFactory.NewTrs(ext)

    output.Set(transcription)
    output.SetMinTime(transcription.GetMinTime())
    output.SetMaxTime(transcription.GetMaxTime())

    output.write(unicode(filename))
