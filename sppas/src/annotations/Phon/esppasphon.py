#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
#
# Copyright (C) 2011-2013  Brigitte Bigi
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.
# ######################################################################### #


# ######################################################################### #
# DEPRECATED since 2013!
# ######################################################################### #


import sys
import os
from os.path import *
from subprocess import Popen, PIPE, STDOUT

SPPAS = dirname( dirname( dirname( dirname( abspath(__file__) ) ) ))

import annotations.log
from annotationdata.transcription import Transcription
import annotationdata.io
from utils.name import genName


# ######################################################################### #
class esppasPhon:
    """ ESPPAS phonetization.
    """

    def __init__(self,logfile=None):
        """ Create a new esppasPhon instance.
            Parameters:
                - logfile is a file descriptor of the log file.
        """
        self.logfile = logfile

    # End __init__
    # ------------------------------------------------------------------------


    def old_run( self, inputfilename, outputphonfile=None, outputtokensfile=None ):
        """ Run the Phonetization process from a transcription.

            For details, see:
            B. Bigi, P. Péri, R. Bertrand (2012)
            Orthographic Transcription: which Enrichment is required for phonetization?
            Language Resources and Evaluation Conference, Istanbul (Turkey),
            pages 1756-1763, ISBN 978-2-9517408-7-7.

            INPUT: an enriched orthographic transcription
            BRIEF: Get the TO, create a tree, call LIA_Tagg, update the tree,
            call LIA_Phon, update the tree, then get the phonetization.

            Parameters:
                - inputfilename is the input file name
                - outputphonfile is the output file name of the phonetization
                - outputtokensfile is the output file name of the tokenization
            Return:      None
            Exceptions:  IOError
        """

        if not outputphonfile:
            outputphonfile = inputfilename.replace('.TextGrid', '-phon.TextGrid')
        if not outputtokensfile:
            outputtokensfile = inputfilename.replace('.TextGrid', '-tokens.TextGrid')

        # Program names and data dirs
        esppasdir = os.path.join(SPPAS, "scripts")
        esppasdir = os.path.join(esppasdir, "esppas")
        jar = os.path.join(esppasdir, "phonetizationFRTOE.jar")
        etc = os.path.join(esppasdir, "etc")
        etc = os.path.join(etc, " ")
        formate = os.path.join(esppasdir, "formatphonFRTOE.awk")
        rustine = os.path.join(esppasdir, "rustinePhonFRTOE.sh")

        # First command to execute
        command = "java -Dfile.encoding=iso8859-1 -jar "
        command += jar
        # with its parameters:
        command += " -s " + etc
        command += " -i " + inputfilename
        command += " -t 1 "
        tmpoutput = genName().get_name() + ".TextGrid"
        command += " -o " + tmpoutput
        command += " -w " + outputtokensfile
        command += " -v 0 "

        ret = self.run_command( command )
        if not os.path.isfile(tmpoutput):
            raise BaseException('Phon::esppasphon.py. TOE-Phonetization failed.\n')

        # ESPPAS patches
        command = "cat "
        command += tmpoutput
        command += " | gawk -f "
        command += formate
        command += " -l -t -m 250 -s '##' | "
        command += rustine
        command += " > "
        command += outputphonfile

        ret = self.run_command( command )
        #self.run_command( "rm "+tmpoutput )
        if not os.path.isfile(outputphonfile):
            raise BaseException('Phon::esppasphon.py. Post-processing of TOE-Phonetization failed.\n')


    def run( self, inputfilename, outputphonfile=None, outputtokensfile=None ):
        """ Run the Phonetization process from a tokenized input.TO DO.

            Parameters:
                - inputfilename is the input file name
                - outputphonfile is the output file name of the phonetization
                - outputtokensfile is the output file name of the tokenization
            Return:      None
            Exceptions:  IOError
        """

        if not outputphonfile:
            outputphonfile = inputfilename.replace('.TextGrid', '-phon.TextGrid')
        if not outputtokensfile:
            outputtokensfile = inputfilename.replace('.TextGrid', '-tokens.TextGrid')

        # Program names and data dirs
        esppasdir = os.path.join(SPPAS, "scripts")
        esppasdir = os.path.join(esppasdir, "esppas")
        formate = os.path.join(esppasdir, "formatphonFRTOE.awk")
        rustine = os.path.join(esppasdir, "rustinePhonFRTOE.sh")

        # ALGORITHM:
        # - EXTRACT EACH INTERVAL
        # - CALL LIA_PHON ON THIS INTERVAL
        # - GET RESULT AND PUT IN AN OUTPUT TIER

        # Write the appropriate tier in a LIA-style text file
        # it also will convert input from UTF8 to iso8859-1
        try:
            inputok = genName().get_name() + ".liatxt"
            trs = Transcription()
            trs.Append( inputfilename.get_tier(1) )
            annotationdata.io.write(inputok,trs)
        except Exception:
            raise BaseException('Phon::esppasphon.py. Processing of phonetization failed.\n')

        # Execute LIA_Phon
        command = "cat "
        command += inputok
        command += " | $LIA_PHON_REP/script/lia_text2phon > "
        command += tmpoutput

        # ESPPAS patches
        command = "cat "
        command += tmpoutput
        command += " | gawk -f "
        command += formate
        command += " -l -t -m 250 -s '##' | "
        command += rustine
        command += " > "
        command += outputphonfile

        ret = self.run_command( command )
        #self.run_command( "rm "+tmpoutput )
        if not os.path.isfile(outputphonfile):
            raise BaseException('Phon::esppasphon.py. Post-processing of TOE-Phonetization failed.\n')


    # ###################################################################### #
    # Private!                                                               #
    # ###################################################################### #

    def run_command(self,command):
        """ Execute a command, wait, and print output in the log file.
            Parameters:
                - command is a string to represent the command to execute
            Return:      1 if output contains "OK" 0 otherwise
            Exceptions:  none
        """
        # Execute command and get output
        p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
        retval = p.wait()
        line = p.communicate()

        # Write the program output at the end of the log file
        if len(line[0]) and self.logfile:
            self.logfile.print_message(line[0])

        # Fix the return value
        if retval or (len(line[0]) and not "OK" in line[0]):
            return 0  # Execution failed
        return 1  # Execution succeed

    # End run
    # ------------------------------------------------------------------------


