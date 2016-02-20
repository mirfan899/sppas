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
# File: channelfragmentextracter.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Nicolas Chazeau (n.chazeau94@gmail.com), Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import struct
from channel import Channel
from signals import audioutils

# ---------------------------------------------------------------------------

class ChannelFragmentExtracter:
    """
    @authors: Nicolas Chazeau
    @contact: n.chazeau94@gmail.com
    @license: GPL, v3
    @summary: A channel utilitary class to extract a fragment from a channel.
    """

    def __init__(self, channel):
        """
        Constructor.

        """
        self.channel = channel
        self.framerate = channel.get_framerate()
        self.sampwidth = channel.get_sampwidth()
        self.nframes = channel.get_nframes()

    # End __init__
    # -----------------------------------------------------------------------

    def extract_fragment(self, begin, end = 0):
        """
        Extract a fragment between the beginning and the end chosen

        @param begin (int : number of frames) the beggining of the fragment to extract
        @param end (int: number of frames) the end of the fragment to extract

        @return the fragment extracted in an Channel object

        """

        if begin > self.nframes:
            raise NameError("The beginning can't be upper than the duration")
        elif end > self.nframes:
            raise NameError("The end can't be upper than the duration")
        elif begin > end and end != 0:
            raise NameError("The end can't be upper than the beginning")
        elif begin < 0 or end < 0:
            raise NameError("Beginning and End can't be negative values")

        posbegin = int(begin*self.channel.get_sampwidth())
        if end == 0:
            frames = self.channel.frames[posbegin:]
        else:
            posend = int(end*self.channel.get_sampwidth())
            frames = self.channel.frames[posbegin:posend]


        return Channel(self.channel.get_framerate(), self.channel.get_sampwidth(), frames)

