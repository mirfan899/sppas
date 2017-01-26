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
# File: annotationpro.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import codecs
import datetime

from ..transcription import Transcription
from ..label.label import Label
from ..ptime.point import TimePoint
from ..ptime.interval import TimeInterval
from ..annotation import Annotation

# ----------------------------------------------------------------------------

SUBTITLE_RADIUS = 0.005

# ----------------------------------------------------------------------------

def SubTimePoint(time):
    return TimePoint(time, SUBTITLE_RADIUS)

# ----------------------------------------------------------------------------


class SubRip(Transcription):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents one of the subtitles file formats.
    """

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new Transcription instance.
        """
        Transcription.__init__(self, name, mintime, maxtime)

    # ------------------------------------------------------------------------

    @staticmethod
    def __parseTime(timestring):
        timestring = timestring.strip()
        dt = (datetime.datetime.strptime(timestring, '%H:%M:%S,%f') -
              datetime.datetime.strptime('', ''))
        return dt.total_seconds()

    # ------------------------------------------------------------------------

    @staticmethod
    def __formatTime(secondCount):
        dt = datetime.datetime.utcfromtimestamp(secondCount)
        return dt.strftime('%H:%M:%S,%f')[:-3]

    # ------------------------------------------------------------------------

    def read(self, filename):
        with codecs.open(filename, 'r', 'utf-8') as fp:

            tier = self.NewTier('Subs')

            line = ''

            while(not line.strip().isdigit()):
                line = fp.next()

            try:
                while True:
                    line = fp.next()  # skip number

                    start, stop = map(SubRip.__parseTime, line.split('-->'))
                    time = TimeInterval(SubTimePoint(float(start)),
                                        SubTimePoint(float(stop)))

                    line = fp.next()
                    label = line.strip()
                    line = fp.next()
                    while(line.strip() != ''):
                        label += '\n' + line.strip()
                        line = fp.next()
                    line = fp.next()

                    tier.Add(Annotation(time, Label(label)))
            except StopIteration:
                tier.Add(Annotation(time, Label(label)))

        self.SetMinTime(0.)
        self.SetMaxTime(self.GetEnd())

    # End read
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------

    def write(self, filename):
        with codecs.open(filename, 'w', 'utf-8', buffering=8096) as fp:
            if self.GetSize() != 1:
                raise Exception(
                    "Cannot write a multi tier annotation to a srt.")

            number = 1
            for annotation in self[0]:
                if(annotation.GetLabel().GetValue().strip() == ''):
                    continue

                fp.write('%d\n' % number)
                number += 1

                if annotation.GetLocation().IsInterval():
                    begin = SubRip.__formatTime(
                        annotation.GetLocation().GetBeginMidpoint())
                    end = SubRip.__formatTime(
                        annotation.GetLocation().GetEndMidpoint())
                else:
                    # SubRip does not support point based annotation
                    # so we'll make a 1 second subtitle
                    begin = SubRip.__formatTime(
                        annotation.GetLocation().GetPointMidpoint())
                    end = SubRip.__formatTime(
                        annotation.GetLocation().GetPointMidpoint() + 1)
                fp.write('%s --> %s\n' % (begin, end))

                fp.write('%s\n\n' % annotation.GetLabel().GetValue())

    # End write
    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class SubViewer(Transcription):
    """
    @authors: Jibril Saffi, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents one of the subtitles file formats.
    """

    __metadataTypes = [
        'author',
        'source',
        'filepath',
        'comment']

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new Transcription instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)

    # ------------------------------------------------------------------------

    @staticmethod
    def __parseTime(timestring):
        timestring = timestring.strip()
        dt = (datetime.datetime.strptime(timestring, '%H:%M:%S.%f') -
              datetime.datetime.strptime('', ''))
        return dt.total_seconds()

    # ------------------------------------------------------------------------

    @staticmethod
    def __formatTime(secondCount):
        dt = datetime.datetime.utcfromtimestamp(secondCount)
        return dt.strftime('%H:%M:%S.%f')[:-4]

    # ------------------------------------------------------------------------

    def read(self, filename):
        with codecs.open(filename, 'r', 'utf-8') as fp:

            title = 'Subs'
            line = '['
            delay = 0.

            while(not line.strip() == '[END INFORMATION]'):
                if(line.startswith('[TITLE]')):
                    title = line[line.find(']')+1:].strip()
                elif(line.startswith('[DELAY]')):
                    delay = float(line[line.find(']')+1:].strip())

                else:
                    for m in SubViewer.__metadataTypes:
                        if(line.startswith('[%s]' % m.upper())):
                            self.metadata[m] = line[line.find(']')+1:].strip()
                line = fp.next()

            while(line.startswith('[')):
                line = fp.next()

            tier = self.NewTier(title)

            try:
                while True:
                    start, stop = map(SubViewer.__parseTime, line.split(','))
                    time = TimeInterval(SubTimePoint(delay + float(start)),
                                        SubTimePoint(delay + float(stop)))
                    line = fp.next()

                    label = ''
                    while(line.strip() != ''):
                        label += line.replace('[br]', '\n')
                        line = fp.next()

                    line = fp.next()

                    tier.Add(Annotation(time, Label(label)))

            except StopIteration:
                tier.Add(Annotation(time, Label(label)))

        self.SetMinTime(0.)
        self.SetMaxTime(self.GetEnd())

    # End read
    # ------------------------------------------------------------------------

    def write(self, filename):
        with codecs.open(filename, 'w', 'utf-8', buffering=8096) as fp:
            if self.GetSize() != 1:
                raise Exception(
                    "Cannot write a multi tier annotation to a srt.")

            fp.write((
                '[INFORMATION]\n'
                '[TITLE] %s\n') %
                    self[0].GetName())

            for m in SubViewer.__metadataTypes:
                if(m in self.metadata):
                    fp.write((
                        '[%s] %s\n') % (
                            m.upper(),
                            self.metadata[m]))

            fp.write(
                '[END INFORMATION]\n'
                '[SUBTITLE]\n')

            for annotation in self[0]:
                if(annotation.GetLabel().GetValue().strip() == ''):
                    continue

                if annotation.GetLocation().IsInterval():
                    begin = SubViewer.__formatTime(
                        annotation.GetLocation().GetBeginMidpoint())
                    end = SubViewer.__formatTime(
                        annotation.GetLocation().GetEndMidpoint())
                else:
                    # SubViewer does not support point based annotation
                    # so we'll make a 1 second subtitle
                    begin = SubViewer.__formatTime(
                        annotation.GetLocation().GetPointMidpoint())
                    end = SubViewer.__formatTime(
                        annotation.GetLocation().GetPointMidpoint() + 1)
                fp.write('%s,%s\n' % (begin, end))

                fp.write('%s\n\n' % annotation.GetLabel().GetValue())

    # End write
    # -----------------------------------------------------------------------
