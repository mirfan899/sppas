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
# File: sppasbase.py
# ---------------------------------------------------------------------------

import logging
from sp_glob import ERROR_ID, WARNING_ID, OK_ID, INFO_ID
from annotations.diagnosis import sppasDiagnosis

# ---------------------------------------------------------------------------

class sppasBase( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS Base class of any automatic annotation.

    """
    def __init__(self, logfile=None):
        """
        Base class for any SPPAS automatic annotation.

        """
        # Log messages for the user
        self.logfile = logfile

        # List of options to configure the automatic annotation
        self._options = {}

        # A file diagnostician
        self._diag = sppasDiagnosis()

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def get_option(self, key):
        """
        Return the option value of a given key or raise an Exception.

        """
        return self._options[key]

    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        @param options (option)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def print_message(self, message, indent=3, status=None):
        """
        Print a message either in the user log.

        """
        if self.logfile:
            self.logfile.print_message(message, indent=indent, status=status)

        elif len(message) > 0:
            if status is None:
                logging.debug( message )
            else:
                if status == INFO_ID:
                    logging.info( message )
                elif status == WARNING_ID:
                    logging.warning( message )
                elif status == ERROR_ID:
                    logging.error( message )
                else:
                    logging.debug( message )

    # -----------------------------------------------------------------------

    def print_options(self):
        """
        Print the list of options in the user log.

        """
        self.print_message("Options: ", indent=2, status=None)
        for k,v in self._options.items():
            self.print_message(" - %s: %s"%(k,v), indent=3, status=None)

    # -----------------------------------------------------------------------

    def print_diagnosis(self, *filenames):
        """
        Print the diagnosis of a list of files in the user log.

        """
        self.print_message("Diagnosis: ", indent=2, status=None)
        for filename in filenames:
            if filename is not None:
                (s,m) = self._diag.checkfile( filename )
                self.print_message(" - %s: %s"%(filename,m), indent=3, status=None)

    # -----------------------------------------------------------------------
