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
# File: basevolume.py
# ---------------------------------------------------------------------------

import calculus.stats.central      as central
import calculus.stats.variability  as variability
import calculus.stats.moment       as moment

# ---------------------------------------------------------------------------

class BaseVolume( object ):
    """
    @authors:      Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      A class to estimates stats of the volume of an audio channel.

    The volume is the estimation of RMS values, sampled with a window of 10ms.

    """
    def __init__(self):
        """
        Constructor.

        """
        self.volumes = []
        self.rms     = 0
        self.winlen  = 0.01

    # -----------------------------------------------------------------------

    def get_winlen(self):
        """
        Return the windows length that was used to estimate the volume values.

        """
        return self.winlen

    # -----------------------------------------------------------------------

    def volume(self):
        """
        Return the global volume value (rms).
        @return (int)

        """
        return self.rms

    # -----------------------------------------------------------------------

    def volume_at(self, index):
        """
        Return the value of the volume at a given index (rms).
        @return (int)

        """
        return self.volumes[index]

    # -----------------------------------------------------------------------

    def volumes(self):
        """
        Return the list of volume values (rms).
        @return (int)

        """
        return self.volumes

    # -----------------------------------------------------------------------

    def len(self):
        """
        Return the number of RMS values that were estimated.
        @return (int)

        """
        return len(self.volumes)

    # -----------------------------------------------------------------------

    def min(self):
        """
        Returns the minimum of RMS values.
        @return (int)

        """
        return central.fmin(self.volumes)

    # -----------------------------------------------------------------------

    def max(self):
        """
        Returns the maximum of RMS values.
        @return (int)

        """
        return central.fmax(self.volumes)

    # -----------------------------------------------------------------------

    def mean(self):
        """
        Returns the mean of RMS values.
        @return (float)

        """
        return central.fmean(self.volumes)

    # -----------------------------------------------------------------------

    def median(self):
        """
        Returns the median of RMS values.
        @return (float)

        """
        return central.fmedian(self.volumes)

    # -----------------------------------------------------------------------

    def variance(self):
        """
        Returns the sample variance of RMS values.
        @return (int)

        """
        return variability.lvariance(self.volumes)

    # -----------------------------------------------------------------------

    def stdev(self):
        """
        Returns the standard deviation of RMS values.
        @return (int)

        """
        return variability.lstdev(self.volumes)

    # -----------------------------------------------------------------------

    def coefvariation(self):
        """
        Returns the coefficient of variation of RMS values (given as a percentage).
        @return (float)

        """
        return moment.lvariation(self.volumes)

    # -----------------------------------------------------------------------

    def zscores(self):
        """
        Returns the z-scores of RMS values.
        The z-score determines the relative location of a data value.
        @return (list of float)

        """
        return variability.lzs(self.volumes)

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.volumes)

    # ------------------------------------------------------------------------------------

    def __iter__(self):
        for x in self.volumes:
            yield x

    # ------------------------------------------------------------------------------------

    def __getitem__(self, i):
        return self.volumes[i]

    # ------------------------------------------------------------------------

