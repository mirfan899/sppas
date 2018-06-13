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

    src.structs.predicate.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

    By definition, a predicate takes quantified entities as input and
    outputs either True or False.

"""


class sppasPredicate(object):
    """
    :author:       Brigitte Bigi, Tatsuya Watanabe
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Define AND, OR and NOT operators for functions. 

    """
    def __init__(self, pred):
        """ Create a sppasPredicate instance.
        
        :param pred: Boolean function.
        
        >>> pred = sppasPredicate(lambda x: x % 3 == 0) | sppasPredicate(lambda x: x % 5 == 0)
        >>> [x for x in range(16) if pred(x)]
        [0, 3, 5, 6, 9, 10, 12, 15]

        >>> pred = sppasPredicate(lambda x: x % 3 == 0) & sppasPredicate(lambda x: x % 5 == 0)
        >>> [x for x in range(16) if pred(x)]
        [0, 15]
        
        """
        self.__pred = pred

    # -----------------------------------------------------------------------

    def __call__(self, *args, **kwargs):
        """ Allows this class to be callable like a function.

        Expected arguments are quantified entities on which the predicate
        has to be applied.

        """
        return self.__pred(*args, **kwargs)

    # -----------------------------------------------------------------------

    def __or__(self, other):
        """ Implements OR operator between self and other functions. """

        def func(*args, **kwargs):
            return self(*args, **kwargs) or other(*args, **kwargs)
        func.__name__ = "%s OR %s" % (str(self), str(other))
        return sppasPredicate(func)

    # -----------------------------------------------------------------------

    def __and__(self, other):
        """ Implements AND operator between self and other functions. """

        def func(*args, **kwargs):
            return self(*args, **kwargs) and other(*args, **kwargs)
        func.__name__ = "%s AND %s" % (str(self), str(other))
        return sppasPredicate(func)

    # -----------------------------------------------------------------------

    def __invert__(self):
        """ Implements NOT operator between self and other functions. """

        def func(*args, **kwargs):
            return not self(*args, **kwargs)
        func.__name__ = "NOT (%s)" % (str(self),)
        return sppasPredicate(func)

    # -----------------------------------------------------------------------

    def __str__(self):
        return self.__pred.__name__
