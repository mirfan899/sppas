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

    src.calculus.calculusexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for calculus package.

"""
from . import t

# -----------------------------------------------------------------------

VECTORS_ERROR = ":ERROR 3010: "
EUCLIDIAN_DISTANCE_ERROR = ":ERROR 3020: "

# -----------------------------------------------------------------------


class VectorsError(Exception):
    """ :ERROR 3010: Both vectors p and q must have the same length and must contain probabilities. """

    def __init__(self):
        self.parameter = VECTORS_ERROR + (t.gettext(VECTORS_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class EuclidianDistanceError(ValueError):
    """ :ERROR 3020: Error while estimating Euclidian distances of rows and columns. """

    def __init__(self):
        self.parameter = EUCLIDIAN_DISTANCE_ERROR + (t.gettext(EUCLIDIAN_DISTANCE_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------
