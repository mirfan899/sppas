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
import logging

from sppas.src.annotationdata import Tier
from sppas.src.annotationdata import Annotation
from sppas.src.annotationdata import TimeInterval
from sppas.src.annotationdata import TimePoint
from sppas.src.annotationdata import Label
from sppas.src.annotationdata import Text

import sppas.src.audiodata.autils as autils

# --------------------------------------------------------------------------


class AnchorTier(Tier):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Extended Tier allowing to store anchor-annotations.

    This class extends Tier() and allows to store anchors as annotations.
    Two main methods are added:
    1. Append silences;
    2. Fix a flexible time-based window: given a "from-time", it estimates
       the couple ("from-time","to-time") to match the next hole in the tier,
       with a given maximum delay between both values.

    """
    def __init__(self, name="Anchors"):
        """Creates a new AnchorTier instance, with default values.

        :param name: (str) Name of the anchors tier
        
        """
        Tier.__init__(self, name)

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
    # ------------------------------------------------------------------------

    def set_duration(self, duration):
        """Set the duration of the tier.

        :param duration: (float) Duration in seconds.

        """
        duration = float(duration)
        if duration <= 0.:
            raise Exception("%f is an invalid tier duration." % duration)

        self._duration = duration

    # ------------------------------------------------------------------------

    def set_win_delay(self, delay):
        """Set the expected delay for a window.

        :param delay: (float)

        """
        delay = float(delay)
        if delay <= self._out_delay:
            raise ValueError("%f is a too short window delay." % delay)

        self._win_delay = delay

    # ------------------------------------------------------------------------

    def set_ext_delay(self, delay):
        """Set the extra delay that is possible to add for a window.

        :param delay: (float)

        """
        delay = float(delay)
        if delay <= 0.:
            raise ValueError("%f is an invalid delay." % delay)

        self._ext_delay = delay

    # ------------------------------------------------------------------------

    def set_out_delay(self, delay):
        """Set the minimum delay that is acceptable for a window.

        :param delay: (float)

        """
        delay = float(delay)
        if delay <= 0. or delay >= self._win_delay:
            raise ValueError("%f is an invalid delay." % delay)

        self._out_delay = delay

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def append_silences(self, channel):
        """Append silences as anchors.

        :param channel: (sppasChannel)

        """
        logging.debug(" ... Search silences:")

        # We have to find tracks first
        tracks_times = autils.search_channel_speech(channel,
                                                    self._win_length,
                                                    self._min_sil_dur,
                                                    self._min_track_dur,
                                                    self._shift_dur_start,
                                                    self._shift_dur_end)
        radius = self._win_length / 2.
        toprec = 0.

        # Then, the silences are the holes between tracks
        for (from_time, to_time) in tracks_times:
            if toprec < from_time:
                begin = TimePoint(toprec, radius)
                if begin == 0.:
                    begin = TimePoint(toprec, radius)
                end = TimePoint(from_time, radius)
                a = Annotation(TimeInterval(begin, end), Label("#"))
                self.Append(a)
            toprec = to_time

        # A silence at the end?
        if toprec < self._duration:
            begin = TimePoint(toprec, radius)
            end = TimePoint(self._duration, 0.)
            a = Annotation(TimeInterval(begin, end), Label("#"))
            self.Append(a)

        for i, a in enumerate(self):
            logging.debug(" ... ... %i: %s" % (i, a))

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
              if there is an anchor in interval [from_time, from_time+delay+margin]
                (this is to ensure that the next window won't be too small)

            - from_time + delay

        :param from_time: (float) The point in time from which the window has to be found
        :returns: a tuple with (from_time, to_time)

        """
        from_time, to_time = self._recurs_fix_window(from_time, self._win_delay)

        # take a quick look at the next window... just to be sure it won't be too small
        nf, nt = self._recurs_fix_window(to_time, self._win_delay)
        if nf == from_time and (nt-nf) < self._win_delay:
            to_time = nt

        return from_time, to_time

    # ------------------------------------------------------------------------

    def check_holes_durations(self, duration):
        """Check if all holes have a duration lesser than the given one.

        :param duration: (float)

        """
        for i in range(1, self.GetSize()):
            last_end = self[i-1].GetLocation().GetEnd().GetMidpoint()
            cur_begin = self[i].GetLocation().GetBegin().GetMidpoint()
            if (cur_begin-last_end) > duration:
                return False

        return True

    # ------------------------------------------------------------------------

    def check_holes_ntokens(self, ntokens):
        """Check if indexed-anchors make all holes lesser or equal than ntokens.
        The last one can't be tested.

        :param ntokens: (int)

        """
        if self.GetSize() == 0:
            return False

        from_token = 0
        a = self.near_indexed_anchor(0., 1)

        while a is not None:
            to_token = a.GetLabel().GetTypedValue()
            if to_token-from_token > ntokens:
                return False
            from_token = to_token
            a = self.near_indexed_anchor(a.GetLocation().GetEnd().GetMidpoint(), 1)

        return True

    # ------------------------------------------------------------------------

    def near_indexed_anchor(self, time_value, direction):
        """Search the nearest indexed anchor (an anchor with a positive integer).

        :param time_value: (float)
        :param direction: (int)
                - forward 1
                - backward -1

        """
        if direction not in [1, -1]:
            raise ValueError('Unexpected direction value.')

        value_point = TimePoint(time_value)
        previ = -1
        i = self.Near(value_point, direction)
        while i != -1 and i != previ:

            label = self[i].GetLabel()
            content = label.GetTypedValue()

            test_inside = False
            if direction == -1 and self[i].GetLocation().GetEnd() > value_point:
                test_inside = True
            if direction == 1 and self[i].GetLocation().GetBegin() < value_point:
                test_inside = True

            previ = i
            if label.IsSilence() is True or content < 0 or test_inside is True:
                if direction == -1:
                    value_point = self[i].GetLocation().GetBegin()
                else:
                    value_point = self[i].GetLocation().GetEnd()
                i = self.Near(value_point, direction)

        if i == -1:
            return None
        if self[i].GetLabel().IsSilence() is True:
            return None

        return self[i]

    # ------------------------------------------------------------------------

    def fill_evident_holes(self):
        """Fill holes if we find consecutive index values in prev/next anchors."""

        to_add = []

        for i in range(1, len(self)):
            prevann = self[i-1]
            curann = self[i]
            if prevann.GetLabel().IsSilence():
                continue
            if curann.GetLabel().IsSilence():
                continue
            # there is a hole
            if prevann.GetLocation().GetEnd() < curann.GetLocation().GetBegin():
                idxprev = prevann.GetLabel().GetTypedValue()
                idxcur = curann.GetLabel().GetTypedValue()
                prevend = prevann.GetLocation().GetEnd()
                curbegin = curann.GetLocation().GetBegin()
                if idxprev+1 == idxcur-1:
                    text = Text(idxprev+1, data_type="int")
                    hole = Annotation(TimeInterval(prevend, curbegin), Label(text))
                    to_add.append(hole)

        for a in to_add:
            self.Add(a)

        return len(to_add)

    # ------------------------------------------------------------------------

    def export(self, toklist):
        """Create the "Chunks" tier and return it.

        :param toklist: Tokens used to fill the intervals.

        """
        tier = Tier("Chunks")

        # Append silences in the result and pop them from the list of anchors
        anchors = AnchorTier()
        for ann in self:
            if ann.GetLabel().IsSilence():
                try:
                    tier.Append(ann.Copy())
                except Exception:
                    logging.debug("Error: Silence not appended: %s" % ann)
                    pass
            else:
                try:
                    anchors.Append(ann.Copy())
                except Exception:
                    logging.debug("Error: Anchor not appended: %s" % ann)
                    pass

        # Fill the holes when prev-index and next-index made a sequence
        anchors.fill_evident_holes()

        # Fill holes between anchors
        for i in range(1, len(anchors)):
            prevann = anchors[i-1]
            curann = anchors[i]
            # there is a hole
            if prevann.GetLocation().GetEnd() < curann.GetLocation().GetBegin():

                idxprev = prevann.GetLabel().GetTypedValue()
                idxcur = curann.GetLabel().GetTypedValue()
                prevend = prevann.GetLocation().GetEnd()
                curbegin = curann.GetLocation().GetBegin()

                if idxprev+1 == idxcur:
                    # hum... a little bit of hack!!!
                    holeduration = curbegin.GetMidpoint()-prevend.GetMidpoint()
                    if holeduration < 0.055:
                        prevend.SetMidpoint(curbegin.GetMidpoint())
                    elif holeduration < 0.505 and prevann.GetLocation().GetDuration().GetValue() < 0.105:
                        prevend.SetMidpoint(curbegin.GetMidpoint())

                elif (idxprev+1) < idxcur-1:
                    texte = " ".join(toklist[idxprev+1:idxcur])
                    begin = prevend.GetMidpoint()
                    end = curbegin.GetMidpoint()
                    hole = Annotation(TimeInterval(TimePoint(begin), TimePoint(end)), Label(texte))
                    anns = tier.Find(begin, end, overlaps=True)
                    if len(anns) == 0:
                        try:
                            tier.Add(hole)
                        except Exception:
                            pass

        # Append chunk of anchors
        start = 0
        end = 0
        to_continue = True
        if end+1 >= anchors.GetSize():
            to_continue = False

        while to_continue:

            idxcur = anchors[end].GetLabel().GetTypedValue()
            idxnex = anchors[end+1].GetLabel().GetTypedValue()
            endtimecur = anchors[end].GetLocation().GetEnd()
            begtimenex = anchors[end+1].GetLocation().GetBegin()

            # a sequence of anchors is finished if either:
            #  - next anchor index does not directly follow the current one
            #  - next anchor time does not directly follow the current one
            #  - we already appended enough anchors in the chunk

            if idxcur+1 != idxnex or (end-start) > 10 or begtimenex > endtimecur:
                # append the chunk
                idxstart = anchors[start].GetLabel().GetTypedValue()
                chunk_text = " ".join(toklist[idxstart:idxcur+1])
                tbegin = anchors[start].GetLocation().GetBegin()
                tend = anchors[end].GetLocation().GetEnd()
                ann = Annotation(TimeInterval(tbegin, tend), Label(chunk_text))

                tier.Remove(tbegin, tend, overlaps=True)
                tier.Add(ann)

                start = end + 1

            end += 1

            if anchors.GetSize() <= end+1:
                # the last chunk found
                if start <= end:
                    idxstart = anchors[start].GetLabel().GetTypedValue()
                    idxcur = anchors[end].GetLabel().GetTypedValue()

                    chunk_text = " ".join(toklist[idxstart:idxcur+1])
                    tbegin = anchors[start].GetLocation().GetBegin()
                    tend = anchors[end].GetLocation().GetEnd()
                    ann = Annotation(TimeInterval(tbegin, tend), Label(chunk_text))

                    tier.Remove(tbegin, tend, overlaps=True)
                    tier.Add(ann)

                to_continue = False

        # Begin of the tier
        fi = anchors[0].GetLabel().GetTypedValue()
        ft = tier[0].GetLocation().GetBegin()
        at = anchors[0].GetLocation().GetBegin()
        if ft == 0.:
            # a silence to start
            ft = tier[0].GetLocation().GetEnd()
        else:
            ft = TimePoint(0.)
        if fi > 0 and ft < at:
            chunk_text = " ".join(toklist[0:fi])
            ann = Annotation(TimeInterval(ft, at), Label(chunk_text))
            tier.Add(ann)

        # End of the tier
        fi = anchors[-1].GetLabel().GetTypedValue()
        fi += 1
        ft = tier[-1].GetLocation().GetEnd()
        at = anchors[-1].GetLocation().GetEnd()
        if ft == self._duration:
            # a silence to end
            ft = tier[-1].GetLocation().GetBegin()
        else:
            ft = TimePoint(self._duration)
        if fi < len(toklist) and at < ft:
            chunk_text = " ".join(toklist[fi+1:len(toklist)])
            ann = Annotation(TimeInterval(at, ft), Label(chunk_text))
            tier.Add(ann)

        chunk_tier = Tier("Chunks")
        i = 1
        while i < tier.GetSize():

            prevtext = tier[i-1].GetLabel().GetValue()
            curtext = tier[i].GetLabel().GetValue()
            newtext = prevtext + " " + curtext

            if tier[i-1].GetLabel().IsSilence() is False and \
                    tier[i].GetLabel().IsSilence() is False and \
                    (len(prevtext.split()) < 3 or len(newtext.split()) < 12):
                a = Annotation(TimeInterval(tier[i-1].GetLocation().GetBegin(), tier[i].GetLocation().GetEnd()), Label(newtext))
                chunk_tier.Append(a)
                i += 1
            else:
                chunk_tier.Append(tier[i-1])

            i += 1

        return chunk_tier

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _recurs_fix_window(self, from_time, delay=4.):
        """Recursive method to fix a window.

        :param from_time: (float) The point in time from which the window has to be found
        :param delay: (float) Expected duration of the window
        :returns: (from_time,to_time)

        """
        # The to_time value corresponding to a full window
        to_time = min(from_time + delay, self._duration)

        if self.GetSize() == 0:
            return from_time, to_time

        # Main stop condition: we reach the end of the tier.
        if from_time >= self._duration:
            return self._duration, self._duration

        # Do we have already anchors between from_time and to_time?
        anns = self.Find(from_time, to_time, overlaps=True)
        if len(anns) > 0 and from_time == anns[0].GetLocation().GetEnd().GetMidpoint():
            anns.pop(0)

        if len(anns) > 0:

            # from_time is perhaps INSIDE an anchor or at the beginning of an anchor.
            if from_time >= anns[0].GetLocation().GetBegin().GetMidpoint():
                from_time = anns[0].GetLocation().GetEnd().GetMidpoint()
                if from_time < self._duration:
                    return self._recurs_fix_window(from_time, delay)
            else:
                to_time = anns[0].GetLocation().GetBegin().GetMidpoint()
                if from_time == to_time:
                    to_time = anns[0].GetLocation().GetEnd().GetMidpoint()

        if (to_time-from_time) < self._out_delay:
            from_time = to_time
            return self._recurs_fix_window(from_time, delay)

        return from_time, to_time
