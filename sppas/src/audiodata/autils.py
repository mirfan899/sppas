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
# File: autils.py
# ----------------------------------------------------------------------------
"""
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Audio utilities.
"""

import audiodata.io
from audiodata.audio            import AudioPCM
from audiodata.channel          import Channel
from audiodata.channelframes    import ChannelFrames
from audiodata.channelformatter import ChannelFormatter
from audiodata.channelsilence   import ChannelSilence

# ------------------------------------------------------------------------

def frames2times(listframes, framerate):
    """
    Convert a list of frame' into a list of time' values.

    @param listframes (list) tuples (from_pos,to_pos)
    @return a list of tuples (from_time,to_time)

    """
    listtimes = []
    fm = float(framerate)

    for (s,e) in listframes:
        fs = float(s) / fm
        fe = float(e) / fm
        listtimes.append( (fs, fe) )

    return listtimes

# ------------------------------------------------------------------

def times2frames(listtimes, framerate):
    """
    Convert a list of time' into a list of frame' values.

    @param listframes (list) tuples (from_time,to_time)
    @return a list of tuples (from_pos,to_pos)

    """
    listframes = []
    fm = float(framerate)
    for (s,e) in listtimes:
        fs = int(s*fm)
        fe = int(e*fm)
        listframes.append( (fs, fe) )

    return listframes

# ------------------------------------------------------------------

def extract_audio_channel(inputaudio, idx):
    """
    Return the channel of a specific index from an audio file name.

    @param inputaudio (str - IN) Audio file name.
    @param idx (int - IN) Channel index

    """
    idx = int(idx)
    audio = audiodata.io.open(inputaudio)
    i = audio.extract_channel(idx)
    channel = audio.get_channel(i)
    audio.close()

    return channel

# ------------------------------------------------------------------------

def extract_channel_fragment(channel, fromtime, totime, silence=0.):
    """
    Extract a fragment of a channel in the interval [fromtime,totime].
    Eventually, surround it by silences.

    @param channel  (Channel - IN)
    @param fromtime (float - IN) From time value in seconds.
    @param totime   (float - IN) To time value in seconds.
    @param silence  (float - IN) Duration value in seconds.

    """
    framerate = channel.get_framerate()

    # Extract the fragment of the channel
    startframe = int(fromtime*framerate)
    toframe    = int(totime*framerate)
    fragmentchannel = channel.extract_fragment(begin=startframe, end=toframe)

    # Get all the frames of this fragment
    nbframes = fragmentchannel.get_nframes()
    cf = ChannelFrames( fragmentchannel.get_frames( nbframes ) )

    # surround by silences
    if silence > 0.:
        cf.prepend_silence( silence*framerate )
        cf.append_silence(  silence*framerate )

    return Channel( 16000, 2, cf.get_frames() )

# ------------------------------------------------------------------------

def search_channel_speech(channel):
    """
    Return a list of tracks (i.e. speech intervals where energy is high enough).
    Use only default parameters.

    @param channel (Channel - IN) The channel we'll try to find tracks
    @return A list of tuples (fromtime,totime)

    """
    chansil = ChannelSilence( channel )
    chansil.search_silences()
    chansil.filter_silences( 0.250 )
    tracks = chansil.extract_tracks()
    tracks.append( (channel.get_nframes(),channel.get_nframes()) )
    trackstimes = frames2times(tracks, channel.get_framerate())

    return trackstimes

# ------------------------------------------------------------------------

def format_channel(channel, framerate, sampwith):
    """
    Return a channel with the requested framerate and sampwidth.

    """
    fm = channel.get_framerate()
    sp = channel.get_sampwidth()
    if fm != framerate or sp != sampwith:
        formatter = ChannelFormatter( channel )
        formatter.set_framerate( framerate )
        formatter.set_sampwidth( sampwith )
        formatter.convert()
        return formatter.get_channel()

    return channel

# ------------------------------------------------------------------------

def write_channel(audioname, channel):
    """
    Write a channel as an audio file.

    @param audioname (str - IN) Audio file name to write
    @param channel (Channel - IN) Channel to be saved

    """
    audio_out = AudioPCM()
    audio_out.append_channel( channel )
    audiodata.io.save( audioname, audio_out )

# ------------------------------------------------------------------------


