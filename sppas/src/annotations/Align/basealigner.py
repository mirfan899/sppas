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
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------


class baseAligner:
    """
    Factory class for an automatic alignment system, ie a system to perform
    phonetic speech segmentation.
    """

    def __init__(self, model, mapping, logfile=None):
        """
        Create a new baseAligner instance.

        @param model is the acoustic model file name,
        @param logfile is a file descriptor of a log file (see log.py).

        """
        self._encoding ='utf-8'
        self._model    = model
        self._logfile  = logfile
        self._infersp  = False

        self._mapping = mapping
        self._mappingpatch = {}
        self._mappingpatch["UNK"] = "sil"

    # End __init__
    # ------------------------------------------------------------------------


    def set_infersp(self, infersp):
        """
        Fix the infersp option.
        If infersp is set to True, sppasAlign() will add a short pause at
        the en of each token, and the automatic aligner will infer if it is
        appropriate or not.

        @param infersp is a Boolean

        """
        self._infersp = infersp

    # End set_infersp
    # ----------------------------------------------------------------------


    def gen_dependencies(self, phones, grammarname, dictname):
        """
        Generate the dependencies (grammar, dictionary).

        @param phones is the phonetization to align (spaces separate tokens, pipes separate variants, dots separate phones)
        @param dfaname is the file name of the grammar (output)
        @param dictname is the dictionary file name (output)

        """
        pass

    # End gen_dependencies
    # ------------------------------------------------------------------------


    def run_alignment(self, inputwav, basename, outputalign):
        """
        Execute the external program to perform alignment.

        @param inputwav is the wav input file name.
        @param basename is the basename for the grammar file and the dictionary file
        @param outputalign is the output file name.

        """
        raise NotImplementedError

    # End run_alignment
    # ------------------------------------------------------------------------
