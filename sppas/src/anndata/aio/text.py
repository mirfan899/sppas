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
    ~~~~~~~~~~~~~~~~~~~~~~~

    Text readers and writers: raw text, column-based text, csv.

"""
import codecs
import re

from sppas import encoding

from ..anndataexc import AioMultiTiersError
from ..anndataexc import AioLineFormatError
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

from .basetrs import sppasBaseIO

# ----------------------------------------------------------------------------

COLUMN_SEPARATORS = [' ', ',', ';', ':', '\t']

# ----------------------------------------------------------------------------


class sppasBaseText(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS base text reader and writer.

    """
    def __init__(self, name=None):
        """ Initialize a new sppasBaseText instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
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
        self._accept_gaps = True
        self._accept_overlaps = True

    # ----------------------------------------------------------------------------

    @staticmethod
    def make_point(data):
        """ Convert data into the appropriate digit type, or not.

        :param data: (any type)
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

    @staticmethod
    def format_quotation_marks(text):
        """ Remove initial and final quotation mark.

        :param text: (str)
        :returns: the text without initial and final quotation mark.

        """
        if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
            text = text[1:-1]

        if len(text) >= 2 and text.startswith("'") and text.endswith("'"):
            text = text[1:-1]

        return text

    # -----------------------------------------------------------------

    @staticmethod
    def split_lines(lines, separator=" "):
        """ Split the lines with the given separator.

        :param lines: (list) List of lines
        :param separator: (char) a character used to separate columns of the lines
        :returns: List of columns (list) or None

        """
        columns = list()
        nb_col = -1
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            split_line = line.split(separator)
            if nb_col == -1:
                nb_col = len(split_line)
            if nb_col != len(split_line):
                return None
            columns.append(split_line)

        return columns

    # -----------------------------------------------------------------

    @staticmethod
    def fix_location(content_begin, content_end):
        """ Fix the location from the content of the data.

        :param content_begin: (str) The content of a column representing
        the begin of a localization.
        :param content_end: (str) The content of a column representing
        the end of a localization.
        :returns: sppasLocation or None

        """
        begin = sppasBaseText.format_quotation_marks(content_begin)
        end = sppasBaseText.format_quotation_marks(content_end)

        has_begin = len(begin.strip()) > 0
        has_end = len(end.strip()) > 0

        if has_begin and has_end:
            b = sppasBaseText.make_point(begin)
            e = sppasBaseText.make_point(end)
            if b == e:
                localization = sppasPoint(b)
            else:
                localization = sppasInterval(sppasPoint(b), sppasPoint(e))

        elif has_begin:
            localization = sppasPoint(sppasBaseText.make_point(begin))

        elif has_end:
            localization = sppasPoint(sppasBaseText.make_point(end))

        else:
            return None

        return sppasLocation(localization)

# ----------------------------------------------------------------------------


