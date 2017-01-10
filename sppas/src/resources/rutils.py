# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              the automatic
#           \__   |__/  |__/  |___| \__             annotation and
#              \  |     |     |   |    \             analysis
#           ___/  |     |     |   | ___/              of speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2017  Brigitte Bigi
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
# File: src.resources.rutils.py
# ----------------------------------------------------------------------------

import codecs
import pickle
import logging
import os
import os.path


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

DUMP_FILENAME_EXT = ".dump"
ENCODING = "utf-8"

# ----------------------------------------------------------------------------


def to_lower(entry):
    """
    Return a unicode string with lower case.

    :param entry: (str or Unicode)
    :returns: Unicode

    """
    try:
        e = entry.decode('utf8')
    except UnicodeEncodeError:
        e = entry

    return e.lower()

# ----------------------------------------------------------------------------


def to_strip(entry):
    """
    Strip a string.
    (remove also multiple spaces inside the string)

    :param entry: (str or Unicode)
    :returns: Unicode

    """
    try:
        e = entry.decode('utf8')
    except UnicodeEncodeError:
        e = entry
    e = e.replace(u'\ufeff', ' ')

    return " ".join(e.split())

# ----------------------------------------------------------------------------


def get_dump_filename(filename):
    """
    Return the file name of the dump version of filename.

    :param filename (String)
    :returns: dump filename

    """

    fileName, fileExt = os.path.splitext(filename)

    return fileName + DUMP_FILENAME_EXT

# ----------------------------------------------------------------------------


def has_dump(filename):
    """
    Test if a dump file exists for filename and if it is up-to-date.

    :param filename: (str)
    :returns: (bool)

    """
    dump_filename = get_dump_filename(filename)
    if os.path.isfile(dump_filename):
        tascii = os.path.getmtime(filename)
        tdump = os.path.getmtime(dump_filename)
        if tascii < tdump:
            return True

    return False

# ----------------------------------------------------------------------------


def load_from_dump(filename):
    """
    Load the file from a dumped file.

    :param filename: (str)
    :returns: loaded data or None

    """
    if has_dump(filename) is False:
        return None

    dump_filename = get_dump_filename(filename)

    try:
        with codecs.open(dump_filename, 'rb') as f:
            data = pickle.load(f)
    except Exception as e:
        logging.info('Load dumped data failed: %s' % str(e))
        os.remove(dump_filename)
        return None

    return data

# ----------------------------------------------------------------------------


def save_as_dump(data, filename):
    """
    Save the data as a dumped file.

    :param data: The data to save
    :param filename: File name for the data
    :returns: (bool)

    """
    dump_filename = get_dump_filename(filename)

    try:
        with codecs.open(dump_filename, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        logging.info('Save a dumped data failed: %s' % str(e))
        return False

    return True

# ----------------------------------------------------------------------------
