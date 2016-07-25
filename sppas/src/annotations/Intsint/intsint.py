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

import math

# ----------------------------------------------------------------------------

BIG_NUMBER = 32764

# List of "absolute" tones
TONES_ABSOLUTE = [ 'T', 'M', 'B' ]
# List of "relative" tones
TONES_RELATIVE = [ 'H', 'L', 'U', 'D', 'S' ]

# ----------------------------------------------------------------------------

def octave(value):
    return math.log(value) / math.log(2)

# ----------------------------------------------------------------------------

def linear(value):
    return 2 ** value

# -------------------------------------------------------------------

class Intsint( object ):
    """
    @author:       Tatsuya Watanabe, Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Provide optimal INTSINT coding for sequence of target points.

    INTSINT is an acronym for INternational Transcription System for INTonation.
    It was originally developed by Daniel Hirst in his 1987 thesis as a
    prosodic equivalent of the International Phonetic Alphabet, and the
    INTSINT alphabet was subsequently used in Hirst & Di Cristo (eds) 1998
    in just over half of the chapters.

    INTSINT codes the intonation of an utterance by means of an alphabet of
    8 discrete symbols constituting a surface phonological representation
    of the intonation:

        T (Top),
        H (Higher),
        U (Upstepped),
        S (Same),
        M (mid),
        D (Downstepped),
        L (Lower),
        B (Bottom).

    These tonal symbols are considered phonological in that they represent
    discrete categories and surface since each tonal symbol corresponds to
    a directly observable property of the speech signal.

    INTSINT is evaluated from a set of selected F0 targets.

    """
    def __init__(self):
        """
        Create a new INTSINT instance.

        """
        # parameters for data checking.
        self.MIN_F0 = 60   # (Hz)
        self.MAX_F0 = 600  # (Hz)

        # parameters for optimization.
        self.MIN_PAUSE = 0.5   # seconds
        self.MIN_RANGE = 0.5   # octaves
        self.MAX_RANGE = 2.5   # octaves
        self.STEP_RANGE = 0.1  # octaves
        self.MEAN_SHIFT = 50   # (Hz)
        self.STEP_SHIFT = 1    # (Hz)

        # parameters for target estimation.
        self.HIGHER = 0.5
        self.LOWER  = 0.5
        self.UP     = 0.25
        self.DOWN   = 0.25

        # All tones
        self.TONES = TONES_ABSOLUTE + TONES_RELATIVE

        self.reset()

    # -------------------------------------------------------------------

    def reset(self):
        """
        Fix all member to their initial value.

        """
        self.best_intsint  = None
        self.best_estimate = None

        self.intsint = []
        self.estimates = []
        self.targets = []
        self.time = []

        self.mid = 0
        self.top = 0
        self.bottom = 0
        self.last_estimate = 0

        self.best_mid = 0
        self.best_range = 0
        self.min_mean = 0
        self.max_mean = 0
        self.min_ss_error = 0

    # -------------------------------------------------------------------

    def adjust_f0(self, f0):
        """
        Return F0 value within self range of values.

        @param f0 (float) Input pitch value.
        @return Normalized pitch value.

        """
        if f0 < self.MIN_F0:
            return  self.MIN_F0

        if f0 > self.MAX_F0:
            return self.MAX_F0

        return f0

    # -------------------------------------------------------------------

    def init(self, momeltargets):
        """
        Initialize INTSINT attributes from a list of targets.

        @param momeltargets (list) List of tuples with time (in seconds) and target (Hz).

        """
        self.reset()
        for (time,target) in momeltargets:
            # Convert f0 to octave scale
            self.targets.append( octave(self.adjust_f0(target)) )
            self.time.append( time )

        self.intsint = [""]*len(self.targets)
        self.estimates = [0]*len(self.targets)

        sum_octave = sum( self.targets )
        mean_f0 = float(sum_octave) / float(len(self.targets))
        linear_mean_f0 = round( linear(mean_f0) )
        self.min_mean = linear_mean_f0 - self.MEAN_SHIFT
        self.max_mean = linear_mean_f0 + self.MEAN_SHIFT
        self.min_ss_error = BIG_NUMBER

    # -------------------------------------------------------------------

    def optimise(self, mid, _range):
        """
        Fix tones.

        """
        self.top = mid + _range / 2
        self.bottom = mid - _range / 2
        f0 = self.targets[0]

        if self.top - f0 < math.fabs(f0 - mid):
            self.intsint[0] = "T"
        elif f0 - self.bottom < math.fabs(f0 - mid):
            self.intsint[0] = "B"
        else:
            self.intsint[0] = "M"

        estimate = self.estimate(self.intsint[0], self.last_estimate)
        self.estimates[0] = estimate
        error = math.fabs(estimate - self.targets[0])
        ss_error = error * error
        self.last_estimate = estimate

        for i in range(1, len(self.targets)):
            target = self.targets[i]

            # after pause choose from (MTB)
            if self.time[i] - self.time[i - 1] > self.MIN_PAUSE:
                if self.top - target < math.fabs(target - mid):
                    self.intsint[i] = "T"
                elif target - self.bottom < math.fabs(target - mid):
                    self.intsint[i] = "B"
                else:
                    self.intsint[i] = "M"
            # elsewhere any tone except M
            else:
                min_difference = BIG_NUMBER
                best_tone = ""
                for tone in self.TONES:
                    if tone != "M":
                        estimate = self.estimate(tone, self.last_estimate)
                        difference = math.fabs(target - estimate)
                        if difference < min_difference:
                            min_difference = difference
                            best_tone = tone

                self.intsint[i] = best_tone

            estimate = self.estimate(self.intsint[i], self.last_estimate)
            self.estimates[i] = estimate
            error = math.fabs(estimate - self.targets[i])
            ss_error += error * error
            self.last_estimate = estimate

        if ss_error < self.min_ss_error:
            self.min_ss_error = ss_error
            self.best_range = _range
            self.best_mid = mid
            self.best_intsint = self.intsint[:]
            self.best_estimate = self.estimates[:]

    # -------------------------------------------------------------------

    def estimate(self, tone, last_target):
        """
        Estimates f0 from current tone and last target.

        """
        if tone == "M":
            estimate = self.mid
        elif tone == "S":
            estimate = last_target
        elif tone == "T":
            estimate = self.top
        elif tone == "H":
            estimate = last_target + (self.top - last_target) * self.HIGHER
        elif tone == "U":
            estimate = last_target + (self.top - last_target) * self.UP
        elif tone == "B":
            estimate = self.bottom
        elif tone == "L":
            estimate = last_target - (last_target - self.bottom) * self.LOWER
        elif tone == "D":
            estimate = last_target - (last_target - self.bottom) * self.DOWN

        return estimate

    # -------------------------------------------------------------------

    def recode(self):
        """
        Recode within the parameters space.
        mean +/- 50 Hz for key and [0.5..2.5 octaves] for range.

        """
        _range = self.MIN_RANGE

        while _range < self.MAX_RANGE:
            lm = self.min_mean
            while lm < self.max_mean:
                self.mid = octave(lm)
                self.optimise(self.mid, _range)
                lm += self.STEP_SHIFT

            _range += self.STEP_RANGE

    # -------------------------------------------------------------------

    def annotate(self, momeltargets):
        """
        Provide optimal INTSINT coding for sequence of target points.

        """
        if len(momeltargets) < 2:
            raise IOError("Not enough targets to estimate INTSINT.")

        self.init(momeltargets)
        self.recode()
        return self.best_intsint

# -----------------------------------------------------------------------

if __name__ == "__main__":
    intsint = Intsint()
    momeltargets = [(0.1,240), (0.4, 340), (0.6,240), (0.7,286)]
    print intsint.annotate( momeltargets )

