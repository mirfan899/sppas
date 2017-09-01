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
# File: sclite.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import codecs

from ..transcription import Transcription
from ..media import Media
from ..label.label import Label
from ..ptime.point import TimePoint
from ..ptime.interval import TimeInterval
from ..annotation import Annotation

from .utils import point2interval
from .utils import gen_id

# ----------------------------------------------------------------------------

SCLITE_RADIUS = 0.0005


def ScliteTimePoint(time):
    return TimePoint(time, SCLITE_RADIUS)

# ----------------------------------------------------------------------------


class TimeMarkedConversation(Transcription):
    """
    @authors: Jibril Saffi, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents one of the native format of Sclite tool.

    http://www.itl.nist.gov/iad/mig/tools/

    """

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        Transcription.__init__(self, name, mintime, maxtime)

    # ------------------------------------------------------------------------

    def read(self, filename):
        with codecs.open(filename, 'r', 'utf-8') as fp:

            channels = {}

            for line in fp:
                if line.strip().startswith(';;') or line.strip() == '':
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
                    ScliteTimePoint(float(begin)),
                    ScliteTimePoint(float(begin) + float(duration)))

                label = Label(word)
                if score is not None:
                    label.Get()[0].SetScore(float(score))

                tier.Add(Annotation(interval, label))

        m = Media(gen_id(), wavname)
        self.SetMedia( m )
        for tier in self:
            tier.SetMedia( m )
        self.SetName( wavname )
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

    def __write_tier(self, tier, filefp, channel):

        if tier.IsPoint():
            tier = point2interval(tier, SCLITE_RADIUS)

        for annotation in tier:
            wavname  = tier.GetMedia().url if tier.GetMedia() is not None else self.GetName()
            begin    = annotation.GetLocation().GetBeginMidpoint()
            duration = annotation.GetLocation().GetDuration().GetValue()
            word     = annotation.GetLabel().GetValue()
            score    = annotation.GetLabel().GetLabel().GetScore()

            filefp.write('%s %s %s %s %s %s\n' % (
                wavname,
                channel,
                begin,
                duration,
                word,
                score))

    # End __write_tier
    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class SegmentTimeMark(Transcription):
    """
    @authors: Jibril Saffi, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents one of the native format of Sclite tool.

    http://www.itl.nist.gov/iad/mig/tools/

    """

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        Transcription.__init__(self, name, mintime, maxtime)

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
                    ScliteTimePoint(float(begin)),
                    ScliteTimePoint(float(end)))

                label = Label(word)

                tier.Add(Annotation(interval, label))

        m = Media(gen_id(), wavname)
        self.SetMedia( m )
        for tier in self:
            tier.SetMedia( m )
        self.SetName( wavname )
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

    def __write_tier(self, tier, filefp):

        if tier.IsPoint():
            tier = point2interval(tier, SCLITE_RADIUS)

        for annotation in tier:
            wavname  = tier.GetMedia().url if tier.GetMedia() is not None else self.GetName()
            begin    = annotation.GetLocation().GetBeginMidpoint()
            end      = annotation.GetLocation().GetEndMidpoint()
            word = annotation.GetLabel().GetValue()

            if('speaker' not in tier.metadata):
                speaker = 'none'
            else:
                speaker = tier.metadata['speaker']

            channel = tier.GetName()

            filefp.write('%s %s %s %s %s %s\n' % (
                wavname,
                channel,
                speaker,
                begin,
                end,
                word))

    # -----------------------------------------------------------------
