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

    src.anndata.aio.text.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Text reader and writer.

"""
import codecs
import re

from sppas.src.sp_glob import encoding

from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

from .basetrs import sppasBaseIO

# ----------------------------------------------------------------------------

def make_point(data):
    if data.isdigit():
        return int(data)
    try:
        d = float(data)
    except Exception:
        d = data
    return d

# ----------------------------------------------------------------------------


class sppasRawText(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS raw text reader and writer.

    """
    @staticmethod
    def detect(filename):
        with codecs.open(filename, 'r', encoding):
            pass
        return True

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new RawText instance.

        :param name: (str) This transcription name.

        """
        sppasBaseIO.__init__(self, name)

    # -----------------------------------------------------------------

    def read(self, filename):
        """ Read a raw file and fill the Transcription.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', encoding) as fp:
            lines = fp.readlines()

        # Tab-delimited??
        tdf = True
        for line in lines:
            tab = line.split('\t')
            if len(tab) != 3:
                tdf = False

        if tdf is False:
            self.__format_raw_lines(lines)

        else:
            trs = sppasCSV()
            rows = []
            for line in lines:
                row = "Transcription\t" + line
                rows.append(row)
            trs.format_columns_lines(rows, "\t")
            self.set(trs)

    # -----------------------------------------------------------------

    def __format_raw_lines(self, lines):
        """ Format lines of a raw text.
        Each CR/LF is a unit separator, NOT added into the transcription.
        Each # is a unit separator, added as a silence mark into the transcription.

        :param lines: (list) List of lines.

        """
        tier = self.create_tier('RawTranscription')

        n = 1
        for line in lines:
            line = line.strip()
            # we ought not to have to remove the BOM

            if line.find("#") > -1:
                phrases = map(lambda s: s.strip(), re.split('(#)', line))
                # The separator '#' is included in the tab
                for phrase in phrases:
                    if len(phrase) > 0:
                        tier.append(sppasRawText.__read_annotation(phrase, n))
                        n += 1

            elif len(line) > 0:
                tier.append(sppasRawText.__read_annotation(line, n))
                n += 1

    # -----------------------------------------------------------------

    @staticmethod
    def __read_annotation(phrase, number):
        """ Return an annotation.

        :param phrase: (str)
        :param number: (int) rank of the phrase

        """
        return sppasAnnotation(sppasLocation(sppasPoint(number)), sppasLabel(sppasTag(phrase)))

    # -----------------------------------------------------------------

    def write(self, filename):
        """ Write a RawText file.

        :param filename: (str)

        """
        pass

    # -----------------------------------------------------------------

# ----------------------------------------------------------------------------


class sppasCSV(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS CSV reader and writer.

    """
    @staticmethod
    def detect(filename):
        csv_line = re.compile(
            '^(("([^"]|"")*"|[^",]*),)+("([^"]|"")*"|[^",]*)$')

        with codecs.open(filename, 'r', encoding) as fp:
            detected = True
            for i in range(1, 10):
                if not csv_line.match(fp.next()):
                    detected = False

        return detected

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new CSV instance.

        :param name: (str) This transcription name.

        """
        sppasBaseIO.__init__(self, name)

    # -----------------------------------------------------------------

    def read(self, filename, separator=','):
        """ Read a CSV file and fill the Transcription.

        :param filename: (str)
        :param separator: (char)

        """
        with codecs.open(filename, "r", 'utf-8-sig') as fp:
            lines = fp.readlines()

        self.format_columns_lines(lines, separator)

    # -----------------------------------------------------------------

    def format_columns_lines(self, lines, separator):
        """ Append lines content into self.

        :param lines: (list)
        :param separator: (char)

        """
        for i, line in enumerate(lines):
            # DOIT PRENDRE LES GUILLEMETS EN CONSIDERATION...

            row = line.split(separator)
            if len(row) != 4:
                raise IOError('Invalid line number %d: %r.' % (i+1, line))

            name, begin, end, text = row

            # The following does not suppose that the file is sorted by tiers
            tier = self.find(name)
            if tier is None:
                tier = self.create_tier(name)

            has_begin = len(begin.strip()) > 0
            has_end = len(end.strip()) > 0

            if has_begin and has_end:
                b = make_point(begin)
                e = make_point(end)
                if b == e:
                    localization = sppasPoint(b)
                else:
                    localization = sppasInterval(sppasPoint(b), sppasPoint(e))

            elif has_begin:
                localization = sppasPoint(make_point(begin))

            elif has_end:
                localization = sppasPoint(make_point(end))

            else:
                raise IOError('Invalid line number %d: %r.' % (i, line))

            tier.add(sppasAnnotation(sppasLocation(localization), sppasLabel(sppasTag(text))))


