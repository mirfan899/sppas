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
__authors__   = """Brigitte Bigi (contact@sppas.org)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import codecs
import re
import logging

from ..transcription import Transcription
from ..pitch import Pitch
from ..label.label import Label
from ..ptime.point import TimePoint
from ..ptime.interval import TimeInterval
from ..annotation import Annotation
from ..tier import Tier

from .utils import merge_overlapping_annotations
from .utils import fill_gaps

# ----------------------------------------------------------------------------

PRAAT_RADIUS = 0.0005


def PraatTimePoint(time):
    return TimePoint(time, PRAAT_RADIUS)

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


class PitchTier(Pitch):
    """
    @authors: Jibril Saffi, Brigitte Bigi
    @contact: contact@sppas.org
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
                        Annotation(PraatTimePoint(number), Label(value, 'float')))
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
    @contact: contact@sppas.org
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
    # proceedReader
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
                        Annotation(PraatTimePoint(number), Label(value, 'float')))
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
            tier.Append(Annotation(PraatTimePoint(number), Label(v, 'float')))
            number = number + delta

        self._tier = tier

    # ------------------------------------------------------------------------
