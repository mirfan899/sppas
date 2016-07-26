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
# File: praat.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import codecs
import re

from utils import merge_overlapping_annotations
from utils import fill_gaps
from annotationdata.transcription import Transcription
from annotationdata.pitch import Pitch
from annotationdata.label.label import Label
import annotationdata.ptime.point
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation
from annotationdata.tier import Tier

# ----------------------------------------------------------------------------

PRAAT_RADIUS = 0.0005

# ----------------------------------------------------------------------------

def TimePoint(time):
    return annotationdata.ptime.point.TimePoint(time, PRAAT_RADIUS)

# ----------------------------------------------------------------------------

def parse_int(line):
    """
    Parse an integral value from a line of a Praat formatted file.
    """
    try:
        sline = line.strip()
        val = sline[sline.rfind(' ')+1:]
        return int(val)
    except:
        raise Exception(
            "could not parse int value on line: %s" %
            repr(line))

# ----------------------------------------------------------------------------

def parse_float(line):
    """
    Parse a floating point value from a line of a Praat formatted file.
    """
    try:
        sline = line.strip()
        val = sline[sline.rfind(' ')+1:]
        return round(float(val), 10)
    except:
        raise Exception(
            "could not parse float value on line: %s" %
            repr(line))

# ----------------------------------------------------------------------------

def parse_string(iterator):
    """
    Parse a string from one or more lines of a Praat formatted file.
    """
    firstLine = iterator.next()
    if firstLine.rstrip().endswith('"'):
        firstLine = firstLine.rstrip()
        return firstLine[firstLine.find('"')+1:-1]
    else:
        firstLine = firstLine[firstLine.find('"')+1:]

    currentLine = iterator.next()

    while not currentLine.rstrip().endswith('"'):
        firstLine += currentLine
        currentLine = iterator.next()

    currentLine = currentLine.rstrip()[:-1]
    firstLine += currentLine

    return firstLine

# ----------------------------------------------------------------------------

def detect_praat_file(filename, ftype):
    with codecs.open(filename, 'r', 'utf-8') as it:
        fileType = parse_string(it)
        objectClass = parse_string(it)
        return (fileType == "ooTextFile" and objectClass == ftype)

# ----------------------------------------------------------------------------

