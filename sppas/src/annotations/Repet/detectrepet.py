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

    src.annotations.Repet.detectrepet.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from .datastructs import DataRepetition

# ----------------------------------------------------------------------------


class Rules(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Rules to select repetitions.

    """

    @staticmethod
    def is_relevant_token(token, speaker):
        """ Ask for the token of a speaker to be relevant.
        A token is considered as relevant if:

            1. It is not an hesitation, a silence, a pause, a laugh,
             dummy or a noise
            2. It is not in the stop-list

        :param token: (str)
        :param speaker: (DataSpeaker)

        """
        if speaker.is_token(token) is True:
            # stop words are not relevant
            return not speaker.is_stopword(token)

        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def apply_rules_one_token(current, speaker):
        """ Apply rules to decide whether if ONE token is a self-repetition
        or not.

        Rules are:

            - the token must occur next;
            - the token must be relevant.

        :param current: (int)
        :param speaker: (DataSpeaker)

        """
        token = speaker.get_token(current)

        # is a repeated token?
        next_token = speaker.get_next_token(current)
        is_repeated = speaker.is_token_repeated(current, next_token, speaker)
        if is_repeated == -1:
            return False

        # Keep all immediate repeat
        # if is_repeated == speaker.get_next_token(current):
        #    return True
        # Keep only a relevant token
        return Rules.is_relevant_token(token, speaker)

    # -----------------------------------------------------------------------

    @staticmethod
    def apply_rules_syntagme(start, end, speaker1, speaker2):
        """ Apply rule 1 to decide if selection is a repetition or not.

        Rule 1: The selection must contain at least one relevant token.

        :param start: (int)
        :param end: (int)
        :param speaker1: (DataSpeaker)
        :param speaker2: (DataSpeaker)

        """
        nb_relevant = 0
        # Is there only stopwords?
        for i in range(start, end + 1):
            token = speaker1.get_token(i)
            if Rules.is_relevant_token(token, speaker2) is True:
                nb_relevant += 1

        return nb_relevant > 0

    # -----------------------------------------------------------------------

    @staticmethod
    def apply_rules_strict(start, end, speaker1, speaker2):
        """ Apply rule 2 to decide if selection is a repetition or not.

        Rule 2: The selection is a repetition if it respect at least one of
        the following criteria:

            - selection contains at least 3 tokens;
            - the repetition is strict (the source is strictly included into the echo).

        :param start: (int)
        :param end: (int)
        :param speaker1: (DataSpeaker)
        :param speaker2: (DataSpeaker)

        """
        # At least 3 tokens are acceptable
        if (end-start) < 2:
            return False

        # Test if the echo is strict

        # create a string with the tokens of the echoing spk
        l = ""
        for i in range(len(speaker2)):
            l = l + " " + speaker2.get_token(i)

        # create a string with the tokens of the source speaker
        t = ""
        for i in range(start,end+1):
            t = t + " " + speaker1.get_token(i)

        return t in l

# ----------------------------------------------------------------------------


class Repetitions(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Repetition automatic detection.
    
    DETECT THE SOURCE, then find where are the echos.

    """
    def __init__(self):
        """ Create a new Repetitions instance. """

        self.__repetitions = list()

    # ------------------------------------------------------------------
    # Getters and Setters
    # ------------------------------------------------------------------

    def get_source(self, idx):
        """ Return the source of a given repetition.

        :param idx: (int) Index of the repetition
        :returns: source as a tuple: (start, end)

        """
        return self.__repetitions[idx].get_source()

    # ------------------------------------------------------------------

    def get_echos(self, idx):
        """ Return the echos of a given repetition.

        :param idx: (int) Index of the repetition
        :returns: list of echos as tuples: (start, end)

        """
        return self.__repetitions[idx].get_echos()

    # ------------------------------------------------------------------
    # Search for repetitions
    # ------------------------------------------------------------------

    @staticmethod
    def find_repetition(current, nextt, speaker1, speaker2=None):
        """ Find all echos of a source.
        
        :param current: 
        :param nextt: 
        :param speaker1: 
        :param speaker2: 
        :returns: DataRepetition()
        
        """
        # Data structure to store the repetition
        data_repet = DataRepetition(current, nextt)

        # Find all repeated tokens of each token of the source
        repeats = list()

        ridx = 0
        i = current
        while i <= nextt:
            repeats.append(list())
            if speaker2 is None:
                idx2 = speaker1.is_token_repeated(i, nextt+1, speaker1)
            else:
                idx2 = speaker1.is_token_repeated(i, 0, speaker2)

            while idx2 != -1:
                repeats[ridx].append(idx2)
                if speaker2 is None:
                    idx2 = speaker1.is_token_repeated(i, idx2+1, speaker1)
                else:
                    idx2 = speaker1.is_token_repeated(i, idx2+1, speaker2)
            i += 1
            ridx += 1

        # Filter the repetitions (try to get the longest sequence)
        if len(repeats) == 1:
            data_repet.add_echo(repeats[0][0], repeats[0][0])
        else:
            i = 0
            while i < len(repeats):
                repeated = Repetitions.__get_longest_repeated(i, repeats)
                data_repet.add_echo(repeated[0], repeated[-1])
                i += len(repeated)

        return data_repet

    # ------------------------------------------------------------------

    @staticmethod
    def __get_longest_repeated(start, repeats):
        """ Select the longest echo from start position in repeats. """

        path_repeats = []
        for i in range(len(repeats[start])):
            path_repeats.append([])
            path_repeats[i].append(repeats[start][i])

            for j in range(start+1, len(repeats)):
                precvalue = path_repeats[-1][-1]
                v = 0
                if precvalue not in repeats[j]:
                    if (precvalue+1) not in repeats[j]:
                        if (precvalue+2) not in repeats[j]:
                            if (precvalue-1) not in repeats[j]:
                                break
                            else:
                                v = repeats[j].index(precvalue-1)
                        else:
                            v = repeats[j].index(precvalue+2)
                    else:
                        v = repeats[j].index(precvalue+1)
                else:
                    v = repeats[j].index(precvalue)
                path_repeats[i].append(repeats[j][v])

        # return the (first of the) longest path:
        return sorted(max(path_repeats, key=lambda x: len(x)))

    # -----------------------------------------------------------------------

    def detect(self, speaker1, limit, speaker2=None):
        """ Detect repetitions in tokens.
        Detect self-repetitions if speaker2 is None and other-repetitions if
        speaker2 is set.

        :param speaker1: (DataSpeaker)
        :param limit: (int) Go no longer than limit to find repetitions
        :param speaker2: (DataSpeaker) can be the same speaker as speaker1

        """
        self.__repetitions = list()
        current_spk2 = 0
        if speaker2 is None:
            speaker2 = speaker1
            current_spk2 = None

        # Get repeated strings, Apply the rules, Add the repeats
        current = 0
        nextt = Repetitions.get_longest(current, speaker1, current_spk2, speaker2)

        while current < len(speaker1) and current < limit:

            if nextt == -1:
                # No source detected
                current += 1
                nextt = Repetitions.get_longest(current, speaker1, current_spk2, speaker2)

            else:
                # A source is detected

                # Self-Repetitions
                if current_spk2 is None:

                    # Get real length (ignoring pauses, hesitations, etc)
                    source_len = 0
                    for i in range(current, nextt+1):
                        if speaker1.is_token(speaker1.get_token(i)) is True:
                            source_len += 1

                    if source_len == 1:
                        keep_me = False
                        for i in range(current, nextt+1):
                            if speaker2.is_token(speaker1.get_token(i)) is True:
                                keep_me = Rules.apply_rules_one_token(i, speaker1)

                        if keep_me is True:
                            d = Repetitions.find_repetition(current, current, speaker1)
                            self.__repetitions.append(d)

                        current += 1
                        nextt = Repetitions.get_longest(current, speaker1, None, speaker1)

                    else:
                        keeprepeat = Rules.apply_rules_syntagme(current, nextt, speaker1, speaker1)
                        if keeprepeat is True:
                            d = Repetitions.find_repetition(current, nextt, speaker1)
                            self.__repetitions.append(d)
                            current = nextt + 1
                            nextt = Repetitions.get_longest(current, speaker1, None, speaker1)
                        else:
                            # Try with a shorter repeat (remove last token)
                            nextt -= 1

                # Other-Repetitions:
                else:

                    # Rule 1:
                    # keep any repetition containing at least 1 relevant token
                    # (i.e. a token not in the stop-list)
                    keeprepeat = Rules.apply_rules_syntagme(current, nextt, speaker1, speaker1)
                    if keeprepeat is False:
                        # Rule 2: keep any repetition if N>2 and strict echo
                        if Rules.apply_rules_strict(current, nextt, speaker1, speaker2) is True:
                            keeprepeat = True

                    if keeprepeat is True:
                        d = Repetitions.find_repetition(current, nextt, speaker1, speaker2)
                        self.__repetitions.append(d)

                    current = nextt + 1
                    nextt = Repetitions.get_longest(current, speaker1, None, speaker2)

    # ------------------------------------------------------------------

    @staticmethod
    def get_longest(current1, speaker1, current2=None, speaker2=None):
        """ Return the index of the last token of the longest repeated
        string, or -1.

        For self-repetitions, current2 must be None.
        For other-repetitions, speaker1 is the source and speaker2 is
        the echo.

        :param current1: (int)
        :param speaker1: (DataSpeaker)
        :param current2: (int)
        :param speaker2: (DataSpeaker2)

        """
        # the current token
        token1 = speaker1.get_token(current1)
        if speaker1.is_token(token1) is False:
            return -1

        last_token = -1
        # Get the longest string
        for t in range(current1, len(speaker1)):

            # for self repetition or other-repetition:
            if current2 is None:
                param2 = speaker1.get_next_token(t)
            else:
                param2 = current2

            # search
            repet_idx = speaker1.is_token_repeated(t, param2, speaker2)
            if repet_idx > -1:
                if current2 is None and repet_idx == t:
                    return t
                last_token = t
            else:
                break

        return last_token

    # ------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------

    def __iter__(self):
        for a in self.__repetitions:
            yield a

    def __getitem__(self, i):
        return self.__repetitions[i]

    def __len__(self):
        return len(self.__repetitions)