class sppasRawText(sppasBaseText):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS raw text reader and writer.

    RawText does not support multiple tiers.
    RawText accepts no tiers.
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
        try:
            with codecs.open(filename, 'r', encoding) as fp:
                fp.readline()
                pass
        except Exception:
            return False

        return True

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new RawText instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseText.__init__(self, name)

        self._accept_multi_tiers = False

    # -----------------------------------------------------------------

    def read(self, filename):
        """ Read a raw file and fill the Transcription.
        The file can be a simple raw text (without location information).
        It can also be a column-based (table-style) file, so that each
        column represents the annotation of a tier (1st and 2nd tiers
        are indicating the location).

        :param filename: (str)

        """
        with codecs.open(filename, 'r', encoding) as fp:
            lines = fp.readlines()

        # Column-delimited??
        nb_col = 0
        columns = None
        sep = None
        for separator in COLUMN_SEPARATORS:
            columns = sppasBaseText.split_lines(lines, separator)
            if columns is not None and len(columns) > 0 and len(columns[0]) > nb_col:
                sep = separator
        if sep is not None:
            columns = sppasBaseText.split_lines(lines, separator)

        if columns is None:
            self.__format_raw_lines(lines)

        if len(columns) == 0:
            return
        if len(columns[0]) == 1:
            self.__format_raw_lines(lines)
        else:
            self.__format_columns(columns)

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
                        location = sppasLocation(sppasPoint(n))
                        label = sppasLabel(sppasTag(phrase))
                        tier.create_annotation(location, label)
                        n += 1

            elif len(line) > 0:
                location = sppasLocation(sppasPoint(n))
                label = sppasLabel(sppasTag(line))
                tier.create_annotation(location, label)
                n += 1

    # -----------------------------------------------------------------

    def __format_columns(self, columns):
        """ Format columns of a column-based text.

        :param columns: (list) List of columns (list).

        - 1st column: the begin localization (required)
        - 2nd column: the end localization (required)
        - 3rd column: the label of the 1st tier (optional)
        - 4th column: the label of the 2nd tier (optional)
        - ...

        """
        nb_col = len(columns[0])
        # Create the tiers (one tier per column) but
        # the name of the tiers are unknown...
        self.create_tier('RawTranscription')
        for i in range(3, nb_col):
            self.create_tier('Tier-{:d}'.format(i-2))

        # Create the annotations of the tiers
        for instance in columns:
            location = sppasBaseText.fix_location(instance[0], instance[1])
            for i in range(2, nb_col):
                label = sppasLabel(sppasTag(instance[i]))
                self[i-2].create_annotation(location, label)

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
                    if annotation.get_label() is None:
                        t = ""
                    else:
                        t = annotation.get_label().get_best().get_content()
                    if point:
                        mp = annotation.get_lowest_localization().get_midpoint()
                        fp.write("{}\t\t{}\n".format(mp, t))
                    else:
                        b = annotation.get_lowest_localization().get_midpoint()
                        e = annotation.get_highest_localization().get_midpoint()
                        fp.write("{}\t{}\t{}\n".format(b, e, t))

            fp.close()

# ----------------------------------------------------------------------------


class sppasCSV(sppasBaseText):
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
        sppasBaseText.__init__(self, name)

        self._accept_multi_tiers = True

    # -----------------------------------------------------------------

    def read(self, filename, separator=',', signed=True):
        """ Read a CSV file.

        :param filename: (str)
        :param separator: (char)
        :param signed: (bool) Indicate if the encoding is UTF-8 signed.
        If False, the default encoding is used.

        """
        enc = encoding
        if signed is True:
            enc = 'utf-8-sig'

        with codecs.open(filename, "r", enc) as fp:
            lines = fp.readlines()
            fp.close()

        if len(lines) > 0:
            self.format_columns_lines(lines, separator)

    # -----------------------------------------------------------------

    def format_columns_lines(self, lines, separator):
        """ Append lines content into self.

        It doesn't suppose that the file is sorted by tiers

        :param lines: (list)
        :param separator: (char)

        """
        for i, line in enumerate(lines):

            row = line.split(separator)
            if len(row) < 4:
                raise AioLineFormatError(i+1, line)

            # Fix the name of the tier (column 1)
            name = sppasBaseText.format_quotation_marks(row[0])
            tier = self.find(name)
            if tier is None:
                tier = self.create_tier(name)

            # Fix the location (columns 2 and 3)
            location = sppasBaseText.fix_location(row[1], row[2])
            if location is None:
                raise AioLineFormatError(i + 1, line)

            # Fix the label (the other columns)
            text = sppasBaseText.format_quotation_marks(" ".join(row[3:]))

            # Add the new annotation
            tier.create_annotation(location, sppasLabel(sppasTag(text)))

    # -----------------------------------------------------------------

    def write(self, filename, signed=True):
        """ Write a CSV file.

        :param filename: (str)
        :param signed: (bool) Indicate if the encoding is UTF-8 signed.
        If False, the default encoding is used.

        """
        enc = encoding
        if signed is True:
            enc = 'utf-8-sig'

        with codecs.open(filename, 'w', enc, buffering=8096) as fp:

            for tier in self._tiers:

                name = tier.get_name()
                point = tier.is_point()

                for annotation in tier:
                    t = annotation.get_label().get_best().get_content()
                    if point:
                        mp = annotation.get_lowest_localization().get_midpoint()
                        fp.write('"{}",{},,"{}"\n'.format(name, mp, t))
                        print('"{}",{},,"{}"\n'.format(name, mp, t))
                    else:
                        b = annotation.get_lowest_localization().get_midpoint()
                        e = annotation.get_highest_localization().get_midpoint()
                        fp.write('"{}",{},{},"{}"\n'.format(name, b, e, t))
                        print('"{}",{},{},"{}"\n'.format(name, b, e, t))

            fp.close()
