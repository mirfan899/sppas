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
# File: anchors.py
# ----------------------------------------------------------------------------

import logging
from annotationdata import Tier, Annotation, TimeInterval, TimePoint, Label, Text
import audiodata.autils as autils

# --------------------------------------------------------------------------

class AnchorTier( Tier ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Extended Tier allowing to store anchor-annotations.

    This class extends Tier() and allows to store anchors as annotations.
    Two main methods are added:
    1. Append silences;
    2. Fix a flexible time-based window: given a "from-time", it estimates
       the couple ("from-time","to-time") to match the next hole in the tier,
       with a given maximum delay between both values.

    """
    def __init__(self, name="Anchors"):
        """
        Creates a new AnchorTier instance, with default values.

        """
        Tier.__init__(self, name)
        self.reset()

    # ------------------------------------------------------------------------

    def reset(self):
        """
        Fix default values of all members.

        """
        self._duration = 0.

        # For the silence search
        self._winlenght     = 0.020
        self._minsildur     = 0.250
        self._mintrackdur   = 0.300
        self._shiftdurstart = 0.
        self._shiftdurend   = 0.

        # For the windowing
        self._windelay = 4.
        self._extdelay = 1.
        self._outdelay = 0.2

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set_duration(self, duration):
        """
        Set the duration of the tier (in sec.).

        """
        duration = float(duration)
        if duration <= 0.:
            raise Exception("%f is an invalid tier duration."%(duration))

        self._duration = duration

    # ------------------------------------------------------------------------

    def set_windelay(self, delay):
        """
        Set the expected delay for a window.

        """
        delay = float(delay)
        if delay <= self._outdelay:
            raise ValueError("%f is a too short window delay."%(delay))

        self._windelay = delay

    # ------------------------------------------------------------------------

    def set_extdelay(self, delay):
        """
        Set the extra delay that is possible to add for a window.

        """
        delay = float(delay)
        if delay <= 0.:
            raise ValueError("%f is an invalid delay."%(delay))

        self._extdelay = delay

    # ------------------------------------------------------------------------

    def set_outdelay(self, delay):
        """
        Set the minimum delay that is acceptable for a window.

        """
        delay = float(delay)
        if delay <= 0. or delay >= self._windelay:
            raise ValueError("%f is an invalid delay."%(delay))

        self._outdelay = delay

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def append_silences(self, channel):
        """
        Append silences as anchors.

        """
        logging.debug(" ... Search silences:")

        # We have to find tracks first
        trackstimes = autils.search_channel_speech( channel, self._winlenght, self._minsildur, self._mintrackdur, self._shiftdurstart, self._shiftdurend )
        radius = self._winlenght/ 2.
        toprec = 0.

        # Then, the silences are the holes between tracks
        for (fromtime,totime) in trackstimes:
            if toprec < fromtime:
                begin = TimePoint(toprec,radius)
                if begin == 0.:
                    begin = TimePoint(toprec,radius)
                end = TimePoint(fromtime,radius)
                a = Annotation(TimeInterval(begin, end), Label("#"))
                self.Append(a)
            toprec = totime

        # A silence at the end?
        if toprec < self._duration:
            begin = TimePoint(toprec,radius)
            end = TimePoint(self._duration,0.)
            a = Annotation(TimeInterval(begin, end), Label("#"))
            self.Append(a)

        for i,a in enumerate(self):
            logging.debug(" ... ... %i: %s"%(i,a))

    # ------------------------------------------------------------------------

    def fix_window(self, fromtime):
        """
        Return the "totime" corresponding to a flexible-sized window.
        The window aims at covering the holes of the tier. If there is
        no hole after fromtime, this method returns a tuple with
        fromtime=totime.

        if fromtime is inside an anchor:
            fromtime = end-anchor-time

        totime is either:

            - fromtime + begin-of-the-next-anchor
              if there is an anchor in interval [fromtime,fromtime+delay]

            - fromtime + begin-of-the-next-anchor
              if there is an anchor in interval [fromtime,fromtime+delay+margin]
                (this is to ensure that the next window won't be too small)

            - fromtime + delay

        @param fromtime (float) The point in time from which the window has to be found
        @return (fromtime,totime)

        """
        (fromtime,totime) = self._recurs_fix_window(fromtime, self._windelay)

        # take a quick look at the next window... just to be sure it won't be too small
        (nf,nt) = self._recurs_fix_window(totime, self._windelay)
        if nf == fromtime and (nt-nf) < self._windelay:
            totime = nt

        return (fromtime,totime)

    # ------------------------------------------------------------------------

    def check_holes_durations(self, duration):
        """
        Check if all holes have a duration lesser than the given one.

        """
        for i in range(1,self.GetSize()):
            lastend  = self[i-1].GetLocation().GetEnd().GetMidpoint()
            curbegin = self[i].GetLocation().GetBegin().GetMidpoint()
            if (curbegin-lastend) > duration:
                return False

        return True

    # ------------------------------------------------------------------------

    def check_holes_ntokens(self, ntokens):
        """
        Check if indexed-anchors make all holes lesser or equal than ntokens.
        The last one can't be tested.

        """
        if self.GetSize() == 0:
            return False

        fromtoken = 0
        a = self.near_indexed_anchor(0., 1)

        while a is not None:
            totoken = a.GetLabel().GetTypedValue()
            if totoken-fromtoken > ntokens:
                return False
            fromtoken = totoken
            a = self.near_indexed_anchor( a.GetLocation().GetEnd().GetMidpoint(), 1)

        return True

    # ------------------------------------------------------------------------

    def near_indexed_anchor(self, timevalue, direction):
        """
        Search the nearest indexed anchor (an anchor with a positive integer).

        @param time (float)
        @param direction: (int)
                - forward 1
                - backward -1

        """
        if not direction in [1,-1]:
            raise ValueError('Unexpected direction value.')

        valuepoint = TimePoint(timevalue)
        previ = -1
        i = self.Near( valuepoint, direction )
        while i != -1 and i != previ:

            label = self[i].GetLabel()
            content = label.GetTypedValue()

            testinside=False
            if direction == -1 and self[i].GetLocation().GetEnd() > valuepoint:
                testinside = True
            if direction == 1 and self[i].GetLocation().GetBegin() < valuepoint:
                testinside = True

            previ = i
            if label.IsSilence() is True or content < 0 or testinside is True:
                if direction == -1:
                    valuepoint = self[i].GetLocation().GetBegin()
                else:
                    valuepoint = self[i].GetLocation().GetEnd()
                i = self.Near( valuepoint, direction )

        if i == -1:
            return None
        if self[i].GetLabel().IsSilence() is True:
            return None

        return self[i]

    # ------------------------------------------------------------------------

    def fill_evident_holes(self):
        """
        Fill holes if we find consecutive index values in prev/next anchors.

        """
        toadd=[]
        for i in range(1,len(self)):
            prevann = self[i-1]
            curann  = self[i]
            if prevann.GetLabel().IsSilence():
                continue
            if curann.GetLabel().IsSilence():
                continue
            # there is a hole
            if prevann.GetLocation().GetEnd() < curann.GetLocation().GetBegin():
                idxprev = prevann.GetLabel().GetTypedValue()
                idxcur  = curann.GetLabel().GetTypedValue()
                if idxprev+1 == idxcur-1:
                    text = Text( idxprev+1, data_type="int" )
                    hole = Annotation( TimeInterval(prevann.GetLocation().GetEnd(), curann.GetLocation().GetBegin()), Label(text) )
                    toadd.append(hole)

        for a in toadd:
            self.Add(a)

        return len(toadd)

    # ------------------------------------------------------------------------

    def export(self, toklist):
        tier = Tier("TokenizedAnchors")

        # Append silences in the result and pop them from the list of anchors
        anchors = AnchorTier()
        for ann in self:
            if ann.GetLabel().IsSilence():
                try:
                    tier.Append( ann.Copy() )
                except Exception:
                    logging.debug("Error: Silence not appended: %s"%ann)
                    pass
            else:
                try:
                    anchors.Append( ann.Copy() )
                except Exception:
                    logging.debug("Error: Anchor not appended: %s"%ann)
                    pass

        # Fill the holes when prev-index and next-index made a sequence
        anchors.fill_evident_holes()
        for ann in anchors:
            print " --> ",ann

        # Add holes between anchors
        for i in range(1,len(anchors)):
            prevann = anchors[i-1]
            curann  = anchors[i]
            # there is a hole
            if prevann.GetLocation().GetEnd() < curann.GetLocation().GetBegin():
                idxprev = prevann.GetLabel().GetTypedValue()
                idxcur  = curann.GetLabel().GetTypedValue()
                if (idxprev+1) < idxcur-1:
                    texte = " ".join( toklist[idxprev+1:idxcur])
                    begin = prevann.GetLocation().GetEnd()
                    end   = curann.GetLocation().GetBegin()
                    hole = Annotation( TimeInterval(begin,end), Label(texte) )
                    anns = tier.Find( begin, end, overlaps=True )
                    if len(anns) == 0:
                        tier.Add(hole)

        # Append chunk of anchors
        start = 0
        end   = 0
        tocontinue = True
        if end+1 >= anchors.GetSize():
            tocontinue = False

        while tocontinue:

            idxcur = anchors[end].GetLabel().GetTypedValue()
            idxnex = anchors[end+1].GetLabel().GetTypedValue()

            # we finished a sequence of anchors
            if idxcur+1 != idxnex or (end-start)>10:
                # append the chunk
                idxstart = anchors[start].GetLabel().GetTypedValue()
                chunktext = " ".join( toklist[ idxstart:idxcur+1 ] )
                tbegin = anchors[start].GetLocation().GetBegin()
                tend   = anchors[end].GetLocation().GetEnd()
                ann = Annotation( TimeInterval(tbegin,tend), Label(chunktext) )

                tier.Remove(tbegin,tend,overlaps=True)
                tier.Add( ann )

                start = end + 1

            end = end + 1

            if end+1 >= anchors.GetSize():
                # the last chunk found
                if start <= end:
                    idxstart = anchors[start].GetLabel().GetTypedValue()
                    idxcur = anchors[end].GetLabel().GetTypedValue()

                    chunktext = " ".join( toklist[ idxstart:idxcur+1 ] )
                    tbegin = anchors[start].GetLocation().GetBegin()
                    tend   = anchors[end].GetLocation().GetEnd()
                    ann = Annotation( TimeInterval(tbegin,tend), Label(chunktext) )

                    tier.Remove(tbegin,tend,overlaps=True)
                    tier.Add( ann )

                tocontinue = False

        return tier

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _recurs_fix_window(self, fromtime, delay=4.):
        """
        Recursive method to fix a window.

        @param fromtime (float) The point in time from which the window has to be found
        @param delay (float) Expected duration of the window
        @return (fromtime,totime)

        """
        # The totime value corresponding to a full window
        totime = min(fromtime + delay, self._duration)

        if self.GetSize() == 0:
            return (fromtime,totime)

        # Main stop condition: we reach the end of the tier.
        if fromtime >= self._duration:
            return (self._duration,self._duration)

        # Do we have already anchors between fromtime and totime?
        anns = self.Find( fromtime, totime, overlaps=True )
        if len(anns)>0 and fromtime == anns[0].GetLocation().GetEnd().GetMidpoint():
            anns.pop(0)

        if len(anns)>0:

            # fromtime is perhaps INSIDE an anchor or at the beginning of an anchor.
            if fromtime >= anns[0].GetLocation().GetBegin().GetMidpoint():
                fromtime = anns[0].GetLocation().GetEnd().GetMidpoint()
                if totime < self._duration:
                    return self._recurs_fix_window( fromtime, delay )
            else:
                totime = anns[0].GetLocation().GetBegin().GetMidpoint()
                if fromtime == totime:
                    totime = anns[0].GetLocation().GetEnd().GetMidpoint()

        if (totime-fromtime) < self._outdelay:
            fromtime = totime
            return self._recurs_fix_window( fromtime, delay )

        return (fromtime,totime)

# ------------------------------------------------------------------
