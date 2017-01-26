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
# File: channelsilence.py
# ----------------------------------------------------------------------------

from .audioframes import AudioFrames
from .channel import Channel
from .channelvolume import ChannelVolume

# ----------------------------------------------------------------------------


class ChannelSilence(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      This class implements the silence finding on a channel.

    """
    def __init__(self, channel, winlenght=0.01):
        """
        Constructor.

        @param channel (Channel) the input channel object
        @param winlenght (float) duration of a window for the estimation of the volume

        """
        self.channel = channel
        self.volstats = ChannelVolume(channel, winlenght)
        self.__silences = []

    # ------------------------------------------------------------------

    def get_channel(self):
        return self.channel

    def get_volstats(self):
        return self.volstats

    # ------------------------------------------------------------------
    # DEPRECATED Silence detection. Used until sppas-1.7.8.
    # ------------------------------------------------------------------

    def tracks(self, m):
        """
        Yield tuples (from,to) of the tracks, from the result of get_silence().
        @deprecated

        """
        from_pos = 0
        if len(self.silence)==0:
        # No silence: Only one track!
            yield 0,self.channel.get_nframes()
            return
        # At least one silence
        for to_pos, next_from in self.silence:
            if (to_pos - from_pos) >= (m * self.channel.get_framerate()):
                # Track is long enough to be considered a track.
                yield int(from_pos), int(to_pos)
            from_pos = next_from

        # Last track after the last silence
        # (if the silence does not end at the end of the channel)
        to_pos = self.channel.get_nframes()
        if (to_pos - from_pos) >= (m * self.channel.get_framerate()):
            yield int(from_pos), int(to_pos)


    def get_silence(self, p=0.250, v=150, s=0.):
        """
        Estimates silences from an audio file.
        @deprecated

        @param p (float) Minimum silence duration in seconds
        @param v (int) Expected minimum volume (rms value)
        @param s (float) Shift delta duration in seconds
        @return a set of frames corresponding to silences.

        """
        self.channel.seek(0)
        self.silence = []

        # Once silence has been found, continue searching in this interval
        nbreadframes = int(self.volstats.get_winlen() * self.channel.get_framerate())
        afterloop_frames = int(nbreadframes/2) #int((nbreadframes/2) * self.channel.get_framerate())
        initpos = i = self.channel.tell()

        # This scans the file in steps of frames whether a section's volume
        # is lower than silence_cap, if it is it is written to silence.
        while i < self.channel.get_nframes():

            curframe = self.channel.get_frames(nbreadframes)

            a = AudioFrames( curframe, self.channel.get_sampwidth(), 1)
            #volume = audioutils.get_rms(curframe, self.channel.get_sampwidth())
            volume = a.rms()
            if volume < v:

                # Continue searching in smaller steps whether the silence is
                # longer than read frames but smaller than read frames * 2.
                while volume < v and self.channel.tell() < self.channel.get_nframes():
                    curframe = self.channel.get_frames(afterloop_frames)

                    a = AudioFrames( curframe, self.channel.get_sampwidth(), 1)
                    volume = a.rms()
                    #volume   = audioutils.get_rms(curframe, self.channel.get_sampwidth())

                # If the last sequence of silence ends where the new one starts
                # it's a continuous range.
                if self.silence and self.silence[-1][1] == i:
                    self.silence[-1][1] = self.channel.tell()
                else:
                # append if silence is long enough
                    duree = self.channel.tell() - i
                    nbmin = int( (p+s) * self.channel.get_framerate())
                    if duree > nbmin:
                        # Adjust silence start-pos
                        __startpos = i + ( s * self.channel.get_framerate() )
                        # Adjust silence end-pos
                        __endpos = self.channel.tell() - ( s * self.channel.get_framerate() )
                        self.silence.append([__startpos, __endpos])

            i = self.channel.tell()

        # Return the position in the file to where it was when we got it.
        self.channel.seek(initpos)

    # ------------------------------------------------------------------
    # Utility method
    # ------------------------------------------------------------------

    def track_data(self, tracks):
        """
        Get the track data: a set of frames for each track.

        @param tracks (list of tuples) List of (from_pos,to_pos)

        """
        nframes = self.channel.get_nframes()
        for from_pos, to_pos in tracks:
            if nframes < from_pos:
                # Accept a "DELTA" of 10 frames, in case of corrupted data.
                if nframes < from_pos-10:
                    raise ValueError("Position %d not in range(%d)" % (from_pos, nframes))
                else:
                    from_pos = nframes
            # Go to the provided position
            self.channel.seek(from_pos)
            # Keep in mind the related frames
            yield self.channel.get_frames(to_pos - from_pos)

    # ------------------------------------------------------------------

    def refine(self, pos, threshold, winlenght=0.005, direction=1):
        """
        Refine the position of a silence around a given position.

        @param pos (int) Initial position of the silence
        @param threshold (int) RMS threshold value for a silence
        @param winlenght (float) Windows duration to estimate the RMS
        @return new position

        """
        delta = int(self.volstats.get_winlen() * self.channel.get_framerate())
        from_pos = max(pos-delta,0)
        self.channel.seek( from_pos )
        frames = self.channel.get_frames( delta*2 )
        c = Channel( self.channel.get_framerate(), self.channel.get_sampwidth(), frames )
        volstats = ChannelVolume( c, winlenght )

        if direction==1:
            for i,v in enumerate(volstats):
                if v > threshold:
                    return (from_pos + i*( int(winlenght*self.channel.get_framerate())))
        if direction==-1:
            i=len(volstats)
            for v in reversed(volstats):
                if v > threshold:
                    return (from_pos + (i*( int(winlenght*self.channel.get_framerate()))))
                i = i-1

        return pos

    # ------------------------------------------------------------------

    def extract_tracks(self, mintrackdur=0.300, shiftdurstart=0.010, shiftdurend=0.010):
        """
        Return a list of tuples (from_pos,to_pos) of the tracks.

        @param mintrackdur (float) The minimum duration for a track (in seconds)
        @param shiftdurstart (float) The time to remove to the start boundary (in seconds)
        @param shiftdurend (float) The time to add to the end boundary (in seconds)

        """
        tracks = []

        # No silence: Only one track!
        if len(self.__silences)==0:
            tracks.append( (0,self.channel.get_nframes()) )
            return tracks

        # Convert values: time into frame
        delta      = int(mintrackdur   * self.channel.get_framerate())
        shiftstart = int(shiftdurstart * self.channel.get_framerate())
        shiftend   = int(shiftdurend   * self.channel.get_framerate())
        from_pos = 0

        for to_pos, next_from in self.__silences:

            shift_from_pos = max(from_pos - shiftstart, 0)
            shift_to_pos   = min(to_pos + shiftend, self.channel.get_nframes())

            if (shift_to_pos-shift_from_pos) >= delta:
                # Track is long enough to be considered a track.
                tracks.append( (int(shift_from_pos), int(shift_to_pos)) )

            from_pos = next_from

        # Last track after the last silence
        # (if the silence does not end at the end of the channel)
        to_pos = self.channel.get_nframes()
        if (to_pos - from_pos) >= delta:
            tracks.append( (int(from_pos), int(to_pos)) )

        return tracks

    # ------------------------------------------------------------------
    # New silence detection
    # ------------------------------------------------------------------

    def search_threshold_vol(self):
        """
        Try to fix optimally the threshold for speech/silence segmentation.
        This is a simple observation of the distribution of rms values.

        @return (int) volume value

        """
        vmin  = self.volstats.min()
        vmean = self.volstats.mean()
        vcvar = 1.5 * self.volstats.coefvariation()
        alt = (vmean-vmin)/5.
        if alt > vcvar:
            vcvar=alt

        return vmin + int((vmean - vcvar))

    # ------------------------------------------------------------------

    def search_silences(self, threshold=0, mintrackdur=0.08):
        """
        Search windows with a volume lesser than a given threshold.

        @param threshold (int) Expected minimum volume (rms value)
        If threshold is set to 0, search_minvol() will assign a value.
        @param mintrackdur (float) The very very minimum duration for
        a track (in seconds).

        """
        if threshold == 0:
            threshold = self.search_threshold_vol()

        # This scans the volumes whether it is lower than threshold,
        # if it is it is written to silence.
        self.__silences = []
        inside = False
        idxbegin = 0
        ignored  = 0
        delta = int(mintrackdur / self.volstats.get_winlen())

        for i,v in enumerate(self.volstats):
            if v < threshold:
                if inside is False:
                    # It's the beginning of a block of zero volumes
                    idxbegin = i
                    inside = True
            else:
                if inside is True:
                    # It's the end of a block of non-zero volumes...
                    # or not if the track is very short!
                    if (i-idxbegin) > delta:
                        inside = False
                        idxend   = i-ignored #-1 # not use -1 because we want the end of the frame
                        from_pos = int(idxbegin * self.volstats.get_winlen() * self.channel.get_framerate())
                        to_pos   = int(idxend   * self.volstats.get_winlen() * self.channel.get_framerate())

                        # Find the boundaries with a better precision
                        w = self.volstats.get_winlen()/4.
                        from_pos = self.refine(from_pos, threshold, w, direction=-1)
                        to_pos   = self.refine(to_pos,   threshold, w, direction=1)

                        self.__silences.append((from_pos,to_pos))
                        ignored = 0
                    else:
                        ignored += 1

        # Last interval
        if inside is True:
            start_pos = int(idxbegin * self.volstats.get_winlen() * self.channel.get_framerate())
            end_pos   = self.channel.get_nframes()
            self.__silences.append((start_pos,end_pos))

        return threshold

    # ------------------------------------------------------------------

    def filter_silences(self, minsildur=0.200):
        """
        Filtered the current silences.

        @param minsildur (float) Minimum silence duration in seconds

        """
        if len(self.__silences) == 0:
            return 0

        filteredsil = []
        for (start_pos,end_pos) in self.__silences:
            sildur = float(end_pos-start_pos) / float(self.channel.get_framerate())
            if sildur > minsildur:
                filteredsil.append( (start_pos,end_pos) )

        self.__silences = filteredsil

        return len(self.__silences)

#         print "Number of silences: ",len(self.__silences)
#         print "Silences: "
#         for (s,e) in self.__silences:
#             print " (",float(s)/float(self.channel.get_framerate())," ; ",float(e)/float(self.channel.get_framerate()),")"

    # ------------------------------------------------------------------

    def set_silences(self, silences):
        """
        Fix manually silences!

        @param silences (list of tuples (start_pos,end_pos))

        """
        self.__silences = silences

    # ------------------------------------------------------------------

    def reset_silences(self):
        """
        Reset silences.

        """
        self.__silences = []

    # -----------------------------------------------------------------------
    #
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__silences)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for x in self.__silences:
            yield x

    # -----------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__silences[i]

    # -----------------------------------------------------------------------
