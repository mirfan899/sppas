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
# File: _bools.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Tatsuya Watanabe, Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import re
import operator

# ----------------------------------------------------------------------------
# Functions to compare 2 strings
# ----------------------------------------------------------------------------


def exact(text1, text2):
    """
    Return True text1 and text2 contain the same characters.

    @param text1: (str)
    @param text2: (str)
    @return: (bool)

    """
    return text1 == text2


def iexact(text1, text2):
    """
    Case-insensitive exact.

    @param text1: (str)
    @param text2: (str)
    @return: (bool)

    """
    return text1.lower() == text2.lower()


def startswith(text1, text2):
    """
    Return True if text1 starts with text2.

    @param text1: (str)
    @param text2: (str)
    @return: (bool)

    """
    return text1.startswith(text2)


def istartswith(text1, text2):
    """
    Case-insensitive startswith.

    @param text1: (str)
    @param text2: (str)
    @return: (bool)

    """
    return text1.lower().startswith(text2.lower())


def endswith(text1, text2):
    """
    Return True if text1 ends with text2.

    @param text1: (str)
    @param text2: (str)
    @return: (bool)

    """
    return text1.endswith(text2)


def iendswith(text1, text2):
    """
    Case-insensitive endswith.

    @param text1: (str)
    @param text2: (str)
    @return: (bool)

    """
    return text1.lower().endswith(text2.lower())


def contains(text1, text2):
    """
    Return True if text1 contains text2.

    @param text1: (str)
    @param text2: (str)
    @return: (bool)

    """
    return text2 in text1


def icontains(text1, text2):
    """
    Case-insensitive contains.

    @param text1: (str)
    @param text2: (str)
    @return: (bool)

    """
    return text2.lower() in text1.lower()


def regexp(text, pattern):
    """
    Return True if text matches pattern.

    @param text: (str)
    @param pattern: (str)
    @return: (bool)

    """
    return True  if re.match(pattern, text) else False


# ----------------------------------------------------------------------------
# Functions to compare 2 numbers (in case of numerical labels)
# ----------------------------------------------------------------------------

def equal(x1, x2):
    """
    Return True if numerical value x1 is equal to x2.

    @param x1: (int, float)
    @param x2: (int, float)
    @return: (bool)

    """
    return x1 == x2


def greater(x1, x2):
    """
    Return True if numerical value x1 is greater than x2.

    @param x1: (int, float)
    @param x2: (int, float)
    @return: (bool)

    """
    return x1 > x2


def lower(x1, x2):
    """
    Return True if numerical value x1 is less than x2.

    @param x1: (int, float)
    @param x2: (int, float)
    @return: (bool)

    """
    return x1 < x2



# ----------------------------------------------------------------------------
# Functions to evaluate a boolean (in case of boolean label)
# ----------------------------------------------------------------------------

def bool(x1, x2):
    """
    Return True if boolean x is equal to boolean x2.

    @param x1: boolean
    @param x2: boolean
    return (boolean)

    """
    return x1 == x2

# ----------------------------------------------------------------------------



# ----------------------------------------------------------------------------
# Functions to deal with Annotation()
# ----------------------------------------------------------------------------


def begin(annotation):
    """
    Get the begin TimePoint of an annotation, or the point.

    @param annotation: (Annotation)
    @return: (TimePoint)

    """
    return annotation.GetLocation().GetPoint() if annotation.GetLocation().IsPoint() else annotation.GetLocation().GetBegin()


def end(annotation):
    """
    Get the end TimePoint of an annotation, or the point.

    @param annotation: (Annotation)
    @return: (TimePoint)

    """
    return annotation.GetLocation().GetPoint() if annotation.GetLocation().IsPoint() else annotation.GetLocation().GetEnd()


def duration(annotation):
    """
    Get the duration of an annotation.

    @param annotation: (Annotation)
    @return: (float)

    """
    return annotation.GetLocation().GetDuration()

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Factory Function
# ----------------------------------------------------------------------------

def create(name, arg, opt="best"):
    """
    Create a function.

    @param name: (str) function name

        - exact
        - iexact
        - startswith
        - istartswith
        - endswith
        - iendswith
        - contains
        - icontains
        - regexp

        - equal
        - greater
        - lower

        - bool

        - begin_lt
        - begin_le
        - begin_gt
        - begin_ge
        - begin_eq
        - end_lt
        - end_le
        - end_gt
        - end_ge
        - end_eq

        - duration_lt
        - duration_le
        - duration_gt
        - duration_ge
        - duration_eq

    @param arg:
    @param opt: option to be used while creating the function:
    "best": search on the best label only, and return true if it is matching the expected function
    "any": search in all labels, and return true if one of them is matching the expected function
    @return: boolean

    """
    functions = name.split("_")
    module = globals()

    if len(functions) == 1:
    # Only one function of this module will be used.

        # get the function corresponding to the given name
        func = module.get(functions[0], None)
        if not func:
            raise Exception('Unknown function: %s' % name)

        # specific case of string/unicode labels, except if regexp
        if "regexp" not in name and isinstance(arg,str):
            arg = " ".join(arg.split())

        if opt=="any":
            def wrap(annotation):
                return any(func(l.GetTypedValue(), arg) for l in annotation.GetLabel().GetLabels())
        else:
            def wrap(annotation):
                return func(annotation.GetLabel().GetTypedValue(), arg)

    elif len(functions) == 2:
    # Two functions of this module will be used.

        func = module.get(functions[0], None)
        comparator = getattr(operator, functions[1], None)
        if None in (func, comparator):
            raise Exception('Unknown function: %s' % name)

        def wrap(annotation):
            time = func(annotation)
            return comparator(time, arg)

    else:
    # No more functions are accepted!
        raise Exception('Unknown function: %s' % name)

    return wrap

# ----------------------------------------------------------------------------
