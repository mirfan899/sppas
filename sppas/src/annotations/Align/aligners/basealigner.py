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
# File: basealigner.py
# ---------------------------------------------------------------------------

import os
import random
import shutil
from datetime import date

from resources.acm.tiedlist import TiedList

# ---------------------------------------------------------------------------

class BaseAligner:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Base class for an automatic alignment system.

    A base class for a system to perform phonetic speech segmentation.

    """
    def __init__(self, modelfilename):
        """
        Constructor.

        @param modelfilename (str) the acoustic model file name

        """
        self._model    = modelfilename

        self._infersp  = False
        self._outext   = "" # output file name extension
        self._phones   = "" # string of the phonemes to time-align
        self._tokens   = "" # string of the tokens to time-align

    # -----------------------------------------------------------------------

    def get_outext(self):
        """
        Return the extension for output files.

        @return str

        """
        return self._outext

    # -----------------------------------------------------------------------

    def get_infersp(self):
        """
        Return the infersp option value.

        @return boolean value

        """
        return self._infersp

    # -----------------------------------------------------------------------

    def set_infersp(self, infersp):
        """
        Fix the infersp option.

        @param infersp (bool) If infersp is set to True, the system will
        add a short pause at the end of each token, and the automatic aligner
        will infer if it is appropriate or not.

        """
        self._infersp = infersp

    # -----------------------------------------------------------------------

    def add_tiedlist(self, entries):
        """
        Add missing triphones/biphones in the tiedlist of the model.

        @param entries (list) List of missing entries into the tiedlist.

        """
        tiedfile = os.path.join(self._model, "tiedlist")
        if os.path.exists( tiedfile ) is False:
            return []

        tie = TiedList()
        tie.load( tiedfile )
        addentries = []
        for entry in entries:
            if tie.is_observed( entry ) is False and tie.is_tied( entry ) is False:
                ret = tie.add_tied( entry )
                if ret is True:
                    addentries.append(entry)

        if len(addentries) > 0:
            today          = str(date.today())
            randval        = str(int(random.random()*10000))
            backuptiedfile = os.path.join(self._model, "tiedlist."+today+"."+randval)
            shutil.copy( tiedfile,backuptiedfile )
            tie.save( tiedfile )

        return addentries

    # ------------------------------------------------------------------------

    def set_phones(self, phones):
        """
        Fix the pronunciations of each token.

        @param phones (str)

        """
        self._phones = phones

    # ------------------------------------------------------------------------

    def set_tokens(self, tokens):
        """
        Fix the tokens.

        @param tokens (str)

        """
        self._tokens = tokens

    # -----------------------------------------------------------------------

    def run_alignment(self, inputwav, outputalign):
        """
        Execute an external program to perform forced-alignment.
        It is expected that the alignment is performed on a file with a size
        less or equal to a sentence (sentence/IPUs/segment/utterance).

        @param inputwav (str - IN) the audio input file name, of type PCM-WAV 16000 Hz, 16 bits
        @param outputalign (str - OUT) the output file name

        @return (str) A message of the external program.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------
