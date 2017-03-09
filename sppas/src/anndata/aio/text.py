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

from ..anndataexc import AioMultiTiersError
from ..anndataexc import AioLineFormatError
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

from .basetrs import sppasBaseIO

# ----------------------------------------------------------------------------


def make_point(data):
    """ Convert data into the appropriate type.

    :param data: (str)
    :returns: data converted into int, float or unchanged.

    """
    if data.isdigit():
        return int(data)
    try:
        d = float(data)
    except Exception:
        d = data
    return d

# ----------------------------------------------------------------------------


def format_quotation_marks(text):
    """ Clean text data...

    :param text: (str)
    :returns: the text without initial and final quotation mark.

    """
    if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
        text = text[1:-1]

    if len(text) >= 2 and text.startswith("'") and text.endswith("'"):
        text = text[1:-1]

    return text

# ----------------------------------------------------------------------------


class sppasRawText(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS raw text reader and writer.

    RawText does not support alternatives labels nor locations. Only the ones
    with the best score are saved.
    RawText can save only one tier.
    RawText does not support controlled vocabularies.
    RawText does not support hierarchy.
    RawText does not support metadata.
    RawText does not support media assignment.
    RawText supports points and intervals. It does not support disjoint intervals.
    RawText does not support alternative tags.
    RawText does not support radius.

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
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = False
        self._accept_no_tiers = True
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = True
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = True

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
        if len(self._tiers) > 1:
            raise AioMultiTiersError(self.__class__.__name__)

        with codecs.open(filename, 'w', encoding, buffering=8096) as fp:

            if self.is_empty() is True:
                return

            tier = self[0]
            point = tier.is_point()
            if tier.is_empty():
                return

            if tier.get_name() == "RawTranscription":
                for annotation in tier:
                    fp.write(annotation.get_label().get_best().get_content() + '\n')
            else:
                for annotation in tier:
                    t = annotation.get_label().get_best().get_content()
                    if point:
                        mp = annotation.get_lowest_localization().get_midpoint()
                        fp.write("{}\t{}\t{}\n".format(mp, t))
                    else:
                        b = annotation.get_lowest_localization().get_midpoint()
                        e = annotation.get_highest_localization().get_midpoint()
                        fp.write("{}\t{}\t{}\n".format(b, e, t))

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
        """ Read a CSV file in UTF-8 signed encoding.

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

            row = line.split(separator)
            if len(row) < 4:
                raise AioLineFormatError(i+1, line)

            name = format_quotation_marks(row[0])
            begin = format_quotation_marks(row[1])
            end = format_quotation_marks(row[2])
            text = format_quotation_marks(row[3:])

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
                raise AioLineFormatError(i+1, line)

            tier.add(sppasAnnotation(sppasLocation(localization), sppasLabel(sppasTag(text))))

    # -----------------------------------------------------------------

    def write(self, filename):
        """ Write a CSV file in UTF-8 signed encoding.

        :param filename: (str)

        """
        with codecs.open(filename, 'w', 'utf-8-sig', buffering=8096) as fp:

            for tier in self._tiers:
                name = tier.get_name()
                point = tier.is_point()

                for annotation in tier:
                    t = annotation.get_label().get_best().get_content()
                    if point:
                        mp = annotation.get_lowest_localization().get_midpoint()
                        fp.write('"{}",{},,{},"{}"\n'.format(name, mp, t))
                    else:
                        b = annotation.get_lowest_localization().get_midpoint()
                        e = annotation.get_highest_localization().get_midpoint()
                        fp.write('"{}",{},{},"{}"\n'.format(name, b, e, t))
