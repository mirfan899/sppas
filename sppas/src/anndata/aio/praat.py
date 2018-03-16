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

    src.anndata.aio.praat.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Praat - Doing phonetic with computers, is a GPL tool developed by:

        | Paul Boersma and David Weenink
        | Phonetic Sciences, University of Amsterdam
        | Spuistraat 210
        | 1012VT Amsterdam
        | The Netherlands

    See: http://www.fon.hum.uva.nl/praat/

"""
import codecs
import re

from sppas import encoding
from sppas.src.utils.makeunicode import u

from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioLineFormatError
from ..anndataexc import AioNoTiersError
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

from .aioutils import fill_gaps, merge_overlapping_annotations
from .basetrs import sppasBaseIO

# ----------------------------------------------------------------------------


class sppasBasePraat(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Base class for readers and writers of Praat files.
    
    """
    @staticmethod
    def detect(filename):
        """ Parse a configuration file.

        :param filename: (str) Configuration file name.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', encoding) as fp:
                line = fp.readline()
                file_type = sppasBasePraat._parse_string(line)
                return file_type == "ooTextFile"
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

    # -----------------------------------------------------------------

    @staticmethod
    def make_point(midpoint, radius=0.0005):
        """ In Praat, the localization is a time value, so a float.

        :param midpoint: (float, str, int) a time value (in seconds).
        :param radius: (float): vagueness (in seconds)
        :returns: (sppasPoint)

        """
        try:
            midpoint = float(midpoint)
            radius = float(radius)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")

        return sppasPoint(midpoint, radius)

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new Praat instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = False
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
        self._accept_gaps = False
        self._accept_overlaps = False

    # -----------------------------------------------------------------

    @staticmethod
    def _parse_int(line, line_number=0):
        """ Parse an integer value from a line of a Praat formatted file.

        >>> sppasBasePraat._parse_int("intervals: size = 23")
        >>> 23

        :param line: (str) The line to parse and get value
        :param line_number: (int) Number of the given line
        :returns: (int)

        """
        try:
            line = line.strip()
            val = line[line.rfind(' ') + 1:]
            return int(val)
        except:
            raise AioLineFormatError(line_number, line)

    # ----------------------------------------------------------------------------

    @staticmethod
    def _parse_float(line, line_number=0):
        """ Parse a floating point value from a line of a Praat formatted file.

        >>> sppasBasePraat._parse_float("xmin = 11.9485310906")
        >>> 11.9485310906

        :param line: (str) The line to parse and get value
        :param line_number: (int) Number of the given line
        :returns: (float)

        """
        try:
            line = line.strip()
            val = line[line.rfind(' ') + 1:]
            return float(val)
        except:
            raise AioLineFormatError(line_number, line)

    # ----------------------------------------------------------------------------

    @staticmethod
    def _parse_string(text):
        """ Parse a text from one or more lines of a Praat formatted file.

        :param text: (str or list of str)
        :returns: (str)

        """
        if isinstance(text, list):
            first_line = text[0]
            if first_line.rstrip().endswith('"'):
                first_line = first_line.rstrip()
                return first_line[first_line.find('"') + 1:-1]
            else:
                first_line = first_line[first_line.find('"') + 1:]

            current_line = " ".join(text[1:])
            current_line = current_line.rstrip()[:-1]
            first_line += current_line
            return first_line

        else:
            text = text.strip()
            return text[text.find('"') + 1:-1]

    # ----------------------------------------------------------------------------

    @staticmethod
    def _parse_string_label(iterator):
        """ Parse a string from one or more lines of a Praat formatted file.

        :param iterator: file pointer
        :returns: (str)

        """
        first_line = iterator.next()
        if first_line.rstrip().endswith('"'):
            first_line = first_line.rstrip()
            return first_line[first_line.find('"') + 1:-1]
        else:
            first_line = first_line[first_line.find('"') + 1:]

        current_line = iterator.next()

        while not current_line.rstrip().endswith('"'):
            first_line += current_line
            current_line = iterator.next()

        current_line = current_line.rstrip()[:-1]
        first_line += current_line

        return first_line

    # -----------------------------------------------------------------

    @staticmethod
    def _serialize_header(file_class, xmin, xmax):
        """ Serialize the header of a Praat file.

        :param file_class: (str) Objects class in this file
        :param xmin: (float) Start time
        :param xmax: (float) End time
        :returns: (str)

        """
        header = 'File type = "ooTextFile"\n'
        header += 'Object class = "{:s}"\n'.format(file_class)
        header += '\n'
        header += 'xmin = {:.18}\n'.format(xmin)
        header += 'xmax = {:.18}\n'.format(xmax)
        return header

    # -----------------------------------------------------------------

    @staticmethod
    def _serialize_label_text(label):
        """ Convert a label into a string. """

        if label is None:
            text = ""
        elif label.get_best() is None:
            text = ""
        elif label.get_best().is_empty():
            text = ""
        else:
            text = label.get_best().get_content()

        if '"' in text:
            text = re.sub('([^"])["]([^"])', '\\1""\\2', text)
            text = re.sub('([^"])["]([^"])', '\\1""\\2',
                          text)  # miss occurrences if 2 " are separated by only 1 character
            text = re.sub('([^"])["]$', '\\1""', text)  # miss occurrences if " is at the end of the label!
            text = re.sub('^["]([^"])', '""\\1', text)  # miss occurrences if " is at the beginning of the label
            text = re.sub('^""$', '""""', text)
            text = re.sub('^"$', '""', text)

        return '\t\ttext = "{:s}"\n'.format(text)

    # -----------------------------------------------------------------

    @staticmethod
    def _serialize_label_value(label):
        """ Convert a label with a numerical value into a string. """

        if label is None:
            return None
        if label.get_best() is None:
            return None
        if label.get_best().is_empty():
            return None
        text = label.get_best().get_content()
        return "\t\tvalue = {:s}".format(text)

