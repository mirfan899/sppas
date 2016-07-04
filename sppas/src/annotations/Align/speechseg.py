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
# File: speechseg.py
# ----------------------------------------------------------------------------

import codecs

from sp_glob import encoding
from resources.rutils   import ToStrip

import aligners

# ----------------------------------------------------------------------------

class SpeechSegmenter:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Automatic speech segmentation.

    Speech segmentation of a unit of speech (an IPU/utterance/sentence/segment).

    """
    def __init__(self, model, alignername=aligners.DEFAULT_ALIGNER):
        """
        Constructor.

        @param model is the acoustic model directory name. It is expected
        to contain at least a file with name "hmmdefs". It can also contain:
            - tiedlist file;
            - monophones.repl file;
            - config file.
        Any other file will be ignored.

        """
        # Options, must be fixed before to instantiate the aligner
        self._infersp = False

        # The acoustic model directory
        self._modeldir = model

        # The automatic alignment system:
        # The basic aligner is used:
        #   - when the track contains only one phoneme;
        #   - when the automatic alignment system failed to perform segmn.
        self.set_aligner(alignername)
        self._basicaligner = aligners.instantiate(None)
        self._instantiate_aligner()

    # ------------------------------------------------------------------------

    def set_model(self, model):
        """
        Fix an acoustic model to perform time-alignment.

        @param model (string) Directory that contains the Acoustic Model.

        """
        self._modeldir = model
        self._instantiate_aligner()

    # ----------------------------------------------------------------------

    def set_aligner(self, alignername):
        """
        Fix the name of the aligner, one of ALIGNERS.

        @param alignername (string) Case-insensitive name of an aligner system.

        """
        alignername = aligners.check(alignername)
        self._alignerid = alignername
        self._instantiate_aligner()

    # ----------------------------------------------------------------------

    def set_infersp(self, infersp):
        """
        Fix the automatic inference of short pauses.

        @param infersp (bool) If infersp is set to True, a short pause is
        added at the end of each token, and the automatic aligner will infer
        if it is relevant or not.

        """
        self._infersp = infersp
        self._aligner.set_infersp( infersp )

    # ----------------------------------------------------------------------

    def get_aligner(self):
        """
        Return the aligner name.

        """
        return self._alignerid

    # ----------------------------------------------------------------------

    def get_aligner_ext(self):
        """
        Return the output file extension the aligner will use.

        """
        return self._aligner.get_outext()

    # ----------------------------------------------------------------------

    def get_model(self):
        """
        Return the model directory name.

        """
        return self._modeldir

    # ------------------------------------------------------------------------

    def segmenter(self, audiofilename, phonname, tokenname, alignname):
        """
        Call an aligner to perform speech segmentation and manage errors.

        @param audiofilename (str - IN) the audio file name of an IPU
        @param phonname (str - IN) the file name with the phonetization
        @param tokenname (str - IN) the file name with the tokenization
        @param alignname (str - OUT) the file name to save the result

        @return A message of the aligner in case of any problem, or
        an empty string if success.

        """
        # Get the phonetization and tokenization strings to time-align.
        phones = ""
        tokens = ""

        if phonname is not None:
            phones = self._readline(phonname)
        self._aligner.set_phones( phones )
        self._basicaligner.set_phones( phones )

        if tokenname is not None:
            tokens = self._readline(tokenname)
        self._aligner.set_tokens( tokens )
        self._basicaligner.set_tokens( tokens )

        # Do not align nothing!
        if len(phones) == 0:
            self._basicaligner.run_alignment(audiofilename, alignname)
            return "Empty annotation: nothing to align."

        # Do not align only one phoneme!
        if len(phones.split()) <= 1 and "-" not in phones:
            self._basicaligner.run_alignment(audiofilename, alignname)
            return ""

        # Execute Alignment
        ret = self._aligner.run_alignment(audiofilename, alignname)

        return ret

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _instantiate_aligner(self):
        """
        Instantiate self._aligner to the appropriate Aligner system.

        """
        self._aligner = aligners.instantiate( self._modeldir,self._alignerid )
        self._aligner.set_infersp( self._infersp )

    # ------------------------------------------------------------------------

    def _readline(self, filename):
        """
        Return the first line of filename, formatted.

        """
        try:
            with codecs.open(filename, 'r', encoding) as fp:
                return ToStrip(fp.readline())
        except Exception:
            return "" # IOError

        return "" # Empty file

    # ----------------------------------------------------------------------
