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

"""
import logging
import os

from sppas.src.config import annots
from sppas.src.config import annotations_translation
from sppas.src.utils.makeunicode import u
from sppas.src.utils.fileutils import sppasFileUtils

from .diagnosis import sppasDiagnosis

# ---------------------------------------------------------------------------

MSG_OPTIONS = annotations_translation.gettext(":INFO 1050: ")
MSG_DIAGNOSIS = annotations_translation.gettext(":INFO 1052: ")
MSG_ANN_FILE = (annotations_translation.gettext(":INFO 1056: "))

# ---------------------------------------------------------------------------


class sppasBaseAnnotation(object):
    """Base class for any automatic annotations integrated into SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, logfile=None, name="Annotation"):
        """Base class for any SPPAS automatic annotation.

        :param logfile: (sppasLog)

        """
        # The public name of the automatic annotation
        self.name = name

        # Log messages for the user
        self.logfile = logfile

        # List of options to configure the automatic annotation
        self._options = dict()

    # -----------------------------------------------------------------------
    # Shared methods to fix options and to annotate
    # -----------------------------------------------------------------------

    def get_option(self, key):
        """Return the option value of a given key or raise KeyError.

        :param key: (str) Return the value of an option, or None.
        :raises: KeyError

        """
        return self._options[key]

    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        :param options: (list of sppasOption)

        """
        pass

    # -----------------------------------------------------------------------

    def batch_processing(self, file_names, progress=None, output_format=annots.extension):
        """Perform the annotation on a set of files.

        :param file_names: (list of str) List of file to annotate
        :param progress: ProcessProgressTerminal() or ProcessProgressDialog()
        :param output_format: (str) Output file extension (starting with a dot)
        :returns: (int) Number of files processed with success

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # To communicate with the interface:
    # -----------------------------------------------------------------------

    def print_message(self, message, indent=3, status=None):
        """Print a message in the user log.

        :param message: (str) The message to communicate
        :param indent: (int) Shift the message with indents
        :param status: (int) A status identifier

        """
        message = u(message)
        if self.logfile:
            self.logfile.print_message(message,
                                       indent=indent,
                                       status=status)

        elif len(message) > 0:
            if status is None:
                logging.info(message)
            else:
                if status == annots.info:
                    logging.info(message)

                elif status == annots.warning:
                    logging.warning(message)

                elif status == annots.error:
                    logging.error(message)

                elif status == annots.ok:
                    logging.info(message)

                else:
                    logging.debug(message)

    # -----------------------------------------------------------------------

    def print_filename(self, filename, status=None):
        """Print the annotation name applied on a filename in the user log.

        :param filename: (str) Name of the file to annotate.
        :param status: (int) 1-4 value or None

        """
        if self.logfile:
            fn = os.path.basename(filename)
            self.print_message(MSG_ANN_FILE.format(fn),
                               indent=1,
                               status=status)
        else:
            logging.info(MSG_ANN_FILE.format(filename))

    # -----------------------------------------------------------------------

    def print_options(self):
        """Print the list of options in the user log."""
        if self.logfile:
            self.print_message(MSG_OPTIONS + ": ",
                               indent=2,
                               status=None)
        else:
            logging.info(MSG_OPTIONS)

        for k, v in self._options.items():
            msg = " - {!s:s}: {!s:s}".format(k, v)
            if self.logfile:
                self.print_message(msg, indent=3, status=None)
            else:
                logging.info(msg)

    # -----------------------------------------------------------------------

    def print_diagnosis(self, *filenames):
        """Print the diagnosis of a list of files in the user log.

        :param filenames: (list) List of files.

        """
        for filename in filenames:
            if filename is not None:
                fn = os.path.basename(filename)
                (s, m) = sppasDiagnosis.check_file(filename)
                msg = MSG_ANN_FILE.format(fn) + ": {!s:s}".format(m)
                if self.logfile:
                    self.print_message(msg, indent=1, status=None)
                else:
                    logging.info(msg)

    # -----------------------------------------------------------------------

    def print_newline(self):
        """Print an empty line."""
        if self.logfile:
            self.logfile.print_newline()

    # ------------------------------------------------------------------------

    def _get_filename(self, filename, extensions):
        """Return a filename corresponding to one of the extensions.

        :param filename: input file name
        :param extensions: the list of expected extension
        :returns: a file name of the first existing file with an expected
        extension or None

        """
        base_name = os.path.splitext(filename)[0]
        for ext in extensions:
            ext_filename = base_name + ext
            new_filename = sppasFileUtils(ext_filename).exists()
            if new_filename is not None and os.path.isfile(new_filename):
                return new_filename

        return None