# ----------------------------------------------------------------------------


class sppasTextGrid(sppasBasePraat):
    """
    :author:       Brigitte Bigi, Jibril Saffi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS TextGrid reader and writer.

    TextGrid supports multiple tiers in a file.
    TextGrid does not support empty files (file with no tiers).
    TextGrid does not support alternatives labels nor locations. Only the ones
    with the best score are saved.
    TextGrid does not support controlled vocabularies.
    TextGrid does not support hierarchy.
    TextGrid does not support metadata.
    TextGrid does not support media assignment.
    TextGrid supports points and intervals. It does not support disjoint intervals.
    TextGrid does not support alternative tags (here called "text").
    TextGrid does not support radius.

    Both "short TextGrid" and "long TextGrid" file formats are supported.

    """
    @staticmethod
    def detect(filename):
        """ Check whether a file is of TextGrid format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', encoding) as it:
                file_type = sppasBasePraat._parse_string(it)
                object_class = sppasBasePraat._parse_string(it)
                return file_type == "ooTextFile" and object_class == "TextGrid"
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasTextGrid instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBasePraat.__init__(self, name)

        self._accept_point = True
        self._accept_interval = True

    # -----------------------------------------------------------------

    def read(self, filename):
        """ Read a TextGrid file.

        :param filename: is the input file name, ending by ".TextGrid"

        """
        with codecs.open(filename, 'r', encoding, buffering=8096) as it:
            try:
                for i in range(6):
                    it.next()

                # if the size isn't named, we must be in a short TextGrid file
                tier_count_line = it.next().strip()
                is_long = not tier_count_line.isdigit()
                tier_count = sppasBasePraat._parse_int(tier_count_line, line_number=7)

                if is_long:
                    it.next()

                for i in range(tier_count):
                    self.__read_tier(it, is_long)

            except StopIteration:
                pass
                # FIXME: we should probably warn the user
                #       that the file has invalid size values

            it.close()

    # -----------------------------------------------------------------

    def __read_tier(self, it, is_long):
        """ Reads a tier from the contents of a TextGrid file.
        Beware, this function will advance the iterator passed.

        :param it: An iterator to the contents of the file
             pointing where the tier starts.
        :param is_long: A boolean which is false if the TextGrid is in short form.

        """
        if is_long:
            it.next()

        tier_type = sppasBasePraat._parse_string(it)
        tier_name = sppasBasePraat._parse_string(it)

        tier = self.create_tier(tier_name)

        it.next()
        it.next()

        item_count = sppasBasePraat._parse_int(it.next(), 11)

        if tier_type == "IntervalTier":
            read_annotation = sppasTextGrid.__read_interval_annotation
        elif tier_type == "TextTier":
            read_annotation = sppasTextGrid.__read_point_annotation
        else:
            raise Exception("Tier type " + tier_type + " cannot be parsed.")

        for i in range(item_count):
            if is_long:
                it.next()
            read_annotation(it, tier)

    # -----------------------------------------------------------------

    @staticmethod
    def __read_point_annotation(it, tier):
        """ Read an annotation from an IntervalTier in the contents of a TextGrid file.
        Beware, this function will advance the iterator passed.

        :param it: an iterator to the contents of the file
             pointing where the annotation starts
        :param tier: the tier where we will add the read annotation

        """
        midpoint = sppasBasePraat._parse_float(it.next())
        tag_content = sppasBasePraat._parse_string(it)

        tier.create_annotation(sppasLocation(sppasBasePraat.make_point(midpoint)),
                               sppasLabel(sppasTag(tag_content)))

    # ------------------------------------------------------------------------

    @staticmethod
    def __read_interval_annotation(it, tier):
        """ Read an annotation from an IntervalTier in the contents of a TextGrid file
        Beware, this function will advance the iterator passed.

        :param it: an iterator to the contents of the file
             pointing where the annotation starts
        :param tier: the tier where we will add the read annotation

        """
        begin = sppasBasePraat.make_point(sppasBasePraat._parse_float(it.next()))
        end = sppasBasePraat.make_point(sppasBasePraat._parse_float(it.next()))
        interval = sppasInterval(begin, end)
        tag_content = sppasBasePraat._parse_string(it)
        tag_content = tag_content.replace('""', '"')  # praat double quotes.
        tier.create_annotation(sppasLocation(interval),
                               sppasLabel(sppasTag(tag_content)))

    # ------------------------------------------------------------------------
    # Writer
    # ------------------------------------------------------------------------

    def convert_for_textgrid(self):
        """ Create a transcription in which the content is compatible for a TextGrid support.

        No controlled vocabulary, no media, no hierarchy, no metadata and...
        no gap between annotations, no overlapping annotations.

        :returns: sppasTranscription

        """
        if self.is_empty():
            raise AioNoTiersError("TextGrid")

        trs = sppasTextGrid()
        min_point = self.get_min_loc()
        max_point = self.get_max_loc()
        for i, tier in enumerate(self._tiers):
            if tier.is_empty() is False:

                new_tier = tier.copy()
                new_tier.set_ctrl_vocab(None)
                new_tier.set_media(None)
                new_tier.set_parent(None)
                # annotations
                if new_tier.is_interval() is True:
                    new_tier = fill_gaps(new_tier, min_point, max_point)
                    new_tier = merge_overlapping_annotations(new_tier)

                trs.append(new_tier)

        return trs

    # ------------------------------------------------------------------------

    def write(self, filename):
        """ Write a TextGrid file.

        :param filename: (str)

        """
        trs = self.convert_for_textgrid()
        min_time = trs.get_min_loc().get_midpoint()
        max_time = trs.get_max_loc().get_midpoint()

        with codecs.open(filename, 'w', encoding, buffering=8096) as fp:

            # Write the header
            fp.write(sppasTextGrid._serialize_textgrid_header(min_time,
                                                              max_time,
                                                              len(trs)))

            # Write each tier
            for i, tier in enumerate(trs):

                # Write the header of the tier
                fp.write(sppasTextGrid._serialize_tier_header(tier, i+1))

                # Write annotations of the tier
                is_point = tier.is_point()
                for a, annotation in enumerate(tier):
                    if is_point is True:
                        fp.write(sppasTextGrid._serialize_point_annotation(annotation, a+1))
                    else:
                        fp.write(sppasTextGrid._serialize_interval_annotation(annotation, a+1))

            fp.close()

    # ------------------------------------------------------------------------

    @staticmethod
    def _serialize_textgrid_header(xmin, xmax, size):
        """ Create a string with the header of the textgrid. """

        content = sppasBasePraat._serialize_header("TextGrid", xmin, xmax)
        content += 'tiers? <exists>\n'
        content += 'size = {:d}\n'.format(size)
        content += 'item []:\n'
        return content

    # ------------------------------------------------------------------------

    @staticmethod
    def _serialize_tier_header(tier, tier_number):
        """ Create the string with the header for a new tier. """

        content = '\titem [{:d}]:\n'.format(tier_number)
        content += '\t\tclass = "{:s}"'.format('IntervalTier' if tier.is_interval() else 'TextTier')
        content += '\t\tname = "{:s}"\n'.format(tier.get_name())
        content += '\t\txmin = {:.18}\n'.format(tier.get_first_point().get_midpoint())
        content += '\t\txmax = {:.18}\n'.format(tier.get_last_point().get_midpoint())
        content += '\t\tintervals: size = {:d}\n'.format(len(tier))
        return content

    # ------------------------------------------------------------------------

    @staticmethod
    def _serialize_interval_annotation(annotation, number):
        """ Converts an annotation consisting of intervals to the TextGrid format.

        A time value can be written with a maximum of 18 digits, like in Praat.

        :param annotation: (sppasAnnotation)
        :param number: (int) the index of the annotation in the tier + 1.
        :returns: (unicode)

        """
        content = '\t\tintervals [{:d}]:\n'.format(number)
        content += '\t\txmin = {:.18}\n'.format(annotation.get_lowest_localization().get_midpoint())
        content += '\t\txmax = {:.18}\n'.format(annotation.get_highest_localization().get_midpoint())
        content += sppasBasePraat._serialize_label_text(annotation.get_label())
        return u(content)

    # ------------------------------------------------------------------------

    @staticmethod
    def _serialize_point_annotation(annotation, number):
        """ Converts an annotation consisting of points to the TextGrid format.

        :param annotation: (sppasAnnotation)
        :param number: (int) the index of the annotation in the tier + 1.
        :returns: (unicode)

        """
        text = annotation.get_label().get_best().get_content()
        return u(
            '        points [{:d}]:\n'
            '            time = {:.18}\n'
            '            mark = "{:s}"\n').format(
                number,
                annotation.get_lowest_localization().get_midpoint(),
                text)

# ----------------------------------------------------------------------------


class sppasBaseNumericalTier(sppasBasePraat):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS PitchTier, IntensityTier, etc reader and writer.

    Support of Praat file formats with only one tier of numerical values like
    pitch, intensity, etc.

    """
    def __init__(self, name=None):
        """ Initialize a new sppasBaseNumericalTier instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBasePraat.__init__(self, name)

        self._accept_multi_tiers = False
        self._accept_no_tiers = False
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = False
        self._accept_overlaps = False

# ----------------------------------------------------------------------------


class sppasPitchTier(sppasBaseNumericalTier):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS PitchTier reader and writer.

    """
    @staticmethod
    def detect(filename):
        """ Check whether a file is of PitchTier format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', encoding) as it:
                file_type = sppasBasePraat._parse_string(it)
                object_class = sppasBasePraat._parse_string(it)
                return file_type == "ooTextFile" and object_class == "PitchTier"
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasPitchTier instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseNumericalTier.__init__(self, name)

# ----------------------------------------------------------------------------


class sppasIntensityTier(sppasPitchTier):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS IntensityTier reader and writer.

    """
    @staticmethod
    def detect(filename):
        """ Check whether a file is of IntensityTier format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'r', encoding) as it:
                file_type = sppasBasePraat._parse_string(it)
                object_class = sppasBasePraat._parse_string(it)
                return file_type == "ooTextFile" and object_class == "IntensityTier"
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasIntensityTier instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseNumericalTier.__init__(self, name)

    # -----------------------------------------------------------------

