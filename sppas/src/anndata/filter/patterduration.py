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

    src.anndata.filter.patternduration.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Search in durations of annotations.

"""
import operator
import functools

from sppas.src.utils.datatype import sppasType
from sppas.src.structs.predicate import sppasPredicate
from ..anndataexc import AnnDataTypeError
from .patternbase import sppasPatternBaseCompare

# ---------------------------------------------------------------------------


class sppasPatternDurationCompare(sppasPatternBaseCompare):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Pattern matching on strings.

    """
    def __init__(self):
        """ Create a sppasPatternDurationCompare instance. """

        sppasPatternBaseCompare.__init__(self)
        self.methods['eq'] = sppasPatternDurationCompare.eq
        self.methods['ne'] = sppasPatternDurationCompare.ne
        self.methods['gt'] = sppasPatternDurationCompare.gt
        self.methods['lt'] = sppasPatternDurationCompare.lt
        self.methods['le'] = sppasPatternDurationCompare.le
        self.methods['ge'] = sppasPatternDurationCompare.ge

    # -----------------------------------------------------------------------

    @staticmethod
    def eq(x1, x2):
        """ Return True if numerical value x1 is equal to x2.

        :param x1: (int, float)
        :param x2: (int, float)
        :returns: (bool)

        """
        if sppasType().is_number(x2) is False:
            raise AnnDataTypeError(x2, "int/float")

        return x1 == x2

    # -----------------------------------------------------------------------

    @staticmethod
    def ne(x1, x2):
        """ Return True if numerical value x1 is different to x2.

        :param x1: (int, float)
        :param x2: (int, float)
        :returns: (bool)

        """
        if sppasType().is_number(x2) is False:
            raise AnnDataTypeError(x2, "int/float")

        return x1 != x2

    # -----------------------------------------------------------------------

    @staticmethod
    def gt(x1, x2):
        """ Return True if numerical value x1 is greater than x2.

        :param x1: (int, float)
        :param x2: (int, float)
        :returns: (bool)

        """
        if sppasType().is_number(x2) is False:
            raise AnnDataTypeError(x2, "int/float")

        return x1 > x2

    # -----------------------------------------------------------------------

    @staticmethod
    def lt(x1, x2):
        """ Return True if numerical value x1 is lower than x2.

        :param x1: (int, float)
        :param x2: (int, float)
        :returns: (bool)

        """
        if sppasType().is_number(x2) is False:
            raise AnnDataTypeError(x2, "int/float")

        return x1 < x2

    # -----------------------------------------------------------------------

    @staticmethod
    def ge(x1, x2):
        """ Return True if numerical value x1 is greater or equal than x2.

        :param x1: (int, float)
        :param x2: (int, float)
        :returns: (bool)

        """
        if sppasType().is_number(x2) is False:
            raise AnnDataTypeError(x2, "int/float")

        return x1 >= x2

    # -----------------------------------------------------------------------

    @staticmethod
    def le(x1, x2):
        """ Return True if numerical value x1 is lower or equal than x2.

        :param x1: (int, float)
        :param x2: (int, float)
        :returns: (bool)

        """
        if sppasType().is_number(x2) is False:
            raise AnnDataTypeError(x2, "int/float")

        return x1 <= x2

    # -----------------------------------------------------------------------

    def create(self, name, arg, opt="margin"):
        """ Create the function corresponding to the given name.

        The name must correspond to only one method of this class.

        :param name: (str) Name of the function
        :param arg: (str) Argument of the function
        :param opt: (str) Compare using the duration margin (estimated from the localization radius).
        Instead, the exact duration value is compared.

        :returns: function

        """
        # get the function corresponding to the given name
        pattern_funct = self.get(name)

        # define the function to be returned:
        # the one matching with the given name and applied with the given argument.
        def wrap_function(annotation):
            """ The created function to be returned.

            :param annotation: (sppasAnnotation) Annotation for which the
            function has to be applied on its duration.

            """
            durations = list()
            for location in annotation.get_locations():
                for loc, score in location:
                    if opt == "margin":
                        durations.append(loc.duration())
                    else:
                        durations.append(loc.duration().get_value())

            return any(pattern_funct(d, arg) for d in durations)

        return wrap_function

# ---------------------------------------------------------------------------


class PatternDuration(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Predicate Factory for search in annotation about its duration.

    """
    def __new__(cls, **kwargs):
        """ Create the predicate for a selection of the duration of an annotation.

        :param kwargs:
            gt: greater than
            lt: lower than
            eq: equal
            ge: greater or equal than
            le: lower or equal than

        :returns: (sppasPredicate)

        """
        functions = list()
        if not kwargs:
            functions.append(lambda a: True)

        for func_name, param in kwargs.items():
            funct = sppasPatternDurationCompare().create(func_name, param)
            functions.append(funct)

        return functools.reduce(operator.and_, (sppasPredicate(f) for f in functions))