class TextGrid(Transcription):
    """
    @authors: Jibril Saffi, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents a TextGrid Transcription.

    TextGrid is the native file format of the GPL tool Praat:
    Doing phonetic with computers.

    See: http://www.fon.hum.uva.nl/praat/

    Important remark:
    As TextGrid is a (very) poor file format, some information will be LOST:
        - the radius value of each time points
        - some annotations if they overlap with other ones (a solution is
        used to keep a maximum of information, but some annotations may
        be lost).
        - CtrlVocab, Media, Metadata, Hierarchy, etc...

    """
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Create a new TextGrid Transcription instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)

    # ------------------------------------------------------------------------

    @staticmethod
    def detect(filename):
        return detect_praat_file(filename, "TextGrid")

    # ------------------------------------------------------------------------
    # Reader
    # ------------------------------------------------------------------------

    def read(self, filename):
        """
        Read a TextGrid file.

        @param filename: is the input file name, ending by ".TextGrid"
        @raise IOError:
        @raise Exception:
        """
        with codecs.open(filename, 'r', 'utf-8') as it:
            try:
                for i in range(6):
                    it.next()

                # if the size isn't named, we must be in a short TextGrid file
                tier_count_line = it.next().strip()
                is_long = not tier_count_line.isdigit()
                tier_count = parse_int(tier_count_line)

                if is_long:
                    it.next()

                for i in range(tier_count):
                    self.__read_tier(it, is_long)

            except StopIteration:
                pass
                # FIXME: we should probably warn the user
                #       that his file has invalid size values
            finally:
                self.SetMinTime(0.)
                self.SetMaxTime(self.GetEnd())

    # End read
    # ------------------------------------------------------------------------

    def __read_tier(self, it, is_long):
        """
        Reads a tier from the contents of a TextGrid file.
        Beware, this function will advance the iterator passed.

        @param it: An iterator to the contents of the file
             pointing where the tier starts.
        @param is_long: A boolean which is false if the TextGrid is in short form.
        """
        if is_long:
            it.next()

        tier_type = parse_string(it)
        tier_name = parse_string(it)

        tier = self.NewTier()
        tier.SetName(tier_name)

        it.next()
        it.next()

        item_count = parse_int(it.next())

        if tier_type == "IntervalTier":
            read_annotation = TextGrid.__read_interval_annotation
        elif tier_type == "TextTier":
            read_annotation = TextGrid.__read_point_annotation
        else:
            raise Exception("Tier type "+tier_type+" cannot be parsed.")

        for i in range(item_count):
            if is_long:
                it.next()
            read_annotation(it, tier)

    # ------------------------------------------------------------------------

    @staticmethod
    def __read_point_annotation(it, tier):
        """
        Read an annotation from an IntervalTier in the contents of a TextGrid file.
        Beware, this function will advance the iterator passed.

        @param it: an iterator to the contents of the file
             pointing where the annotation starts
        @param tier: the tier where we will add the read annotation
        """
        loc_s = parse_float(it.next())
        label = parse_string(it)

        tier.Add(Annotation(TimePoint(loc_s), Label(label)))

    # ------------------------------------------------------------------------

    @staticmethod
    def __read_interval_annotation(it, tier):
        """
        Read an annotation from an IntervalTier in the contents of a TextGrid file
        Beware, this function will advance the iterator passed.

        @param it an iterator to the contents of the file
             pointing where the annotation starts
        @param tier  the tier where we will add the read annotation
        """
        beg = TimePoint(parse_float(it.next()))
        end = TimePoint(parse_float(it.next()))
        label = parse_string(it)
        label = label.replace('""', '"') # praat double quotes.
        interval = TimeInterval(beg, end)
        tier.Add(Annotation(interval, Label(label)))

    # ------------------------------------------------------------------------
    # Writer
    # ------------------------------------------------------------------------

    def write(self, filename):
        """
        Write a TextGrid file.
        """
        if self.IsEmpty():
            raise Exception("Can not write an empty content in a file.")

        if self.GetMinTime() is None:
            self.SetMinTime(0.)
        if self.GetMaxTime() is None:
            self.SetMaxTime(self.GetEnd())

        with codecs.open(filename, 'w', 'utf-8', buffering=8096) as fp:
            fp.write((
                'File type = "ooTextFile"\n'
                'Object class = "TextGrid"\n'
                '\n'
                'xmin = %s\n'
                'xmax = %s\n'
                'tiers? <exists>\n'
                'size = %d\n'
                'item []:\n') % (
                    self.GetMinTime(),
                    self.GetMaxTime(),
                    self.GetSize()))

            for i, tier in enumerate(self, 1):
                fp.write(self.__format_tier(tier, i))

    # End write
    # ------------------------------------------------------------------------

    def __format_tier(self, tier, number):
        """
        Format a tier from a transcription to the TextGrid format.
        @param number: The position of the tier in the list of all tiers.
        """
        # Fill empty tiers because TextGrid does not support empty tiers.
        if tier.IsEmpty():
            tier.Append(Annotation(
                TimeInterval(TimePoint(self.GetMinTime()),
                             TimePoint(self.GetMaxTime()))))

        if tier.IsTimeInterval():
            tier = fill_gaps(tier, self.GetMinTime(), self.GetMaxTime())
            tier = merge_overlapping_annotations(tier)

        result = (
            '    item [%d]:\n'
            '        class = "%s"\n'
            '        name = "%s"\n'
            '        xmin = %f\n'
            '        xmax = %f\n'
            '        intervals: size = %s\n') % (
                number,
                'IntervalTier' if tier.IsInterval() else 'TextTier',
                tier.GetName(),
                tier.GetBeginValue(),
                tier.GetEndValue(),
                tier.GetSize())

        if tier.IsTimeInterval():
            format_annotation = TextGrid.__format_interval_annotation
        elif tier.IsTimePoint():
            format_annotation = TextGrid.__format_point_annotation
        else:
            raise IOError('Unsupported tier type. Praat textgrid files only support Time Intervals or Time Points.')

        for j, an in enumerate(tier, 1):
            result += format_annotation(an, j)
        return result

    # ------------------------------------------------------------------------

    @staticmethod
    def __format_interval_annotation(annotation, number):
        """
        Formats an annotation consisting of intervals to the TextGrid format.
        @param number: The position of the annotation in the list of all annotations.
        """
        label = annotation.GetLabel().GetValue()
        if '"' in label:
            label = re.sub('([^"])["]([^"])', '\\1""\\2', label)
            label = re.sub('([^"])["]([^"])', '\\1""\\2', label) # miss occurrences if 2 " are separated by only 1 character
            label = re.sub('([^"])["]$', '\\1""', label) # miss occurrences if " are at the end of the label!
            label = re.sub('^["]([^"])', '""\\1', label) # miss occurrences if " are at the beginning of the label!

        return (
            '        intervals [%d]:\n'
            '            xmin = %s\n'
            '            xmax = %s\n'
            '            text = "%s"\n') % (
                number,
                annotation.GetLocation().GetBeginMidpoint(),
                annotation.GetLocation().GetEndMidpoint(),
                label)

    # ------------------------------------------------------------------------

    @staticmethod
    def __format_point_annotation(annotation, number):
        """
        Formats an annotation consisting of points to the TextGrid format.
        @param number: The position of the annotation in the list of all annotations.
        """
        return (
            '        points [%d]:\n'
            '            time = %s\n'
            '            mark = "%s"\n') % (
                number,
                annotation.GetLocation().GetPointMidpoint(),
                annotation.GetLabel().GetValue())

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class PitchTier(Pitch):
    """
    @authors: Jibril Saffi, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents a PitchTier file, a native format of Praat software.

    PitchTier (like TextGrid) is one of the native file formats of the
    GPL tool Praat: Doing phonetic with computers.

    See: http://www.fon.hum.uva.nl/praat/

    """

    def __init__(self):
        Pitch.__init__(self)

    # -----------------------------------------------------------------------

    @staticmethod
    def detect(filename):
        return detect_praat_file(filename, "PitchTier")

    # ------------------------------------------------------------------------

    def read(self, filename):
        """
        Read a PitchTier file (from Praat).
        """
        self.__delta = 0.
        with codecs.open(filename, 'r', 'utf-8') as it:
            try:
                for i in range(5):
                    it.next()

                # if the size isn't named, we must be in a short PitchTier file
                point_count_line = it.next().strip()
                is_long = not point_count_line.isdigit()
                point_count = parse_int(point_count_line)

                self._tier = self.NewTier("Pitch")
                self._tier.SetDataType("int")

                for i in range(point_count):
                    if is_long:
                        it.next()

                    number = parse_float(it.next())
                    value = parse_float(it.next())

                    self._tier.Append(
                        Annotation(TimePoint(number), Label(value, 'float')))
            except StopIteration:
                pass
                # FIXME: we should probably warn the user
                #       that his file has invalid size values
            finally:
                self.SetMinTime(0.)
                self.SetMaxTime(self.GetEnd())

    # End read
    # ------------------------------------------------------------------------

    def write(self, filename):
        """
        Write a PitchTier file.
        @param filename: is the output file name
        """
        with codecs.open(filename, 'w', 'utf-8', buffering=8096) as fp:
            # Header
            fp.write((
                'File type = "ooTextFile"\n'
                'Object class = "PitchTier"\n'
                '\n'
                'xmin = %f\n'
                'xmax = %f\n'
                'points: size = %d\n') % (
                   self._tier.GetBeginValue(),
                   self._tier.GetEndValue(),
                   self._tier.GetSize()))

            for i, annotation in enumerate(self._tier, 1):
                fp.write(self.__format_annotation(annotation, i))

    # End write
    # ------------------------------------------------------------------------

    @staticmethod
    def __format_annotation(annotation, number):
        """
        Formats a Pitch annotation to the PitchTier format.
        @param number: The position of the annotation in the list of all annotations.
        """
        return (
            '    points [%d]:\n'
            '        number = %s\n'
            '        value = %s\n') % (
               number,
               annotation.GetLocation().GetPoint().GetMidpoint(),
               annotation.GetLabel().GetValue())

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class IntensityTier(Transcription):
    """
    @authors: Jibril Saffi, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents an Intensity Tier Transcription.

    IntensityTier (like TextGrid) is one of the native file formats of the
    GPL tool Praat: Doing phonetic with computers.

    See: http://www.fon.hum.uva.nl/praat/

    """

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new Intensity Transcription instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)
        self._tier = Tier()

    # ------------------------------------------------------------------------

    @staticmethod
    def detect(filename):
        return detect_praat_file(filename, "IntensityTier")

    # -----------------------------------------------------------------

    def Set(self, trs):
        """
        Set a transcription.
        @param trs: (Transcription)
        @raise TypeError:
        """
        if isinstance(trs, Transcription) is False:
            raise TypeError("Transcription argument required, not %s" % trs)

        if trs.IsEmpty():
            self._tiers = []
            self._tier = Tier()
        else:
            tiers = [tier.Copy() for tier in trs]
            self._tiers = tiers
            self._tier = self._tiers[0]

    # -----------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Reader
    # ------------------------------------------------------------------------

    def read(self, filename):
        """
        Read an IntensityTier file (from Praat).
        """
        self.__delta = 0.
        with codecs.open(filename, 'r', 'utf-8') as it:
            try:
                for i in range(5):
                    it.next()

                # if the size isn't named, we must be in a short PitchTier file
                point_count_line = it.next().strip()
                is_long = not point_count_line.isdigit()
                point_count = parse_int(point_count_line)

                self._tier = self.NewTier("Pitch")
                self._tier.SetDataType("int")

                for i in range(point_count):
                    if is_long:
                        it.next()

                    number = parse_float(it.next())
                    value = parse_float(it.next())

                    self._tier.Append(
                        Annotation(TimePoint(number), Label(value, 'float')))
            except StopIteration:
                pass
                # FIXME: we should probably warn the user
                #       that his file has invalid size values
            finally:
                self.SetMinTime(0)
                self.SetMaxTime(self.GetEnd())

    # End read
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Writer
    # ------------------------------------------------------------------------

    def write(self, filename):
        """
        Write an IntensityTier  file.
        @param filename: is the output file name
        """
        if self.IsEmpty() and self._tier.IsEmpty():
            raise IOError('pitch.py. Writing error: empty pitch tier.\n')

        with codecs.open(filename, 'w', 'utf-8', buffering=8096) as fp:
            # Header
            fp.write((
                'File type = "ooTextFile"\n'
                'Object class = "IntensityTier"\n'
                '\n'
                'xmin = %f\n'
                'xmax = %f\n'
                'points: size = %d\n') % (
                   self._tier.GetBeginValue(),
                   self._tier.GetEndValue(),
                   self._tier.GetSize()))

            for i, annotation in enumerate(self._tier, 1):
                fp.write(self.__format_annotation(annotation, i))

    # End write
    # ------------------------------------------------------------------------

    @staticmethod
    def __format_annotation(annotation, number):
        """
        Formats an Intensity annotation to the IntensityTier format.
        @param number: The position of the annotation in the list of all annotations.
        """
        return (
            '    points [%d]:\n'
            '        number = %s\n'
            '        value = %s\n') % (
               number,
               annotation.GetLocation().GetPoint().GetMidpoint(),
               annotation.GetLabel().GetValue())

    # ------------------------------------------------------------------------

    def set_intensity(self, values, delta):
        """
        Create an intensity tier from intensity values.
        @param values: is an array with intensity values
        @param delta: is the delta time between 2 values
        @raise ValueError:
        """
        if len(values) == 0:
            raise ValueError("Intensity.set_intensity: Empty array values")

        tier = self.NewTier()
        number = 0
        for v in range(values):
            tier.Append(Annotation(TimePoint(number), Label(v, 'float')))
            number = number + delta

        self._tier = tier

    # ------------------------------------------------------------------------
