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
# File: wavpitch.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------

class WavePitch(object):
    """
    A pitch wav utility class.
    ToDo:
    Implements 3 different methods (at least) to estimate pitch and
    an algorithm to "vote" (exactly as in Signaix, by R. Espesser).

    """
    def __init__(self, delta=0.01):
        """
        Creates a new WavePitch instance with empty pith values.
        """
        self.pitch = []
        self.delta = delta


    # ##################################################################### #
    # Getters and Setters
    # ##################################################################### #

    def get_pitch(self, time):
        """
        Return the pitch value at a given time.

        @param time: a float value representing the time in seconds.
        @return float

        """
        idx = int(time/self.delta) + 1
        if len(self.pitch) < idx:
            return self.pitch[idx]
        else:
            raise ValueError('%d not in range' % idx)

    # ------------------------------------------------------------------

    def get_pitch_list(self):
        """
        Return pitch values.

        """
        return self.pitch

    # ------------------------------------------------------------------

    def get_pitch_delta(self):
        """
        Return the delta used to estimate pitch.

        """
        return self.delta

    # ------------------------------------------------------------------

    def get_size(self):
        """
        Return the number of pitch values.

        """
        return len(self.pitch)

    # ------------------------------------------------------------------

    def eval_pitch(self, filename, delta=0.01):
        """
        Eval pitch values... (TODO)
        At this stage, this will do: NOTHING!

        """
        self.delta = delta
        pass

    # ------------------------------------------------------------------
