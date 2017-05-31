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

    src.annotations.Intsint.sppasintsint.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import sppas.src.annotationdata.aio
from sppas.src.annotationdata.transcription import Transcription

from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import NoInputError
from ..annotationsexc import EmptyInputError

from .intsint import Intsint

# ---------------------------------------------------------------------------


class sppasIntsint(sppasBaseAnnotation):
    """
    :author:       Tatsuya Watanabe, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS integration of the INTSINT automatic annotation.

    """
    def __init__(self, logfile=None):
        """ Create a new sppasIntsint instance.

        :param logfile: (sppasLog)

        """
        sppasBaseAnnotation.__init__(self, logfile)

        self.intsint = Intsint()

    # -----------------------------------------------------------------------
    # Methods to annotate
    # -----------------------------------------------------------------------

    @staticmethod
    def anchors_from_tiers(momel_tier):
        """ Initialize INTSINT attributes from a Tier with anchors.
        
        :param momel_tier: (Tier)

        """
        targets = []
        for target in momel_tier:
            f0 = float(target.GetLabel().GetValue())
            targets.append((target.GetLocation().GetPointMidpoint(), f0))

        return targets

    # -------------------------------------------------------------------

    @staticmethod
    def tones_to_tier(tones, momel_tier):
        """ Convert the INTSINT result into a tier.
        
        :param tones: (list)
        :param momel_tier: (Tier)

        """
        intsint_tier = momel_tier.Copy()
        intsint_tier.SetName("INTSINT")

        for tone, target in zip(tones, intsint_tier):
            target.GetLabel().SetValue(tone)

        return intsint_tier

    # -------------------------------------------------------------------

    @staticmethod
    def get_input_tier(trs_input):
        """ Return the tier with anchors.

        :param trs_input: (Transcription)
        :returns: Tier

        """
        for tier in trs_input:
            if "momel" in tier.GetName().lower():
                return tier
        for tier in trs_input:
            if "anchors" in tier.GetName().lower():
                return tier

        return None

    # -----------------------------------------------------------------------

    def run(self, input_filename, output_filename):
        """ Run the INTSINT annotation process on an input file.

        :param input_filename: (str) the input file name with momel
        :param output_filename: (str) the output file name of the INTSINT tier

        """
        # Get the tier to be annotated.
        trs_input = sppas.src.annotationdata.aio.read(input_filename)
        tier_input = self.get_input_tier(trs_input)
        if tier_input is None:
            raise NoInputError
        if tier_input.IsEmpty() is True:
            raise EmptyInputError(name=tier_input.GetName())

        # Annotate the tier
        targets = sppasIntsint.anchors_from_tiers(tier_input)
        tones = self.intsint.annotate(targets)
        tier_intsint = sppasIntsint.tones_to_tier(tones, tier_input)

        # Save
        trs_output = Transcription("sppasINTSINT")
        trs_output.Append(tier_intsint)

        # Save in a file
        sppas.src.annotationdata.aio.write(output_filename, trs_output)
