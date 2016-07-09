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
# File: spkrate.py
# ----------------------------------------------------------------------------

class SpeakerRate:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Speaker speech rate evaluator.

    The average speaking rate will vary across languages and situations.
    In conversational English, the average rate of speech for men is 125
    words per minute. Women average 150 words per minute. Television
    newscasters frequently hit 175+ words per minute (= 3 words/sec.).
    See: http://sixminutes.dlugan.com/speaking-rate/

    In CID, if we look at all tokens of the IPUs, the speaker rate is:
        - AB: 4.55 tokens/sec.
        - AC: 5.29 tokens/sec.
        - AP: 5.15 tokens/sec.
    See: http://sldr.org/sldr000720/

    To ensure we'll consider enough words, we'll fix a very large value by
    default, i.e. 12 tokens/second.

    """
    def __init__(self):
        self._spkrate = 12.

    # ----------------------------------------------------------------------

    def get_value(self):
        return self._spkrate

    # ----------------------------------------------------------------------

    def set_value(self, value):
        value = float(value)
        if value <= 0. or value >= 100.:
            raise ValueError('Expected a reasonable value of speaking rate. Got: %f'%value)
        self._spkrate = value

    # ----------------------------------------------------------------------

    def mul(self, coef):
        coef = float(coef)
        self.set_value( self._spkrate * coef )

    # ----------------------------------------------------------------------

    def eval_from_duration(self, duration, ntokens ):
        """
        Evaluate the speaking rate in number of tokens per seconds.

        """
        ntokens  = float(ntokens)
        duration = float(duration)
        self.set_value( ntokens / duration )

    # ----------------------------------------------------------------------

    def eval_from_tracks(self, trackstimes, ntokens ):
        """
        Evaluate the speaking rate in number of tokens per seconds.

        """
        duration = sum( [(e-s) for (s,e) in trackstimes] )
        self.eval_from_duration( duration, ntokens )

    # ----------------------------------------------------------------------

    def ntokens(self, duration):
        """

        @param duration (float - IN) Speech duration in seconds.
        @return a maximum number of tokens we could expect for this duration.

        """
        return int(duration*self._spkrate)

# ----------------------------------------------------------------------

    def duration(self, ntokens):
        """
        """
        return float(ntokens) / self._spkrate

# ----------------------------------------------------------------------
