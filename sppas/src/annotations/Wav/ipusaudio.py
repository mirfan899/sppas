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
# File: ipusaudio.py
# ---------------------------------------------------------------------------

from audiodata.channelsilence import ChannelSilence

# ---------------------------------------------------------------------------

class IPUsAudio( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      An IPUs segmenter from audio.

    IPUs - Inter-Pausal Units are blocks of speech bounded by silent pauses
    of more than X ms, and time-aligned on the speech signal.

    """
    MIN_SIL_DUR = 0.08
    MIN_IPU_DUR = 0.08

    def __init__(self, channel):
        """
        Creates a new IPUsAudio instance.

        """
        super(IPUsAudio, self).__init__()
        self.reset()
        self.set_channel(channel)

    # ------------------------------------------------------------------

    def reset(self):
        """
        Set default values.

        """
        self.min_sil_dur   = 0.250
        self.min_ipu_dur   = 0.300
        self.vol_threshold = 0
        self.shift_start   = 0.010
        self.shift_end     = 0.020
        self.win_lenght    = 0.020
        self.auto_vol      = True

        self.bornestart = False
        self.borneend   = False

    # ------------------------------------------------------------------
    # Manage Channel
    # ------------------------------------------------------------------

    def get_channel(self):
        """
        Return the channel.

        """
        return self.chansil.get_channel()

    # ------------------------------------------------------------------

    def set_channel(self, channel):
        """
        Set a new Channel.

        """
        if channel is not None:
            self.chansil = ChannelSilence( channel, self.win_lenght )
        else:
            self.chansil = None

    # ------------------------------------------------------------------

    def reset_silences(self):
        """
        Reset the list of silences.

        """
        if self.chansil is not None:
            self.chansil.reset_silences()

    # ------------------------------------------------------------------

    def set_silences(self, silences):
        """
        Fix the list of silences.

        """
        if self.chansil is not None:
            self.chansil.set_silences( silences )


    # ------------------------------------------------------------------
    # Setters for members
    # ------------------------------------------------------------------

    def set_vol_threshold(self, vol_threshold):
        """
        Fix the default minimum volume value to find silences.

        @param vol_threshold (int) RMS value

        """
        self.vol_threshold = int(vol_threshold)
        if vol_threshold == 0:
            self.auto_vol = True
        else:
            self.auto_vol = False

    # ------------------------------------------------------------------

    def set_min_silence(self, min_sil_dur):
        """
        Fix the default minimum duration of a silence.

        @param min_sil_dur (float) Duration in seconds.

        """
        self.min_sil_dur = float(min_sil_dur)

    # ------------------------------------------------------------------

    def set_min_speech(self, min_ipu_dur):
        """
        Fix the default minimum duration of an IPU.

        @param min_ipu_dur (float) Duration in seconds.

        """
        self.min_ipu_dur = float(min_ipu_dur)

    # ------------------------------------------------------------------

    def set_vol_win_lenght(self, winlength):
        """
        Fix the default windows length for RMS estimations.

        @param winlength (float) Duration in seconds.

        """
        self.win_lenght = max(winlength, 0.005)

    # ------------------------------------------------------------------

    def set_shift(self, s):
        """
        Fix the default minimum boundary shift value.

        @param s (float) Duration in seconds.

        """
        self.shift_start = float(s)
        self.shift_end   = float(s)

    # ------------------------------------------------------------------

    def set_shift_start(self, s):
        """
        Fix the default minimum boundary shift value.

        @param s (float) Duration in seconds.

        """
        self.shift_start = float(s)

    # ------------------------------------------------------------------

    def set_shift_end(self,s):
        """
        Fix the default minimum boundary shift value.

        @param s (float) Duration in seconds.

        """
        self.shift_end = float(s)

    # ------------------------------------------------------------------

    def min_channel_duration(self):
        """
        Return the minimum duration we expect for a channel.

        """
        d1 = self.min_sil_dur+self.shift_start+self.shift_end
        d2 = self.min_ipu_dur+self.shift_start+self.shift_end
        return max(d1,d2)

    # ------------------------------------------------------------------

    def set_bound_start(self, sil=False):
        """
        Fix if it is expected (or not) to find a silence at the beginning of the channel.

        """
        self.bornestart = sil

    # ------------------------------------------------------------------

    def set_bound_end(self, sil=False):
        """
        Fix if it is expected (or not) to find a silence at the end of the channel.

        """
        self.borneend = sil

    # ------------------------------------------------------------------
    # Silence/Speech segmentation
    # ------------------------------------------------------------------

    def extract_tracks(self, min_ipu_dur=None, shift_start=None, shift_end=None):
        """
        Return a list of tuples (from_pos,to_pos) of tracks.
        The tracks are found from the current list of silences.

        @param min_ipu_dur (float) The minimum duration for a track (in seconds)
        @param shiftdurstart (float) The time to remove to the start boundary (in seconds)
        @param shiftdurend (float) The time to add to the end boundary (in seconds)
        @return (list of tuples)

        """
        if self.chansil is None:
            return []

        if min_ipu_dur is None:
            min_ipu_dur=self.min_ipu_dur
        if shift_start is None:
            shift_start=self.shift_start
        if shift_end is None:
            shift_end=self.shift_end

        return self.chansil.extract_tracks(min_ipu_dur, shift_start, shift_end)

    # ------------------------------------------------------------------

    def search_tracks(self, volume):
        """
        Return the tracks if volume is used as threshold.

        """
        if self.chansil is None:
            return []

        self.chansil.search_silences(volume, mintrackdur=IPUsAudio.MIN_IPU_DUR)
        self.chansil.filter_silences(self.min_sil_dur)
        return self.extract_tracks()

    # ------------------------------------------------------------------

    def check_boundaries(self, tracks):
        """
        Check if silences at start and end are as expected.

        @return bool

        """
        if len(tracks) == 0:
            return False
        if self.chansil is None:
            return False

        if self.bornestart is False and self.borneend is False:
            # we do not know anything about silences at start and end
            # then, everything is ALWAYS OK!
            return True

        first_from_pos = tracks[0][0]
        last_to_pos = tracks[len(tracks)-1][1]

        # If I expected a silence at start... and I found a track
        if self.bornestart is True and first_from_pos==0:
            return False

        # If I expected a silence at end... and I found a track
        if self.borneend is True and last_to_pos==self.chansil.get_channel().get_nframes():
            return False

        return True

    # ------------------------------------------------------------------

    def split_into_vol(self, nbtracks):
        """
        Try various volume values to estimate silences then get the expected number of tracks.

        @param nbtracks is the expected number of IPUs
        @return number of tracks

        """
        if self.chansil is None:
            return 0

        volstats = self.chansil.get_volstats()
        # Min volume in the speech
        vmin = volstats.min()
        # Max is set to the mean
        vmax = volstats.mean()
        # Step is necessary to not exaggerate a detailed search!
        # step is set to 5% of the volume between min and mean.
        step = int( (vmax - vmin) / 20.0 )
        # Min and max are adjusted
        vmin += step
        vmax -= step

        # First Test !!!
        self.vol_threshold = vmin
        tracks = self.search_tracks(vmin)
        n = len(tracks)
        b = self.check_boundaries(tracks)

        while (n != nbtracks or b is False):
            # We would never be done anyway.
            if (vmax==vmin) or (vmax-vmin) < step:
                return n

            # Try with the middle volume value
            vmid = int(vmin + (vmax - vmin) / 2.0)
            if n > nbtracks:
                # We split too often. Need to consider less as silence.
                vmax = vmid
            elif n < nbtracks:
                # We split too seldom. Need to consider more as silence.
                vmin = vmid
            else:
                # We did not find start/end silence.
                vmin += step

            # Find silences with these parameters
            self.vol_threshold = int(vmid)
            tracks = self.search_tracks(vmid)
            n = len(tracks)
            b = self.check_boundaries(tracks)

        return n

    # ------------------------------------------------------------------

    def split_into(self, nbtracks):
        """
        Try various volume values, pause durations and silence duration to get silences.

        @param nbtracks is the expected number of IPUs. 0=auto.

        """
        if self.chansil is None:
            raise Exception('No audio data.')

        if self.auto_vol is True:
            self.vol_threshold = self.chansil.search_threshold_vol()

        if nbtracks == 0:
            self.search_tracks( self.vol_threshold )
            return 0

        # Try with default parameters:
        tracks = self.search_tracks( self.vol_threshold )
        n = len(tracks)
        b = self.check_boundaries(tracks)

        if n == nbtracks and b is True:
            return n

        # Try with default lengths (change only volume):
        n = self.split_into_vol( nbtracks )

        if n > nbtracks:

            # We split too often. Try with larger' values.
            while n > nbtracks:
                self.min_sil_dur += self.win_lenght
                self.min_ipu_dur += self.win_lenght
                n = self.split_into_vol( nbtracks )

        elif n < nbtracks:

            # We split too seldom. Try with shorter' values of silences
            p = self.min_sil_dur
            m = self.min_ipu_dur
            while n < nbtracks and self.min_sil_dur > IPUsAudio.MIN_SIL_DUR:
                self.min_sil_dur -= self.win_lenght
                n = self.split_into_vol( nbtracks )

            # we failed... try with shorter' values of ipus
            if n < nbtracks:
                self.min_sil_dur = p
                while n < nbtracks and self.min_ipu_dur > IPUsAudio.MIN_IPU_DUR:
                    self.min_ipu_dur -= self.win_lenght
                    n = self.split_into_vol( nbtracks )

                # we failed... try with shorter' values of both sil/ipus
                if n < nbtracks:
                    self.min_ipu_dur = m
                    while n < nbtracks and self.min_sil_dur > IPUsAudio.MIN_SIL_DUR and self.min_ipu_dur > IPUsAudio.MIN_IPU_DUR:
                        self.min_ipu_dur -= self.win_lenght
                        self.min_sil_dur -= self.win_lenght
                        n = self.split_into_vol( nbtracks )

        return n

    # ------------------------------------------------------------------
