#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
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
from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
import annotationdata.ptime.point
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation


SCLITE_RADIUS = 0.0005


def TimePoint(time):
    return annotationdata.ptime.point.TimePoint(time, SCLITE_RADIUS)


class TimeMarkedConversation(Transcription):

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        Transcription.__init__(self, name, coeff, mintime, maxtime)

    # End __init__
    # -----------------------------------------------------------------

    def read(self, filename):
        with codecs.open(filename, 'r', 'utf-8') as fp:

            channels = {}

            for line in fp:
                if(line.strip().startswith(';;') or
                   line.strip() == ''):
                    continue

                line = line.strip().split()
                wavname, channel, begin, duration, word = line[:5]
                if len(line) > 5:
                    score = line[-1]
                else:
                    score = None

                if channel in channels:
                    tier = channels[channel]
                else:
                    tier = self.NewTier(channel)
                    channels[channel] = tier

                interval = TimeInterval(
                    TimePoint(float(begin)),
                    TimePoint(float(begin) + float(duration)))

                label = Label(word)
                if(score is not None):
                    label.Get()[0].SetScore(float(score))

                tier.Add(Annotation(interval, label))

        self.SetName(wavname)
        self.SetMinTime(0.)
        self.SetMaxTime(self.GetEnd())

    # End read
    # -----------------------------------------------------------------

    def write(self, filename):
        with codecs.open(filename, 'w', 'utf-8', buffering=8096) as fp:
            size = self.GetSize()
            if size == 1:
                self.__write_tier(self[0], fp, 'A')
            elif size == 2:
                self.__write_tier(self[0], fp, 'A')
                self.__write_tier(self[1], fp, 'B')
            else:
                raise Exception(
                    "Cannot write more than two annotations to a ctm")

    # End write
    # -----------------------------------------------------------------

    def __write_tier(self, tier, file, channel):
            for annotation in tier:
                wavname = self.GetName()

                if annotation.GetLocation().IsInterval():
                    begin = annotation.GetLocation().GetBeginMidpoint()
                    duration = (
                        annotation.GetLocation().GetEndMidpoint() - begin)
                else:
                    raise Exception(
                        "Can't export point annotations to ctm file")

                word = annotation.GetLabel().GetValue()

                score = annotation.GetLabel().GetLabel().GetScore()

                file.write('%s %s %s %s %s %s\n' % (
                    wavname,
                    channel,
                    begin,
                    duration,
                    word,
                    score))

    # End __write_tier
    # -----------------------------------------------------------------


class SegmentTimeMark(Transcription):
    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        Transcription.__init__(self, name, coeff, mintime, maxtime)

    # End __init__
    # -----------------------------------------------------------------

    def read(self, filename):
        with codecs.open(filename, 'r', 'utf-8') as fp:

            channels = {}

            for line in fp:
                if(line.strip().startswith(';;') or
                   line.strip() == ''):
                    continue

                line = line.strip().split(None, 5)
                wavname, channel, speaker, begin, end, word = line

                if channel in channels:
                    tier = channels[channel]
                else:
                    tier = self.NewTier(channel)
                    channels[channel] = tier
                    tier.metadata['speaker'] = speaker

                interval = TimeInterval(
                    TimePoint(float(begin)),
                    TimePoint(float(end)))

                label = Label(word)

                tier.Add(Annotation(interval, label))

        self.SetName(wavname)
        self.SetMinTime(0.)
        self.SetMaxTime(self.GetEnd())

    # End read
    # -----------------------------------------------------------------

    def write(self, filename):
        with codecs.open(filename, 'w', 'utf-8', buffering=8096) as fp:
            for tier in self:
                self.__write_tier(tier, fp)

    # End write
    # -----------------------------------------------------------------

    def __write_tier(self, tier, file):
            for annotation in tier:
                wavname = self.GetName()

                if annotation.GetLocation().IsInterval():
                    begin = annotation.GetLocation().GetBeginMidpoint()
                    end = annotation.GetLocation().GetEndMidpoint()
                else:
                    raise Exception(
                        "Can't export point annotations to stm file")

                word = annotation.GetLabel().GetValue()

                if('speaker' not in tier.metadata):
                    speaker = 'none'
                else:
                    speaker = tier.metadata['speaker']

                channel = tier.GetName()

                file.write('%s %s %s %s %s %s\n' % (
                    wavname,
                    channel,
                    speaker,
                    begin,
                    end,
                    word))

    # End __write_tier
    # -----------------------------------------------------------------
