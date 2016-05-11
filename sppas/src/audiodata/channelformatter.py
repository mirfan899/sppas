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
# File: channelformatter.py
# ----------------------------------------------------------------------------

from audiodata.monofragment import MonoFragment
from audiodata.channel      import Channel
from audiodata              import audioutils

# ----------------------------------------------------------------------------

class ChannelFormatter( object ):
    """
    @authors:      Nicolas Chazeau, Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      A channel formatter class.

    """
    def __init__(self, channel):
        """
        Constructor.

        """
        self.channel   = channel
        self.framerate = channel.get_framerate()
        self.sampwidth = channel.get_sampwidth()

    # ----------------------------------------------------------------------
    # Getters
    # ----------------------------------------------------------------------

    def get_framerate(self):
        """
        Return the expected frame rate for the channel.
        Notice that while convert is not applied, it can be different of the
        current one of the channel.

        @return the frame rate that will be used by the converter

        """
        return self.framerate


    def get_sampwidth(self):
        """
        Return the expected sample width for the channel.
        Notice that while convert is not applied, it can be different of the
        current one  of the channel.

        @return the sample width that will be used by the converter

        """
        return self.sampwidth

    # ----------------------------------------------------------------------
    # Setters
    # ----------------------------------------------------------------------

    def set_framerate(self, framerate):
        """
        Return the expected frame rate for the channel.
        Notice that while convert is not applied, it can be different of the
        current one  of the channel.

        @param the frame rate that will be used by the converter

        """
        self.framerate = framerate


    def set_sampwidth(self, sampwidth):
        """
        Fix the expected sample width for the channel.
        Notice that while convert is not applied, it can be different of the
        current one  of the channel.

        @param the sample width that will be used by the converter

        """
        self.sampwidth = sampwidth

    # ----------------------------------------------------------------------
    # Workers
    # ----------------------------------------------------------------------

    def sync(self, channel):
        """
        Convert the channel owned by the ChannelFormatter with the parameters from the channel put in input.

        @param channel (Channel) the channel used as a model

        """
        self.sampwidth = channel.get_sampwidth()
        self.framerate = channel.get_framerate()
        self.convert()

    # ----------------------------------------------------------------------

    def remove_frames(self, begin, end):
        """
        Convert the channel by removing frames.

        @param begin (int) the position of the beginning of the frames to remove
        @param end (int) the position of the end of the frames to remove

        """
        newchannel = Channel()
        newchannel.set_frames( self.channel.frames[:begin*self.sampwidth] + self.channel.frames[end*self.sampwidth:] )
        newchannel.sampwidth = self.sampwidth
        newchannel.framerate = self.framerate
        self.channel = newchannel

    # ----------------------------------------------------------------------

    def add_frames(self, frames, position):
        """
        Convert the channel by adding frames.

        @param position (int) the position where the frames will be inserted

        """
        newchannel = Channel()
        newchannel.set_frames( self.channel.frames[:position*self.sampwidth] + frames + self.channel.frames[position*self.sampwidth:] )
        newchannel.sampwidth = self.sampwidth
        newchannel.framerate = self.framerate
        self.channel = newchannel

    # ----------------------------------------------------------------------

    def append_frames(self, frames):
        """
        Convert the channel by appending frames.

        @param frames (string) the frames to append

        """
        newchannel = Channel()
        newchannel.set_frames( self.channel.frames + frames )
        newchannel.sampwidth = self.sampwidth
        newchannel.framerate = self.framerate
        self.channel = newchannel

    # ----------------------------------------------------------------------

    def bias(self, bias):
        """
        Convert the channel by applying a bias on the frames.

        @param bias (int) the value to bias the frames

        """
        newchannel = Channel()
        newchannel.sampwidth = self.sampwidth
        newchannel.framerate = self.framerate
        newchannel.set_frames(audioutils.bias(self.channel.frames, self.sampwidth, bias))

        self.channel = newchannel

    # ----------------------------------------------------------------------

    def mul(self, factor):
        """
        Convert the channel by multiplying the frames by the factor.

        @param bias (int) the factor to multiply the frames

        """
        newchannel = Channel()
        newchannel.sampwidth = self.sampwidth
        newchannel.framerate = self.framerate
        newchannel.set_frames(audioutils.mul(self.channel.frames, self.sampwidth, factor))

        self.channel = newchannel

    # ----------------------------------------------------------------------

    def remove_offset(self):
        """
        Convert the channel by removing the offset in the channel.

        """
        newchannel = Channel()
        newchannel.sampwidth = self.sampwidth
        newchannel.framerate = self.framerate
        avg = audioutils.avg(self.channel.frames, self.sampwidth)
        newchannel.set_frames(audioutils.bias(self.channel.frames, self.sampwidth, - avg))

        self.channel = newchannel

    # ----------------------------------------------------------------------

    def convert(self):
        """
        Convert the channel to the expected sample width and frame rate.

        """
        newchannel = Channel()
        newchannel.set_frames( self.__convert_frames( self.channel.frames ) )
        newchannel.sampwidth = self.sampwidth
        newchannel.framerate = self.framerate

        self.channel = newchannel

    # ----------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------

    def __convert_frames(self, frames):
        """
        Convert frames to the expected sample width and frame rate.

        @param frames (string) the frames to convert

        """
        f = frames
        fragment = MonoFragment(f)
        #Convert the sample width if it needs to
        if (self.channel.get_sampwidth() != self.sampwidth):
            fragment.changesampwidth(self.channel.get_sampwidth(), self.sampwidth)

        #Convert the self.framerate if it needs to
        if (self.channel.get_framerate() != self.framerate):
            fragment.resample(self.sampwidth, self.channel.get_framerate(), self.framerate)

        return fragment.get_frames()

# --------------------------------------------------------------------------
