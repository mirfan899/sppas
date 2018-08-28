# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.annotations.ipusaudio.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Silence/speech automatic segmentation system.

"""
from sppas.src.audiodata.channelsilence import sppasChannelSilence

# ---------------------------------------------------------------------------


class IPUsAudio(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      An automatic silence/speech segmentation system.

    Silence/speech segmentation aims at finding IPUs.
    IPUs - Inter-Pausal Units are blocks of speech bounded by silent pauses
    of more than X ms, and time-aligned on the speech signal.

    """
    MIN_SIL_DUR = 0.08
    MIN_IPU_DUR = 0.08
    DEFAULT_MIN_SIL_DUR = 0.250
    DEFAULT_MIN_IPU_DUR = 0.300
    DEFAULT_VOL_THRESHOLD = 0

    def __init__(self, channel):
        """Creates a new IPUsAudio instance.

        :param channel: (audiodata.Channel)
        
        """
        super(IPUsAudio, self).__init__()
        
        self._min_sil_dur = IPUsAudio.DEFAULT_MIN_SIL_DUR
        self._min_ipu_dur = IPUsAudio.DEFAULT_MIN_IPU_DUR
        self._vol_threshold = IPUsAudio.DEFAULT_VOL_THRESHOLD
        self._win_length = 0.020
        self._shift_start = 0.010
        self._shift_end = 0.020
        self._auto_vol = True
        self._sil_at_start = False
        self._sil_at_end = False

        self._channel_sil = None
        self.set_channel(channel)

    # ------------------------------------------------------------------
    # Manage Channel
    # ------------------------------------------------------------------

    def get_track_data(self, tracks):
        """Return the audio data of tracks. 
        
        :param tracks: List of tracks. A track is a tuple (start, end).
        :returns: List of audio data
        
        """
        return self._channel_sil.track_data(tracks)

    # ------------------------------------------------------------------

    def get_channel(self):
        """Return the channel."""
        
        return self._channel_sil.get_channel()

    # ------------------------------------------------------------------

    def set_channel(self, channel):
        """Set a new Channel.

        :param channel: (audiodata.Channel)
        
        """
        if channel is not None:
            self._channel_sil = sppasChannelSilence(channel, self._win_length)
        else:
            self._channel_sil = None

    # ------------------------------------------------------------------

    def reset_silences(self):
        """Reset the list of silences."""
        
        if self._channel_sil is not None:
            self._channel_sil.reset_silences()

    # ------------------------------------------------------------------

    def set_silences(self, silences):
        """Fix the list of silences.

        :param silences: List of tuples (from_pos, to_pos)

        """
        if self._channel_sil is not None:
            self._channel_sil.set_silences(silences)

    # ------------------------------------------------------------------
    # Getters for members
    # ------------------------------------------------------------------

    def get_win_length(self):
        """Return the windows length used to estimate the RMS."""
        return self._win_length

    def get_vol_threshold(self):
        """Return the volume threshold used to find silences vs tracks."""
        return self._vol_threshold

    def get_min_sil_dur(self):
        """Return the minimum duration of a silence."""
        return self._min_sil_dur

    def get_min_ipu_dur(self):
        """Return the minimum duration of a track."""
        return self._min_ipu_dur

    # ------------------------------------------------------------------
    # Setters for members
    # ------------------------------------------------------------------

    def set_vol_threshold(self, vol_threshold):
        """Fix the default minimum volume value to find silences.

        :param vol_threshold: (int) RMS value

        """
        self._vol_threshold = int(vol_threshold)
        if self._vol_threshold < 0:
            self._vol_threshold = IPUsAudio.DEFAULT_VOL_THRESHOLD
        if vol_threshold == 0:
            self._auto_vol = True
        else:
            self._auto_vol = False

    # ------------------------------------------------------------------

    def set_min_silence(self, min_sil_dur):
        """Fix the default minimum duration of a silence.

        :param min_sil_dur: (float) Duration in seconds.

        """
        self._min_sil_dur = float(min_sil_dur)
        if self._min_sil_dur < 0.02:
            self._min_sil_dur = IPUsAudio.DEFAULT_MIN_SIL_DUR

    # ------------------------------------------------------------------

    def set_min_speech(self, min_ipu_dur):
        """Fix the default minimum duration of an IPU.

        :param min_ipu_dur: (float) Duration in seconds.

        """
        self._min_ipu_dur = float(min_ipu_dur)
        if self._min_ipu_dur < 0.02:
            IPUsAudio.DEFAULT_MIN_IPU_DUR

    # ------------------------------------------------------------------

    def set_vol_win_length(self, win_length):
        """Fix the default windows length for RMS estimations.

        :param win_length: (float) Duration in seconds.

        """
        self._win_length = max(win_length, 0.005)

    # ------------------------------------------------------------------

    def set_shift(self, s):
        """Fix the default minimum boundary shift value for start and end.

        :param s: (float) Duration in seconds.

        """
        self.set_shift_start(s)
        self.set_shift_end(s)

    # ------------------------------------------------------------------

    def set_shift_start(self, s):
        """Fix the default minimum boundary shift value.

        :param s: (float) Duration in seconds.

        """
        s = float(s)
        if -self._min_ipu_dur < s < self._min_sil_dur:
            self._shift_start = s

    # ------------------------------------------------------------------

    def set_shift_end(self, s):
        """Fix the default minimum boundary shift value.

        :param s: (float) Duration in seconds.

        """
        s = float(s)
        if -self._min_ipu_dur < s < self._min_sil_dur:
            self._shift_end = s

    # ------------------------------------------------------------------

    def min_channel_duration(self):
        """Return the minimum duration we expect for a channel."""

        d = max(self._min_sil_dur, self._min_ipu_dur)
        return d + self._shift_start + self._shift_end

    # ------------------------------------------------------------------

    def set_bound_start(self, expect_sil=False):
        """Set if it is expected (or not) to find a silence at the
        beginning of the channel.

        :param expect_sil: (bool)

        """
        self._sil_at_start = expect_sil

    # ------------------------------------------------------------------

    def set_bound_end(self, expect_sil=False):
        """Set if it is expected (or not) to find a silence at the end
        of the channel.

        :param expect_sil: (bool)

        """
        self._sil_at_end = expect_sil

    # ------------------------------------------------------------------
    # Silence/Speech segmentation
    # ------------------------------------------------------------------

    def extract_tracks(self, min_ipu_dur=None, shift_start=None, shift_end=None):
        """Return a list of tuples (from_pos,to_pos) of tracks.
        The tracks are found from the current list of silences.

        :param min_ipu_dur: (float) The minimum duration for a track (in seconds)
        :param shift_start: (float) The time to remove to the start boundary (in seconds)
        :param shift_end: (float) The time to add to the end boundary (in seconds)
        :returns: (list of tuples) Return a list of tuples (from_pos,to_pos) of the tracks.

        """
        if self._channel_sil is None:
            return []

        if min_ipu_dur is None:
            min_ipu_dur = self._min_ipu_dur
        if shift_start is None:
            shift_start = self._shift_start
        if shift_end is None:
            shift_end = self._shift_end

        return self._channel_sil.extract_tracks(min_ipu_dur, shift_start, shift_end)

    # ------------------------------------------------------------------

    def search_tracks(self, volume):
        """Search the tracks if the given volume is used as threshold.

        :param volume: (int) RMS threshold value (0=auto)
        :returns: (list of tuples) Return a list of tuples (from_pos,to_pos) of the tracks.

        """
        if self._channel_sil is None:
            return []

        self._channel_sil.search_silences(volume, mintrackdur=IPUsAudio.MIN_IPU_DUR)
        self._channel_sil.filter_silences(self._min_sil_dur)
        return self.extract_tracks()

    # ------------------------------------------------------------------

    def check_boundaries(self, tracks):
        """Check if silences at start and end are as expected.

        :param tracks:
        :returns: (bool)

        """
        if len(tracks) == 0:
            return False
        if self._channel_sil is None:
            return False

        if self._sil_at_start is False and self._sil_at_end is False:
            # we do not know anything about silences at start and end
            # then, everything is ALWAYS OK!
            return True

        first_from_pos = tracks[0][0]
        last_to_pos = tracks[len(tracks)-1][1]

        # If I expected a silence at start... and I've found a track
        if self._sil_at_start is True and first_from_pos == 0:
            return False

        # If I expected a silence at end... and I've found a track
        if self._sil_at_end is True and last_to_pos == self._channel_sil.get_channel().get_nframes():
            return False

        return True

    # ------------------------------------------------------------------

    def split_into_vol(self, nb_tracks):
        """Try various volume values to estimate silences then get the
        expected number of tracks.

        :param nb_tracks: (int) the expected number of tracks
        :returns: number of tracks found

        """
        if self._channel_sil is None:
            return 0

        volstats = self._channel_sil.get_volstats()
        # Min volume in the speech
        vmin = volstats.min()
        # Max is set to the mean
        vmax = volstats.mean()
        # Step is necessary to not exaggerate a detailed search!
        # step is set to 5% of the volume between min and mean.
        step = int((vmax - vmin) / 20.0)
        # Min and max are adjusted
        vmin += step
        vmax -= step

        # First Test !!!
        self._vol_threshold = vmin
        tracks = self.search_tracks(vmin)
        n = len(tracks)
        b = self.check_boundaries(tracks)

        while n != nb_tracks or b is False:
            # We would never be done anyway.
            if (vmax == vmin) or (vmax-vmin) < step:
                return n

            # Try with the middle volume value
            vmid = int(vmin + (vmax - vmin) / 2.0)
            if n > nb_tracks:
                # We split too often. Need to consider less as silence.
                vmax = vmid
            elif n < nb_tracks:
                # We split too seldom. Need to consider more as silence.
                vmin = vmid
            else:
                # We did not find start/end silence.
                vmin += step

            # Find silences with these parameters
            self._vol_threshold = int(vmid)
            tracks = self.search_tracks(vmid)
            n = len(tracks)
            b = self.check_boundaries(tracks)

        return n

    # ------------------------------------------------------------------

    def split_into(self, nb_tracks=0):
        """Try various volume values, pause durations and silence
        duration to get silences.

        :param nb_tracks: (int) the expected number of IPUs. 0=auto.

        """
        if self._channel_sil is None:
            raise Exception('No audio data.')

        if self._auto_vol is True:
            self._vol_threshold = self._channel_sil.search_threshold_vol()

        if nb_tracks == 0:
            self.search_tracks(self._vol_threshold)
            return 0

        # Try with default parameters:
        tracks = self.search_tracks(self._vol_threshold)
        n = len(tracks)
        b = self.check_boundaries(tracks)

        if n == nb_tracks and b is True:
            return n

        # Try with default lengths (change only volume):
        n = self.split_into_vol(nb_tracks)

        if n > nb_tracks:

            # We split too often. Try with larger' values.
            while n > nb_tracks:
                self._min_sil_dur += self._win_length
                self._min_ipu_dur += self._win_length
                n = self.split_into_vol(nb_tracks)

        elif n < nb_tracks:

            # We split too seldom. Try with shorter' values of silences
            p = self._min_sil_dur
            m = self._min_ipu_dur
            while n < nb_tracks and self._min_sil_dur > IPUsAudio.MIN_SIL_DUR:
                self._min_sil_dur -= self._win_length
                n = self.split_into_vol(nb_tracks)

            # we failed... try with shorter' values of ipus
            if n < nb_tracks:
                self._min_sil_dur = p
                while n < nb_tracks and self._min_ipu_dur > IPUsAudio.MIN_IPU_DUR:
                    self._min_ipu_dur -= self._win_length
                    n = self.split_into_vol(nb_tracks)

                # we failed... try with shorter' values of both sil/ipus
                if n < nb_tracks:
                    self._min_ipu_dur = m
                    while n < nb_tracks and \
                            self._min_sil_dur > IPUsAudio.MIN_SIL_DUR and \
                            self._min_ipu_dur > IPUsAudio.MIN_IPU_DUR:
                        self._min_ipu_dur -= self._win_length
                        self._min_sil_dur -= self._win_length
                        n = self.split_into_vol(nb_tracks)

        return n
