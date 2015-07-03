#!/usr/bin/env python2
# encoding: utf-8
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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


import codecs
import datetime
from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
import annotationdata.ptime.point
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation


SUBTITLE_RADIUS = 0.0005


def TimePoint(time):
    return annotationdata.ptime.point.TimePoint(time, SUBTITLE_RADIUS)


class SubRip(Transcription):
    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """
        Creates a new Transcription instance.

        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)

    # End __init__
    # -----------------------------------------------------------------

    @staticmethod
    def __parseTime(timestring):
        timestring = timestring.strip()
        dt = (datetime.datetime.strptime(timestring, '%H:%M:%S,%f') -
              datetime.datetime.strptime('', ''))
        return dt.total_seconds()

    # End __parseTime
    # -----------------------------------------------------------------

    @staticmethod
    def __formatTime(secondCount):
        dt = datetime.datetime.utcfromtimestamp(secondCount)
        return dt.strftime('%H:%M:%S,%f')[:-3]

    # End __formatTime
    # -----------------------------------------------------------------

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
                    time = TimeInterval(TimePoint(float(start)),
                                        TimePoint(float(stop)))

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
    # -----------------------------------------------------------------

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
    # -----------------------------------------------------------------


class SubViewer(Transcription):

    __metadataTypes = [
        'author',
        'source',
        'filepath',
        'comment']

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """
        Creates a new Transcription instance.

        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)

    # End __init__
    # -----------------------------------------------------------------

    @staticmethod
    def __parseTime(timestring):
        timestring = timestring.strip()
        dt = (datetime.datetime.strptime(timestring, '%H:%M:%S.%f') -
              datetime.datetime.strptime('', ''))
        return dt.total_seconds()

    # End __parseTime
    # -----------------------------------------------------------------

    @staticmethod
    def __formatTime(secondCount):
        dt = datetime.datetime.utcfromtimestamp(secondCount)
        return dt.strftime('%H:%M:%S.%f')[:-4]

    # End __formatTime
    # -----------------------------------------------------------------

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
                    time = TimeInterval(TimePoint(delay + float(start)),
                                        TimePoint(delay + float(stop)))
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
    # -----------------------------------------------------------------

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
    # -----------------------------------------------------------------
