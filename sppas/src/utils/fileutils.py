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
# File: fileutils.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import os
import random
import codecs
import re
import logging
import tempfile
from datetime import date

# ----------------------------------------------------------------------------

def exists(filename):
    """
    os.path.exists() revisited!
        - case-insensitive
        - return the filename or None
    """
    for x in os.listdir( os.path.dirname(filename)):
        if os.path.basename(filename.lower()) == x.lower():
            return os.path.join(os.path.dirname(filename),x)
    return None

# ----------------------------------------------------------------------------

def get_files(directory,extension,recurs=True):
    """
    Get a file list of a directory.

    @param directory is the directory to find files
    @param extension is the file extension to filter the directory content

    @return a list of files

    """
    filelist = []
    if os.path.exists(directory):
        filelist = dirEntries(directory, recurs, extension)
        #filelist = [x for x in os.listdir(directory) if x.lower().endswith(extension.lower())]
    else:
        message = "ERROR: The directory "+directory+" does not exists."
        raise IOError(message)
    return filelist

# ----------------------------------------------------------------------------

def dirEntries(dir_name, subdir, extension):
    """
    Return a list of file names found in directory 'dir_name'.

    If 'subdir' is True, recursively access subdirectories under 'dir_name'.
    Additional argument, if any, is file extension to match filenames.

    """
    fileList = []
    for file in os.listdir(dir_name):
        dirfile = os.path.join(dir_name, file)
        if os.path.isfile(dirfile):
            if not extension:
                fileList.append(dirfile)
            else:
                if dirfile.lower().endswith(extension.lower()):
                    fileList.append(dirfile)
        # recursively access file names in subdirectories
        elif os.path.isdir(dirfile) and subdir:
            fileList.extend(dirEntries(dirfile, subdir, extension))
    return fileList

# ----------------------------------------------------------------------------

def set_tmpfilename():
    randval = random.random()    # random float
    #tmp = "tmp_"+str(datetime.datetime.now())
    tmp = "tmp_"+str(randval)
    return tmp

# ----------------------------------------------------------------------------

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

def gen_name():
    """
    Set a new file name.
    Generates a random name of a non-existing file or directory.
    """
    name = "/"
    while os.path.exists(name) is True:

        # random float value
        randval  = str(int(random.random()*10000))
        # process pid
        pid      = str(os.getpid())
        # today's date
        today    = str(date.today())

        # filename
        filename = "sppas_tmp_"+today+"_"+pid+"_"+randval

        # final file name is path/filename
        tempdir = tempfile.gettempdir() # get the system temporary directory
        name = os.path.join(tempdir,filename)

    return name

# ----------------------------------------------------------------------------

def format_filename(entry):
    # Remove multiple spaces
    __str = re.sub(u"[\s]+", ur" ", entry)
    # Spaces at beginning and end
    __str = re.sub(u"^[ ]+", ur"", __str)
    __str = re.sub(u"[ ]+$", ur"", __str)
    # Replace spaces by underscores
    __str = re.sub(u'\s', ur'_', __str)

    return __str

def string_to_ascii(entry):
    # Replace non-ASCII characters by underscores
    return re.sub(r'[^\x00-\x7F]','_', entry)

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
