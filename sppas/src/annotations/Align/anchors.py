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

from annotationdata.tier import Tier

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
        self._windelay = 3.
        self._outdelay = 0.2

    # ------------------------------------------------------------------------

    def set_windelay(self, delay):
        delay = float(delay)
        if delay <= self._outdelay:
            raise ValueError("%f is a too short window delay."%(delay))

        self._windelay = delay

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
        (fromtime,totime) = self._fix_window(fromtime, self._windelay)

        extendeddelay = self._windelay + self._windelay/3.
        (nf,nt) = self._fix_window(fromtime, extendeddelay)
        if (nt-nf) < extendeddelay:
            totime = nt

        return (fromtime,totime)

    # ------------------------------------------------------------------------

    def _fix_window(self, fromtime, delay=4.):
        """
        Recursive method to fix a window.

        """
        # The totime corresponding to a full window
        totime = fromtime + delay

        # Main stop condition: we reach the end of the tier.
        if fromtime >= self.GetEnd():
            return (self.GetEnd().GetMidpoint(),self.GetEnd().GetMidpoint())

        # Do we have already anchors between fromtime and totime?
        anns = self.Find( fromtime, totime, overlaps=True )
        if len(anns)>0:

            # fromtime is perhaps INSIDE an anchor or at the beginning of an anchor.
            if fromtime >= anns[0].GetLocation().GetBegin().GetMidpoint():
                return self._fix_window( anns[0].GetLocation().GetEnd().GetMidpoint(), delay )
            else:
                totime = anns[0].GetLocation().GetBegin().GetMidpoint()
                if fromtime == totime:
                    totime = anns[0].GetLocation().GetEnd().GetMidpoint()

        if (totime-fromtime) < self._outdelay:
            fromtime = totime
            return self._fix_window( fromtime, delay )

        return (fromtime,totime)

# ------------------------------------------------------------------
