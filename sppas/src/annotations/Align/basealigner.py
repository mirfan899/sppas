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

from resources.mapping import Mapping
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
    def __init__(self, modelfilename, mapping=None):
        """
        Constructor.

        @param modelfilename (str) the acoustic model file name
        @param mapping (Mapping) a mapping table to convert the phone set

        """
        if mapping is None:
            mapping = Mapping()
        if isinstance(mapping, Mapping) is False:
            raise TypeError('Aligner expected a Mapping as argument.')

        self._model    = modelfilename
        self._mapping  = mapping
        self._infersp  = False
        self._outext   = ""

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

    def gen_dependencies(self, phones, grammarname, dictname):
        """
        Generate the files the aligner will need (grammar, dictionary).

        @param phones (str - IN) the phonetization to align (spaces separate tokens, pipes separate variants, minus separate phones)
        @param grammarname (str - OUT) the file name of the grammar
        @param dictname (str - OUT) the dictionary file name

        """
        pass

    # -----------------------------------------------------------------------

    def run_alignment(self, inputwav, basename, outputalign):
        """
        Execute an external program to perform forced-alignment.

        @param inputwav (str - IN) the audio input file name, of type PCM-WAV 16000 Hz, 16 bits
        @param basename (str - IN) the base name of the grammar file and of the dictionary file
        @param outputalign (str - OUT) the output file name

        @return (str) A message of the external program.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------
