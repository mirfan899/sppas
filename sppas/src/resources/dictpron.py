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

    src.resources.dictpron.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Class to manage pronunciation dictionaries.

"""
import codecs
import logging

from sppas import encoding
from sppas import unk_stamp
from sppas.src.utils.makeunicode import sppasUnicode

from .dumpfile import sppasDumpFile
from .resourcesexc import FileIOError, FileFormatError

# ---------------------------------------------------------------------------


class sppasDictPron(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Pronunciation dictionary manager.

    A pronunciation dictionary contains a list of tokens, each one with a list
    of possible pronunciations.

    sppasDictPron can load the dictionary from an HTK-ASCII file. Each line of
    such file looks like the following:
        acted [acted] { k t e d
        acted(2) [acted] { k t i d
    The first columns indicates the tokens, eventually followed by the variant
    number into braces. The second column (with brackets) is ignored. It should
    contain the token. Other columns are the phones separated by whitespace.
    sppasDictPron accepts missing variant numbers, empty brackets, or  missing
    brackets.

        >>> d = sppasDictPron('eng.dict')
        >>> d.add_pron('acted', '{ k t e')
        >>> d.add_pron('acted', '{ k t i')

    Then, the phonetization of a token can be accessed with get_pron() method:

        >>> print(d.get_pron('acted'))
        >>>{-k-t-e-d|{-k-t-i-d|{-k-t-e|{-k-t-i

    The following convention is adopted to represent the pronunciation
    variants:

        - '-' separates the phones (X-SAMPA standard)
        - '|' separates the variants

    Notice that tokens in the dict are case-insensitive.

    """
    PHONEMES_SEPARATOR = "-"
    VARIANTS_SEPARATOR = "|"

    # -----------------------------------------------------------------------

    def __init__(self, dict_filename=None, nodump=False):
        """ Create a sppasDictPron instance.

        :param dict_filename: (str) Name of the file of the pronunciation dictionary
        :param nodump: (bool) Create or not a dump file.

        A dump file is a binary version of the dictionary. Its size is greater
        than the original ASCII dictionary but the time to load it is divided
        by two or three.

        """
        self._filename = dict_filename

        # The pronunciation dictionary
        self._dict = dict()

        # Either read the dictionary from a dumped file or from the original
        # ASCII one.
        if dict_filename is not None:

            dp = sppasDumpFile(dict_filename)
            data = None

            # Try first to get the dict from a dump file (at least 2 times faster)
            if nodump is False:
                data = dp.load_from_dump()

            # Load from ascii if:
            # 1st load, or, dump load error, or dump older than ascii
            if data is None:
                self.load_from_ascii(dict_filename)
                if nodump is False:
                    dp.save_as_dump(self._dict)
            else:
                self._dict = data

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_unkstamp(self):
        """ Returns the unknown words stamp. """

        return unk_stamp

    # -----------------------------------------------------------------------

    def get(self, entry, substitution=unk_stamp):
        """ Return the pronunciations of an entry in the dictionary.

        :param entry: (str) A token to find in the dictionary
        :param substitution: (str) String to return if token is missing of the dict
        :returns: unicode of the pronunciations or the substitution.

        """
        s = sppasDictPron.format_token(entry)
        return self._dict.get(s, substitution)

    # -----------------------------------------------------------------------

    def get_pron(self, entry):
        """ Return the pronunciations of an entry in the dictionary.

        :param entry: (str) A token to find in the dictionary
        :returns: unicode of the pronunciations or the unknown stamp.

        """
        s = sppasDictPron.format_token(entry)
        return self._dict.get(s, unk_stamp)

    # -----------------------------------------------------------------------

    def is_unk(self, entry):
        """ Return True if an entry is unknown (not in the dictionary).

        :param entry: (str) A token to find in the dictionary
        :returns: bool

        """
        return sppasDictPron.format_token(entry) not in self._dict

    # -----------------------------------------------------------------------

    def is_pron_of(self, entry, pron):
        """ Return True if pron is a pronunciation of entry.
        Phonemes of pron are separated by "-".

        :param entry: (str) A unicode token to find in the dictionary
        :param pron: (str) A unicode pronunciation
        :returns: bool

        """
        s = sppasDictPron.format_token(entry)

        if s in self._dict:
            p = sppasUnicode(pron).to_strip()
            return p in self._dict[s].split(sppasDictPron.VARIANTS_SEPARATOR)

        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def format_token(entry):
        """ Remove the CR/LF, tabs, multiple spaces and others... and lowerise.

        :param entry: (str) a token
        :returns: formatted token

        """
        t = sppasUnicode(entry).to_strip()
        return sppasUnicode(t).to_lower()

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def add_pron(self, token, pron):
        """ Add a token/pron to the dict.

        :param token: (str) Unicode string of the token to add
        :param pron: (str) A pronunciation in which the phonemes are separated by whitespace

        """
        entry = sppasDictPron.format_token(token)

        new_pron = sppasUnicode(pron).to_strip()
        new_pron = new_pron.replace(" ", sppasDictPron.PHONEMES_SEPARATOR)

        # Already a pronunciation for this token?
        cur_pron = ""
        if entry in self._dict:
            # ... don't append an already known pronunciation
            if self.is_pron_of(entry, new_pron) is False:
                cur_pron = self.get_pron(entry) + sppasDictPron.VARIANTS_SEPARATOR
            else:
                cur_pron = self.get_pron(entry)
                new_pron = ""

        # Get the current pronunciation and append the new one
        new_pron = cur_pron + new_pron

        # Add (or change) the entry in the dict
        self._dict[entry] = new_pron

    # -----------------------------------------------------------------------

    def map_phones(self, map_table):
        """ Create a new dictionary by changing the phoneme strings,
        depending on a mapping table.

        :param map_table: (Mapping) A mapping table
        :returns: a sppasDictPron instance with mapped phones

        """
        map_table.set_reverse(True)
        delimiters = [sppasDictPron.VARIANTS_SEPARATOR, sppasDictPron.PHONEMES_SEPARATOR]
        new_dict = sppasDictPron()

        for key, value in self._dict.items():
            new_dict._dict[key] = map_table.map(value, delimiters)

        return new_dict

    # -----------------------------------------------------------------------
    # File management
    # -----------------------------------------------------------------------

    def load_from_ascii(self, filename):
        """ Load a pronunciation dictionary from an HTK-ASCII file.

        :param filename: (str) Pronunciation dictionary file name

        """
        try:
            with codecs.open(filename, 'r', encoding) as fd:
                lines = fd.readlines()
        except Exception:
            raise FileIOError(filename)

        for l, line in enumerate(lines):

            uline = sppasUnicode(line).to_strip()

            # Ignore empty lines and check the number of columns
            if len(uline) == 0:
                continue
            if len(uline) == 1:
                raise FileFormatError(l, uline)

            # The entry is before the "[" and the pronunciation is after the "]"
            i = uline.find("[")
            if i == -1:
                i = uline.find(" ")
            entry = uline[:i]
            endline = uline[i:]
            j = endline.find("]")
            if j == -1:
                j = endline.find(" ")
            new_pron = endline[j+1:]

            # Phonetic variant of an entry (i.e. entry ends with (XX))
            i = entry.find("(")
            if i > -1:
                if ")" in entry[i:]:
                    entry = entry[:i]

            self.add_pron(entry, new_pron)

    # -----------------------------------------------------------------------

    def save_as_ascii(self, filename, with_variant_nb=True, with_filled_brackets=True):
        """ Save the pronunciation dictionary in HTK-ASCII format.

        :param filename: (str) Dictionary file name
        :param with_variant_nb: (bool) Write the variant number or not
        :param with_filled_brackets: (bool) Fill the bracket with the token or not

        """
        try:
            with codecs.open(filename, 'w', encoding=encoding) as output:

                for entry, value in sorted(self._dict.items(), key=lambda x: x[0]):
                    variants = value.split(sppasDictPron.VARIANTS_SEPARATOR)

                    for i, variant in enumerate(variants, 1):
                        variant = variant.replace(sppasDictPron.PHONEMES_SEPARATOR, " ")
                        brackets = entry
                        if with_filled_brackets is False:
                            brackets = ""
                        if i > 1 and with_variant_nb is True:
                            line = "{:s}({:d}) [{:s}] {:s}\n".format(entry, i, brackets, variant)
                        else:
                            line = "{:s} [{:s}] {:s}\n".format(entry, brackets, variant)
                        output.write(line)

        except Exception as e:
            logging.info('Saving the dictionary in ASCII failed: {:s}'.format(str(e)))
            return False

        return True

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __len__(self):
        return len(self._dict)

    # ------------------------------------------------------------------------

    def __contains__(self, item):
        s = sppasDictPron.format_token(item)
        return s in self._dict

    # ------------------------------------------------------------------------

    def __iter__(self):
        for a in self._dict:
            yield a
