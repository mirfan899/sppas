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
# File: sppasintsint.py
# ---------------------------------------------------------------------------

from annotations.sppasbase import sppasBase

import annotationdata.aio
from annotationdata.transcription import Transcription

from annotations.Intsint.intsint import Intsint

from sp_glob import ERROR_ID, WARNING_ID, INFO_ID, OK_ID

# ---------------------------------------------------------------------------

class sppasIntsint( sppasBase ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS integration of the INTSINT automatic annotation.

    """
    def __init__(self, logfile=None):
        """

        """
        sppasBase.__init__(self, logfile)

        self.intsint = Intsint()


    # -----------------------------------------------------------------------
    # Methods to annotate
    # -----------------------------------------------------------------------

    def targets_from_tier(self, momeltier):
        """
        Initialize INTSINT attributes from momel Tier.

        """
        targets = []
        for target in momeltier:
            f0 = float( target.GetLabel().GetValue() )
            targets.append( (target.GetLocation().GetPointMidpoint(),f0) )

        return targets

    # -------------------------------------------------------------------

    def tones_to_tier(self, toneslist, momeltier):
        """
        Convert the INTSINT result into a tier.

        """
        intsinttier = momeltier.Copy()
        intsinttier.SetName("INTSINT")

        for tone,target in zip(toneslist,intsinttier):
            target.GetLabel().SetValue( tone )

        return intsinttier

    # -------------------------------------------------------------------

    def get_input_tier(self, trsinput):
        """
        Return the tier to estimate INTSINT.

        @param trsinput (Transcription)
        @return Tier

        """
        tierinput = None
        for tier in trsinput:
            if "momel" in tier.GetName().lower():
                tierinput = tier
                break

        return tierinput

    # -----------------------------------------------------------------------

    def run( self, inputfilename, outputfile ):
        """
        Run the INTSINT annotation process on an input file.

        @param inputfilename (str - IN) the input file name with momel
        @param outputfile (str - IN) the output file name of the INTSINT tier

        """
        # Get the tier to be annotated.
        trsinput = annotationdata.aio.read( inputfilename )
        tierinput = self.get_input_tier(trsinput)
        if tierinput is None:
            raise Exception("No tier found with momel. "
                            "One of the tier names must contain 'momel'.")

        # Annotate the tier
        targets = self.targets_from_tier( tierinput )
        toneslist = self.intsint.annotate( targets )
        tierintsint = self.tones_to_tier( toneslist, tierinput )

        # Save
        trsoutput = Transcription("sppasIntsint")
        trsoutput.Append( tierintsint )

        # Save in a file
        annotationdata.aio.write( outputfile,trsoutput )

    # -----------------------------------------------------------------------
