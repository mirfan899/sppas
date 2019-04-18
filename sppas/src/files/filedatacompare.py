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

from .filedata import FilePath, FileRoot, FileName


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


class sppasRootCompare(sppasBaseCompare):
    """Comparison methods for FileRoot.

        :author:       Brigitte Bigi
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      develop@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

        :Example: Three different ways to compare a file data content to a given string

            >>> tc = sppasRootCompare()
            >>> tc.exact(FileRoot("oriana1"), u("oriana1"))
            >>> tc.methods['exact'](FileRoot("oriana1"), u("oriana1"))
            >>> tc.get('exact')(FileRoot("oriana1"), u("oriana1"))

        """

    def __init__(self):
        """Create a sppasRootCompare instance."""
        super(sppasRootCompare, self).__init__()

        # Compare the id to a text value
        self.methods['exact'] = sppasRootCompare.exact
        self.methods['iexact'] = sppasRootCompare.iexact
        self.methods['startswith'] = sppasRootCompare.startswith
        self.methods['istartswith'] = sppasRootCompare.istartswith
        self.methods['endswith'] = sppasRootCompare.endswith
        self.methods['iendswith'] = sppasRootCompare.iendswith
        self.methods['contains'] = sppasRootCompare.contains
        self.methods['icontains'] = sppasRootCompare.icontains
        self.methods['regexp'] = sppasRootCompare.regexp

        # Compare check/expand to a boolean value
        self.methods['check'] = sppasRootCompare.check
        self.methods['expand'] = sppasRootCompare.expand

    # -----------------------------------------------------------------------
    # Root identifier
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(root, value):
        """Test if root strictly matches value.

        :param root: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return root.id == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(root, value):
        """Test if root matches value without case sensitive.

        :param root: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return root.id.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(root, value):
        """Test if root starts with the characters of the value.

        :param root: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return root.id.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(root, value):
        """Case-insensitive startswith.

        :param root: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return root.id.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(root, value):
        """Test if root ends with the characters of the value.

        :param root: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return root.id.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(root, value):
        """Case-insensitive endswith.

        :param root: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return root.id.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(root, value):
        """Test if the root contains the value.

        :param root: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in root.id

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(root, value):
        """Case-insensitive contains.

        :param root: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in root.id.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(root, pattern):
        """Test if text matches pattern.

        :param root: (FileRoot) Root to compare.
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")
        text = root.id

        return True if re.match(pattern, text) else False

    # -----------------------------------------------------------------------
    # Check/Expand members
    # -----------------------------------------------------------------------

    @staticmethod
    def check(root, value):
        """Compare check member to the given value.

        :param root: (FileRoot) Root to compare.
        :param value: (bool) Boolean to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")

        return root.check is bool(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def expand(root, value):
        """Compare expand member to the given value.

        :param root: (FileRoot) Root to compare.
        :param value: (bool) Boolean to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(root, FileRoot) is False:
            raise sppasTypeError(root, "FileRoot")

        return root.expand is bool(value)


# ---------------------------------------------------------------------------


class sppasFileNameCompare(sppasBaseCompare):

    def __init__(self):
        """Create a sppasRootCompare instance."""
        super(sppasFileNameCompare, self).__init__()

        # Compare the id to a text value
        self.methods['exact'] = sppasFileNameCompare.exact
        self.methods['iexact'] = sppasFileNameCompare.iexact
        self.methods['startswith'] = sppasFileNameCompare.startswith
        self.methods['istartswith'] = sppasFileNameCompare.istartswith
        self.methods['endswith'] = sppasFileNameCompare.endswith
        self.methods['iendswith'] = sppasFileNameCompare.iendswith
        self.methods['contains'] = sppasFileNameCompare.contains
        self.methods['icontains'] = sppasFileNameCompare.icontains
        self.methods['regexp'] = sppasFileNameCompare.regexp

    # -----------------------------------------------------------------------
    # FileName name
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(file, value):
        """Test if name strictly matches value.

        :param file: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return file.name == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(file, value):
        """Test if name matches value without case sensitive.

        :param file: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return file.name.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(file, value):
        """Test if name starts with the characters of the value.

        :param file: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return file.name.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(file, value):
        """Case-insensitive startswith.

        :param file: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return file.name.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(file, value):
        """Test if name ends with the characters of the value.

        :param file: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return file.name.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(file, value):
        """Case-insensitive endswith.

        :param file: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return file.name.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(file, value):
        """Test if the name contains the value.

        :param file: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in file.name

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(file, value):
        """Case-insensitive contains.

        :param file: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileRoot) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in file.name.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(file, pattern):
        """Test if text matches pattern.

        :param file: (FileName) Name to compare.
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        text = file.name

        return True if re.match(pattern, text) else False

# ---------------------------------------------------------------------------

class sppasFileNameExtensionCompare(sppasBaseCompare):

    def __init__(self):
        """Create a sppasFileNameExtensionComparator instance."""
        super(sppasFileNameExtensionCompare, self).__init__()

        # Compare the id to a text value
        self.methods['exact'] = sppasFileNameExtensionCompare.exact
        self.methods['iexact'] = sppasFileNameExtensionCompare.iexact
        self.methods['startswith'] = sppasFileNameExtensionCompare.startswith
        self.methods['istartswith'] = sppasFileNameExtensionCompare.istartswith
        self.methods['endswith'] = sppasFileNameExtensionCompare.endswith
        self.methods['iendswith'] = sppasFileNameExtensionCompare.iendswith
        self.methods['contains'] = sppasFileNameExtensionCompare.contains
        self.methods['icontains'] = sppasFileNameExtensionCompare.icontains
        self.methods['regexp'] = sppasFileNameExtensionCompare.regexp

    # -----------------------------------------------------------------------
    # FileName Extension
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(file, value):
        """Test if name strictly matches value.

        :param file: (FileName) Extension to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return file.extension == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(file, value):
        """Test if extension matches value without case sensitive.

        :param file: (FileName) Extension to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return file.extension.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(file, value):
        """Test if extension starts with the characters of the value.

        :param file: (FileName) Extension to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return file.extension.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(file, value):
        """Case-insensitive startswith.

        :param file: (FileName) Extension to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return file.extension.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(file, value):
        """Test if extension ends with the characters of the value.

        :param file: (FileName) Extension to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return file.extension.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(file, value):
        """Case-insensitive endswith.

        :param file: (FileName) Extension to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return file.extension.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(file, value):
        """Test if the name contains the value.

        :param file: (FileName) Extension to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in file.extension

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(file, value):
        """Case-insensitive contains.

        :param file: (FileName) Extension to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in file.extension.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(file, pattern):
        """Test if text matches pattern.

        :param file: (FileName) Extension to compare.
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")
        text = file.extension

        return True if re.match(pattern, text) else False

# ---------------------------------------------------------------------------


class sppasFileNamePropertiesCompare(sppasBaseCompare):

    def __init__(self):
        """Create a sppasFileNameExtensionComparator instance."""
        super(sppasFileNamePropertiesCompare, self).__init__()

        # Compare the id to a text value
        self.methods['lock'] = sppasFileNamePropertiesCompare.lock

    # -----------------------------------------------------------------------
    # FileName Properties
    # -----------------------------------------------------------------------

    @staticmethod
    def lock(file, value):
        """Compare lock member to the given value

        :param file: (FileName) File to compare.
        :param value: (bool) Boolean to be compared with.
        :returns: (bool)
        :raises: sppasTypeError
        """
        if isinstance(file, FileName) is False:
            raise sppasTypeError(file, "FileName")

        return file.lock is bool(value)

# ---------------------------------------------------------------------------