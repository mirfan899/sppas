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

    src.annotations.Repet.rules.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The set of rules to accept or reject a repetition.

"""
from sppas.src.resources.vocab import sppasVocabulary
from .datastructs import Entry

# ----------------------------------------------------------------------------


class Rules(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Rules to select repetitions.

    Proposed rules deal with the number of words, the word frequencies and
    distinguish if the repetition is strict or not. The following rules are
    proposed for other-repetitions:

        - Rule 1: A source is accepted if it contains one or more relevant
        token. Relevance depends on the speaker producing the echo;
        - Rule 2: A source which contains at least K tokens is accepted
        if the repetition is strict.

    Rule number 1 need to fix a clear definition of the relevance of a
    token. Un-relevant tokens are then stored in a stop-list.
    The stop-list also should contain very frequent tokens in the given
    language like adjectives, pronouns, etc.

    """
    def __init__(self, stop_list=None):
        """ Creates a Rules instance.

        :param stop_list: (sppasVocabulary) List of un-relevant tokens.

        """
        self.__stoplist = sppasVocabulary()
        if stop_list is not None:
            if isinstance(stop_list, sppasVocabulary):
                self.__stoplist = stop_list
            else:
                for token in stop_list:
                    self.__stoplist.add(token)

    # -----------------------------------------------------------------------

    def is_relevant_token(self, token):
        """ Ask for the token of a speaker to be relevant or not.
        A token is considered as relevant if:

            1. It is not a silence, a pause, a laugh, dummy or a noise;
            2. It is not in the stop-list.

        :param token: (str) The token to be checked.

        """
        e = Entry(token)
        if e.is_token() is True:
            # stop words are not relevant
            return self.__stoplist.is_unk(e.get_formatted())

        return False

    # -----------------------------------------------------------------------

    def count_relevant_tokens(self, start, end, speaker):
        """ Estimates the number of relevant tokens between start and end (included).

        :param start: (int)
        :param end: (int)
        :param speaker: (DataSpeaker)
        :returns: (int)

        """
        nb_relevant = 0

        for i in range(start, end + 1):
            token = speaker.get_token(i)
            if self.is_relevant_token(token) is True:
                nb_relevant += 1

        return nb_relevant

    # -----------------------------------------------------------------------

    def apply_rules_one_token(self, current, speaker):
        """ Apply rules to decide whether if ONE token is a self-repetition
        or not.

        Rules are:

            - the token must occur next (!);
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

        # Keep all immediate repetitions
        # if is_repeated == speaker.get_next_token(current):
        #    return True
        # Keep only a relevant token
        return self.is_relevant_token(token)

    # -----------------------------------------------------------------------

    def apply_rules_syntagme(self, start, end, speaker1):
        """ Apply rule 1 to decide if selection is a repetition or not.

        Rule 1: The selection of tokens of speaker 1 must contain at least
        one relevant token for speaker 2.

        :param start: (int)
        :param end: (int)
        :param speaker1: (DataSpeaker)
        :returns: (bool)

        """
        return self.count_relevant_tokens(start, end, speaker1) > 0

    # -----------------------------------------------------------------------

    def apply_rules_strict(self, start, end, speaker1, speaker2):
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

        # create a string with the tokens of the source speaker
        source = ""
        for i in range(start, end+1):
            source = source + " " + speaker1.get_token(i)

        # create a string with the tokens of the echoing spk
        echo = ""
        for i in range(len(speaker2)):
            echo = echo + " " + speaker2.get_token(i)

        return source in echo
