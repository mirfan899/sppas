#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.

from .transcription import Transcription
from .tier import Tier


class Pitch(Transcription):
    """
    Represents a Transcription with pitch values.
    """
    def __init__(self,
                 name="Pitch",
                 delta=0.01,
                 mintime=0., maxtime=0.):

        """
        Creates a new Pitch Tier instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)

    # ------------------------------------------------------------------------------------

    def Set(self, trs, name="empty"):
        """
        Set a transcription.

        @param trs: (Transcription)

        """
        if isinstance(trs, Transcription) is False:
            raise TypeError("Transcription argument required, not %s" % trs)

        if trs.IsEmpty():
            self._tiers = []
            self._tier = Tier(data_type="int")
        else:
            tiers = [tier.Copy() for tier in trs]
            self._tiers = tiers
            self._tier = self._tiers[0]

    # ------------------------------------------------------------------------------------

    def __add_points_affine(self, array, delta,
                            time1, pitch1,
                            time2, pitch2):
        """ add_points_affine
            Definition:
            On appelle fonction affine la relation qui,
            à tout nombre x, associe le nombre y tel que :
            y = mx + p
            Une fonction affine est definie par son coefficient
            m et le nombre p.
            Pour une fonction affine donnee, l’accroissement des images
            (c’est-à-dire la difference entre deux images) est
            proportionnel à l’accroissement des antecedents correspondants
            suivant le coefficient m.
            Par consequent, il suffit de connaître les images y1 et y2
            de deux nombres x1 et x2 par une fonction affine pour
            pouvoir determiner la valeur du coefficient m :
            m =  y2 − y1 / x2 − x1
            On peut ensuite en deduire la valeur de p, et donc
            l’expression generale de la fonction affine.
        """
        # Timesep is rounded to milliseconds
        timesep = round(time2-time1, 3)
        # A too long time between 2 values. Pitch is set to zero.
        if timesep > 0.02:
            m = 0
            p = 0
        else:
            # affine function parameters
            m = (pitch2-pitch1) / timesep
            p = pitch1 - (m * time1)
        # number of values to add in the time interval
        steps = int(timesep/delta)
        # then, add values:
        for step in range(1, steps):
            if steps > 3:
                x = (step*delta) + time1
                y = (m * x) + p
            else:
                y = 0.
            array.append(y)

    # ------------------------------------------------------------------------------------

    def __add_points_linear(self, array, delta,
                            time1, pitch, time2):
        """
        Add_points linear.
        """
        # Timesep is rounded to milliseconds
        timesep = round(time2-time1, 3)
        # A too long time between 2 values. Pitch is set to zero.
        if timesep > 0.02:
            p = 0
        else:
            p = pitch
        # number of values to add in the time interval
        steps = int(timesep/delta)
        # then, add values:
        for step in range(1, steps):
            array.append(p)

    # ------------------------------------------------------------------------------------

    def get_pitch_list(self, delta=0.01):
        """
        Return a list of pitch values from the pitch tier.

        @param delta:

        """
        pitch = []
        # Get the number of pitch values of the tier
        if self._tier.IsEmpty():
            raise Exception("Empty pitch transcription.")

        # From time=0 to the first pitch value, pitch is 0.
        time1 = float(self._tier[0].GetLocation().GetPointMidpoint())
        pitch1 = float(self._tier[0].GetLabel().GetValue())
        steps = int(time1/delta) - 1
        for step in range(steps):
            pitch.append(0)

        for annotation in self._tier[1:]:
            time2 = annotation.GetLocation().GetPointMidpoint()
            pitch2 = float(annotation.GetLabel().GetValue())
            pitch.append(pitch1)
            self.__add_points_affine(pitch, delta,
                                     time1, pitch1,
                                     time2, pitch2)
            time1 = time2
            pitch1 = pitch2
        pitch.append(pitch2)

        return pitch
        self._tier = Tier(data_type="int")

    # ------------------------------------------------------------------------------------
