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

import logging

import annotationdata.io
from annotationdata.tier import Tier
from annotationdata.transcription import Transcription

from resources.dictpron import DictPron
from phonetize import DictPhon

from sp_glob import ERROR_ID, WARNING_ID, OK_ID
from sp_glob import UNKSTAMP

# ---------------------------------------------------------------------------

class sppasPhon( object ):
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
    def __init__(self, dictfilename, logfile=None):
        """
        Constructor.

        @param dictfilename (str) is the pronunciation dictionary file name
        (HTK-ASCII format, utf8).
        @param logfile (sppasLog) is a log file utility class member.

        """
        pdict = DictPron(dictfilename, unkstamp=UNKSTAMP, nodump=False)
        self.phonetizer = DictPhon( pdict )
        self.logfile = logfile

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

        @param unk (bool) If unk is set to True, the system will attempt to
        phonetize unknown entries (i.e. tokens missing in the dictionary).
        Otherwise, the phonetization of an unknown entry unit is set to the
        default string.

        """
        self._options['phonunk'] = unk

    # -----------------------------------------------------------------------

    def set_usestdtokens(self,stdtokens):
        """
        Fix the stdtokens option.

        @param stdtokens (bool) If it is set to True, the phonetization
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

        @param dictfilename (str) The pronunciation dictionary.

        """
        pdict = DictPron(dictfilename, unkstamp=UNKSTAMP, nodump=False)
        self.phonetizer = DictPhon( pdict )

    # -----------------------------------------------------------------------

    def phonetize(self, label):
        """
        Phonetize a text.

        @param label (str) The string to be phonetized.
        @return phonetization of `label`.

        """
        tab = self.phonetizer.get_phon_tokens( label.split(), phonunk=self._options['phonunk'])
        tabphon = []
        for t,p,s in tab:
            message = None
            if s == ERROR_ID:
                message = "%s is missing in the dictionary and can't be phonetized automatically."%t
                return ""
            else:
                tabphon.append( p )
                if s == WARNING_ID:
                    message = "%s is missing in the dictionary. It was automatically phonetized as: %s"%(t,p)

            if message:
                if self.logfile:
                    self.logfile.print_message(message, indent=3, status=s)
                else:
                    logging.info('Phonetization. %s'%message)

        return " ".join(tabphon)

    # -----------------------------------------------------------------------

    def convert(self, tier, variants=True):
        """
        Phonetize all labels of a tier.

        @param tier (Tier) contains the orthographic transcription previously tokenized.
        @return A tier with name "Phonetization"

        """
        t = Tier("Phonetization")
        if tier is None: return t

        for a in tier:
            phon = ''
            # Do not phonetize an unlabelled interval!
            if not a.GetLabel().IsEmpty():
                try:
                    # Do not phonetize silences
                    if a.GetLabel().IsSilence() is True:
                        phon = a.GetLabel().GetValue()
                    elif a.GetLabel().IsPause() is True:
                        phon = "sil"
                    else:
                        _label = a.GetLabel().GetValue()
                        # Do not phonetize empty intervals!
                        if len(_label)>0:
                            phon = self.phonetize( _label )
                except Exception as e:
                    raise Exception('Phonetization error of %s. Error: %s'%(a,str(e)))

            new_phon = a.Copy()
            new_phon.GetLabel().SetValue( phon )
            t.Append( new_phon )

        return t

    # -----------------------------------------------------------------------

    def save(self, trsinput, inputfilename, trsoutput, outputfile=None):
        """
        Save depending on the given data.
        If no output file name is given, output is appended to the input.

        @param trsinput (Transcription)
        @param inputfilename (str)
        @param trsoutput (Transcription)
        @param outputfile (str)

        """
        # Append to the input
        if outputfile is None:
            for tier in trsoutput:
                trsinput.Append(tier)
            trsoutput  = trsinput
            outputfile = inputfilename

        # Save in a file
        annotationdata.io.write( outputfile,trsoutput )

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

    # -----------------------------------------------------------------------

    def run( self, inputfilename, outputfile=None ):
        """
        Run the Phonetization process on an input file.

        @param inputfilename is the input file name
        @param outputfile is the output file name of the phonetization

        """
        # Get the tier to be phonetized.
        trsinput = annotationdata.io.read( inputfilename )
        tierinput = self.get_input_tier(trsinput)
        if tierinput is None:
            raise Exception("No tier found with tokenization. "
                            "One of the tier names must contain 'tok' (or 'trans').")

        # Phonetize the tier
        tierphon = self.convert( tierinput )

        # Save
        trsoutput = Transcription()
        trsoutput.Append( tierphon )
        self.save(trsinput, inputfilename, trsoutput, outputfile)

    # -----------------------------------------------------------------------
