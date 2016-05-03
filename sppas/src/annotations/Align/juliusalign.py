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

import os
import codecs
import re

from subprocess import Popen, PIPE, STDOUT

from basealigner import BaseAligner

from sp_glob import encoding

# ----------------------------------------------------------------------------

class JuliusAligner( BaseAligner ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Julius automatic alignment system.

    http://julius.sourceforge.jp/en_index.php

    `Julius` is a high-performance, two-pass large vocabulary continuous
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
    def __init__(self, modelfilename, mapping=None):
        """
        Constructor.

        JuliusAligner aligns one inter-pausal unit.

        @param modelfilename (str) the acoustic model file name
        @param mapping (Mapping) a mapping table to convert the phone set

        """
        BaseAligner.__init__(self, modelfilename, mapping)
        self._outext = "palign"

    # ------------------------------------------------------------------------

    def gen_dependencies(self, phones, grammarname, dictname):
        """
        Generate the dependencies (grammar, dictionary) for julius.

        @param phones (str) the phonetization to align (spaces separate tokens, pipes separate variants, dots separate phones)
        @param grammarname (str) the file name of the grammar (output)
        @param dictname (str) the dictionary file name (output)

        """
        # Map phonemes from SAMPA to the expected one.
        self._mapping.set_keepmiss(True)
        self._mapping.set_reverse( True )
        phones = self._mapping.map(phones)

        with codecs.open(grammarname, 'w', encoding) as fdfa,\
                codecs.open(dictname, 'w', encoding) as fdict:

            tokenslist = phones.strip().split(" ")
            tokenidx = 0
            nbtokens = (len(tokenslist)-1)

            for pron in tokenslist:

                # dictionary:
                for variant in pron.split("|"):

                    fdict.write( str(tokenidx)+' ' )
                    fdict.write("[w_"+str(tokenidx)+"] ")
                    fdict.write(variant.replace("-",' ')+"\n" )

                # grammar:
                if tokenidx == 0:
                    fdfa.write( str(tokenidx)+" "+str(nbtokens)+" "+str(tokenidx+1)+" 0 1\n")
                else:
                    fdfa.write( str(tokenidx)+" "+str(nbtokens)+" "+str(tokenidx+1)+" 0 0\n")
                tokenidx += 1
                nbtokens -= 1

            # last line of the grammar
            fdfa.write( str(tokenidx)+" -1 -1 1 0\n")

    # ------------------------------------------------------------------------

    def run_julius(self, inputwav, basename, outputalign):
        """
        Perform the speech segmentation.

        Call the system command `julius`.

        """
        tiedlist = os.path.join(self._model, "tiedlist")
        hmmdefs  = os.path.join(self._model, "hmmdefs")
        config   = os.path.join(self._model, "config")

        # Create the command
        command = 'echo '
        command += inputwav
        command += ' | julius -input file -h '

        # its parameters
        command += '"' + hmmdefs.replace('"', '\\"') + '"'
        command += ' -gram '
        command += '"' + basename.replace('"', '\\"') + '"'
        if os.path.isfile(tiedlist):
            command += ' -hlist '
            command += '"' + tiedlist.replace('"', '\\"') + '"'
        command += ' -palign -multipath -penalty1 5.0 -penalty2 20.0 -iwcd1 max -gprune safe -m 10000 -b2 1000 -sb 1000.0 -smpFreq 16000'
        if self._infersp is True:
            command += ' -spmodel "sp" -iwsp -iwsppenalty -70.0'
        # By David Yeung, force Julius to use configuration file of HTK
        if os.path.isfile(config):
            command += ' -htkconf '
            command += '"' + config.replace('"', '\\"') + '"'

        # the output of the command
        command += ' > '
        command += '"' + outputalign.replace('"', '\\"') + '"'

        # Execute the command
        p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
        p.wait()
        line = p.communicate()

        # Julius not installed
        if len(line[0]) > 0 and line[0].find("not found") > -1:
            raise OSError( "julius is not properly installed. See installation instructions for details." )

        # Bad command
        if len(line[0]) > 0 and line[0].find("-help") > -1:
            raise OSError( "julius command failed." )

        # Check output file
        if os.path.isfile( outputalign ) is False:
            raise Exception('julius did not created an alignment file.')

    # ------------------------------------------------------------------------

    def run_alignment(self, inputwav, basename, outputalign):
        """
        Perform the speech segmentation.

        @param inputwav (str) the audio input file name, of type PCM-WAV 16000 Hz, 16 bits
        @param basename (str) the base name of the grammar file and of the dictionary file
        @param outputalign (str) the output file name

        """
        self.run_julius(inputwav, basename, outputalign)
        with codecs.open(outputalign, 'r', encoding) as f:
            lines = f.readlines()

        entries = []
        for line in lines:
            if line.find("Error: voca_load_htkdict")>-1 and line.find("not found")>-1:
                line = re.sub("[ ]+", " ", line)
                line = line.strip()
                line = line[line.find('"')+1:]
                line = line[:line.find('"')]
                if len(line)>0:
                    entries = line.split(" ")

        message = ""
        if len(entries) > 0:
            added = self.add_tiedlist(entries)
            if len(added) > 0:
                message = "The acoustic model was modified. The following entries were successfully added into the tiedlist: "
                message = message + " ".join(added) + "\n"
                self.run_julius(inputwav, basename, outputalign)
                with codecs.open(outputalign, 'r', encoding) as f:
                    lines = f.readlines()

        errorlines = ""
        for line in lines:
            if line.startswith("Error:") and not " line " in line:
                errorlines = errorlines + line

        if len(errorlines) > 0:
            raise Exception(message + errorlines)

        return message

    # ------------------------------------------------------------------------
