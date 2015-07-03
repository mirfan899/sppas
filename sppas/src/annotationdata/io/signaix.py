#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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

from annotationdata.pitch import Pitch
from annotationdata.label.label import Label
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation


class HzPitch(Pitch):

    __delta = 0.01

    def __init__(self):
        Pitch.__init__(self)

    # End __init__
    # -----------------------------------------------------------------

    @staticmethod
    def detect(filename):
        with open(filename, "r") as pitchfile:
            for line in pitchfile:
                try:
                    float(line)
                except ValueError:
                    return False
        return True

    # End detect
    # -----------------------------------------------------------------

    def read(self, filename):
        """
        Read pitch values from an ascii file (one column)
        and set a value each 0.01 ms.

        """
        with open(filename, "r") as pitchfile:
            try:
                tier = self.NewTier("Pitch")
                tier.SetDataType("int")
                self._tier = tier

                # The reference time point of each interval is the middle
                timeref = HzPitch.__delta/2.  # Start time
                for line in pitchfile:
                    tier.Append(Annotation(TimePoint(timeref,
                                                     HzPitch.__delta/2.),
                                           Label(float(line), 'float')))
                    timeref = timeref + HzPitch.__delta
            finally:
                self.SetMinTime(0)
                self.SetMaxTime(self.GetEnd())

    # End read
    # -----------------------------------------------------------------

    def write(self, filename):
        """
        Write a .hz file.

        @param filename: is the output file name

        """
        with open(filename, "w", buffering=8096) as fp:
            __pitcharray = self.get_pitch_list()
            for i in range(len(__pitcharray)):
                fp.write("%f\n" % __pitcharray[i])

    # End write
    # -----------------------------------------------------------------
