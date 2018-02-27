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

    src.anndata.aio.sclite.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Sclite readers and writers: ctm, stm file formats.
    The program sclite is a tool for scoring and evaluating the output of
    speech recognition systems.

    Sclite is part of the NIST SCTK Scoring Tookit:
    https://www.nist.gov/itl/iad/mig/tools

    File formats description:
    http://www1.icsi.berkeley.edu/Speech/docs/sctk-1.2/infmts.htm#ctm_fmt_name_0

"""
import codecs
import re

from sppas import encoding

from sppas.src.utils.makeunicode import sppasUnicode
from ..anndataexc import AioLocationTypeError
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioLineFormatError
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag
from ..media import sppasMedia

from .basetrs import sppasBaseIO

# ---------------------------------------------------------------------------


class sppasBaseSclite(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS base sclite reader and writer.

    * * * * * * Current version does not support alternations. * * * * * *

    """
    def __init__(self, name=None):
        """ Initialize a new sppasBaseSclite instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = True
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = True
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = True

    # -----------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        """ In Sclite, the localization is a time value, so a float. """

        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")

        return sppasPoint(midpoint, radius=0.005)

    # -----------------------------------------------------------------

    @staticmethod
    def is_comment(line):
        """ Check if the line is a comment.

        :param line: (str)
        :return: boolean

        """
        sp = sppasUnicode(line)
        line = sp.to_strip()
        return line.startswith(";;")

# ----------------------------------------------------------------------------


class sppasCTM(sppasBaseSclite):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS ctm reader and writer.

    This is the reader/writer the time marked conversation input files to be
    used for scoring the output of speech recognizers via the NIST sclite()
    program.

    CTM :== <F> <C> <BT> <DUR> word [ <CONF> ]

    where:
        <F> -> The waveform filename.
            NOTE: no pathnames or extensions are expected.
        <C> -> The waveform channel. Either "A" or "B".
            The text of the waveform channel is not restricted by sclite.
            The text can be any text string without whitespace so long as the
            matching string is found in both the reference and hypothesis
            input files.
        <BT> -> The begin time (seconds) of the word, measured from the
            start time of the file.
        <DUR> -> The duration (seconds) of the word.
        <CONF> -> Optional confidence score.

    The file must be sorted by the first three columns: the first and the
    second in ASCII order, and the third by a numeric order.

    Lines beginning with ';;' are considered comments and are ignored.
    Blank lines are also ignored.

    * * *  NOT IMPLEMENTED * * *
    Alternations are also accepted in CTM like for example:
        ;;
        7654 A * * <ALT_BEGIN>
        7654 A 12.00 0.34 UM
        7654 A * * <ALT>
        7654 A 12.00 0.34 UH
        7654 A * * <ALT_END>
        ;;
        5555 A * * <ALT_BEGIN>
        5555 A 222.77 0.32 BYEBYE
        5555 A * * <ALT>
        5555 A 222.78 0.12 BYE
        5555 A 222.93 0.16 BYE
        5555 A * * <ALT_END>
        ;;
        5555 A * * <ALT_BEGIN>
        5555 A 186.32 0.01 D-
        5555 A * * <ALT>
        5555 A * * <ALT_END>

    """
    @staticmethod
    def detect(filename):
        try:
            with codecs.open(filename, 'r', encoding) as fp:
                lines = fp.readlines()
                for line in lines:
                    line = line.strip()
                    if sppasBaseSclite.is_comment(line) is True:
                        continue
                    if len(line) == 0:
                        continue
                    tab = line.split()
                    if len(tab) < 4 or len(tab) > 6:  # expected is 4 to 6
                        return False
        except Exception:
            return False

        return True

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new CTM instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseSclite.__init__(self, name)

    # -----------------------------------------------------------------

    @staticmethod
    def check_line(line, line_number=0):
        """ Check whether a line is correct or not.

        :param line: (str)
        :param line_number: (int)
        :return: (bool)

        """
        # Ignore comments
        if sppasBaseSclite.is_comment(line):
            return False

        # Ignore blank lines
        if len(line) == 0:
            return False

        # a column-delimited line
        tab_line = line.split()
        if len(tab_line) < 4 or len(tab_line) > 6:
            raise AioLineFormatError(line_number, line)

        # an alternation
        if tab_line[2] != "*":
            float(tab_line[2])  # begin
            float(tab_line[3])  # duration

        return True

    # -----------------------------------------------------------------

    def get_tier(self, line):
        """ Return the tier related to the given line.
        Find the tier or create it

        :param line: (str)
        :return: (bool)

        """
        tab_line = line.split()
        tier_name = tab_line[0] + "-" + tab_line[1]
        tier = self.find(tier_name)
        if tier is None:
            # Create the media linked to the tier
            media = self._create_media(tab_line[0].strip())

            # Create the tier and set metadata
            tier = self.create_tier(tier_name, media=media)
            tier.set_meta("media_channel", tab_line[1])

        return tier

    # -----------------------------------------------------------------

    @staticmethod
    def get_score(line):
        """ Return the score of the label of a given line.

        :param line: (str)
        :return: (float) or None if no score is given

        """
        tab_line = line.split()
        score = None
        if len(tab_line) > 5:
            try:
                score = float(tab_line[-1])
            except ValueError:
                pass

        return score

    # -----------------------------------------------------------------

    def read(self, filename):
        """ Read a ctm file and fill the Transcription.
        It creates a tier for each channel observed in the file.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', encoding) as fp:
            lines = fp.readlines()
            fp.close()

        self._serialize_lines(lines)

    # -----------------------------------------------------------------

    def _serialize_lines(self, lines):
        """ Fill the transcription from the lines of the CTM file. """

        in_alt = False
        alternates = list()

        # Extract rows, create tiers and metadata.
        for i, line in enumerate(lines):

            # format and check the line
            line = sppasUnicode(line).to_strip()
            if sppasCTM.check_line(line, i+1) is False:
                continue

            # check for the tier (find it or create it)
            tier = self.get_tier(line)

            tab_line = line.strip().split()
            wavname, channel, begin, duration, word = tab_line[:5]

            # the score of the word
            score = sppasCTM.get_score(line)

            # check for an alternative annotation
            if begin == "*":
                if word == "<ALT_BEGIN>":
                    alternates = list()
                    in_alt = True
                    sppasCTM._add_alt_annotations(tier, alternates)
                elif word == "<ALT>":
                    # we add the alternations into the tier
                    for ann in alternates:
                        tier.add(ann)
                    alternates = list()
                else:
                    alternates = list()
                    in_alt = False
                    # we SHOULD add the alternations into the tier
                    # sppasCTM._add_alt_annotations(tier, alternates)
                continue

            ann = sppasCTM._create_annotation(begin, duration, word, score)
            if in_alt is False:
                tier.add(ann)
            else:
                alternates.append(ann)

    # -----------------------------------------------------------------

    @staticmethod
    def _add_alt_annotations(tier, ann):
        """ Add the annotations into the tier. """
        try:
            tier.add(ann)
        except Exception:
            pass

    # -----------------------------------------------------------------

    def _create_media(self, media_name):
        """ Return the media of the given name (create it if necessary). """

        media = None
        idt = media_name
        for m in self._media:
            if m.get_filename() == idt:
                media = m
        if media is None:
            media = sppasMedia(idt)

        return media

    # -----------------------------------------------------------------

    @staticmethod
    def _create_annotation(begin, duration, word, score):
        """ Return the annotation corresponding to data of a line. """

        word = sppasUnicode(word).clear_whitespace()
        label = sppasLabel(sppasTag(word), score)
        begin = float(begin)
        end = begin + float(duration)
        location = sppasLocation(sppasInterval(sppasBaseSclite.make_point(begin),
                                               sppasBaseSclite.make_point(end)))
        return sppasAnnotation(location, label)

    # ------------------------------------------------------------------------

    def write(self, filename):
        """ Write a transcription into a file.

        :param filename: (str)

        """
        raise NotImplementedError
        with codecs.open(filename, 'w', encoding, buffering=8096) as fp:

            for tier in self:
                waveform = "a"
                channel = "A"
                for ann in tier:
                    if ann.get_best_tag().is_empty() is False:
                        line = "{:s} {:s} ".format(waveform, channel)
                        line += sppasCTM._serialize_annotation(ann)
                        line += "\n"
                        fp.write(line)

            fp.close()

    # -----------------------------------------------------------------

    @staticmethod
    def _serialize_annotation(ann):
        """ Convert an annotation into a line for CTM files.

        :param ann: (sppasAnnotation)
        :returns: (str)

        """
        # no label defined, or empty label
        if ann.get_best_tag().is_empty():
            return ""
        if ann.get_location().is_point():
            raise AioLocationTypeError('Sclite CTM', 'points')

        tag_content = ann.get_best_tag().get_content()
        begin = ann.get_lowest_localization().get_midpoint()
        duration = ann.get_highest_localization().get_midpoint() - begin
        return "{:f} {:f} {:s}\n".format(begin, duration, tag_content)

# ----------------------------------------------------------------------------


class sppasSTM(sppasBaseSclite):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS stm reader and writer.

    This is the reader/writer for the segment time marked files to be used
    for scoring the output of speech recognizers via the NIST sclite() program.

    STM :== <F> <C> <S> <BT> <ET> [ <LABEL> ] transcript . . .

    where:
        <F> -> The waveform filename.
            NOTE: no pathnames or extensions are expected.
        <C> -> The waveform channel. Either "A" or "B".
            The text of the waveform channel is not restricted by sclite.
            The text can be any text string without witespace so long as the
            matching string is found in both the reference and hypothesis
            input files.
        <S> -> The speaker id, no restrictions apply to this name.
        <BT> -> The begin time (seconds) of the word, measured from the
            start time of the file.
        <ET> -> The end time (seconds) of the segment.
        <LABEL> -> A comma separated list of subset identifiers enclosed
            in angle brackets
        transcript -> The transcript can take on two forms:
            1) a whitespace separated list of words, or
            2) the string "IGNORE_TIME_SEGMENT_IN_SCORING".
            The list of words can contain an transcript alternation using
            the following BNF format:
                ALTERNATE :== "{" <text> ALT+ "}"
                ALT :== "/" <text>
                TEXT :== 1 thru n words | "@" | ALTERNATE

    The file must be sorted by the first and second columns in ASCII order,
    and the fourth in numeric order.

    Lines beginning with ';;' are considered comments and are ignored.
    Blank lines are also ignored.

    """
    @staticmethod
    def detect(filename):
        try:
            with codecs.open(filename, 'r', encoding) as fp:
                lines = fp.readlines()
                for line in lines:
                    if sppasBaseSclite.is_comment(line) is True:
                        continue
                    tab = line.split()
                    if len(tab) < 6:
                        return False
            return True
        except Exception:
            pass

        return False

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new STM instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseSclite.__init__(self, name)

