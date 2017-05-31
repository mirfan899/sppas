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

    src.audiodata.audiopitch.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TO BE IMPLEMENTED.
"""


class AudioPitch(object):
    """
    A pitch audio utility class.
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

    # ------------------------------------------------------------------

    def get_pitch(self, time):
        """ Return the pitch value at a given time.

        :param time: a float value representing the time in seconds.
        :returns: float

        """
        idx = int(time/self.delta) + 1
        if len(self.pitch) < idx:
            return self.pitch[idx]
        else:
            raise ValueError('%d not in range' % idx)

    # ------------------------------------------------------------------

    def get_pitch_list(self):
        """ Return pitch values. """
        return self.pitch

    # ------------------------------------------------------------------

    def get_pitch_delta(self):
        """ Return the delta used to estimate pitch. """
        return self.delta

    # ------------------------------------------------------------------

    def get_size(self):
        """ Return the number of pitch values. """
        return len(self.pitch)

    # ------------------------------------------------------------------

    def eval_pitch(self, filename):
        """
        Eval pitch values... (TODO)
        At this stage, this will do: NOTHING!

        """
        raise NotImplementedError

    # ------------------------------------------------------------------
