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

    src.calculus.kappa.py
    ~~~~~~~~~~~~~~~~~~~~~

    Inter-observer variation can be measured in any situation in which two or
    more independent observers are evaluating the same thing. The Kappa
    statistic seems the most commonly used measure of inter-rater agreement
    in Computational Linguistics.

"""

from __future__ import division

from .geometry.distances import squared_euclidian as sq

# ----------------------------------------------------------------------------


class Kappa(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    :summary:      Inter-observer variation estimation.

    Kappa is intended to give the reader a quantitative measure of the
    magnitude of agreement between observers.
    The calculation is based on the difference between how much agreement is
    actually present (“observed” agreement) compared to how much agreement
    would be expected to be present by chance alone (“expected” agreement).

    >>> p = [ (1., 0.), (0., 1.), (0., 1.), (1., 0.), (1., 0.) ]
    >>> q = [ (1., 0.), (0., 1.), (1., 0.), (1., 0.), (1., 0.) ]
    >>> kappa = Kappa(p, q)
    >>> print p, "is ok? (expect true):", kappa.check_vector(p)
    >>> print q, "is ok? (expect true):", kappa.check_vector(q)
    >>> print "Kappa value:",kappa.evaluate()

    """
    def __init__(self, p, q):
        """ Create a Kappa instance with two lists of tuples p and q.

        >>> p=[ (1., 0.), (1.,0.), (0.8,0.2) ]

        :param p: a vector of tuples of float values
        :param q: a vector of tuples of float values

        """
        self.p = p
        self.q = q

    # -----------------------------------------------------------------------

    def sqv(self):
        """ Estimates the Euclidian distance between two vectors.

        :param p: a vector of tuples of float values
        :param q: a vector of tuples of float values
        :returns: v

        """
        if len(self.p) != len(self.q):
            raise Exception('Both vectors p and q must have the same length '
                            '(got respectively %d and %d).' % 
                            (len(self.p), len(self.q)))

        return sum([sq(x, y) for (x, y) in zip(self.p, self.q)])

    # -----------------------------------------------------------------------

    def sqm(self):
        """ Estimates the Euclidian distance between two vectors.

        :returns: row and col

        """
        if len(self.p) != len(self.q):
            raise Exception('Both vectors p and q must have the same length '
                            '(got respectively %d and %d).' % 
                            (len(self.p), len(self.q)))

        row = list()
        for x in self.p:
            row.append(sum(sq(x, y) for y in self.q))

        col = list()
        for y in self.q:
            col.append(sum(sq(y, x) for x in self.p))

        return row, col

    # -----------------------------------------------------------------------

    def check(self):
        """ Check if the given p and q vectors are correct to be used.

        :returns: bool

        """
        return self.check_vector(self.p) and self.check_vector(self.q)

    # -----------------------------------------------------------------------

    def evaluate(self):
        """ Estimates the Cohen's Kappa between two lists of tuples p and q.

        The tuple size corresponds to the number of categories, each value is
        the score assigned to each category for a given sample.

        :returns: float value

        """
        v = self.sqv() / float(len(self.p))
        row, col = self.sqm()
        if sum(row) != sum(col):
            raise Exception('Hum... error while estimating Euclidian distances.')
        r = sum(row) / float(len(self.p)**2)
        if r == 0.:
            return 1.

        return 1.0 - v/r

    # -----------------------------------------------------------------------

    def check_vector(self, v):
        """
        Check if the vector is correct to be used.

        :param v: a vector of tuples of probabilities.

        """
        # Must contain data!
        if v is None or len(v) == 0:
            return False

        for t in v:
            # Must contain tuples only.
            if not type(t) is tuple:
                return False
            # All tuples have the same size (more than 1).
            if len(t) != len(v[0]) or len(t) < 2:
                return False
            # Tuple values are probabilities.
            s = 0
            for p in t:
                if p < 0. or p > 1.0:
                    return False
                s += p
            if s < 0.999 or s > 1.001:
                return False

        return True

# ----------------------------------------------------------------------------
