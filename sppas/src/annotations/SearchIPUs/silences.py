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

    src.annotations.SeachIPUs.silences.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
from sppas.src.audiodata.channel import sppasChannel
from sppas.src.audiodata.channelvolume import sppasChannelVolume

# ---------------------------------------------------------------------------


class sppasSilences(object):
    """Silence search on a channel of an audio file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Silences are stored in a list of (from_pos,to_pos) values, indicating
    the frame from which the silences are beginning and ending respectively.

    """

    def __init__(self, channel, win_len=0.020, vagueness=0.005):
        """Create a sppasSilences instance.

        :param channel: (sppasChannel) the input channel
        :param win_len: (float) duration of a window
        :param vagueness: (float) Windows length to estimate the boundaries.

        Maximum value of vagueness is win_len.
        The duration of a window (win_len) is relevant for the estimation
        of the rms values.

        Radius (see sppasPoint) is the 2*vagueness of the boundaries.

        """
        self._win_len = win_len
        self._vagueness = vagueness

        self._channel = None
        self.__volume_stats = None
        self.__silences = list()
        if channel is not None:
            self.set_channel(channel)

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_vagueness(self, vagueness):
        """Windows length to estimate the boundaries.

        :param vagueness: (float) Maximum value of radius is win_len.

        """
        self._vagueness = min(vagueness, self._win_len)

    # -----------------------------------------------------------------------

    def get_vagueness(self):
        """Get the vagueness value (=2*radius)."""
        return self._vagueness

    # -----------------------------------------------------------------------

    def set_channel(self, channel):
        """Set a channel, then reset all previous results.

        :param channel: (sppasChannel)

        """
        if isinstance(channel, sppasChannel) is False:
            raise TypeError('Expected a sppasChannel, got {:s} instead'
                            ''.format(str(type(channel))))

        self._channel = channel
        self.__volume_stats = sppasChannelVolume(channel, self._win_len)
        self.__silences = list()

    # -----------------------------------------------------------------------

    def get_volstats(self):
        """Return the sppasChannelVolume() estimated on the channel."""
        return self.__volume_stats

    # -----------------------------------------------------------------------

    def set_silences(self, silences):
        """Fix manually silences.

        To be use carefully!

        :param silences: (list of tuples (start_pos, end_pos))

        """
        # check if it's really a list of tuples
        if isinstance(silences, list) is False:
            raise TypeError('Expected a list, got {:s}'
                            ''.format(type(silences)))
        for v in silences:
            v[0] = int(v[0])
            v[1] = int(v[1])

        # ok, assign value
        self.__silences = silences

    # -----------------------------------------------------------------------

    def reset_silences(self):
        """Reset silences to an empty list."""
        self.__silences = list()

    # -----------------------------------------------------------------------
    # Utility methods for tracks
    # -----------------------------------------------------------------------

    def track_data(self, tracks):
        """Yield the track data: a set of frames for each track.

        :param tracks: (list of tuples) List of (from_pos,to_pos)

        """
        if self._channel is None:
            return

        nframes = self._channel.get_nframes()
        for from_pos, to_pos in tracks:
            if nframes < from_pos:
                # Accept a "DELTA" of 10 frames, in case of corrupted data.
                if nframes < from_pos-10:
                    raise ValueError("Position {:d} not in range({:d})"
                                     "".format(from_pos, nframes))
                else:
                    from_pos = nframes

            # Go to the provided position
            self._channel.seek(from_pos)
            # Keep in mind the related frames
            yield self._channel.get_frames(to_pos - from_pos)

    # -----------------------------------------------------------------------

    def extract_tracks(self, min_track_dur, shift_dur_start, shift_dur_end):
        """Return the tracks, deduced from the silences and track constrains.

        :param min_track_dur: (float) The minimum duration for a track
        :param shift_dur_start: (float) The time to remove to the start bound
        :param shift_dur_end: (float) The time to add to the end boundary
        :returns: list of tuples (from_pos,to_pos)

        Duration is in seconds.

        """
        if self._channel is None:
            return []

        tracks = list()

        # No silence: Only one track!
        if len(self.__silences) == 0:
            tracks.append((0, self._channel.get_nframes()))
            return tracks

        # Convert values from time to frames
        delta = int(min_track_dur * self._channel.get_framerate())
        shift_start = int(shift_dur_start * self._channel.get_framerate())
        shift_end = int(shift_dur_end * self._channel.get_framerate())
        from_pos = 0

        for to_pos, next_from in self.__silences:

            if (to_pos-from_pos) >= delta:
                # Track is long enough to be considered an IPU.
                # Apply the shift values
                shift_from_pos = max(from_pos - shift_start, 0)
                shift_to_pos = min(to_pos + shift_end,
                                   self._channel.get_nframes())
                # Store as it
                tracks.append((int(shift_from_pos), int(shift_to_pos)))

            from_pos = next_from

        # Last track after the last silence
        # (if the silence does not end at the end of the channel)
        to_pos = self._channel.get_nframes()
        if (to_pos - from_pos) >= delta:
            tracks.append((int(from_pos), int(to_pos)))

        return tracks

    # -----------------------------------------------------------------------
    # Silence detection
    # -----------------------------------------------------------------------

    def fix_threshold_vol(self):
        """Fix the threshold for tracks/silences segmentation.

        This is an observation of the distribution of rms values.

        :returns: (int) volume value

        """
        vmin = max(self.__volume_stats.min(), 0)  # provide negative values
        logging.debug("RMS min={:d}".format(vmin))
        vmax = self.__volume_stats.max()
        logging.debug("RMS max={:d}".format(vmax))
        vmean = self.__volume_stats.mean()
        logging.debug("RMS mean={:.2f}".format(vmean))
        vmedian = self.__volume_stats.median()
        logging.debug("RMS median={:2f}".format(vmedian))
        vvar = self.__volume_stats.coefvariation()
        logging.debug("RMS coef. var={:2f}".format(vvar))

        # Remove very high volume values
        volumes = sorted(self.__volume_stats.volumes())
        index = 0.80*len(volumes)

        rms_threshold = volumes[int(index)]
        nb = 0
        for i, v in enumerate(self.__volume_stats):
            if v > rms_threshold:
                self.__volume_stats.set_volume_value(i, rms_threshold)
                nb += 1

        vmin = max(self.__volume_stats.min(), 0)  # provide negative values
        vmean = self.__volume_stats.mean()
        vmedian = self.__volume_stats.median()
        vvar = self.__volume_stats.coefvariation()
        vcvar = 2. * vvar

        # alternative, in case the audio is not as good as expected!
        # (too low volume, or outliers which make the coeff var very high)
        if vmedian > vmean:
            # often means a lot of low volume values
            index = 0.50 * len(volumes)
            threshold = vmin + volumes[int(index)]
        elif vcvar > vmean:
            if vvar > vmean:
                # often means some crazy values
                threshold = (vmean-vmin) / 5.
            else:
                threshold = int(vmin) + int((vmean - vvar))
        else:
            threshold = int(vmin) + int((vmean - vcvar))

        logging.debug('Threshold value for the search of silences: {:d}'
                      ''.format(threshold))
        return threshold

    # -----------------------------------------------------------------------

    def search_silences(self, threshold=0):
        """Search windows with a volume lesser than a given threshold.

        This is then a search for silences. All windows with a volume
        higher than the threshold are considered as tracks and not included
        in the result. Block of silences lesser than min_sil_dur are
        also considered tracks.

        :param threshold: (int) Expected minimum volume (rms value)
        If threshold is set to 0, search_minvol() will assign a value.
        :returns: threshold

        """
        if self._channel is None:
            return 0

        if threshold == 0:
            threshold = self.fix_threshold_vol()

        # This scans the volumes whether it is lower than threshold,
        # and if true, it is written to silence.
        self.__silences = list()
        inside = False  # inside a silence or not
        idx_begin = 0
        nframes = self.__volume_stats.get_winlen() * \
                    self._channel.get_framerate()

        i = 0
        for v in self.__volume_stats:
            if v < threshold:
                # It's a small enough volume to consider the window a silence
                if inside is False:
                    # We consider it like the beginning of a block of silences
                    idx_begin = i
                    inside = True
                # else: it's the continuation of a silence

            else:
                # It's a big enough volume to consider the window an IPU
                if inside is True:
                    # It's the first window of an IPU
                    # so it's the end of a silence
                    idx_end = i - 1

                    # # Adjust the boundary for the beginning of the silence
                    # from_pos_sil = int(idx_begin * nframes)
                    # from_pos = self.__adjust_bound(from_pos_sil, threshold, direction=-1)
                    #
                    # # For the end of the silence
                    # to_pos = int(idx_end * nframes)
                    # new_to_pos = self.__adjust_bound(to_pos, threshold, direction=1)
                    # if new_to_pos > to_pos:
                    #     d = float(new_to_pos - to_pos) / \
                    #         float(self._channel.get_framerate())
                    #     increment = math.ceil(
                    #         d / self.__volume_stats.get_winlen())
                    #     i += int(increment)
                    # to_pos = new_to_pos

                    self.__silences.append((int(idx_begin * nframes),
                                            int(idx_end * nframes)))
                    inside = False

                # else: it's the continuation of an IPU

            i += 1

        # Last interval
        if inside is True:
            start_pos = int(idx_begin *
                            self.__volume_stats.get_winlen() *
                            self._channel.get_framerate())
            end_pos = self._channel.get_nframes()
            self.__silences.append((start_pos, end_pos))

        return threshold

    # -----------------------------------------------------------------------

    def filter_silences(self, threshold, min_sil_dur=0.200):
        """Filter the current silences.

        :param threshold: (int) Expected minimum volume (rms value)
        If threshold is set to 0, search_minvol() will assign a value.
        :param min_sil_dur: (float) Minimum silence duration in seconds
        :returns: Number of silences with the expected minimum duration

        """
        if len(self.__silences) == 0:
            return 0
        if threshold == 0:
            threshold = self.fix_threshold_vol()

        # self.__silences = self.__filter_silences(self.__silences, min_sil_dur)
        # return len(self.__silences)

        # Filter the current very small silences
        reduced = min_sil_dur / 2.
        reduced = max(reduced, 2. * self._win_len)
        filtered_sil = self.__filter_silences(self.__silences, reduced)

        # Adjust boundaries of the silences
        adjusted = list()
        for (from_pos, to_pos) in filtered_sil:
            new_from_pos = self.__adjust_bound(from_pos, threshold, direction=-1)
            new_to_pos = self.__adjust_bound(to_pos, threshold, direction=1)
            adjusted.append((new_from_pos, new_to_pos))

        # Re-filter
        self.__silences = self.__filter_silences(adjusted, min_sil_dur)

        return len(self.__silences)

    # -----------------------------------------------------------------------

    def __filter_silences(self, silences, min_sil_dur=0.200):
        """Filter the given silences.

        :param min_sil_dur: (float) Minimum silence duration in seconds
        :returns: filtered silences

        """
        filtered_sil = list()
        for (start_pos, end_pos) in silences:
            sil_dur = float(end_pos-start_pos) / \
                      float(self._channel.get_framerate())
            if sil_dur > min_sil_dur:
                filtered_sil.append((start_pos, end_pos))

        return filtered_sil

    # -----------------------------------------------------------------------

    def __adjust_bound(self, pos, threshold, direction=0):
        """Adjust the position of a silence around a given position.

        Here "around" the position means in a range of 18 windows,
        i.e. 6 before + 12 after the position.

        :param pos: (int) Initial position of the silence
        :param threshold: (int) RMS threshold value for a silence
        :param direction: (int)

        :returns: new position

        """
        if self._vagueness == self._win_len:
            return pos
        if direction not in (-1, 1):
            return pos
        c = 0.5
        if direction == 1:
            c = 3

        # Extract the frames of the windows around the pos
        delta = int(c * self.__volume_stats.get_winlen() * self._channel.get_framerate())
        start_pos = int(max(pos - delta, 0))
        self._channel.seek(start_pos)
        frames = self._channel.get_frames(int(delta * 3))

        # Create a channel and estimate volume values with a window
        # of vagueness (i.e. 4 times more precise than the original)
        c = sppasChannel(self._channel.get_framerate(),
                         self._channel.get_sampwidth(),
                         frames)
        vol_stats = sppasChannelVolume(c, self._vagueness)

        # we'll see if we can reduce the silence

        if direction == 1:  # silence | ipu
            for idx, v in enumerate(vol_stats):
                shift = idx * (int(self._vagueness * self._channel.get_framerate()))
                if v > threshold:
                    return start_pos + int(shift)

        elif direction == -1:  # ipu | silence
            idx = len(vol_stats)  # = 12 (3 windows of 4 vagueness)
            for v in reversed(vol_stats):
                # if idx < 4: we shifted left
                # if idx > 4: we shifted right (the most frequent)
                if v > threshold:
                    shift = idx * (int(self._vagueness * self._channel.get_framerate()))
                    return start_pos + int(shift)

                idx -= 1

        return pos

    # -----------------------------------------------------------------------
    # overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__silences)

    def __iter__(self):
        for x in self.__silences:
            yield x

    def __getitem__(self, i):
        return self.__silences[i]
