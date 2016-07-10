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
    @summary:      Tier with a windowing method.

    """
    def __init__(self, name="Anchors"):
        """
        Creates a new SegmentsIn instance.

        """
        Tier.__init__(self, name)
        self._windelay = 4.
        self._extdelay = 1.
        self._outdelay = 0.2
        self._duration = 0.

    # ------------------------------------------------------------------------

    def append_silences(self, channel):
        """
        Append silences as anchors.

        @return the duration of speech in the channel

        """
        logging.debug(" ... Search silences:")

        trackstimes = autils.search_channel_speech( channel )
        radius = 0.005
        toprec = 0.
        for (fromtime,totime) in trackstimes:
            # From the previous track to the current track: silence
            if toprec < fromtime:
                begin = toprec
                end   = fromtime
                a     = Annotation(TimeInterval(TimePoint(begin,radius), TimePoint(end,radius)), Label("#"))
                self.Append(a)
            toprec = totime
        if self.GetSize()>0:
            self[-1].GetLocation().SetEndRadius(0.)
            self[0].GetLocation().SetBeginRadius(0.)

        for i,a in enumerate(self):
            logging.debug(" ... ... %i: %s"%(i,a))

        return sum( [(e-s) for (s,e) in trackstimes] )

    # ------------------------------------------------------------------------

    def set_windelay(self, delay):
        delay = float(delay)
        if delay <= self._outdelay:
            raise ValueError("%f is a too short window delay."%(delay))

        self._windelay = delay


    # ------------------------------------------------------------------------

    def set_duration(self, duration):
        duration = float(duration)
        self._duration = duration

    # ------------------------------------------------------------------------

    def fix_window(self, fromtime):
        """
        Return the "totime" corresponding to a flexible-sized window.

        if fromtime inside an anchor:
            fromtime = end-anchor-time

        totime is either:

            - fromtime + begin-of-the-next-anchor
              if there is an anchor in interval [fromtime,fromtime+delay]

            - fromtime + begin-of-the-next-anchor
              if there is an anchor in interval [fromtime,fromtime+delay+margin]
                (this is to ensure that the next window won't be too small)

            - fromtime + delay

        """
        (fromtime,totime) = self._recurs_fix_window(fromtime, self._windelay)

        # take a quick look at the next window... just to be sure it won't be too small
        (nf,nt) = self._recurs_fix_window(totime, self._windelay)
        if (nt-nf) < self._windelay:
            totime = nt

        return (fromtime,totime)

    # ------------------------------------------------------------------------

    def _recurs_fix_window(self, fromtime, delay=4.):
        """
        Recursive method to fix a window.

        """
        print "FROMTIME=",fromtime
        # The totime corresponding to a full window
        totime = min(fromtime + delay, self._duration)

        print "EXPCTED TOTIME=",totime

        if self.GetSize() == 0:
            print "FIRST WINDOW. return ",fromtime,totime
            return (fromtime,totime)

        # Main stop condition: we reach the end of the tier.
        if fromtime >= self._duration:
            return (self._duration,self._duration)

        # Do we have already anchors between fromtime and totime?
        anns = self.Find( fromtime, totime, overlaps=True )
        if len(anns)>0 and fromtime == anns[0].GetLocation().GetEnd().GetMidpoint():
            anns.pop(0)

        if len(anns)>0:

            print "FOUND ANNS",anns[0]

            # fromtime is perhaps INSIDE an anchor or at the beginning of an anchor.
            if fromtime >= anns[0].GetLocation().GetBegin().GetMidpoint():
                fromtime = anns[0].GetLocation().GetEnd().GetMidpoint()
                print "  FROMTIME =",fromtime
                if totime < self._duration:
                    print "  --> next round"
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
