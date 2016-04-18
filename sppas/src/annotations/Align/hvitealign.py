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
# File: hvitealign.py
# ---------------------------------------------------------------------------

import os
from subprocess import Popen, PIPE, STDOUT
import codecs

from basealigner import BaseAligner
from sp_glob import encoding

# ---------------------------------------------------------------------------

class HviteAligner( BaseAligner ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      HVite automatic alignment system.

    http://htk.eng.cam.ac.uk/links/asr_tool.shtml

    """
    def __init__(self, modelfilename, mapping=None):
        """
        Constructor.

        HviteAligner aligns one inter-pausal unit.

        @param modelfilename (str) the acoustic model file name
        @param mapping (Mapping) a mapping table to convert the phone set

        """
        BaseAligner.__init__(self, modelfilename, mapping)
        self._outext = "mlf"

    # -----------------------------------------------------------------------

    def gen_dependencies(self, phones, grammarname, dictname):
        """
        Generate the dependencies (grammar, dictionary) for HVite.

        @param phones is the phonetization to align (spaces separate tokens, pipes separate variants, dots separate phones)
        @param labname is the file name of the tokens (output)
        @param dictname is the dictionary file name (output)

        """
        self._mapping.set_keepmiss(True)
        self._mapping.set_reverse(True)
        phones = self._mapping.map(phones)

        with codecs.open(grammarname, 'w', encoding) as flab,\
                codecs.open(dictname, 'w', encoding) as fdict:

            fdict.write( "SENT-END [] sil\n" )
            fdict.write( "SENT-START [] sil\n" )

            tokenslist = phones.strip().split(" ")
            tokenidx = 0
            nbtokens = (len(tokenslist)-1)

            for pron in tokenslist:

                # dictionary:
                for i,variant in enumerate(pron.split("|")):

                    if self._infersp is True:
                        variant = variant + 'sp'

                    fdict.write( "w_" + str(tokenidx))
                    if i==0:
                        fdict.write(' ')
                    else:
                        fdict.write("("+str(i+1)+") ")
                    fdict.write("[w_"+str(tokenidx)+"] ")
                    fdict.write(variant.replace(".",' ')+"\n" )

                flab.write( "w_" + str(tokenidx)+"\n")

                tokenidx += 1
                nbtokens -= 1

    # -----------------------------------------------------------------------

    def run_hvite(self, inputwav, basename, outputalign):
        """
        Perform the speech segmentation.

        Call the system command `HVite`.

        """
        # Example of use with triphones:
        #
        # HVite -A -D -T 1 -l '*'  -a -b SENT-END -m
        #   -C models-EN/config
        #   -H models-EN/macros
        #   -H models-EN/hmmdefs
        #   -m -t 250.0 150.0 1000.0
        #   -i aligned.out
        #   -y lab
        #   dict/EN.dict
        #   models-EN/tiedlist
        #   file.wav
        #
        # Replace the tiedlist by the list of phonemes for a monophone model

        hmmdefs  = os.path.join(self._model, "hmmdefs")
        macros   = os.path.join(self._model, "macros")
        config   = os.path.join(self._model, "config")
        graph    = os.path.join(self._model, "tiedlist")
        if os.path.isfile(graph) is False:
            graph = os.path.join(self._model, "monophones")

        # Program name
        command = 'HVite -A -D -T 1 -l \'*\'  -a -b SENT-END -m '
        command += ' -C "' + config.replace('"', '\\"') + '"'
        command += ' -H "' + hmmdefs.replace('"', '\\"') + '"'
        if os.path.isfile(macros):
            command += ' -H "' + macros.replace('"', '\\"') + '"'
        command += " -t 250.0 150.0 1000.0"
        command += ' -i "' + outputalign.replace('"', '\\"') + '"'
        command += ' -y lab'
        command += ' "' + basename.replace('"', '\\"') + '"'
        command += ' "' + graph.replace('"', '\\"') + '"'
        command += ' ' + inputwav

        # Execute command
        p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
        p.wait()
        line = p.communicate()

        if len(line[0]) > 0 and line[0].find("not found") > -1:
            raise OSError( "HVite is not properly installed. See installation instructions for details." )

        if len(line[0]) > 0 and line[0].find("ERROR [") > -1:
            raise OSError( "julius command failed." )

        # Check output file
        if os.path.isfile( outputalign ) is False:
            raise Exception('HVite did not created an alignment file.')

    # -----------------------------------------------------------------------

    def run_alignment(self, inputwav, basename, outputalign):
        """
        Execute the external program HVite to align.

        @param inputwav is the wav input file name.
        @param basename is the name of the dictionary file
        @param outputalign is the output file name.

        """
        self.run_hvite(inputwav, basename, outputalign)

        if os.path.isfile(outputalign):
            with codecs.open(outputalign, 'r', encoding) as f:
                lines = f.readlines()
                if len(lines) == 1:
                    raise Exception(lines)

        return ""

    # -----------------------------------------------------------------------
