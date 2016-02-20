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
# File: juliusalign.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import re
import codecs
from subprocess import Popen, PIPE, STDOUT

from basealigner import baseAligner

# ----------------------------------------------------------------------------

class juliusAligner( baseAligner ):
    """
    Julius Alignment.

    http://julius.sourceforge.jp/en_index.php

    "Julius" is a high-performance, two-pass large vocabulary continuous
    speech recognition (LVCSR) decoder software for speech-related researchers
    and developers. Based on word N-gram and context-dependent HMM, it can
    perform almost real-time decoding on most current PCs in 60k word dictation
    task. Major search techniques are fully incorporated such as tree lexicon,
    N-gram factoring, cross-word context dependency handling, enveloped beam
    search, Gaussian pruning, Gaussian selection, etc.
    Besides search efficiency, it is also modularized carefully to be independent
    from model structures, and various HMM types are supported such as
    shared-state triphones and tied-mixture models, with any number of mixtures,
    states, or phones. Standard formats are adopted to cope with other free
    modeling toolkit such as HTK, CMU-Cam SLM toolkit, etc.

    The main platform is Linux and other Unix workstations, and also works on
    Windows. Most recent version is developed on Linux and Windows (cygwin /
    mingw), and also has Microsoft SAPI version. Julius is distributed with
    open license together with source codes.

    Julius has been developed as a research software for Japanese LVCSR since
    1997, and the work was continued under IPA Japanese dictation toolkit
    project (1997-2000), Continuous Speech Recognition Consortium, Japan (CSRC)
    (2000-2003) and currently Interactive Speech Technology Consortium (ISTC).
    """

    def __init__(self, model, mapping, logfile=None):
        """
        Create a new juliusAlign instance.

        @param model is the acoustic model file name,
        @param logfile is a file descriptor of a log file (see log.py).

        """
        baseAligner.__init__(self, model, mapping, logfile)

    # End __init__
    # ------------------------------------------------------------------------


    def gen_dependencies(self, phones, grammarname, dictname):
        """
        Generate the dependencies (grammar, dictionary) for julius.

        @param phones is the phonetization to align (spaces separate tokens, pipes separate variants, dots separate phones)
        @param dfaname is the file name of the grammar (output)
        @param dictname is the dictionary file name (output)

        """
        self._mapping.set_keepmiss(True)
        self._mapping.set_reverse( True )
        phones = self._mapping.map(phones)

        with codecs.open(grammarname, 'w', self._encoding) as fdfa,\
                codecs.open(dictname, 'w', self._encoding) as fdict:

            tokenslist = phones.strip().split(" ")
            tokenidx = 0
            nbtokens = (len(tokenslist)-1)

            for pron in tokenslist:

                # dictionary:
                for variant in pron.split("|"):

                    # map phonemes (if any)
                    variant = '.' + variant + '.'
                    for k,v in self._mappingpatch.items():
                        if k in variant:
                            variant = variant.replace('.'+k+'.', '.'+v+'.')

                    # write
                    fdict.write( str(tokenidx)+' ' )
                    fdict.write("[w_"+str(tokenidx)+"] ")

                    fdict.write(variant.replace(".",' ')+"\n" )

                # dfa grammar
                if tokenidx == 0:
                    fdfa.write( str(tokenidx)+" "+str(nbtokens)+" "+str(tokenidx+1)+" 0 1\n")
                else:
                    fdfa.write( str(tokenidx)+" "+str(nbtokens)+" "+str(tokenidx+1)+" 0 0\n")
                tokenidx += 1
                nbtokens -= 1

            # last line of the grammar
            fdfa.write( str(tokenidx)+" -1 -1 1 0\n")

    # End gen_dependencies
    # ------------------------------------------------------------------------


    def run_alignment(self, inputwav, basename, outputalign):
        """
        Execute the external program julius to align.

        @param inputwav is the wav input file name.
        @param basename is the basename of the DFA grammar file and dictionary file
        @param outputalign is the output file name.

        """
        tiedlist = os.path.join(self._model, "tiedlist")
        hmmdefs  = os.path.join(self._model, "hmmdefs")

        """ By David Yeung, force Julius to use configuration file of HTK
        """
        config = os.path.join(self._model, "config")

        command = 'echo '
        command += inputwav
        command += ' | julius -input file -h '
        command += '"' + hmmdefs.replace('"', '\\"') + '"'
        command += ' -gram '
        command += '"' + basename.replace('"', '\\"') + '"'
        if os.path.isfile(tiedlist):
            command += ' -hlist '
            command += '"' + tiedlist.replace('"', '\\"') + '"'
        """ By David Yeung, force Julius to use configuration file of HTK
        """
        if os.path.isfile(config):
            command += ' -htkconf '
            command += '"' + config.replace('"', '\\"') + '"'

        command += ' -palign -multipath -penalty1 5.0 -penalty2 20.0 -iwcd1 max -gprune safe -m 10000 -b2 1000 -sb 1000.0 -smpFreq 16000'

        if self._infersp is True:
            command += ' -spmodel "sp" -iwsp -iwsppenalty -70.0'

        command += ' > '

        command += '"' + outputalign.replace('"', '\\"') + '"'

        # Execute command

        p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
        retval = p.wait()
        line = p.communicate()

        if len(line[0]) > 0 and line[0].find("not found") > -1:
            if self._logfile:
                self._logfile.print_message(' **************** julius not installed ************** ',status=-1)
            else:
                print " **************** ERROR: julius not installed ************** "
            return 1

        if len(line[0]) > 0 and line[0].find("-help") > -1:
            if self._logfile:
                self._logfile.print_message(' **************** Bad command: **************\n%s '%command, status=-1)
            else:
                print " **************** ERROR: Bad command. **************\n",command
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
                    self._logfile.print_message(l.strip(),indent=4)
            elif self._logfile:
                self._logfile.print_message('No results with command "%r"' % command,indent=3,status=-1)
        except Exception as e:
            if self._logfile:
                self._logfile.print_message(str(e),indent=3,status=-1)
            else:
                print "Julius command: Unknown error!"

        err = 2
        if os.path.isfile(outputalign):
            with codecs.open(outputalign, 'r', self._encoding) as f:
                for line in f:
                    if (line.find("Error: voca_load_htkdict")>-1):
                        if os.path.isfile(tiedlist):
                            err += 3
                        else:
                            return 1
                    elif (line.find("forced alignment ==="))>-1:
                        err -= 1
        return err

    # End run_julius
    # ------------------------------------------------------------------------
