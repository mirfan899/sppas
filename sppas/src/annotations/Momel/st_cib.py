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

    src.annotations.Momel.st_cib.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


class Targets(object):
    """
    :author:       Tatsuya Watanabe, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      A class to store one selected target.

    A target is made of 2 or 3 values:
        - x: float ; required
        - y: float ; required
        - p: int   ; optional
    Use getters and setters to manipulate x, y and p

    """
    def __init__(self):
        """Create a new Targets instance with default values."""

        self.__x = 0.
        self.__y = 0.
        self.__p = 0

    # ------------------------------------------------------------------

    def set(self, x, y, p=0):
        """Set new values to a target.

        :param x: (float)
        :param y: (float)
        :param p: (int)

        """
        self.set_x(x)
        self.set_y(y)
        self.set_p(p)

    # ------------------------------------------------------------------

    def set_x(self, x):
        """Set a new x value to a target.

        :param x: (float)

        """
        self.__x = float(x)

    # ------------------------------------------------------------------

    def set_y(self, y):
        """Set a new y value to a target.

        :param y: (float)

        """
        self.__y = float(y)

    # ------------------------------------------------------------------

    def set_p(self, p):
        """Set a new p value to a target.

        :param p: (int)

        """
        self.__p = int(p)

    # ------------------------------------------------------------------

    def get_x(self):
        """Return the x value of a target."""
        return self.__x

    # ------------------------------------------------------------------

    def get_y(self):
        """Return the y value of a target."""
        return self.__y

    # ------------------------------------------------------------------

    def get_p(self):
        """Return the p value of a target."""
        return self.__p

    # ------------------------------------------------------------------

    def print_cib(self, output, pas_x=1, pas_y=1):
        to_print = str(self.__x * pas_x) + " " + str(self.__y * pas_y)
        output.write(to_print + "\n")
