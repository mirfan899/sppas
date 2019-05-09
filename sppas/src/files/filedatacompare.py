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

    files.filedatacompare.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Classes:
    ========

        - sppasPathCompare() to search for a value in a path name
          (FilePath.id, FilePath.check, FilePath.expand)

    To do:
    =====

        - sppasRootCompare() to search for a value in a root name
          (FileRoot.id, FileRoot.check, FileRoot.expand)

        - sppasNameCompare() to search for a value in a file name
          (FileName.name)

        - sppasExtensionCompare() to search for a value in the extension of a
          file name (FileName.ext)

        - sppasFileCompare() to search for a value in the members of a
          file name (FileName.check, FileName.lock, FileName....)

        - the unitests for all classes and methods.

"""

import unittest
import re
from os.path import dirname

from sppas import sppasTypeError
from sppas.src.utils.makeunicode import text_type
from sppas.src.structs.basecompare import sppasBaseCompare

from .filedata import FilePath

# ---------------------------------------------------------------------------


class sppasPathCompare(sppasBaseCompare):
    """Comparison methods for FilePath.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    :Example: Three different ways to compare a file data content to a given string

        >>> tc = sppasPathCompare()
        >>> tc.exact(FilePath("c:\\Users"), u("c:\\Users"))
        >>> tc.methods['exact'](FilePath("c:\\Users"), u("c:\\Users"))
        >>> tc.get('exact')(FilePath("c:\\Users"), u("c:\\Users"))

    """

    def __init__(self):
        """Create a sppasPathCompare instance."""
        super(sppasPathCompare, self).__init__()

        # Compare the id to a text value
        self.methods['exact'] = sppasPathCompare.exact
        self.methods['iexact'] = sppasPathCompare.iexact
        self.methods['startswith'] = sppasPathCompare.startswith
        self.methods['istartswith'] = sppasPathCompare.istartswith
        self.methods['endswith'] = sppasPathCompare.endswith
        self.methods['iendswith'] = sppasPathCompare.iendswith
        self.methods['contains'] = sppasPathCompare.contains
        self.methods['icontains'] = sppasPathCompare.icontains
        self.methods['regexp'] = sppasPathCompare.regexp

        # Compare check/expand to a boolean value
        self.methods['check'] = sppasPathCompare.check
        self.methods['expand'] = sppasPathCompare.expand

    # -----------------------------------------------------------------------
    # Path identifier
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(path, value):
        """Test if path strictly matches value.

        :param path: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return path.id == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(path, value):
        """Test if path matches value without case sensitive.

        :param path: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return path.id.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(path, value):
        """Test if path starts with the characters of the value.

        :param path: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return path.id.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(path, value):
        """Case-insensitive startswith.

        :param path: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return path.id.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(path, value):
        """Test if path ends with the characters of the value.

        :param path: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return path.id.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(path, value):
        """Case-insensitive endswith.

        :param path: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return path.id.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(path, value):
        """Test if the path contains the value.

        :param path: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in path.id

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(path, value):
        """Case-insensitive contains.

        :param path: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in path.id.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(path, pattern):
        """Test if text matches pattern.

        :param path: (FilePath) Path to compare.
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")
        text = path.id

        return True if re.match(pattern, text) else False

    # -----------------------------------------------------------------------
    # Check/Expand members
    # -----------------------------------------------------------------------

    @staticmethod
    def check(path, value):
        """Compare check member to the given value.

        :param path: (FilePath) Path to compare.
        :param value: (bool) Boolean to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")

        return path.check is bool(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def expand(path, value):
        """Compare expand member to the given value.

        :param path: (FilePath) Path to compare.
        :param value: (bool) Boolean to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(path, FilePath) is False:
            raise sppasTypeError(path, "FilePath")

        return path.expand is bool(value)

# ---------------------------------------------------------------------------


class TestPathCompare(unittest.TestCase):

    def setUp(self):
        self.cmp = sppasPathCompare()

    def test_match(self):
        d = dirname(__file__)
        fp = FilePath(d)

        # fp.id is matching dirname
        self.assertTrue(fp.match([(self.cmp.exact, d, False)]))

        # fp.id is not matching dirname
        self.assertFalse(fp.match([(self.cmp.exact, d, True)]))

        # fp.id is matching dirname and path is checked
        self.assertTrue(fp.match(
            [(self.cmp.exact, d, False),
             (self.cmp.check, True, False)]))

        # fp.id ends with 'files' (the name of the package)!
        self.assertTrue(fp.match([(self.cmp.endswith, "files", False)]))

# ---------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
