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
# File: __init__.py of the package annotationdata
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

"""
annotationdata is a free and open source Python library to access and
search data from annotated data. It can convert file formats like Elan’s EAF,
Praat's TextGrid and others into a Transcription() object and convert into
any of these formats. Those objects allow unified access to linguistic data
from a wide range sources.

Details can be found in the following publication:

    Brigitte Bigi, Tatsuya Watanabe, Laurent Prévot (2014).
    Representing Multimodal Linguistics Annotated data,
    Proceedings of the 9th edition of the Language Resources and Evaluation
    Conference, 26-31 May 2014, Reykjavik, Iceland.

Linguistics annotation, especially when dealing with multiple domains,
makes use of different tools within a given project.
Many tools and frameworks are available for handling rich media data.
The heterogeneity of such annotations has been recognised as a key problem
limiting the inter-operability and re-usability of NLP tools and linguistic
data collections.

In annotation tools, annotated data are mainly represented in the form of
"tiers" or "tracks" of annotations.
The genericity and flexibility of "tiers" is appropriate to represent any
multimodal annotated data because it simply maps the annotations on the
timeline.
In most tools, tiers are series of intervals defined by:

    * a time point to represent the beginning of the interval;
    * a time point to represent the end of the interval;
    * a label to represent the annotation itself.

In Praat, tiers can be represented by a time point and a label (such
tiers are named PointTiers and IntervalTiers).
Of course, depending on the annotation tool, the internal data representation
and the file formats are different.
For example, in Elan, unlabelled intervals are not represented nor saved.
On the contrary, in Praat, tiers are made of a succession of consecutive
intervals (labelled or un-labelled).

The annotationdata API used for data representation is based on the
common set of information all tool are currently sharing.
This allows to manipulate all data in the same way, regardless of the file
type.

This API supports to merge data and annotation from a wide range of
heterogeneous data sources for further analysis.

To get the list of extensions currently supported for reading and writing:

    >>> ext = annotationdata.io.extensions

"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

from os.path import splitext

from trsfactory import TrsFactory
from heuristic import HeuristicFactory
from annotationdata.annotation import Annotation
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.label.label import Label

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------


encoding="utf-8"


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
ext_annotationpro = ['antx', '.[aA][aN][tT][xX]']

extensions     = ['.xra', '.textgrid', '.pitchtier', '.eaf', '.trs', '.csv', '.mrk', '.txt', '.mrk', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', 'anvil', '.antx' ]
extensionsul   = ext_sppas + ext_praat + ext_transcriber + ext_elan + ext_ascii + ext_phonedit + ext_signaix + ext_sclite + ext_htk + ext_subtitles + ext_anvil + ext_annotationpro
extensions_in  = ['.xra', '.TextGrid', '.hz', '.PitchTier', '.eaf', '.trs', '.csv', '.mrk', '.txt', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', '.anvil', '.antx']
extensions_out = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', '.antx' ]
extensions_out_multitiers = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.antx', '.mlf' ]


# ----------------------------------------------------------------------------
# Functions for reading and writing annotated files.
# ----------------------------------------------------------------------------

def getExtension(filename):
    return splitext(filename)[1][1:]

def read(filename):
    """
    Read a transcription file.

    @param filename (string) the file name (including path)

    @raise IOError, UnicodeError, Exception

    @return Transcription

    >>> transcription = annotationdata.io.read('filename')
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
    ext = getExtension(filename).lower()
    try:
        transcription = TrsFactory.NewTrs(ext)
    except KeyError:
        transcription = HeuristicFactory.NewTrs(filename)

    try:
        transcription.read( unicode(filename) )
    except IOError:
        raise
    except UnicodeError as e:
        raise UnicodeError('Encoding error: the file %r contains non-UTF-8 characters: %s' % (filename,e))

    # Each reader has its own solution to assign min and max, anyway
    # take care, if one missed to assign the values!
    if transcription.GetMinTime() is None:
        transcription.SetMinTime( transcription.GetBegin() )
    if transcription.GetMaxTime() is None:
        transcription.SetMaxTime( transcription.GetEnd() )

    return transcription


def write(filename, transcription):
    """
    Write a transcription file.

    @param filename: (string) the file name (including path)
    @param transcription: (Transcription) the Transcription to write.

    @raise IOError:

    """

    ext = getExtension(filename).lower()
    output = TrsFactory.NewTrs(ext)

    output.Set(transcription)
    output.SetMinTime( transcription.GetMinTime() )
    output.SetMaxTime( transcription.GetMaxTime() )

    output.write( unicode(filename) )
