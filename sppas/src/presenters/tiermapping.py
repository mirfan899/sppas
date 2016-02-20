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
# File: tiermapping.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------

from resources.mapping import Mapping

# ----------------------------------------------------------------------------


class TierMapping( Mapping ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Mapping of labels of annotations of a tier.


    """

    def __init__(self, dictname=None):
        """
        Create a new TierMapping instance.

        @param dictname (string) is the file name with the mapping table (2 columns),

        """
        Mapping.__init__(self, dictname)

    # End __init__
    # ------------------------------------------------------------------


    def run( self, tierinput, outtiername=None ):
        """
        Run the TierMapping process on an input tier.

        @param tierinput is the input tier
        @param outtiername is the name to assign to the new tier
        @return a new tier

        """

        if tierinput is None:
            raise Exception("Input tier is None.")

        # Create the output tier
        name = outtiername
        if name is None:
            name = tierinput.GetName()+'-map'
        outtier = tierinput.Copy()
        outtier.SetName( name )

        # hum... nothing to do!
        if tierinput.GetSize() == 0 or self.repl.get_dictsize() == 0:
            return outtier

        # map
        for a in outtier:
            # For each Text instance of this label
            for t in a.GetLabel().GetLabels():
                t.SetValue( self.map( t.GetValue()) )

        return outtier

    # End run
    # ------------------------------------------------------------------------

# End tierMapping
# ---------------------------------------------------------------------------
