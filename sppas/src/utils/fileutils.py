# -*- coding: UTF-8 -*-
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

    src.utils.fileutils.py
    ~~~~~~~~~~~~~~~~~~~~~~

    Utility functions to manage files and directories.
    
"""
import os
import random
import shutil
import codecs
import re
import logging
import tempfile
from datetime import date

# ----------------------------------------------------------------------------


class sppasFileUtils(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Utility file manager for SPPAS.

    >>> sf = sppasFileUtils("path/myfile.txt")
    >>> print(sf.exists())

    """
    def __init__(self, filename=None):
        """ Create a sppasFileUtils and set the current filename. """
        self._filename = filename

    # ------------------------------------------------------------------------

    def set_random(self, root="sppas_tmp", add_today=True, add_pid=True):
        """ Set a random basename.

        :param root: (str) String to start the filename
        :param add_today: (bool) Add today's information to the filename
        :param add_pid: (bool) Add the process PID to the filename
        :returns: a random name of a non-existing file or directory

        """
        # get the system temporary directory
        tempdir = tempfile.gettempdir()
        # initial file name
        name = "/"
        while os.path.exists(name) is True:

            filename = root + "_"

            if add_today:
                today = str(date.today())
                filename = filename + today + "_"
            if add_pid:
                pid = str(os.getpid())
                filename = filename + pid + "_"

            # random float value
            filename = filename + '{:04d}'.format(int(random.random() * 9999))

            # final file name is path/filename
            name = os.path.join(tempdir, filename)

        self._filename = name
        return name

    # ------------------------------------------------------------------------

    def exists(self, directory=None):
        """ Does the file exists, or exists in a given directory.
        Case-insensitive test on all platforms.

        :param directory: (str) Optional directory to test if a file exists.
        :returns: the filename (including directory) or None
    
        """
        if directory is None:
            directory = os.path.dirname(self._filename)

        for x in os.listdir(directory):
            if os.path.basename(self._filename.lower()) == x.lower():
                return os.path.join(directory, x)

        return None

    # ------------------------------------------------------------------------

    def clear_whitespace(self):
        """ Replace whitespace by underscores. """

        # Remove multiple spaces
        __str = re.sub("[\s]+", r" ", self._filename)
        # Spaces at beginning and end
        __str = re.sub("^[ ]+", r"", __str)
        __str = re.sub("[ ]+$", r"", __str)
        # Replace spaces by underscores
        __str = re.sub('\s', r'_', __str)

        self._filename = __str
        return __str

    # ------------------------------------------------------------------------

    def to_ascii(self):
        """ Replace non-ASCII characters by underscores. """

        __str = re.sub(r'[^\x00-\x7F]', '_', self._filename)
        self._filename = __str
        return __str

    # ------------------------------------------------------------------------

    def format(self):
        """ Replace both whitespace and non-ascii characters by underscores. """

        self.clear_whitespace()
        self.to_ascii()
        return self._filename

# ----------------------------------------------------------------------------


class sppasDirUtils(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Utility directory manager for SPPAS.

    >>> sd = sppasDirUtils("my-path")
    >>> print(sd.get_files())

    """
    def __init__(self, dirname):
        """ Create a sppasFileUtils and set the current filename. """
        self._dirname = dirname

    # ------------------------------------------------------------------------

    def get_files(self, extension, recurs=True):
        """ Returns the list of files of the directory.

        :param extension: (str) the file extension to filter the directory
        content
        :param recurs: (bool)
        :returns: a list of files

        """
        if os.path.exists(self._dirname) is False:
            message = "The directory " + self._dirname + " does not exists."
            raise IOError(message)

        return sppasDirUtils.dir_entries(self._dirname, extension, recurs)

    # ------------------------------------------------------------------------

    @staticmethod
    def dir_entries(dir_name, extension, subdir):
        """ Return a list of file names found in directory 'dir_name'.

        If 'subdir' is True, recursively access subdirectories under
        'dir_name'. Additional argument, if any, is file extension to
        match filenames.

        """
        file_list = []
        for dfile in os.listdir(dir_name):
            dirfile = os.path.join(dir_name, dfile)
            if os.path.isfile(dirfile):
                if not extension:
                    file_list.append(dirfile)
                else:
                    if dirfile.lower().endswith(extension.lower()):
                        file_list.append(dirfile)
            # recursively access file names in subdirectories
            elif os.path.isdir(dirfile) and subdir:
                file_list.extend(sppasDirUtils.dir_entries(dirfile, subdir, extension))
        return file_list

# ----------------------------------------------------------------------------


def setup_logging(log_level, filename):
    """
    Setup default logger to log to stderr or and possible also to a file.

    The default logger is used like this:
        >>> import logging
        >>> logging.error(text message)

    """
    formatmsg = "%(asctime)s [%(levelname)s] %(message)s"

    # Setup logging to file if filename is specified
    if filename is not None:
        file_handler = logging.FileHandler(filename, "a+")
        file_handler.setFormatter(logging.Formatter(formatmsg))
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)
    else:
        # Setup logging to stderr
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(formatmsg))
        console_handler.setLevel(log_level)
        logging.getLogger().addHandler(console_handler)

    logging.getLogger().setLevel(log_level)
    logging.info("Logging set up with log level=%s, filename=%s", log_level,filename)

# ----------------------------------------------------------------------------


def fix_audioinput(inputaudioname):
    """
    Fix the audio file name that will be used.
    An only-ascii-based file name without whitespace is set if the
    current audio file name does not fit in these requirements.

    @param inputaudioname (str - IN) Given audio file name

    """
    sf = sppasFileUtils(inputaudioname)
    inputaudio = sf.format()
    if inputaudio != inputaudioname:
        shutil.copy(inputaudioname, inputaudio)

    return inputaudio

# ------------------------------------------------------------------------


def fix_workingdir(inputaudio):
    """
    Fix the working directory to store temporarily the data.

    """
    if len(inputaudio) == 0:
        # Notice that the following generates a directory that the
        # aligners won't be able to access under Windows.
        # No problem with MacOS or Linux.
        sf = sppasFileUtils()
        workdir = sf.set_random()
        while os.path.exists(workdir) is True:
            workdir = sf.set_random()
    else:
        workdir = os.path.splitext(inputaudio)[0]+"-temp"

    os.mkdir(workdir)
    return workdir

# ------------------------------------------------------------------------


def writecsv(filename, rows, separator="\t", encoding="utf-8-sig"):
    """
    Write the rows to the file.
    Args:
        filename (string):
        rows (list):
        separator (string):
        encoding (string):

    """
    with codecs.open(filename, "w+", encoding) as f:
        for row in rows:
            tmp = []
            for s in row:
                if isinstance(s, (float, int)):
                    s = str(s)
                else:
                    s = '"%s"' % s
                tmp.append(s)
            f.write('%s\n' % separator.join(tmp))

# ----------------------------------------------------------------------------
