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
# File: phon.py
# ---------------------------------------------------------------------------

import sppas.src.annotationdata.aio
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.resources.dictpron import DictPron
from sppas.src.resources.mapping import Mapping

from .. import ERROR_ID, WARNING_ID, INFO_ID, OK_ID
from .. import UNKSTAMP
from ..sppasbase import sppasBase
from .phonetize import DictPhon

# ---------------------------------------------------------------------------


class sppasPhon( sppasBase ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS integration of the Phonetization automatic annotation.

    See DictPhon class for details about automatic phonetization.

    How to use sppasPhon?

    >>> p = sppasPhon( dict )
    >>> p.run(inputtrsname, outputphonfile, outputtokensfile)

    """
    def __init__(self, dictfilename, mapfile=None, logfile=None):
        """
        Constructor.

        @param dictfilename (str) is the pronunciation dictionary file name
        (HTK-ASCII format, utf8).
        @param mapfile (str) is the filename of a mapping table. It is used
        to generate new pronunciations by mapping phonemes of the dictionary.
        @param logfile (sppasLog) is a log file utility class member.
        @raise ValueError if loading the dictionary fails

        """
        sppasBase.__init__(self, logfile)

        # Pronunciation dictionary
        self.maptable = None
        if mapfile is not None:
            self.maptable = Mapping( mapfile )

        self.set_dict( dictfilename )

        # List of options to configure this automatic annotation
        self._options = {}
        self._options['phonunk']      = False # Phonetize missing tokens
        self._options['usestdtokens'] = False # Phonetize standard spelling

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        Available options are:
            - unk
            - usesstdtokens

        @param options (option)

        """
        for opt in options:

            key = opt.get_key()

            if key == "unk":
                self.set_unk( opt.get_value() )

            elif key == "usestdtokens":
                self.set_usestdtokens( opt.get_value() )

            else:
                raise Exception('Unknown key option: %s'%key)

    # -----------------------------------------------------------------------

    def set_unk(self, unk):
        """
        Fix the unk option value.

        @param unk (bool - IN) If unk is set to True, the system will attempt
        to phonetize unknown entries (i.e. tokens missing in the dictionary).
        Otherwise, the phonetization of an unknown entry unit is set to the
        default string.

        """
        self._options['phonunk'] = unk

    # -----------------------------------------------------------------------

    def set_usestdtokens(self,stdtokens):
        """
        Fix the stdtokens option.

        @param stdtokens (bool - IN) If it is set to True, the phonetization
        will use the standard transcription as input, instead of the faked
        transcription. This option does make sense only for an Enriched
        Orthographic Transcription.

        """
        self._options['usestdtokens'] = stdtokens

    # -----------------------------------------------------------------------
    # Methods to phonetize series of data
    # -----------------------------------------------------------------------

    def set_dict(self, dictfilename):
        """
        Set the dictionary.

        @param dictfilename (str- IN) The pronunciation dictionary in HTK-ASCII
        format with UTF-8 encoding.

        """
        pdict = DictPron(dictfilename, unkstamp=UNKSTAMP, nodump=False)
        self.phonetizer = DictPhon( pdict, self.maptable )

    # -----------------------------------------------------------------------

    def phonetize(self, entry):
        """
        Phonetize a text.
        Because we absolutely need to match with the number of tokens, this
        method will always return a string: either the automatic phonetization
        (from dict or from phonunk) or the UNKSTAMP.

        @param entry (str- IN) The string to be phonetized.
        @return phonetization of `label`.

        """
        tab = self.phonetizer.get_phon_tokens( entry.split(), phonunk=self._options['phonunk'])
        tabphon = []
        for t,p,s in tab:
            message = None
            if s == ERROR_ID:
                message = "%s is missing of the dictionary and wasn't phonetized."%t
                return UNKSTAMP
            else:
                if s == WARNING_ID:
                    message = "%s is missing of the dictionary, and "%t
                    if len(p) > 0:
                        message = message +"was automatically phonetized as: %s"%p
                    else:
                        message = message +"wasn't phonetized."
                        p = UNKSTAMP
                tabphon.append( p )

            if message:
                self.print_message(message, indent=3, status=s)

        return " ".join(tabphon)

    # -----------------------------------------------------------------------

    def convert(self, tier, variants=True):
        """
        Phonetize all annotation of a tokenized tier.

        @param tier (Tier - IN) contains the orthographic transcription
        previously tokenized.
        @param variants (bool - IN)
        @return A tier with name "Phonetization"

        """
        t = Tier("Phonetization")
        if tier is None:
            return t

        for a in tier:

            af = a.Copy()
            for text in af.GetLabel().GetLabels():

                if text.IsPause() is True:
                    # In case the pronunciation dictionary were not properly fixed.
                    text.SetValue( "sil" )

                elif text.IsEmpty() is False and text.IsSilence() is False:
                    phon = self.phonetize( text.GetValue() )
                    text.SetValue( phon )

            t.Append( af )

        return t

    # -----------------------------------------------------------------------

    def get_input_tier(self, trsinput):
        """
        Return the tier to be phonetized.

        @param trsinput (Transcription)
        @return Tier

        """
        tierinput = None

        pattern = "fake"
        if self._options['usestdtokens'] is True: # Phonetize standard spelling
            pattern = "standard"

        for tier in trsinput:
            if "tok" in tier.GetName().lower() and pattern in tier.GetName().lower():
                tierinput = tier
                break

        if tierinput is None:
            for tier in trsinput:
                if "tok" in tier.GetName().lower():
                    tierinput = tier
                    break

        if tierinput is None:
            for tier in trsinput:
                if "trans" in tier.GetName().lower():
                    tierinput = tier
                    break

        return tierinput

    # ------------------------------------------------------------------------

    def run( self, inputfilename, outputfile ):
        """
        Run the Phonetization process on an input file.

        @param inputfilename (str - IN) the input file name with tokenization
        @param outputfile (str - IN) the output file name of the phonetization

        """
        self.print_options()
        self.print_diagnosis(inputfilename)

        # Get the tier to be phonetized.
        trsinput = sppas.src.annotationdata.aio.read( inputfilename )
        tierinput = self.get_input_tier(trsinput)
        if tierinput is None:
            raise Exception("No tier found with tokenization. "
                            "One of the tier names must contain 'tok' (or 'trans').")

        # Phonetize the tier
        tierphon = self.convert( tierinput )

        # Save
        trsoutput = Transcription("sppasPhon")
        trsoutput.Append( tierphon )

        # Save in a file
        sppas.src.annotationdata.aio.write( outputfile,trsoutput )

    # -----------------------------------------------------------------------
