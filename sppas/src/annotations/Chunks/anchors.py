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

    src.annotations.Chuncks.anchors.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import sys
import logging

from sppas.src.config import symbols

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

import sppas.src.audiodata.autils as autils

# ---------------------------------------------------------------------------

SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]

# ---------------------------------------------------------------------------


class AnchorTier(sppasTier):
    """Extended Tier allowing to store anchor-annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    This class extends sppasTier() and allows to store anchors as annotations.
    Two main methods are added:
    1. Append silences;
    2. Fix a flexible time-based window: given a "from-time", it estimates
       the couple ("from-time", "to-time") to match the next hole in the 
       tier, with a given maximum delay between both values.

    """

    # int value of a silence tag
    SIL = sys.maxsize

    def __init__(self, name="Anchors"):
        """Create a new AnchorTier instance, with default values.

        :param name: (str) Name of the anchors tier
        
        """
        super(AnchorTier, self).__init__(name)

        self._duration = 0.

        # For the silence search
        self._win_length = 0.020
        self._min_sil_dur = 0.250
        self._min_track_dur = 0.300
        self._shift_dur_start = 0.
        self._shift_dur_end = 0.

        # For the windowing
        self._win_delay = 4.
        self._ext_delay = 1.
        self._out_delay = 0.2

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_win_delay(self):
        return self._win_delay

    # ------------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_duration(self, duration):
        """Set the duration of the tier.

        :param duration: (float) Duration in seconds.

        """
        duration = float(duration)
        if duration <= 0.:
            raise Exception("{:f} is an invalid tier duration."
                            "".format(duration))

        self._duration = duration

    # -----------------------------------------------------------------------

    def set_win_delay(self, delay):
        """Set the expected delay for a window.

        :param delay: (float)

        """
        delay = float(delay)
        if delay <= self._out_delay:
            raise ValueError("{:f} is a too short window delay."
                             "".format(delay))

        self._win_delay = delay

    # -----------------------------------------------------------------------

    def set_ext_delay(self, delay):
        """Set the extra delay that is possible to add for a window.

        :param delay: (float)

        """
        delay = float(delay)
        if delay <= 0.:
            raise ValueError("{:f} is an invalid delay.".format(delay))

        self._ext_delay = delay

    # -----------------------------------------------------------------------

    def set_out_delay(self, delay):
        """Set the minimum delay that is acceptable for a window.

        :param delay: (float)

        """
        delay = float(delay)
        if delay <= 0. or delay >= self._win_delay:
            raise ValueError("{:f} is an invalid delay.".format(delay))

        self._out_delay = delay

    # -----------------------------------------------------------------------
    # Workers
    # -----------------------------------------------------------------------

    def append_silences(self, channel):
        """Append silences as anchors.

        :param channel: (sppasChannel)

        """
        logging.debug(" ... Search for silences:")

        # We have to find tracks first
        tracks_times = autils.search_channel_speech(channel,
                                                    self._win_length,
                                                    self._min_sil_dur,
                                                    self._min_track_dur,
                                                    self._shift_dur_start,
                                                    self._shift_dur_end)
        radius = self._win_length / 2.
        to_prec = 0.

        # Silences are the holes between the tracks
        for (from_time, to_time) in tracks_times:
            if to_prec < from_time:
                begin = sppasPoint(to_prec, radius)
                if begin == 0.:
                    begin = sppasPoint(to_prec)
                end = sppasPoint(from_time, radius)
                self.create_annotation(
                    sppasLocation(sppasInterval(begin, end)),
                    sppasLabel(sppasTag(SIL_ORTHO)))
            to_prec = to_time

        # A silence at the end?
        if to_prec < self._duration:
            begin = sppasPoint(to_prec, radius)
            end = sppasPoint(self._duration, 0.)
            self.create_annotation(
                sppasLocation(sppasInterval(begin, end)),
                sppasLabel(sppasTag(AnchorTier.SIL, "int")))

        for i, a in enumerate(self):
            logging.debug(" ... ... {:d}: {:s}".format(i, a))

    # ------------------------------------------------------------------------

    def fix_window(self, from_time):
        """Return the "to_time" corresponding to a flexible-sized window.

        The window aims at covering the holes of the tier. If there is
        no hole after from_time, this method returns a tuple with
        from_time=to_time.

        if from_time is inside an anchor:
            from_time = end-anchor-time

        to_time is either:

            - from_time + begin-of-the-next-anchor
              if there is an anchor in interval [from_time, from_time+delay]

            - from_time + begin-of-the-next-anchor
              if there is an anchor in interval [from_time, 
              from_time+delay+margin] (this is to ensure that the next window
              won't be too small)

            - from_time + delay

        :param from_time: (float) The point in time from which the window 
        has to be found
        :returns: a tuple with (from_time, to_time)

        """
        from_time, to_time = self._recurs_fix_window(from_time, 
                                                     self._win_delay)

        # take a quick look at the next window... 
        # just to be sure it won't be too small
        nf, nt = self._recurs_fix_window(to_time, self._win_delay)
        if nf == from_time and (nt-nf) < self._win_delay:
            to_time = nt

        return from_time, to_time

    # -----------------------------------------------------------------------

    def check_holes_durations(self, duration):
        """Check if all holes have a duration lesser than the given one.

        :param duration: (float)

        """
        for i in range(1, len(self)):
            last_end = self[i-1].get_highest_localization().get_midpoint()
            cur_begin = self[i].get_lowest_localization().get_midpoint()
            if (cur_begin-last_end) > duration:
                return False

        return True

    # ------------------------------------------------------------------------

    def check_holes_ntokens(self, ntokens):
        """Check if indexed-anchors make all holes lesser-or-eq than ntokens.
        
        The last one can't be tested.

        :param ntokens: (int)

        """
        if self.is_empty() is True:
            return False

        from_token = 0
        a = self.near_indexed_anchor(0., 1)

        while a is not None:
            to_token = a.get_best_tag().get_typed_content()
            if to_token-from_token > ntokens:
                return False
            from_token = to_token
            a = self.near_indexed_anchor(
                a.get_highest_localization().get_midpoint(), 1)

        return True

    # ------------------------------------------------------------------------

    def near_indexed_anchor(self, time_value, direction):
        """Search for the nearest indexed anchor.
        
        Search for the next anchor with a positive integer value.

        :param time_value: (float)
        :param direction: (int)
                - forward 1
                - backward -1

        """
        direction = int(direction)
        if direction not in (1, -1):
            raise ValueError('Unexpected direction value {:d}.'
                             ''.format(direction))

        value_point = sppasPoint(time_value)
        previ = -1
        i = self.near(value_point, direction)

        while i != -1 and i != previ:

            tag = self[i].get_best_tag()
            content = tag.get_typed_content()

            test_inside = False
            if direction == -1 and \
                    self[i].get_highest_localization() > value_point:
                test_inside = True
            if direction == 1 and \
                    self[i].get_lowest_localization() < value_point:
                test_inside = True

            previ = i
            if tag.get_typed_content() == AnchorTier.SIL or \
                    content < 0 or \
                    test_inside is True:
                if direction == -1:
                    value_point = self[i].get_lowest_localization()
                else:
                    value_point = self[i].get_highest_localization()
                i = self.near(value_point, direction)

        if i == -1:
            return None
        if self[i].get_best_tag().get_typed_content() == AnchorTier.SIL:
            return None

        return self[i]

    # -----------------------------------------------------------------------

    def fill_evident_holes(self):
        """Fill all holes that are between two consecutive index values.

        Example:
            - annotation A_x has the index 18, at time [t1, t2]
            - annotation A_z has the index 20, at time [t3, t4]; (t3 > t2).

        The hole between A_x and A_z will be filled by annotation A_z with
        the index 19 at time [t2, t3].

        :returns: (int) Number of filled holes

        """
        to_add = []

        for i in range(1, len(self)):
            prev_ann = self[i-1]
            cur_ann = self[i]

            # if previous or current annotation is a silence: nothing to do.
            if prev_ann.get_best_tag().get_typed_content() == AnchorTier.SIL:
                continue
            if cur_ann.get_best_tag().get_typed_content() == AnchorTier.SIL:
                continue

            # if there is a hole
            if prev_ann.get_highest_localization() < \
                    cur_ann.get_lowest_localization():
                idx_prev = prev_ann.get_best_tag().get_typed_content()
                idx_cur = cur_ann.get_best_tag().get_typed_content()
                prev_end = prev_ann.get_highest_localization()
                cur_begin = cur_ann.get_lowest_localization()
                if idx_prev + 1 == idx_cur - 1:
                    hole = sppasAnnotation(
                        sppasLocation(sppasInterval(prev_end, cur_begin)),
                        sppasLabel(sppasTag(idx_prev + 1, "int")))
                    to_add.append(hole)

        for a in to_add:
            self.add(a)

        return len(to_add)

    # -----------------------------------------------------------------------

    def export(self, toklist):
        """Create the "Chunks" tier and return it.

        :param toklist: Tokens used to fill the intervals.

        """
        chunck_tier = sppasTier("Chunks")

        # Append silences in the result and pop them from the list of anchors
        anchors = AnchorTier()
        for ann in self:
            if ann.get_best_tag().get_typed_content() == AnchorTier.SIL:
                try:
                    chunck_tier.create_annotation(
                        ann.get_location().copy(),
                        sppasLabel(sppasTag(SIL_ORTHO))   
                    )
                except:
                    logging.debug("Error: silence not appended: {:s}"
                                  "".format(ann))
                    pass
            else:
                try:
                    anchors.append(ann.copy())
                except:
                    logging.debug("Error: Anchor not appended: {:s}"
                                  "".format(ann))
                    pass

        # Fill the holes when prev-index and next-index made a sequence
        anchors.fill_evident_holes()

        # Fill holes between anchors
        for i in range(1, len(anchors)):
            prevann = anchors[i-1]
            curann = anchors[i]
            # there is a hole
            if prevann.get_highest_localization() < \
                    curann.get_lowest_localization():

                idxprev = prevann.get_best_tag().get_typed_content()
                idxcur = curann.get_best_tag().get_typed_content()
                prevend = prevann.get_highest_localization()
                curbegin = curann.get_lowest_localization()

                if idxprev+1 == idxcur:
                    # hum... a little bit of hack!!!
                    hole_duration = curbegin.get_midpoint()-prevend.get_midpoint()
                    if hole_duration < 0.055:
                        prevend.set_midpoint(curbegin.get_midpoint())
                    elif hole_duration < 0.505 and\
                            prevann.get_location().get_best().duration().get_value() < 0.105:
                        prevend.set_midpoint(curbegin.get_midpoint())

                elif (idxprev+1) < idxcur-1:
                    texte = " ".join(toklist[idxprev+1:idxcur])
                    begin = prevend.get_midpoint()
                    end = curbegin.get_midpoint()
                    hole = sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(begin), sppasPoint(end))), 
                        sppasLabel(sppasTag(texte)))
                    anns = chunck_tier.find(begin, end, overlaps=True)
                    if len(anns) == 0:
                        try:
                            chunck_tier.add(hole)
                        except:
                            pass

        # Append chunk of anchors
        start = 0
        end = 0
        to_continue = True
        if end+1 >= len(anchors):
            to_continue = False

        while to_continue:

            idxcur = anchors[end].get_best_tag().get_typed_content()
            idxnex = anchors[end+1].get_best_tag().get_typed_content()
            endtimecur = anchors[end].get_highest_localization()
            begtimenex = anchors[end+1].get_lowest_localization()

            # a sequence of anchors is finished if either:
            #  - next anchor index does not directly follow the current one
            #  - next anchor time does not directly follow the current one
            #  - we already appended enough anchors in the chunk

            if idxcur+1 != idxnex or (end-start) > 10 or begtimenex > endtimecur:
                # append the chunk
                idxstart = anchors[start].get_best_tag().get_typed_content()
                chunk_text = " ".join(toklist[idxstart:idxcur+1])
                tbegin = anchors[start].get_lowest_localization()
                tend = anchors[end].get_highest_localization()
                ann = sppasAnnotation(
                    sppasLocation(sppasInterval(tbegin, tend)), 
                    sppasLabel(sppasTag(chunk_text)))

                chunck_tier.remove(tbegin, tend, overlaps=True)
                chunck_tier.add(ann)

                start = end + 1

            end += 1

            if len(anchors) <= end+1:
                # the last chunk found
                if start <= end:
                    idxstart = anchors[start].get_best_tag().get_typed_content()
                    idxcur = anchors[end].get_best_tag().get_typed_content()

                    chunk_text = " ".join(toklist[idxstart:idxcur+1])
                    tbegin = anchors[start].get_lowest_localization()
                    tend = anchors[end].get_highest_localization()
                    ann = sppasAnnotation(
                        sppasLocation(sppasInterval(tbegin, tend)),
                        sppasLabel(sppasTag(chunk_text)))

                    chunck_tier.remove(tbegin, tend, overlaps=True)
                    chunck_tier.add(ann)

                to_continue = False

        # Begin of the tier
        fi = anchors[0].get_best_tag().get_typed_content()
        ft = chunck_tier[0].get_lowest_localization()
        at = anchors[0].get_lowest_localization()
        if ft == 0.:
            # a silence to start
            ft = chunck_tier[0].get_highest_localization()
        else:
            ft = sppasPoint(0.)
        if fi > 0 and ft < at:
            chunk_text = " ".join(toklist[0:fi])
            chunck_tier.create_annotation(
                sppasLocation(sppasInterval(ft, at)), 
                sppasLabel(sppasTag(chunk_text))
            )

        # End of the tier
        fi = anchors[-1].get_best_tag().get_typed_content()
        fi += 1
        ft = chunck_tier[-1].get_highest_localization()
        at = anchors[-1].get_highest_localization()
        if ft == self._duration:
            # a silence to end
            ft = chunck_tier[-1].get_lowest_localization()
        else:
            ft = sppasPoint(self._duration)
        if fi < len(toklist) and at < ft:
            chunk_text = " ".join(toklist[fi+1:len(toklist)])
            chunck_tier.create_annotation(
                sppasLocation(sppasInterval(at, ft)), 
                sppasLabel(sppasTag(chunk_text))
            )

        final_chunck_tier = sppasTier("Chunks")
        i = 1
        while i < len(chunck_tier):

            prevtext = chunck_tier[i-1].get_best_tag().get_content()
            curtext = chunck_tier[i].get_best_tag().get_content()
            newtext = prevtext + " " + curtext

            if chunck_tier[i-1].get_best_tag().is_silence() is False and \
                    chunck_tier[i].get_best_tag().is_silence() is False and \
                    (len(prevtext.split()) < 3 or len(newtext.split()) < 12):
                final_chunck_tier.create_annotation(
                    sppasLocation(sppasInterval(chunck_tier[i-1].get_lowest_localization(),
                                                chunck_tier[i].get_highest_localization())),
                    sppasLabel(sppasTag(newtext))
                )
                i += 1
            else:
                final_chunck_tier.append(chunck_tier[i-1])

            i += 1

        return final_chunck_tier

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _recurs_fix_window(self, from_time, delay=4.):
        """Recursive method to fix a window.

        :param from_time: (float) The point in time from which the window
        has to be found
        :param delay: (float) Expected duration of the window
        :returns: (from_time,to_time)

        """
        # The to_time value corresponding to a full window
        to_time = min(from_time + delay, self._duration)

        if len(self) == 0:
            return from_time, to_time

        # Main stop condition: we reach the end of the tier.
        if from_time >= self._duration:
            return self._duration, self._duration

        # Do we have already anchors between from_time and to_time?
        anns = self.find(from_time, to_time, overlaps=True)
        if len(anns) > 0 and from_time == anns[0].get_highest_localization().get_midpoint():
            anns.pop(0)

        if len(anns) > 0:

            # from_time is perhaps INSIDE an anchor or at the beginning of an anchor.
            if from_time >= anns[0].get_lowest_localization().get_midpoint():
                from_time = anns[0].get_highest_localization().get_midpoint()
                if from_time < self._duration:
                    return self._recurs_fix_window(from_time, delay)
            else:
                to_time = anns[0].get_lowest_localization().get_midpoint()
                if from_time == to_time:
                    to_time = anns[0].get_highest_localization().get_midpoint()

        if (to_time-from_time) < self._out_delay:
            from_time = to_time
            return self._recurs_fix_window(from_time, delay)

        return from_time, to_time
