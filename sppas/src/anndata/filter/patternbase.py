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

    src.anndata.filter.patternbase.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


class sppasPatternBaseCompare(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Base class for pattern matching comparisons.

    """
    def __init__(self):
        """ Create a sppasPatternDurationCompare instance. """

        self.methods = dict()

    # -----------------------------------------------------------------------

    def get(self, name):
        """ Return the function of the given name.

        :param name: (str) Simple name of a method of this class

        """
        if name in self.methods:
            return self.methods[name]
        raise ValueError('Unknown function name: %s' % name)

    # -----------------------------------------------------------------------

    def create(self, name, arg, opt="best"):
        """ Create the function corresponding to the given name.

        The name must correspond to only one method of this class.

        :param name: (str) Name of the function
        :param arg: (str) Argument of the function
        :param opt: (str) Options, for annotation selections
        :returns: function

        """
        raise NotImplementedError
