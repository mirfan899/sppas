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
# File: audio.py
# ---------------------------------------------------------------------------

import struct

from audiodata.audioframes   import AudioFrames
from audiodata.audiodataexc  import AudioDataError
from audiodata.channel       import Channel
from audiodata.channelsmixer import ChannelsMixer

# ---------------------------------------------------------------------------

class AudioPCM( object ):
    """
    @authors:      Nicolas Chazeau, Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      An audio file reader/writer utility class.

    Pulse-code modulation (PCM) is a method used to digitally represent sampled
    analog signals. A PCM signal is a sequence of digital audio samples
    containing the data providing the necessary information to reconstruct the
    original analog signal. Each sample represents the amplitude of the signal
    at a specific point in time, and the samples are uniformly spaced in time.
    The amplitude is the only information explicitly stored in the sample

    A PCM stream has two basic properties that determine the stream's fidelity
    to the original analog signal: the sampling rate, which is the number of
    times per second that samples are taken; and the bit depth, which
    determines the number of possible digital values that can be used to
    represent each sample.

    For speech analysis, recommended sampling rate are 16000 (for automatic
    analysis) or 48000 (for manual analysis); and recommended sample depths
    are 16 (for automatic analysis) or 24 bits (for both automatic and manual
    analysis) per sample.

    These variables are user gettable through appropriate methods:
        - nchannels -- the number of audio channels
        - framerate -- the sampling frequency
        - sampwidth -- the number of bytes per audio sample (1, 2 or 4)
        - nframes   -- the number of frames
        - params    -- parameters of the wave file
        - filename  -- the name of the wave file

    The audiofp member is assigned by the IO classes, as WaveIO, AifIO, SunauIO.
    It is expected that it can access the following methods:
        - readframes()
        - writeframes()
        - getsampwidth()
        - getframerate()
        - getnframes()
        - getnchannels()
        - setpos()
        - tell()
        - rewind()

    """
    def __init__(self):
        """
        Creates a new AudioPCM instance.

        """
        super(AudioPCM, self).__init__()
        self.__reset()

        # The list of loaded channels of this audio
        self.channels = []

    # ----------------------------------------------------------------------

    def Set(self, audio):
        """
        Set a new AudioPCM() instance either with an audiofp, or channels or both.

        @param audio (AudioPCM) AudioPCM to set

        """
        self.audiofp  = audio.get_audiofp()
        self.channels = audio.get_channels()

    # ----------------------------------------------------------------------

    def get_channels(self):
        """
        Return the list of uploaded channels.

        @return the list of channels

        """
        return self.channels

    # ----------------------------------------------------------------------

    def get_audiofp(self):
        """
        Return the audio file pointer.

        @return the audio file pointer

        """
        return self.audiofp


    # ----------------------------------------------------------------------
    # Uploaded channels
    # ----------------------------------------------------------------------

    def remove_channel(self, channel):
        """
        Remove the channel from the list of uploaded channels

        @param channel (Channel) the channel to remove

        """
        self.channels.pop(channel)

    # ----------------------------------------------------------------------

    def pop_channel(self, idx):
        """
        Pop the channel at the position given from the list of uploaded channels

        @param idx (int) the index of the channel to remove

        """
        idx = int(idx)
        self.channels.pop(idx)

    # ----------------------------------------------------------------------

    def insert_channel(self, idx, channel):
        """
        Insert a channel at the position given in the list of uploaded channels

        @param channel (Channel) the channel to insert
        @param idx (int) the index where the channel has to be inserted

        """
        idx = int(idx)
        self.channels.insert(idx, channel)

    # ----------------------------------------------------------------------

    def get_channel(self, idx):
        """
        Get an uploaded channel.

        @param idx (int) the index of the channel to return
        @return channel (Channel) the channel wanted

        """
        idx = int(idx)
        return self.channels[idx]

    # ----------------------------------------------------------------------

    def append_channel(self, channel):
        """
        Append a channel to the list of uploaded channels.

        @param channel (Channel) the channel to append
        @return index of the channel

        """
        self.channels.append(channel)
        return len(self.channels) - 1

    # ----------------------------------------------------------------------

    def extract_channel(self, index=0):
        """
        Extract a channel from the Audio File Pointer and append in the list of channels.

        Frames are stored into a Channel() instance.
        Index of the channel in the audio file:
        0 = 1st channel (left); 1 = 2nd channel (right); 2 = 3rd channel...

        @param index (int) The index of the channel to extract
        @return the index of the new Channel() appended in the list

        """
        if not self.audiofp:
            raise AudioDataError

        index = int(index)
        if index < 0:
            raise AudioDataError('Expected the index of channels to extract. Got: %d'%index)

        nc = self.get_nchannels()
        self.seek(0)
        data = self.read_frames(self.get_nframes())

        if nc == 0:
            raise AudioDataError('No channel in the audio file.')

        if index+1 > nc:
            raise AudioDataError('No channel with index %d in the audio file.'%index)

        if nc == 1:
            channel = Channel( self.get_framerate(), self.get_sampwidth(), data )
            return self.append_channel( channel )

        frames = ""
        sw = self.get_sampwidth()
        for i in xrange(index*sw, len(data), nc*sw):
            frames += data[i:i+sw]
        channel = Channel( self.get_framerate(), self.get_sampwidth(), frames )

        return self.append_channel( channel )

    # ----------------------------------------------------------------------
    # Read content, for audiofp
    # ----------------------------------------------------------------------

    def read(self):
        """
        Read a certain amount of frames, depending on frame-duration value.

        @return the frames

        """
        return self.read_frames(self.nbreadframes)

    # ----------------------------------------------------------------------

    def read_frames(self, nframes):
        """
        Read the frames from the audio file.

        @param nframes (int) the number of frames to read
        @return the frames

        """
        if not self.audiofp:
            raise AudioDataError

        return self.audiofp.readframes(nframes)

    # ----------------------------------------------------------------------

    def read_samples(self, nframes):
        """
        Read the samples from the audio file.

        @param nframes (int) the number of frames to read
        @return the samples

        """
        if not self.audiofp:
            raise AudioDataError

        data = self.read_frames(nframes)

        # Unpack to get all values, depending on the number of bytes of each value.
        if self.get_sampwidth() == 4 :
            data = struct.unpack("<%ul" % (len(data) / 4), data)

        elif self.get_sampwidth() == 2 :
            data = struct.unpack("<%uh" % (len(data) / 2), data)

        else :
            data = struct.unpack("%uB"  %  len(data),      data)
            data = [ s - 128 for s in data ]

        nc  = self.get_nchannels()
        samples = []
        if nc > 1:
            # Split channels
            for i in xrange(nc) :
                samples.append([ data[j] for j in xrange(i, len(data), nc) ])
        else:
            samples.append(list(data))

        return samples

    # ----------------------------------------------------------------------
    # Getters, for audiofp
    # ----------------------------------------------------------------------

    def get_sampwidth(self):
        """
        Return the sample width of the Audio File Pointer.

        @return the sample width of the audio file

        """
        if not self.audiofp:
            if len(self.channels) > 0:
                return self.channels[0].get_sampwidth()
            else:
                raise AudioDataError('No data in audio file.')

        return self.audiofp.getsampwidth()

    # ----------------------------------------------------------------------

    def get_framerate(self):
        """
        Return the frame rate of the Audio File Pointer.

        @return the frame rate of the audio file

        """
        if not self.audiofp:
            if len(self.channels) > 0:
                return self.channels[0].get_framerate()
            else:
                raise AudioDataError('No data in audio file.')

        return self.audiofp.getframerate()

    # ----------------------------------------------------------------------

    def get_nframes(self):
        """
        Return the number of frames of the Audio File Pointer.

        @return the number of frames of the audio file

        """
        if not self.audiofp:
            if len(self.channels) > 0:
                return self.channels[0].get_nframes()
            else:
                raise AudioDataError('No data in audio file.')

        return self.audiofp.getnframes()

    # ----------------------------------------------------------------------

    def get_nchannels(self):
        """
        Return the number of channels of the Audio File Pointer.

        @return the number of channels of the audio file

        """
        if not self.audiofp:
            if len(self.channels) > 0:
                return len(self.channels)
            else:
                raise AudioDataError('No data in audio file.')

        return self.audiofp.getnchannels()

    # ----------------------------------------------------------------------

    def get_duration(self):
        """
        Return the duration of the Audio File Pointer.

        @return the duration of the audio file (in seconds)

        """
        if not self.audiofp:
            if len(self.channels) > 0:
                return self.channels[0].get_duration()
            else:
                raise AudioDataError('No data in audio file.')

        return float(self.get_nframes())/float(self.get_framerate())

    # ----------------------------------------------------------------------

    def rms(self):
        """
        Return the root mean square of the whole file

        @return the root mean square of the audio file

        """
        pos = self.tell()
        self.seek(0)
        a = AudioFrames(self.read_frames(self.get_nframes()), self.get_sampwidth(), self.get_nchannels())
        self.seek(pos)

        return a.rms()

    # ----------------------------------------------------------------------

    def clipping_rate(self, factor):
        """
        Return the clipping rate of the frames

        @param factor (float) An interval to be more precise on clipping rate.
        It will consider that all frames outside the interval are clipped.
        Factor has to be between 0 and 1.

        """
        pos = self.tell()
        self.seek(0)
        a = AudioFrames(self.read_frames(self.get_nframes()), self.get_sampwidth())
        self.seek(pos)

        return a.clipping_rate(factor)

    # ----------------------------------------------------------------------
    # Navigate into the audiofp
    # ----------------------------------------------------------------------

    def set_pos(self, pos):
        """
        Fix reader position.
        @deprecated: Use seek instead.
        @param pos (int) the position to set

        """
        if not self.audiofp:
            raise AudioDataError

        self.audiofp.setpos(pos)

    # ----------------------------------------------------------------------

    def seek(self, pos):
        """
        Fix reader position.

        @param pos (int) the position to set

        """
        if not self.audiofp:
            raise AudioDataError

        self.audiofp.setpos(pos)

    # ----------------------------------------------------------------------

    def tell(self):
        """
        Get reader position.

        @return the current position

        """
        if not self.audiofp:
            raise AudioDataError

        return self.audiofp.tell()

    # ----------------------------------------------------------------------

    def rewind(self):
        """
        Get reader position at the beginning of the file.

        """
        if not self.audiofp:
            raise AudioDataError

        return self.audiofp.rewind()


    # ----------------------------------------------------------------------
    # Verify the compatibility between the channels
    # ----------------------------------------------------------------------

    def verify_channels(self):
        """
        Check that the channels have the same parameters.
        Check framerate, sample width and number of frames.

        @return bool

        """
        mixer = ChannelsMixer()
        f = 1./len(self.channels)
        for c in self.channels:
            mixer.append_channel(c,f)
        try:
            mixer.check_channels()
        except AudioDataError:
            return False
        return True

    # ------------------------------------------------------------------------
    # Input/Output
    # ------------------------------------------------------------------------

    def open(self):
        name = self.__class__.__name__
        raise NotImplementedError("%s does not support open()." % name)

    # ------------------------------------------------------------------------

    def save(self):
        name = self.__class__.__name__
        raise NotImplementedError("%s does not support save()." % name)

    # ------------------------------------------------------------------------

    def save_fragments(self):
        name = self.__class__.__name__
        raise NotImplementedError("%s does not support save_fragments()." % name)

    # ------------------------------------------------------------------------

    def close(self):
        """
        Close the audiofp.

        """
        if not self.audiofp:
            raise AudioDataError

        self.audiofp.close()
        self.__reset()

    # ----------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------

    def __reset(self):
        """
        Reset all members to a default value.

        """
        # The audio file pointer
        self.audiofp = None

    # ----------------------------------------------------------------------
    # Overloads
    # ----------------------------------------------------------------------

    def __len__(self):
        return len(self.channels)

    # ------------------------------------------------------------------------------------

    def __iter__(self):
        for x in self.channels:
            yield x

    # ------------------------------------------------------------------------------------

    def __getitem__(self, i):
        return self.channels[i]

    # ------------------------------------------------------------------------
