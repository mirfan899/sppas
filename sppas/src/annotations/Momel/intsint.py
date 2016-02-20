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
# File: intsint.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Tatsuya Watanabe, Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import os
import sys
import getopt
import math

from annotationdata.tier import Tier
from annotationdata.annotation import Annotation
from annotationdata.label.label import Label
from annotationdata.ptime.point import TimePoint


class Intsint(object):
    """
    Provide optimal INTSINT coding for sequence of target points.
    """
    ################################
    # parameters for data checking.#
    ################################
    MIN_F0 = 60   # (Hz)
    MAX_F0 = 600  # (Hz)
    ###############################
    # parameters for optimisation.#
    ###############################
    MIN_PAUSE = 0.5   # seconds
    MIN_RANGE = 0.5   # octaves
    MAX_RANGE = 2.5   # octaves
    STEP_RANGE = 0.1  # octaves
    MEAN_SHIFT = 50   # (Hz)
    STEP_SHIFT = 1    # (Hz)
    BIG_NUMBER = 9999
    ####################################
    # parameters for target estimation.#
    ####################################
    HIGHER = 0.5
    LOWER  = 0.5
    UP     = 0.25
    DOWN   = 0.25
    ##########################
    # a set of tonal symbols.#
    ##########################
    TONES = ("M", "S", "T", "B", "H", "L", "U", "D")

    def __init__(self, momel):
        """
        Create a new Intsint instance.
        Parameters:
            - momel contains a set of target points, with the corresponding f0 value.
        Return a Tier with Intsint coding.
        """
        self.best_intsint = None
        self.best_estimate = None
        self.intsint = []
        self.estimates = []
        self.target_points = []

        self.mid = 0
        self.top = 0
        self.bottom = 0
        self.last_estimate = 0

        self.best_mid = 0
        self.best_range = 0
        self.min_mean = 0
        self.max_mean = 0
        self.min_ss_error = 0

        self.init_intsint(momel)


    def octave(self, value):
        return math.log(value) / math.log(2)


    def linear(self, value):
        return 2 ** value


    def _round(self, value):
        return int(value + 0.5)


    def init_intsint(self, momel):
        """
        Initialize Intsint attributes.
        Parameters:
            - momel contains a set of target points, with the corresponding f0 value.
        Exception: if input tier is not a valid tier.
        Return: None
        """
        if isinstance(momel, Tier):
            if momel.GetSize() < 2:
                raise Exception('Intsint error. There is not enough targets.')
            else:
                self.__init_from_tier(momel)


    def __init_from_tier(self, momel):
        """
        This method is used to initialize Intsint attributes from momel Tier.
        Return None
        """
        self.best_intsint  = None
        self.best_estimate = None
        self.intsint = []
        self.time = []
        self.estimates = []

        self.target_points = []
        sum_octave = 0
        self.size = momel.GetSize()
        for i in range(self.size):
            f0 = float(momel[i].GetLabel().GetValue())
            # make sur F0 is withing limits
            if f0 < Intsint.MIN_F0:
                f0 = Intsint.MIN_F0
            elif f0 > Intsint.MAX_F0:
                f0 = Intsint.MAX_F0

            # f0 converted to octave scale
            octave = self.octave(f0)
            time = momel[i].GetLocation().GetPointMidpoint()  #### HUM.... MUST ALSO KEEP RADIUS !!!!!! TODO

            self.target_points.append(octave)
            self.intsint.append("")
            self.time.append(time)
            self.estimates.append(0)
            sum_octave += octave

        mean_f0 = sum_octave / (i + 1)
        linear_mean_f0 = self._round(self.linear(mean_f0))
        self.min_mean = linear_mean_f0 - Intsint.MEAN_SHIFT
        self.max_mean = linear_mean_f0 + Intsint.MEAN_SHIFT
        self.min_ss_error = Intsint.BIG_NUMBER

    def __to_tier(self, intsint):
        tier = Tier(name="Intsint")
        for time, label in zip(self.time, intsint):
            tier.Append(Annotation(TimePoint(time), Label(label)))
        return tier


    def optimise(self, mid, _range):
        self.top = mid + _range / 2
        self.bottom = mid - _range / 2
        f0 = self.target_points[0]

        if self.top - f0 < math.fabs(f0 - mid):
            self.intsint[0] = "T"
        elif f0 - self.bottom < math.fabs(f0 - mid):
            self.intsint[0] = "B"
        else:
            self.intsint[0] = "M"

        estimate = self.estimate(self.intsint[0], self.last_estimate)
        self.estimates[0] = estimate
        error = math.fabs(estimate - self.target_points[0])
        ss_error = error * error
        self.last_estimate = estimate

        for i in range(1, self.size):
            target = self.target_points[i]

            # after pause choose from (MTB)
            if self.time[i] - self.time[i - 1] > Intsint.MIN_PAUSE:
                if self.top - target < math.fabs(target - mid):
                    self.intsint[i] = "T"
                elif target - self.bottom < math.fabs(target - mid):
                    self.intsint[i] = "B"
                else:
                    self.intsint[i] = "M"
            # elsewhere any tone except M
            else:
                min_difference = Intsint.BIG_NUMBER
                best_tone = ""
                for tone in Intsint.TONES:
                    if tone != "M":
                        estimate = self.estimate(tone, self.last_estimate)
                        difference = math.fabs(target - estimate)
                        if difference < min_difference:
                            min_difference = difference
                            best_tone = tone

                self.intsint[i] = best_tone

            estimate = self.estimate(self.intsint[i], self.last_estimate)
            self.estimates[i] = estimate
            error = math.fabs(estimate - self.target_points[i])
            ss_error += error * error
            self.last_estimate = estimate

        if ss_error < self.min_ss_error:
            self.min_ss_error = ss_error
            self.best_range = _range
            self.best_mid = mid
            self.best_intsint = self.intsint[:]
            self.best_estimate = self.estimates[:]


    def estimate(self, tone, last_target):
        if tone == "M":
            estimate = self.mid
        elif tone == "S":
            estimate = last_target
        elif tone == "T":
            estimate = self.top
        elif tone == "H":
            estimate = last_target + (self.top - last_target) * Intsint.HIGHER
        elif tone == "U":
            estimate = last_target + (self.top - last_target) * Intsint.UP
        elif tone == "B":
            estimate = self.bottom
        elif tone == "L":
            estimate = last_target - (last_target - self.bottom) * Intsint.LOWER
        elif tone == "D":
            estimate = last_target - (last_target - self.bottom) * Intsint.DOWN
        return estimate


    def recode(self):
        """
        Recode within the parameters space
        mean +/- 50 Hz for key and [0.5..2.5 octaves] for range.
        """
        _range = Intsint.MIN_RANGE
        while _range < Intsint.MAX_RANGE:
            lm = self.min_mean
            while lm < self.max_mean:
                self.mid = self.octave(lm)
                self.optimise(self.mid, _range)
                lm += Intsint.STEP_SHIFT

            _range += Intsint.STEP_RANGE


    def run(self):
        """
        Intsint is here.
        """
        self.recode()
        return self.__to_tier(self.best_intsint)
