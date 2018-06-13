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

    src.anndata.filter.patternmatch.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Search in an annotation with pattern matching.

    Pattern matching is the act of checking a given sequence of items for
    the presence of the constituents of some pattern.
    Annotations labels can be of 3 types in anndata (str, num, bool) so
    that this pattern matching allows to create different predicates
    depending on the type of the labels.

"""
import operator
import functools
import re

from sppas.src.structs.predicate import sppasPredicate
from sppas.src.utils.makeunicode import text_type
from sppas.src.utils.makeunicode import sppasUnicode
from sppas.src.utils.datatype import sppasType

from ..anndataexc import AnnDataTypeError
from .patternbase import sppasPatternBaseCompare

# ---------------------------------------------------------------------------


class sppasPatternMatchingCompare(sppasPatternBaseCompare):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Pattern matching comparison methods.

    """
    def __init__(self):
        """ Create a sppasPatternCompare instance. """

        sppasPatternBaseCompare.__init__(self)

        # Methods on strings
        self.methods['exact'] = sppasPatternMatchingCompare.exact
        self.methods['iexact'] = sppasPatternMatchingCompare.iexact
        self.methods['startswith'] = sppasPatternMatchingCompare.startswith
        self.methods['istartswith'] = sppasPatternMatchingCompare.istartswith
        self.methods['endswith'] = sppasPatternMatchingCompare.endswith
        self.methods['iendswith'] = sppasPatternMatchingCompare.iendswith
        self.methods['contains'] = sppasPatternMatchingCompare.contains
        self.methods['icontains'] = sppasPatternMatchingCompare.icontains
        self.methods['regexp'] = sppasPatternMatchingCompare.regexp

        # Methods on numerical values
        self.methods['greater'] = sppasPatternMatchingCompare.greater
        self.methods['lower'] = sppasPatternMatchingCompare.lower
        self.methods['equal'] = sppasPatternMatchingCompare.equal

        # Methods on boolean values
        self.methods['bool'] = sppasPatternMatchingCompare.bool

    # -----------------------------------------------------------------------

    @staticmethod
    def exact(text1, text2):
        """ Test if two texts strictly contain the same characters.

        :param text1: (str)
        :param text2: (str)
        :returns: (bool)

        """
        if isinstance(text1, text_type):
            sp = sppasUnicode(text2)
            t = sp.unicode().strip()
            return text1 == t
        raise AnnDataTypeError(text1, "str/unicode")

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(text1, text2):
        """ Case-insensitive exact.

        :param text1: (str)
        :param text2: (str)
        :returns: (bool)

        """
        if isinstance(text1, text_type):
            sp = sppasUnicode(text2)
            t = sp.unicode().strip()
            return text1.lower() == t.lower()
        raise AnnDataTypeError(text1, "str/unicode")

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(text1, text2):
        """ Test if first text starts with the characters of the second text.

        :param text1: (str)
        :param text2: (str)
        :returns: (bool)

        """
        if isinstance(text1, text_type):
            sp = sppasUnicode(text2)
            t = sp.unicode().strip()
            return text1.startswith(t)
        raise AnnDataTypeError(text1, "str/unicode")

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(text1, text2):
        """ Case-insensitive startswith.

        :param text1: (str)
        :param text2: (str)
        :returns: (bool)

        """
        if isinstance(text1, text_type):
            sp = sppasUnicode(text2)
            t = sp.unicode().strip()
            return text1.lower().startswith(t.lower())
        raise AnnDataTypeError(text1, "str/unicode")

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(text1, text2):
        """ Test if first text ends with the characters of the second text.

        :param text1: (str)
        :param text2: (str)
        :returns: (bool)

        """
        if isinstance(text1, text_type):
            sp = sppasUnicode(text2)
            t = sp.unicode().strip()
            return text1.endswith(t)
        raise AnnDataTypeError(text1, "str/unicode")

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(text1, text2):
        """ Case-insensitive endswith.

        :param text1: (str)
        :param text2: (str)
        :returns: (bool)

        """
        if isinstance(text1, text_type):
            sp = sppasUnicode(text2)
            t = sp.unicode().strip()
            return text1.lower().endswith(t.lower())
        raise AnnDataTypeError(text1, "str/unicode")

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(text1, text2):
        """ Test if the first text contains the second text.

        :param text1: (str)
        :param text2: (str)
        :returns: (bool)

        """
        if isinstance(text1, text_type):
            sp = sppasUnicode(text2)
            t = sp.unicode().strip()
            return t in text1
        raise AnnDataTypeError(text1, "str/unicode")

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(text1, text2):
        """ Case-insensitive contains.

        :param text1: (str)
        :param text2: (str)
        :returns: (bool)

        """
        if isinstance(text1, text_type):
            sp = sppasUnicode(text2)
            t = sp.unicode().strip()
            return t.lower() in text1.lower()
        raise AnnDataTypeError(text1, "str/unicode")

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(text, pattern):
        """ test if text matches pattern.

        :param text: (str)
        :param pattern: (str)
        :returns: (bool)

        """
        if isinstance(text, text_type):
            return True if re.match(pattern, text) else False

        raise AnnDataTypeError(text, "str/unicode")

    # -----------------------------------------------------------------------

    @staticmethod
    def equal(x1, x2):
        """ Return True if numerical value x1 is equal to x2.

        :param x1: (int, float)
        :param x2: (int, float)
        :returns: (bool)

        """
        if sppasType().is_number(x1) is False:
            raise AnnDataTypeError(x1, "int/float")
        if sppasType().is_number(x2) is False:
            raise AnnDataTypeError(x2, "int/float")

        return x1 == x2

    # -----------------------------------------------------------------------

    @staticmethod
    def greater(x1, x2):
        """ Return True if numerical value x1 is greater than x2.

        :param x1: (int, float)
        :param x2: (int, float)
        :returns: (bool)

        """
        if sppasType().is_number(x1) is False:
            raise AnnDataTypeError(x1, "int/float")
        if sppasType().is_number(x2) is False:
            raise AnnDataTypeError(x2, "int/float")

        return x1 > x2

    # -----------------------------------------------------------------------

    @staticmethod
    def lower(x1, x2):
        """ Return True if numerical value x1 is lower than x2.

        :param x1: (int, float)
        :param x2: (int, float)
        :returns: (bool)

        """
        if sppasType().is_number(x1) is False:
            raise AnnDataTypeError(x1, "int/float")
        if sppasType().is_number(x2) is False:
            raise AnnDataTypeError(x2, "int/float")

        return x1 < x2

    # -----------------------------------------------------------------------

    @staticmethod
    def bool(x1, x2):
        """ Return True if boolean x is equal to boolean x2.

        :param x1: (bool)
        :param x2: (bool)
        :returns: (bool)

        """
        if sppasType().is_bool(x1) is False:
            raise AnnDataTypeError(x1, "bool")
        if sppasType().is_bool(x2) is False:
            raise AnnDataTypeError(x2, "bool")

        return x1 == x2

    # -----------------------------------------------------------------------

    def create(self, name, arg, opt=None):
        """ Create the function corresponding to the given name.

        The name must correspond to only one method of this class.

        :param name: (str) Name of the function
        :param arg: (str) Argument of the function
        :param opt: (str) Options [not used].
        :returns: function

        """
        # get the function corresponding to the given name
        pattern_funct = self.get(name)

        # define the function to be returned:
        # the one matching with the given name and applied with the given argument.
        def wrap_function(annotation):
            """ The created function to be returned.

            :param annotation: (sppasAnnotation) Annotation for which the
            function has to be applied on the labels.

            """
            texts = list()
            for label in annotation.get_labels():
                for tag, score in label:
                    texts.append(tag.get_typed_content())

            return any(pattern_funct(t, arg) for t in texts)

        return wrap_function

# ---------------------------------------------------------------------------


class PatternMatching(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Predicate Factory for pattern matching.

    """
    def __new__(cls, **kwargs):
        """ Create the predicate for a pattern matching in an annotation.

        :param kwargs:

            exact (str)
            iexact (str)
            startswith (str)
            istartswith (str)
            endswith (str)
            iendswith
            contains (str)
            icontains
            regexp (str)

            lower (int/float)
            greater (int/float)
            equal (int/float)

            bool (bool)

        :returns: (sppasPredicate)

        """
        functions = list()
        if not kwargs:
            functions.append(lambda a: True)

        for func_name, param in kwargs.items():
            funct = sppasPatternMatchingCompare().create(func_name, param)
            functions.append(funct)

        return functools.reduce(operator.and_, (sppasPredicate(f) for f in functions))
