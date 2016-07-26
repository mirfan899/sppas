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
# File: sppaschunks.py
# ----------------------------------------------------------------------------

import shutil
import os

import utils.fileutils as fileutils

import audiodata.io
import annotationdata.io
from annotationdata.io.utils import gen_id
from annotationdata.media    import Media

from sp_glob import ERROR_ID, WARNING_ID, OK_ID, INFO_ID

from annotations.sppasbase import sppasBase
from annotations.Chunks.chunks import Chunks

# ----------------------------------------------------------------------------

class sppasChunks( sppasBase ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS integration of the Chunk Alignment automatic annotation.

    """
    def __init__(self, model, logfile=None):
        """
        Create a new sppasChunks instance.

        @param model (str) the acoustic model directory name of the language of the text
        @param modelL1 (str) the acoustic model directory name of the mother language of the speaker
        @param logfile (sppasLog)

        """
        sppasBase.__init__(self, logfile)

        self.chunks = Chunks( model )
        self._options['clean']      = True  # Remove temporary files
        self._options['silences']    = self.chunks.get_silences()
        self._options['anchors']     = self.chunks.get_anchors()
        self._options['ngram']       = self.chunks.get_ngram_init()
        self._options['ngrammin']    = self.chunks.get_ngram_min()
        self._options['windelay']    = self.chunks.get_windelay_init()
        self._options['windelaymin'] = self.chunks.get_windelay_min()
        self._options['chunksize']   = self.chunks.get_chunk_maxsize()

    # ------------------------------------------------------------------------
    # Methods to fix options
    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        @param options (option)

        """
        for opt in options:

            key = opt.get_key()

            if "clean" == key:
                self.set_clean( opt.get_value() )

            elif "silences" == key:
                self.chunks.set_silences( opt.get_value() )
                self._options['silences'] = opt.get_value()

            elif "anchors" == key:
                self.chunks.set_anchors( opt.get_value() )
                self._options['anchors'] = opt.get_value()

            elif "ngram" == key:
                self.chunks.set_ngram_init( opt.get_value() )
                self._options['ngram'] = opt.get_value()

            elif "ngrammin" == key:
                self.chunks.set_ngram_min( opt.get_value() )
                self._options['ngrammin'] = opt.get_value()

            elif "windelay" == key:
                self.chunks.set_windelay_init( opt.get_value() )
                self._options['windelay'] = opt.get_value()

            elif "windelaymin" == key:
                self.chunks.set_windelay_min( opt.get_value() )
                self._options['windelaymin'] = opt.get_value()

            elif "chunksize" == key:
                self.chunks.set_chunk_maxsize( opt.get_value() )
                self._options['chunksize'] = opt.get_value()

            else:
                raise KeyError('Unknown key option: %s'%key)

    # ----------------------------------------------------------------------

    def set_clean(self, clean):
        """
        Fix the clean option.

        @param clean (bool - IN) If clean is set to True then temporary files
        will be removed.

        """
        self._options['clean'] = clean

    # ----------------------------------------------------------------------

    def get_phonestier(self, trsinput):
        """
        Return the tier with phonetization or None.

        """
        if trsinput.GetSize() == 1 and trsinput[0].GetName().lower() == "rawtranscription":
            return trsinput[0]

        return None

    # ------------------------------------------------------------------------

    def get_tokenstier(self, trsinput):
        """
        Return the tier with tokens, or None.

        In case of EOT, 2 tiers with tokens are available: std and faked.
        Priority is given to std.

        """
        if trsinput.GetSize() == 1 and trsinput[0].GetName().lower() == "rawtranscription":
            return trsinput[0]

        return None

    # ------------------------------------------------------------------------

    def run(self, phonesname, tokensname, audioname, outputfilename):
        """
        Execute SPPAS Chunks alignment.

        @param phonesname (str - IN) file containing the phonetization
        @param tokensname (str - IN) file containing the tokenization
        @param audioname (str - IN) Audio file name
        @param outputfilename (str - IN) the file name with the result

        @return Transcription

        """
        self.print_options()
        self.print_diagnosis(audioname, phonesname, tokensname)

        # Get the tiers to be time-aligned
        # ---------------------------------------------------------------

        trsinput = annotationdata.io.read( phonesname )
        phontier = self.get_phonestier( trsinput )
        if phontier is None:
            raise IOError("No tier with the raw phonetization was found.")

        try:
            trsinputtok = annotationdata.io.read( tokensname )
            toktier = self.get_tokenstier( trsinputtok )
        except Exception:
            raise IOError("No tier with the raw tokenization was found.")

        # Prepare data
        # -------------------------------------------------------------

        inputaudio = fileutils.fix_audioinput(audioname)
        workdir    = fileutils.fix_workingdir(inputaudio)
        if self._options['clean'] is False:
            self.print_message( "The working directory is: %s"%workdir, indent=3, status=None )

        # Processing...
        # ---------------------------------------------------------------

        try:
            trsoutput = self.chunks.create_chunks( inputaudio,phontier,toktier,workdir )
        except Exception as e:
            self.print_message( str(e) )
            self.print_message("WORKDIR=%s"%workdir)
            if self._options['clean'] is True:
                shutil.rmtree( workdir )
            raise

        # Set media
        # --------------------------------------------------------------

        extm = os.path.splitext(audioname)[1].lower()[1:]
        media = Media( gen_id(), audioname, "audio/"+extm )
        trsoutput.AddMedia( media )
        for tier in trsoutput:
            tier.SetMedia( media )

        # Save results
        # --------------------------------------------------------------
        try:
            self.print_message("Save automatic chunk alignment: ",indent=3)
            # Save in a file
            annotationdata.io.write( outputfilename,trsoutput )
        except Exception:
            if self._options['clean'] is True:
                shutil.rmtree( workdir )
            raise

        # Clean!
        # --------------------------------------------------------------
        # if the audio file was converted.... remove the tmpaudio
        if inputaudio != audioname:
            os.remove(inputaudio)
        # Remove the working directory we created
        if self._options['clean'] is True:
            shutil.rmtree( workdir )

