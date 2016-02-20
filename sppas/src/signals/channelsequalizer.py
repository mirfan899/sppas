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
# File: channelsequalizer.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Nicolas Chazeau (n.chazeau94@gmail.com), Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ---------------------------------------------------------------------------

from signals.monofragment import MonoFragment
from signals.channel import Channel

# ---------------------------------------------------------------------------

class ChannelsEqualizer:
    """
    @authors: Nicolas Chazeau
    @contact: n.chazeau94@gmail.com
    @license: GPL, v3
    @summary: A channel utilitary class to equalize number of frames by appending silence at the end.
    """

    def __init__(self):
        """
        Constructor.

        """
        self.channels = []

    def append_channel(self, channel):
        """
        Append a channel in the list of channels

        @param channel (Channel object) the channel to append

        """
        self.channels.append(channel)

    def equalize(self):
        """
        Equalize the number of frames of all the channels by appending silence at the end.

        """
        nframes = 0
        for i in xrange(len(self.channels)):
            nframes = max(nframes, self.channels[i].get_nframes())

        for i in xrange(len(self.channels)):
            if self.channels[i].get_nframes() < nframes:
                fragment = MonoFragment(self.channels[i].frames)
                fragment.create_silence(nframes - self.channels[i].get_nframes())
                self.channels[i] = Channel(self.channels[i].get_framerate(), self.channels[i].get_sampwidth(), fragment.get_frames())

    def get_channel(self, idx):
        """
        Return the channel wanted

        @param idx (int) the index of the channel to return
        @return the channel wanted

        """
        return self.channels[idx]