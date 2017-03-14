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
# File: log.py
# ----------------------------------------------------------------------------

import datetime
import codecs
import logging
import os

from sppas import program, version, copyright, url, author, contact
from sppas import encoding
from sppas.src.utils.fileutils import sppasFileUtils

# ----------------------------------------------------------------------------


class sppasLog( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      A log file utility class.

    Class to manage the SPPAS automatic annotations log file, which is also
    called the "Procedure Outcome Report".

    """
    def __init__(self, parameters):
        """
        Constructor.

        @param parameters (sppasParam)

        """
        self.parameters = parameters
        self.logfp = codecs.open(os.devnull, 'w', encoding)

    # ----------------------------------------------------------------------
    # File management
    # ----------------------------------------------------------------------

    def close(self):
        self.logfp.close()

    def open_new(self, logfilename):
        self.logfp = codecs.open(logfilename, 'w', encoding)

    def open(self, logfilename):
        self.logfp = codecs.open(logfilename, 'a+', encoding)

    # ----------------------------------------------------------------------
    # Write data
    # ----------------------------------------------------------------------

    def print_step(self, stepnumber):
        """
        Print the annotation step name.

        @param stepnumber (1..N)

        """
        try:
            self.logfp.seek(0, 2) # force to write at the end of the file
            self.logfp.write('-----------------------------------------------------------------------\n')
            self.logfp.write('                       ' + self.parameters.get_step_name(stepnumber) + '\n')
            self.logfp.write('-----------------------------------------------------------------------\n')
        except Exception as e:
            logging.debug( "log.py Print ERROR. Message: %s" % e)

    # ----------------------------------------------------------------------

    def print_message(self, message, indent=0, status=None):
        """
        Print a message at the end of the file.

        @param  message (string) text to print
        @param  indent (int) is the number of indentation to apply to message
        @param  status (int) 0 means OK, 1 means WARNING, 2 means ignored, and
        any other value means ERROR

        """
        try:
            self.logfp.seek(0, 2) # write at the end of the file
            strindent = " ... "*indent
            statustext= ""
            if status is not None:
                if status == 0:
                    statustext="[    OK   ] "
                elif status == 1:
                    statustext="[ WARNING ] "
                elif status == 2:
                    statustext="[ IGNORED ] "
                elif status == 3:
                    statustext="[   INFO  ] "
                else:
                    statustext="[  ERROR  ] "
            self.logfp.write(strindent + statustext + message + "\n")
        except Exception:
            try:
                sf = sppasFileUtils()
                self.logfp.write(strindent + statustext + sf.to_ascii(message) + "\n")
            except Exception:
                logging.debug( "Procedure Outcome Report Message: %s" % message)
                self.logfp.write(strindent + statustext + "See the reason in the console.\n")

    # ----------------------------------------------------------------------

    def print_rawtext(self, text):
        """
        Print a text at the end of the file.

        :param text: (string) text to print

        """
        try:
            self.logfp.seek(0, 2)  # write at the end of the file
            self.logfp.write(text)
        except Exception as e:
            logging.debug("log.py Print ERROR. Message: %s" % str(e))

    # ----------------------------------------------------------------------

    def print_newline(self):
        try:
            self.logfp.write('\n')
        except Exception:
            pass

    # ----------------------------------------------------------------------

    def print_separator(self):
        try:
            self.logfp.write('-----------------------------------------------------------------------\n')
        except Exception:
            pass

    # ----------------------------------------------------------------------

    def print_stat(self, stepnumber, value):
        """
        Print the value for a step.

        @param stepnumber (1..6)
        @param value (0..n)

        """
        try:
            self.logfp.seek(0, 2)  # write at the end of the file
            self.logfp.write('  - ')
            self.logfp.write(self.parameters.get_step_name(stepnumber))
            self.logfp.write(':  ')
            self.logfp.write(str(value))
            self.logfp.write('\n')
        except Exception as e:
            logging.debug("log.py Print ERROR. Message: " % str(e))

    # ----------------------------------------------------------------------

    def print_header(self):
        """
        Write parameters information in a log file.

        """
        self.logfp.seek(0, 2)  # write at the end of the file
        self.print_separator()
        self.print_message('\n' + program + ' - Version ' + version)
        self.print_message(copyright)
        self.print_message('Web site: ' + url)
        self.print_message('Contact: ' + author + "("+ contact + ")\n")
        self.print_separator()

        #self.print_message('\nFile:            ' + self.parameters.get_logfilename())
        self.print_message('Date: ' + str(datetime.datetime.now()))
        self.print_message('Input languages: ')
        for i in range(self.parameters.get_step_numbers()):
            if self.parameters.get_lang(i) is not None :
                self.print_message("  - " + self.parameters.get_step_name(i) + ": " + self.parameters.get_lang(i))
            else:
                self.print_message("  - " + self.parameters.get_step_name(i) + ": --- ")

        self.print_message('Input selection: ')
        for sinput in self.parameters.get_sppasinput():
            self.print_message("  - " + sinput)
        self.print_separator()
        for i in range(self.parameters.get_step_numbers()):
            if self.parameters.get_step_status(i):
                value = "activated"
            else:
                value = "disabled"
            self.print_stat(i, value)
        self.print_separator()
        self.print_newline()
        self.print_message("Extension: %s" % self.parameters.get_output_format())
        self.print_separator()
        self.print_newline()

# ----------------------------------------------------------------------------
