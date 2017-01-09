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
# File: src.resources.slm.statlangmodel.py
# ---------------------------------------------------------------------------

from resources.slm.arpaio import ArpaIO

# ---------------------------------------------------------------------------


class SLM(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Statistical language model representation.

    """
    def __init__(self):
        """
        Constructor.

        """
        self.model = None

    # -----------------------------------------------------------------------

    def set(self, model):
        """
        Set the model.

        @param model (list - IN) List of lists of tuples for 1-gram, 2-grams, ...

        """
        if not (isinstance(model, list) and all([isinstance(m,list) for m in model])):
            raise TypeError('Expected a list of tuples.')

        self.model = model

    # -----------------------------------------------------------------------

    def load_from_arpa(self, filename):
        """
        Load the model from an ARPA-ASCII file.

        @param filename (str - IN) Filename from which to read the model.

        """
        arpaio = ArpaIO()
        self.model = arpaio.load(filename)

    # -----------------------------------------------------------------------

    def save_as_arpa(self, filename):
        """
        Save the model into an ARPA-ASCII file.

        @param filename (str - OUT) Filename in which to write the model.

        """
        arpaio = ArpaIO()
        arpaio.set( self.model )
        arpaio.save( filename )

    # -----------------------------------------------------------------------

    def evaluate(self, filename):
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def interpolate(self, other):
        """
        An N-Gram language model can be constructed from a linear interpolation
        of several models. In this case, the overall likelihood P(w|h) of a
        word w occurring after the history h is computed as the arithmetic
        average of P(w|h) for each of the models.

        The default interpolation method is linear interpolation. In addition,
        log-linear interpolation of models is possible.
        """
        raise NotImplementedError

    # -----------------------------------------------------------------------
