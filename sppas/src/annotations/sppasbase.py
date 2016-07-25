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
    def __init__(self, *args, **kwargs):
        """
        """
        # Log messages for the user
        self.logfile = None
        if "logfile" in kwargs.keys():
            self.logfile = kwargs["logfile"]

        # List of options to configure this automatic annotation
        self._options = {}

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

    def print_message(self, message, indent=3, status=INFO_ID):
        """
        Print a message either in the user log or in the console log.

        """
        if self.logfile:
            self.logfile.print_message(message, indent=indent, status=status)

        elif len(message) > 0:
            if status==INFO_ID:
                logging.info( message )
            elif status==WARNING_ID:
                logging.warning( message )
            elif status==ERROR_ID:
                logging.error( message )
            else:
                logging.debug( message )

    # -----------------------------------------------------------------------
