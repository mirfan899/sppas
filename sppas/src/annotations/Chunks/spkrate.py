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

    src.annotations.Chuncks.spkrate.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


class SpeakerRate(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Speaker speech rate evaluator.

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
    DEFAULT_SPK_RATE = 12.
    
    def __init__(self):
        """ Create a new SpeakerRate instance. """
        
        self._spk_rate = SpeakerRate.DEFAULT_SPK_RATE

    # ----------------------------------------------------------------------

    def get_value(self):
        """ Returns the speaking rate. """
        return self._spk_rate

    # ----------------------------------------------------------------------

    def set_value(self, value):
        """ Set the speaking rate.

        :param value: (float) Speaking rate value.

        """
        value = float(value)
        if value <= 0. or value >= 100.:
            raise ValueError('Expected a reasonable value of speaking rate. Got: %f' % value)
        self._spk_rate = value

    # ----------------------------------------------------------------------

    def mul(self, coef):
        """ Multiply the speaking rate.

        :param coef: (float) coefficient

        """
        coef = float(coef)
        self.set_value(self._spk_rate * coef)

    # ----------------------------------------------------------------------

    def div(self, coef):
        """ Divide the speaking rate.

        :param coef: (float) coefficient

        """
        coef = float(coef)
        self.set_value(self._spk_rate / coef)

    # ----------------------------------------------------------------------

    def eval_from_duration(self, duration, ntokens):
        """ Set the speaking rate in number of tokens per seconds.

        :param duration: (float) Speaking time (in seconds)
        :param ntokens: (int) Number of tokens

        """
        ntokens = float(ntokens)
        duration = float(duration)
        self.set_value(ntokens / duration)

    # ----------------------------------------------------------------------

    def eval_from_tracks(self, tracks_times, ntokens):
        """ Set the speaking rate in number of tokens per seconds.

        :param tracks_times: (List of tracks)
        :param ntokens: (int) Number of tokens

        """
        duration = sum([(e-s) for (s, e) in tracks_times])
        self.eval_from_duration(duration, ntokens)

    # ----------------------------------------------------------------------

    def ntokens(self, duration):
        """ Return the number of expected tokens for a given duration.

        :param duration: (float) Speech duration in seconds.
        :returns: (int) number of tokens

        """
        return int(duration * self._spk_rate)

# ----------------------------------------------------------------------

    def duration(self, ntokens):
        """ Return expected duration for a given number of tokens.

        :param ntokens: (int) Number of tokens
        :returns: (float) duration

        """
        return float(ntokens) / self._spk_rate
