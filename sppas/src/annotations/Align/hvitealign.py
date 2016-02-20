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
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import sys
import os
import re
from subprocess import Popen, PIPE, STDOUT
import codecs

from basealigner import baseAligner

# ----------------------------------------------------------------------------

class hviteAligner( baseAligner ):
    """
    HTK Alignment.

    http://htk.eng.cam.ac.uk/links/asr_tool.shtml

    """

    def __init__(self, model, mapping, logfile=None):
        """
        Create a new hviteAlign instance.

        @param model is the acoustic model file name,
        @param logfile is a file descriptor of a log file (see log.py).

        """
        baseAligner.__init__(self, model, mapping, logfile)

    # End __init__
    # ------------------------------------------------------------------------


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

        with codecs.open(grammarname, 'w', self._encoding) as flab,\
                codecs.open(dictname, 'w', self._encoding) as fdict:

            fdict.write( "SENT-END [] sil\n" )
            fdict.write( "SENT-START [] sil\n" )

            tokenslist = phones.strip().split(" ")
            tokenidx = 0
            nbtokens = (len(tokenslist)-1)

            for pron in tokenslist:

                # dictionary:
                for i,variant in enumerate(pron.split("|")):

                    # map phonemes (if any)
                    variant = ' ' + variant + ' '
                    for k,v in self._mappingpatch.items():
                        if k in variant:
                            variant = variant.replace(' '+k+' ', ' '+v+' ')

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

    # End gen_dependencies
    # ------------------------------------------------------------------------


    def run_alignment(self, inputwav, basename, outputalign):
        """
        Execute the external program HVite to align.

        @param inputwav is the wav input file name.
        @param basename is the name of the dictionary file
        @param outputalign is the output file name.

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
        if not os.path.isfile(graph):
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
        retval = p.wait()
        line = p.communicate()

        if len(line[0]) > 0 and line[0].find("not found") > -1:
            if self._logfile:
                self._logfile.print_message(' **************** HVite not installed ************** ',status=-1)
            else:
                print " **************** ERROR: HVite not installed ************** "
            return 1

        if len(line[0]) > 0 and line[0].find("ERROR [") > -1:
            return 1

        # Write the program output at the end of the log file
        try:
            if len(line[0]) > 0:
                #THIS DOES NOT WORK on Windows if line[0] contains accentuated characters:
                #   l = unicodedata.normalize('NFKD', line[0]).encode('ascii', 'ignore')
                #THEN.... Try an other solution to remove all strange characters in this string:
                import re
                l = re.sub(ur'[^a-zA-Z0-9\',\s]', '',line[0])
                if self._logfile:
                    self._logfile.print_message(l.strip(),indent=4 )
            else:
                if self._logfile:
                    self._logfile.print_message('No results with command "%r"' % command, indent=3,status=-1)
                print "EXEC ERROR 1"
                return 1
        except Exception as e:
            if self._logfile:
                self._logfile.print_message(str(e),indent=3,status=-1)
            else:
                print "Unknown error."
            print "EXEC ERROR 2"
            return 1

        if os.path.isfile(outputalign):
            with codecs.open(outputalign, 'r', self._encoding) as f:
                line = f.readlines()
                if len(line)==1:
                    return 1

        return 0

    # End run_alignment
    # ------------------------------------------------------------------------
