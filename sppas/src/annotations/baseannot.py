"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.annotations.baseannot.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Base class for any automatic annotations integrated into SPPAS.

"""
import logging
import os.path

from sppas.src.config import annotations_translation
from sppas.src.utils.makeunicode import u
from . import ERROR_ID, WARNING_ID, INFO_ID
from .diagnosis import sppasDiagnosis

# ---------------------------------------------------------------------------

_ = annotations_translation.gettext

# ---------------------------------------------------------------------------

MSG_OPTIONS = _(":INFO 1050: ")
MSG_DIAGNOSIS = _(":INFO 1052: ")
MSG_ANN_FILE = (_(":INFO 1056: "))

# ---------------------------------------------------------------------------


class sppasBaseAnnotation(object):
    """SPPAS Base class of any automatic annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    """

    def __init__(self, logfile=None, name="Annotation"):
        """ Base class for any SPPAS automatic annotation.

        :param logfile: (sppasLog) 
        
        """
        # The public name of the automatic annotation
        self.name = name

        # Log messages for the user
        self.logfile = logfile

        # List of options to configure the automatic annotation
        self._options = dict()

        # A file diagnostician
        self.diagnosis = sppasDiagnosis()

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def get_option(self, key):
        """ Return the option value of a given key or raise KeyError. 
        
        :param key: (str) Return the value of an option, or None.
        :raises: KeyError
        
        """
        return self._options[key]

    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options.

        :param options: (list)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def print_message(self, message, indent=3, status=None):
        """ Print a message in the user log.

        :param message: (str) The message to communicate
        :param indent: (int) Shift the message with indents
        :param status: (int) A status identifier
        
        """
        message = u(message)
        if self.logfile:
            self.logfile.print_message(message, indent=indent, status=status)

        elif len(message) > 0:
            if status is None:
                logging.info(message)
            else:
                if status == INFO_ID:
                    logging.info(message)
                elif status == WARNING_ID:
                    logging.warning(message)
                elif status == ERROR_ID:
                    logging.error(message)
                else:
                    logging.debug(message)

    # -----------------------------------------------------------------------

    def print_filename(self, filename, status=None):
        """ Print the annotation name that is applied on a filename in the user log.

        :param filename: (str) Name of the file to annotate.
        :param status: (int) 1-4 value or None

        """
        if self.logfile:
            fn = os.path.basename(filename)
            self.print_message(MSG_ANN_FILE.format(fn), indent=1, status=status)
        else:
            logging.info(MSG_ANN_FILE.format(filename))

    # -----------------------------------------------------------------------

    def print_options(self):
        """ Print the list of options in the user log. """
        
        self.print_message(MSG_OPTIONS + ": ", indent=2, status=None)
        for k, v in self._options.items():
            self.print_message(" - {!s:s}: {!s:s}".format(k, v), indent=3, status=None)

    # -----------------------------------------------------------------------

    def print_diagnosis(self, *filenames):
        """ Print the diagnosis of a list of files in the user log.

        :param filenames: (list) List of files.
        
        """
        self.print_message(MSG_DIAGNOSIS + ": ", indent=2, status=None)
        for filename in filenames:
            if filename is not None:
                fn = os.path.basename(filename)
                (s, m) = sppasDiagnosis.check_file(filename)
                self.print_message(" - {!s:s}: {!s:s}".format(fn, m), indent=3, status=None)
