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
#       Copyright (C) 2011-2015  Brigitte Bigi
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
# ---------------------------------------------------------------------------
# File: detectrepetition.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
from os.path import *
import re

from storage import DataSpeaker
from storage import DataRepetition


class Repetitions:
    """
    Repetition automatic detection.
    DETECT THE SOURCE, then find where is the repetition.
    """

    def __init__(self):
        """
        Create a new Repetitions instance.
        """
        self.tabrepeats = []

    # End __init__
    # ------------------------------------------------------------------


    def get_longest(self, current1, speaker1, current2, speaker2):
        """
        Return the index of the last token of the longest repeated string,
        or -1.

        For self-repetitions, current2 must be None and speaker2=speaker1.
        For other-repetitions, speaker1 is the source and speaker2 is
        the echo.

        @param current1 (int)
        @param speaker1 (DataSpeaker)
        @param current2 (int)
        @param speaker2 (DataSpeaker2)

        """

        # the current token
        token1 = speaker1.get_token(current1)
        if speaker1.is_token( token1 ) is False:
            return -1

        lastt = -1
        # Get the longest string
        for t in range(current1, speaker1.get_size() ):

            # for self repetition or other-repetition:
            if current2 is None:
                param2 = speaker1.get_next_token(t)
            else:
                param2 = current2

            # search
            repeatidx = speaker1.is_token_repeat( t, param2, speaker2)
            if repeatidx > -1:
                if current2 is None and repeatidx == t:
                    return t
                lastt = t
            else:
                break

        return lastt

    # End get_longest
    # ------------------------------------------------------------------


    def is_relevant_token(self, token, speaker):
        """
        Ask the token of a speaker to be relevant.
        Hesitations, silences, pauses and laughs are not considered as
        tokens, then they are not relevant. Stopwords are not relevant.

        @param token (String)
        @param speaker (DataSpeaker)

        """

        if speaker.is_token( token ) is True:
            # stop words are not relevant
            return not speaker.is_stopword( token )

        return False

    # End is_relevant_token
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # Set of rules
    # ------------------------------------------------------------------


    def apply_rules_one_token(self, current, speaker):
        """
        Apply rules to decide if ONE token is a self-repetition or not.
        """
        token = speaker.get_token( current )
        # is a repeated token?
        is_repeated = speaker.is_token_repeat(current,speaker.get_next_token(current),speaker)
        if is_repeated == -1:
            return False
        # Keep all immediate repeat
        #if is_repeated == speaker.get_next_token(current):
        #    return True
        # Distance is more than 1...  Keep only a relevant token
        return self.is_relevant_token( token, speaker )


    def apply_rules_syntagme(self, start, end, speaker1, speaker2):
        """
        Apply rule 1 to decide if selection is a repetition or not.
        """
        nbrelevant = 0
        # Is there only stopwords?
        for i in range(start,end+1):
            token = speaker1.get_token(i)
            if self.is_relevant_token( token, speaker2 ) is True:
                nbrelevant = nbrelevant + 1

        return (nbrelevant > 0)


    def apply_rules_strict(self, start, end, speaker1, speaker2):
        """
        Apply rule 2 to decide if selection is a repetition or not.
        """
        # At least 3 tokens are acceptable
        if (end-start) < 2:
            return False

        # Test if the echo is strict

        # create a string with the tokens of the echoing spk
        l = ""
        for i in range(speaker2.get_size()):
            l = l + " " + speaker2.get_token(i)

        # create a string with the tokens of the source speaker
        t = ""
        for i in range(start,end+1):
            t = t + " " +  speaker1.get_token(i)

        return (t in l)

    # End apply_rules
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # Getters and Setters
    # ------------------------------------------------------------------

    def get_repeats(self):
        return self.tabrepeats

    def get_repeat(self, idx):
        return self.tabrepeats[idx]

    def get_repeat_source(self, idx):
        return self.tabrepeats[idx].get_source()

    def get_repeat_repetition(self, idx):
        return self.tabrepeats[idx].get_repetition()

    def get_repeats_size(self):
        return len(self.tabrepeats)

    # ------------------------------------------------------------------


    def __datarepetition(self, current, nextt, speaker1, speaker2=None):
        datarep = DataRepetition(current, nextt, -1, -1 )

        # Get each repetition of each token of the source
        repeats = []

        ridx = 0
        i = current
        while (i<=nextt):
            repeats.append([])
            if speaker2 is None:
                idx2 = speaker1.is_token_repeat(i, nextt+1, speaker1)
            else:
                idx2 = speaker1.is_token_repeat(i, 0, speaker2)

            while (idx2 != -1):
                repeats[ridx].append(idx2)
                if speaker2 is None:
                    idx2 = speaker1.is_token_repeat(i, idx2+1, speaker1)
                else:
                    idx2 = speaker1.is_token_repeat(i, idx2+1, speaker2)
            i = i + 1
            ridx = ridx + 1

        # Filter the repetitions (try to get the longest sequence)
        if len(repeats) == 1:
            datarep.add_repetition(repeats[0][0],repeats[0][0])
        else:
            #print "ALL:", repeats
            i = 0
            while i < len(repeats):
                repeated = self.__get_longest_repeated(i, repeats)
                datarep.add_repetition(repeated[0],repeated[-1])
                i = i + len(repeated)
                #print "SELECTED:",repeated

        return datarep

    # ------------------------------------------------------------------

    def __get_longest_repeated(self, start, repeats):

        pathrepeats = []
        for i in range(len(repeats[start])):
            pathrepeats.append([])
            pathrepeats[i].append(repeats[start][i])

            for j in range(start+1, len(repeats)):
                precvalue = pathrepeats[-1][-1]
                v = 0
                if not precvalue in repeats[j]:
                    if not (precvalue+1) in repeats[j]:
                        if not (precvalue+2) in repeats[j]:
                            if not (precvalue-1) in repeats[j]:
                                break
                            else:
                                v = repeats[j].index(precvalue-1)
                        else:
                            v = repeats[j].index(precvalue+2)
                    else:
                        v = repeats[j].index(precvalue+1)
                else:
                    v = repeats[j].index(precvalue)
                pathrepeats[i].append(repeats[j][v])

        # return the (first of the) longest path:
        return sorted(max(pathrepeats, key=lambda x: len(x)))


    # ------------------------------------------------------------------


    def detect(self, speaker1, limit, speaker2=None):
        """
        Detect repetitions in a serie of tokens.
        Detect self-repetitions if speaker2 is None and
        other-repetitions if speaker2 is fixed.

        @param speaker1 (DataSpeaker)
        @param speaker2 (DataSpeaker) can be the same speaker as speaker1

        """
        self.tabrepeats = []
        currentspk2 = 0
        if speaker2 == None:
            speaker2 = speaker1
            currentspk2 = None

        # Get repeated strings, Apply the rules, Add the repeats
        current = 0
        nextt = self.get_longest(current, speaker1, currentspk2, speaker2)

        while current < speaker1.get_size() and current < limit:

            if nextt == -1:
                # No source detected
                current = current + 1
                nextt = self.get_longest(current, speaker1, currentspk2, speaker2)

            else:
                # A source is detected

                # Self-Repetitions
                if currentspk2 is None:

                    # Get real length (ignoring pauses, hesitations, etc)
                    sourcelen = 0
                    for i in range(current,nextt+1):
                        if speaker1.is_token( speaker1.get_token(i)) is True:
                            sourcelen = sourcelen + 1

                    if sourcelen == 1:
                        keeprepeat = False
                        for i in range(current,nextt+1):
                            if speaker2.is_token( speaker1.get_token(i)) is True:
                                keeprepeat = self.apply_rules_one_token(i,speaker1)

                        if keeprepeat is True:
                            d = self.__datarepetition(current, current, speaker1)
                            self.tabrepeats.append( d )

                        current = current + 1
                        nextt = self.get_longest(current, speaker1, None, speaker1)

                    else:
                        keeprepeat = self.apply_rules_syntagme(current, nextt, speaker1, speaker1)
                        if keeprepeat is True:
                            d = self.__datarepetition(current, nextt, speaker1)
                            self.tabrepeats.append( d )
                            current = nextt + 1
                            nextt = self.get_longest(current, speaker1, None, speaker1)
                        else:
                            # Try with a shorter repeat (remove last token)
                            nextt = nextt - 1

                # Other-Repetitions:
                else:

                    # Rule 1:
                    # keep any repetition containing at least 1 relevant token
                    # (i.e. a token not in the stop-list)
                    keeprepeat = self.apply_rules_syntagme(current, nextt, speaker1, speaker1)
                    if keeprepeat is False:
                        # Rule 2: keep any repetition if N>2 and strict echo
                        if self.apply_rules_strict(current, nextt, speaker1, speaker2) is True:
                            keeprepeat = True

                    if keeprepeat is True:
                        d = self.__datarepetition(current, nextt, speaker1, speaker2)
                        self.tabrepeats.append( d )

                    current = nextt + 1
                    nextt = self.get_longest(current, speaker1, None, speaker2)

    # End detect
    # ------------------------------------------------------------------


# ------------------------------------------------------------------

if __name__ == "__main__":
    r = Repetitions()
    #l1 = u" # euh le petit garcon a l' air tres tres content # mais le papa n' a pas l' air # content du tout a l' air tres fatigue euh #"
    l1 = u" tout et rien être insolite alors aller y # bon et si on pérorer sur ce que on voir à_travers + tout et rien"
    l2 = u" donc euh # tout et rien être insolite # * oh oui ce être tout_à_fait insolite ouais + ouais ouais ouais ouais ouais surtout que là "

    s1 = DataSpeaker( l1.split() )
    s2 = DataSpeaker( l2.split() )

    r.detect( s1, len(l1.split())-1, None )
    print " ----> got ", r.get_repeats_size(), " SELF-Repetitions"
    for i in range(r.get_repeats_size()):
        r.get_repeat(i).print_echo()

    r.detect( s1, 1, s2 )
    print " ----> got ", r.get_repeats_size(), " OTHER-Repetitions"
    for i in range(r.get_repeats_size()):
        r.get_repeat(i).print_echo()

# ------------------------------------------------------------------
