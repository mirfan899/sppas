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

NO_AUDIO_MSG = "No audio file."

# ---------------------------------------------------------------------------

import struct

from channel   import Channel
from audioframes import AudioFrames

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
        self.__reset()
        self.audiofp = audio.get_audiofp()
        if self.audiofp:
            self.nbreadframes = int(self.frameduration * self.get_framerate())
        self.channels = audio.get_channels()

    # ----------------------------------------------------------------------

    def get_channels(self):
        """
        Return the list of uploaded channels.

        @return the list of channels

        """
        return self.channels


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


    def pop_channel(self, idx):
        """
        Pop the channel at the position given from the list of uploaded channels

        @param idx (int) the index of the channel to remove

        """
        self.channels.pop(idx)


    def insert_channel(self, idx, channel):
        """
        Insert a channel at the position given in the list of uploaded channels

        @param channel (Channel) the channel to insert
        @param idx (int) the index where the channel has to be inserted

        """
        self.channels.insert(idx, channel)


    def get_channel(self, idx):
        """
        Get an uploaded channel.

        @param idx (int) the index of the channel to return
        @return channel (Channel) the channel wanted

        """
        return self.channels[idx]


    def append_channel(self, channel):
        """
        Append a channel to the list of uploaded channels.

        @param channel (Channel) the channel to append

        """
        self.channels.append(channel)


    def extract_channel(self, number):
        """
        Extract a channel from the Audio File Pointer and store frames into
        a Channel() instance.

        @param number (int) number of the channel to extract
        @return the index of the new Channel() in the list

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)

        sw = self.get_sampwidth()
        nc = self.get_nchannels()
        data = self.read_frames(self.get_nframes())

        if nc > 1:
            frames = ''
            for i in xrange(number*sw, len(data), nc*sw):
                for j in xrange(0,sw):
                    frames = frames + data[i+j]

            channel = Channel( self.get_framerate(), self.get_sampwidth(), frames )
        else:
            channel = Channel( self.get_framerate(), self.get_sampwidth(), data )

        self.append_channel( channel )

        return len(self.channels)-1


    # ----------------------------------------------------------------------
    # Read content, for audiofp
    # ----------------------------------------------------------------------

    def read(self):
        """
        Read a certain amount of frames, depending on frame-duration value.

        @return the frames

        """
        return self.read_frames(self.nbreadframes)


    def read_frames(self, nframes):
        """
        Read the frames from the audio file.

        @param nframes (int) the number of frames to read
        @return the frames

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)
        return self.audiofp.readframes(nframes)


    def read_samples(self, nframes):
        """
        Read the samples from the audio file.

        @param nframes (int) the number of frames to read
        @return the samples

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)

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
                raise Exception(NO_AUDIO_MSG)
        return self.audiofp.getsampwidth()


    def get_framerate(self):
        """
        Return the frame rate of the Audio File Pointer.

        @return the frame rate of the audio file

        """
        if not self.audiofp:
            if len(self.channels) > 0:
                return self.channels[0].get_framerate()
            else:
                raise Exception(NO_AUDIO_MSG)
        return self.audiofp.getframerate()


    def get_nframes(self):
        """
        Return the number of frames of the Audio File Pointer.

        @return the number of frames of the audio file

        """
        if not self.audiofp:
            if len(self.channels) > 0:
                return self.channels[0].get_nframes()
            else:
                raise Exception(NO_AUDIO_MSG)
        return self.audiofp.getnframes()


    def get_nchannels(self):
        """
        Return the number of channels of the Audio File Pointer.

        @return the number of channels of the audio file

        """
        if not self.audiofp:
            if len(self.channels) > 0:
                return len(self.channels)
            else:
                raise Exception(NO_AUDIO_MSG)
        return self.audiofp.getnchannels()


    def get_duration(self):
        """
        Return the duration of the Audio File Pointer.

        @return the duration of the audio file (in seconds)

        """
        if not self.audiofp:
            if len(self.channels) > 0:
                return self.channels[0].get_duration()
            else:
                raise Exception(NO_AUDIO_MSG)

        return float(self.get_nframes())/float(self.get_framerate())

    # ----------------------------------------------------------------------
    # Getters, for audiofp, volume information
    # ----------------------------------------------------------------------

    def get_frameduration(self):
        """
        Return the frame-duration used to estimate volumes of the Audio File Pointer.

        @return the frameduration set by default

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)
        return self.frameduration


    def get_minvolume(self):
        """
        Return the min volume of the Audio File Pointer.

        @return the minimum volume

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)
        self.__set_minvolume()

        return self.minvolume


    def get_maxvolume(self):
        """
        Return the max volume of the Audio File Pointer.

        @return the maximum volume

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)
        self.__set_maxvolume()

        return self.maxvolume


    def get_meanvolume(self):
        """
        Return the mean volume of the Audio File Pointer.

        @return the mean volume

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)
        self.__set_minvolume()
        self.__set_maxvolume()
        self.__set_meanvolume()

        return self.meanvolume


    def get_volumes(self):
        """
        Return an array containing the volume of each frame of the Audio file pointer.

        @return an array containing the volume of each frame of the audio file

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)
        vol = []
        nb = 0
        while self.tell() < self.nframes:
            frames  = self.read_frames(self.nbreadframes)
            a = AudioFrames(frames, self.get_sampwidth(), self.get_nchannels())
            vol[nb] = a.rms()
            nb += 1
        return vol


    def get_rms(self):
        """
        Return the root mean square of the whole file

        @return the root mean square of the audio file

        """
        a = AudioFrames(self.read_frames(self.get_nframes()), self.get_sampwidth(), self.get_nchannels())
        return a.rms()


    def get_clipping_rate(self, factor):
        """
        Return the clipping rate of the frames

        @param factor (float) An interval to be more precise on clipping rate.
        It will consider that all frames outside the interval are clipped.
        Factor has to be between 0 and 1.

        """
        a = AudioFrames(self.read_frames(self.get_nframes()), self.get_sampwidth())
        return a.get_clipping_rate(factor)

    # ----------------------------------------------------------------------
    # Navigate into the audiofp
    # ----------------------------------------------------------------------

    def set_pos(self, pos):
        """
        Fix reader position.

        @param pos (int) the position to set

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)
        self.audiofp.setpos(pos)


    def tell(self):
        """
        Get reader position.

        @return the current position

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)
        return self.audiofp.tell()


    def rewind(self):
        """
        Get reader position at the beginning of the file.

        """
        if not self.audiofp:
            raise Exception(NO_AUDIO_MSG)
        return self.audiofp.rewind()


    # ----------------------------------------------------------------------
    # Verify the compatibility between the channels
    # ----------------------------------------------------------------------

    def verify_channels(self):
        """
        Verify that the channels have the same framerate, sample width and number of frames.

        """
        if len(self.channels) == 0:
            raise NameError("No channel detected !")

        sampwidth = self.channels[0].get_sampwidth()
        framerate = self.channels[0].get_framerate()
        nframes = self.channels[0].get_nframes()

        for i in xrange(1, len(self.channels)):
            if self.channels[i].get_sampwidth() != sampwidth:
                raise NameError("Channels have not the same sampwidth ! Convert them before mix.")
            if self.channels[i].get_framerate() != framerate:
                raise NameError("Channels have not the same framerate ! Convert them before mix.")
            if self.channels[i].get_nframes() != nframes:
                raise NameError("Channels have not the same number of frames ! Convert them before mix.")

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
            raise Exception(NO_AUDIO_MSG)
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

        # Set default information about frames
        self.frameduration = 0.01
        self.nbreadframes  = 0

        # Set informations about the volume
        self.minvolume  = None
        self.maxvolume  = None
        self.meanvolume = None

    # ----------------------------------------------------------------------

    def __set_maxvolume(self):
        """
        Set the max volume of the file.
        Max volume for the whole file is the max rms of each frame.

        """
        # Max volume was already estimated
        if self.maxvolume is not None:
            return self.maxvolume

        # Remember current position in the speech file
        pos = self.tell()

        # Rewind to the beginning of the file
        self.rewind()

        # Find the max rms value (explore all frames)
        self.maxvolume = 0
        while self.tell() < self.get_nframes():
            frames = self.read_frames(self.nbreadframes)
            a = AudioFrames(frames, self.get_sampwidth(), self.get_nchannels())
            rms = a.rms()
            if rms > self.maxvolume:
                self.maxvolume = rms

        # Returns to the position where the file was before
        self.set_pos(pos)


    def __set_minvolume(self):
        """
        Min volume for the whole file is the min rms of each frame.

        """
        # Min volume was already estimated
        if self.minvolume is not None:
            return self.minvolume

        # Remember current position in the speech file
        pos = self.tell()

        # Rewind to the begining of the file
        self.rewind()

        # Find the min rms value (explore all frames)
        self.minvolume = 0
        while self.tell() < self.get_nframes():
            frames = self.read_frames(self.nbreadframes)
            a = AudioFrames(frames, self.get_sampwidth(), self.get_nchannels())
            rms = a.rms()
            if rms < self.minvolume or self.minvolume == 0:
                self.minvolume = rms

        # Returns to the position where the file was before
        self.set_pos(pos)


    def __set_meanvolume(self):
        """
        Calculate the mean volume of the adio file (the mean of rms of the whole file).

        """
        # Median volume was already estimated
        if self.meanvolume is not None:
            return self.meanvolume

        # Remember current position in the speech file
        pos = self.tell()

        # Rewind to the beginning of the file
        self.rewind()

        # Get the mean value: the rms of the whole file
        ####mean_volume = self.rms(self.speech.readframes(self.nframes))
        self.meanvolume = 0
        sumrms = 0
        nb = 0
        while self.tell() < self.get_nframes():
            frames = self.read_frames(self.nbreadframes)
            a = AudioFrames(frames, self.get_sampwidth(), self.get_nchannels())
            rms = a.rms()
            sumrms += rms
            nb += 1
        self.meanvolume = sumrms / nb

        # Returns to the position where the file was before
        self.set_pos(pos)


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
