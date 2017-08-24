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

    src.anndata.annlabel.label.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from ..anndataexc import AnnDataTypeError

from .tag import sppasTag

# ----------------------------------------------------------------------------


class sppasLabel(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Represents the label of an Annotation.

    A label is a list of possible sppasTag(), represented as a UNICODE string.
    A data type can be associated, as sppasTag() can be 'int', 'float' or 'bool'.

    """
    def __init__(self, tag=None, score=None):
        """ Creates a new Label instance.

        :param tag: (sppasTag or list of sppasTag)
        :param score: (float)

        """
        self.__tags = list()
        self.__fct = max

        if tag is not None:
            if isinstance(tag, list):
                for t in tag:
                    self.append(t, 1./len(tag))
            else:
                self.append(tag, score)

    # -----------------------------------------------------------------------

    def get_function_score(self):
        """ Return the function used to compare scores. """

        return self.__fct

    # -----------------------------------------------------------------------

    def set_function_score(self, fct_name):
        """ Set a new function to compare scores.

        :param fct_name: one of min or max.

        """
        if fct_name not in (min, max):
            raise AnnDataTypeError(fct_name, "min, max")

        self.__fct = fct_name

    # -----------------------------------------------------------------------

    def append_content(self, content, data_type="str", score=None):
        """ Add a text into the list.

        :param content: (str)
        :param data_type: (str): The type of this text content (str, int, float, bool)
        :param score: (float)

        """
        text = sppasTag(content, data_type)
        self.append(text, score)

    # -----------------------------------------------------------------------

    def append(self, tag, score=None):
        """ Add a sppasTag into the list.

        :param tag: (sppasTag)
        :param score: (float)

        """
        if not isinstance(tag, sppasTag):
            raise AnnDataTypeError(tag, "sppasTag")

        self.__tags.append((tag, score))

    # -----------------------------------------------------------------------

    def remove(self, tag):
        """ Remove a tag of the list.

        :param tag: (sppasTag) the tag to be removed of the list.

        """
        if not isinstance(tag, sppasTag):
            raise AnnDataTypeError(tag, "sppasTag")

        for (t, s) in self.__tags:
            if t == tag:
                self.__tags.remove((t, s))

    # -----------------------------------------------------------------------

    def set_score(self, tag, score):
        """ Set a score to a given tag.

        :param tag: (sppasTag)
        :param score: (float)

        """
        if not isinstance(tag, sppasTag):
            raise AnnDataTypeError(tag, "sppasTag")

        for (t, s) in self.__tags:
            if t == tag:
                s = score

    # -----------------------------------------------------------------------

    def get_best(self):
        """ Return the best sppasTag, i.e. the one with the better score.

        :returns: (sppasTag or None)

        """
        if len(self.__tags) == 0:
            return None

        if len(self.__tags) == 1:
            return self.__tags[0][0]

        _maxt = self.__tags[0][0]
        _maxscore = self.__tags[0][1]
        for (t, s) in reversed(self.__tags):
            if _maxscore is None or (s is not None and s > _maxscore):
                _maxscore = s
                _maxt = t

        return _maxt

    # -----------------------------------------------------------------------

    def contains(self, tag, function='exact'):
        """ Return True if the label contains a given tag.

        :param tag: (sppasTag)
        :param function: Search function
                -    exact (str): exact match
                -    iexact (str): Case-insensitive exact match
                -    startswith (str):
                -    istartswith (str): Case-insensitive startswith
                -    endswith (str):
                -    iendswith: (str) Case-insensitive endswith
                -    contains (str):
                -    icontains: (str) Case-insensitive contains
                -    equal (str): is equal (identical as exact)
                -    greater (str): is greater then
                -    lower (str): is lower than

        """
        if not isinstance(tag, sppasTag):
            raise AnnDataTypeError(tag, "sppasTag")

        if function == "exact" or function == "equal":
            return any([tag == t[0] for t in self.__tags])

        if tag.get_type() == "str":
            search_unicode_content = tag.get_content()
            lsearch_unicode_content = search_unicode_content.lower()
            for t, s in self.__tags:
                unicode_content = t.get_content()
                lunicode_content = unicode_content.lower()
                if function == "iexact" and lunicode_content == lsearch_unicode_content:
                    return True
                elif function == "startswith" and unicode_content.startswith(search_unicode_content):
                    return True
                elif function == "istartswith" and lunicode_content.startswith(lsearch_unicode_content):
                    return True
                elif function == "endswith" and unicode_content.endswith(search_unicode_content):
                    return True
                elif function == "iendswith" and lunicode_content.endswith(lsearch_unicode_content):
                    return True
                elif function == "contains" and search_unicode_content in unicode_content:
                    return True
                elif function == "icontains" and lsearch_unicode_content in lunicode_content:
                    return True

        elif tag.get_type() in ["float", "int"]:
            for t, s in self.__tags:
                if function == "greater" and t.get_typed_content() > tag.get_typed_content():
                    return True
                if function == "lower" and t.get_typed_content() < tag.get_typed_content():
                    return True

        return False

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        st = ""
        for t, s in self.__tags:
            st += "sppasTag({!s:s}, score={:s}), ".format(t, s)
        return st

    # -----------------------------------------------------------------------

    def __str__(self):
        st = ""
        for t, s in self.__tags:
            st += "{!s:s}, {:s} ; ".format(t, s)
        return st

    # -----------------------------------------------------------------------

    def __iter__(self):
        for t in self.__tags:
            yield t

    # -----------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__tags[i]

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__tags)

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        if other is None:
            return False
        if len(self.__tags) != len(other):
            return False
        for (l1, l2) in zip(self.__tags, other):
            if l1[0] != l2[0] or l1[1] != l2[1]:
                return False
        return True
