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
          (FilePath.id, FilePath.state, FilePath.expand)

    To do:
    =====

        - sppasRootCompare() to search for a value in a root name
          (FileRoot.id, FileRoot.state, FileRoot.expand)

        - sppasNameCompare() to search for a value in a file name
          (FileName.name)

        - sppasExtensionCompare() to search for a value in the extension of a
          file name (FileName.ext)

        - sppasFileCompare() to search for a value in the members of a
          file name (FileName.state, FileName.lock, FileName....)

        - the unitests for all classes and methods.

"""

import re

from sppas import sppasTypeError
from .filebase import States
from ..utils.makeunicode import text_type
from ..structs.basecompare import sppasBaseCompare

from .filestructure import FilePath, FileRoot, FileName
from .fileref import FileReference, sppasAttribute

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

        # Compare state/expand to a boolean value
        self.methods['check'] = sppasPathCompare.check

    # -----------------------------------------------------------------------
    # Path identifier
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(fp, value):
        """Test if path strictly matches value.

        :param fp: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fp, FilePath) is False:
            raise sppasTypeError(fp, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return fp.id == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(fp, value):
        """Test if path matches value without case sensitive.

        :param fp: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fp, FilePath) is False:
            raise sppasTypeError(fp, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fp.id.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(fp, value):
        """Test if path starts with the characters of the value.

        :param fp: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fp, FilePath) is False:
            raise sppasTypeError(fp, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fp.id.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(fp, value):
        """Case-insensitive startswith.

        :param fp: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fp, FilePath) is False:
            raise sppasTypeError(fp, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fp.id.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(fp, value):
        """Test if path ends with the characters of the value.

        :param fp: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fp, FilePath) is False:
            raise sppasTypeError(fp, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fp.id.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(fp, value):
        """Case-insensitive endswith.

        :param fp: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fp, FilePath) is False:
            raise sppasTypeError(fp, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fp.id.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(fp, value):
        """Test if the path contains the value.

        :param fp: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fp, FilePath) is False:
            raise sppasTypeError(fp, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in fp.id

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(fp, value):
        """Case-insensitive contains.

        :param fp: (FilePath) Path to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fp, FilePath) is False:
            raise sppasTypeError(fp, "FilePath")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in fp.id.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(fp, pattern):
        """Test if text matches pattern.

        :param fp: (FilePath) Path to compare.
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fp, FilePath) is False:
            raise sppasTypeError(fp, "FilePath")
        text = fp.id

        return True if re.match(pattern, text) else False

    # -----------------------------------------------------------------------
    # Check/Expand members
    # -----------------------------------------------------------------------

    @staticmethod
    def check(fp, value):
        """Compare state member to the given value.

        :param fp: (FilePath) Path to compare.
        :param value: (bool) Boolean to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fp, FilePath) is False:
            raise sppasTypeError(fp, "FilePath")

        return (fp.state is States().CHECKED) == value

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

        # Compare state/expand to a boolean value
        self.methods['check'] = sppasRootCompare.check

    # -----------------------------------------------------------------------
    # Root identifier
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(fr, value):
        """Test if root strictly matches value.

        :param fr: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fr, FileRoot) is False:
            raise sppasTypeError(fr, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return fr.id == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(fr, value):
        """Test if root matches value without case sensitive.

        :param fr: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fr, FileRoot) is False:
            raise sppasTypeError(fr, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fr.id.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(fr, value):
        """Test if root starts with the characters of the value.

        :param fr: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fr, FileRoot) is False:
            raise sppasTypeError(fr, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fr.id.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(fr, value):
        """Case-insensitive startswith.

        :param fr: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fr, FileRoot) is False:
            raise sppasTypeError(fr, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fr.id.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(fr, value):
        """Test if root ends with the characters of the value.

        :param fr: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fr, FileRoot) is False:
            raise sppasTypeError(fr, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fr.id.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(fr, value):
        """Case-insensitive endswith.

        :param fr: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fr, FileRoot) is False:
            raise sppasTypeError(fr, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fr.id.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(fr, value):
        """Test if the root contains the value.

        :param fr: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fr, FileRoot) is False:
            raise sppasTypeError(fr, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in fr.id

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(fr, value):
        """Case-insensitive contains.

        :param fr: (FileRoot) Root to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fr, FileRoot) is False:
            raise sppasTypeError(fr, "FileRoot")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in fr.id.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(fr, pattern):
        """Test if text matches pattern.

        :param fr: (FileRoot) Root to compare.
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fr, FileRoot) is False:
            raise sppasTypeError(fr, "FileRoot")
        text = fr.id

        return True if re.match(pattern, text) else False

    # -----------------------------------------------------------------------
    # Check/Expand members
    # -----------------------------------------------------------------------

    @staticmethod
    def check(fr, value):
        """Compare state member to the given value.

        :param fr: (FileRoot) Root to compare.
        :param value: (bool) Boolean to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fr, FileRoot) is False:
            raise sppasTypeError(fr, "FileRoot")

        return (fr.statefr is States().CHECKED) == value

# ---------------------------------------------------------------------------


class sppasFileNameCompare(sppasBaseCompare):
    """Comparison methods for FileName id.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    :Example: Three different ways to compare a file data content to a given string

    >>> tc = sppasFileNameCompare()
    >>> tc.exact(FileName("oriana1"), u("oriana1"))
    >>> tc.methods['exact'](FileName("oriana1"), u("oriana1"))
    >>> tc.get('exact')(FileName("oriana1"), u("oriana1"))
    """

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
    def exact(fn, value):
        """Test if name strictly matches value.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return fn.name == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(fn, value):
        """Test if name matches value without case sensitive.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fn.name.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(fn, value):
        """Test if name starts with the characters of the value.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fn.name.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(fn, value):
        """Case-insensitive startswith.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fn.name.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(fn, value):
        """Test if name ends with the characters of the value.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fn.name.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(fn, value):
        """Case-insensitive endswith.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fn.name.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(fn, value):
        """Test if the name contains the value.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in fn.name

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(fn, value):
        """Case-insensitive contains.

        :param fn: (FileName) Name to compare.
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileRoot) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in fn.name.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(fn, pattern):
        """Test if text matches pattern.

        :param fn: (FileName) Name to compare.
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        text = fn.name

        return True if re.match(pattern, text) else False

# ---------------------------------------------------------------------------


class sppasFileNameExtensionCompare(sppasBaseCompare):
    """Comparison methods for FileName extension.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    :Example: Three different ways to compare a file data content to a given string

    >>> tc = sppasFileNameExtensionCompare()
    >>> tc.exact(FileName("oriana1"), u("oriana1"))
    >>> tc.methods['exact'](FileName("oriana1"), u("oriana1"))
    >>> tc.get('exact')(FileName("oriana1"), u("oriana1"))
    """

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
    def exact(fn, value):
        """Test if name strictly matches value.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return fn.extension == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(fn, value):
        """Test if extension matches value without case sensitive.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fn.extension.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(fn, value):
        """Test if extension starts with the characters of the value.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fn.extension.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(fn, value):
        """Case-insensitive startswith.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fn.extension.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(fn, value):
        """Test if extension ends with the characters of the value.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fn.extension.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(fn, value):
        """Case-insensitive endswith.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return fn.extension.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(fn, value):
        """Test if the name contains the value.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in fn.extension

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(fn, value):
        """Case-insensitive contains.

        :param fn: (FileName) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in fn.extension.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(fn, pattern):
        """Test if text matches pattern.

        :param fn: (FileName) 
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, "FileName")
        text = fn.extension

        return True if re.match(pattern, text) else False

# ---------------------------------------------------------------------------


class sppasFileNameStateCompare(sppasBaseCompare):
    """Comparison methods for FileName properties.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    :Example: Three different ways to compare a file data content to a given string

    >>> tc = sppasFileNameStateCompare()
    >>> tc.state(FileName("oriana1"), States().UNUSED)
    >>> tc.methods['state'](FileName("oriana1"), States().UNUSED)
    >>> tc.get('state')(FileName("oriana1"), States().UNUSED)
    """

    def __init__(self):
        """Create a sppasFileNameExtensionComparator instance."""
        super(sppasFileNameStateCompare, self).__init__()

        # Compare the state to a given value
        self.methods['state'] = sppasFileNameStateCompare.state

    @staticmethod
    def state(fn, state):
        if isinstance(fn, FileName) is False:
            raise sppasTypeError(fn, FileName)
        if isinstance(state, int) is False:
            raise sppasTypeError(state, 'States')

        return fn.get_state() == state

# ---------------------------------------------------------------------------


class sppasReferenceCompare(sppasBaseCompare):
    """Comparison methods for Category id.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    :Example: Three different ways to compare a file data content to a given string

    >>> tc = sppasReferenceCompare()
    >>> tc.exact(FileReference("mic"), u("mic"))
    >>> tc.methods['exact'](FileReference("mic"), u("mic"))
    >>> tc.get('exact')(FileReference("mic"), u("mic"))
    """

    def __init__(self):
        """Create a sppasReferenceCompare instance."""
        super(sppasReferenceCompare, self).__init__()

        # Compare the id to a text value
        self.methods['exact'] = sppasReferenceCompare.exact
        self.methods['iexact'] = sppasReferenceCompare.iexact
        self.methods['startswith'] = sppasReferenceCompare.startswith
        self.methods['istartswith'] = sppasReferenceCompare.istartswith
        self.methods['endswith'] = sppasReferenceCompare.endswith
        self.methods['iendswith'] = sppasReferenceCompare.iendswith
        self.methods['contains'] = sppasReferenceCompare.contains
        self.methods['icontains'] = sppasReferenceCompare.icontains
        self.methods['regexp'] = sppasReferenceCompare.regexp

    # -----------------------------------------------------------------------
    # Reference Id
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(cat, value):
        """Test if the id strictly matches value.

        :param cat: (Category) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, FileReference) is False:
            raise sppasTypeError(cat, "Reference")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        # perhaps we should test with all systems separators ( '/' or '\' )
        return cat.id == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(cat, value):
        """Test if the id matches value without case sensitive.

        :param cat: (Category) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, FileReference) is False:
            raise sppasTypeError(cat, "Category")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return cat.id.lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(cat, value):
        """Test if the id starts with the characters of the value.

        :param cat: (Category) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, FileReference) is False:
            raise sppasTypeError(cat, "Category")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return cat.id.startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(cat, value):
        """Case-insensitive startswith.

        :param cat: (Category) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, FileReference) is False:
            raise sppasTypeError(cat, "Category")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return cat.id.lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(cat, value):
        """Test if the id ends with the characters of the value.

        :param cat: (Category) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, FileReference) is False:
            raise sppasTypeError(cat, "Category")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return cat.id.endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(cat, value):
        """Case-insensitive endswith.

        :param cat: (Category) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, FileReference) is False:
            raise sppasTypeError(cat, "Category")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return cat.id.lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(cat, value):
        """Test if the id contains the value.

        :param cat: (Category) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, FileReference) is False:
            raise sppasTypeError(cat, "Category")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in cat.id

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(cat, value):
        """Case-insensitive contains.

        :param cat: (Category) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, FileReference) is False:
            raise sppasTypeError(cat, "Category")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in cat.id.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(cat, pattern):
        """Test if id matches pattern.

        :param cat: (Category) 
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(cat, FileReference) is False:
            raise sppasTypeError(cat, "FileName")
        text = cat.id

        return True if re.match(pattern, text) else False

# ---------------------------------------------------------------------------


class sppasAttributeCompare(sppasBaseCompare):
    """Comparison methods for sppasAttribute.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create a sppassppasAttributeCompare instance."""
        super(sppasAttributeCompare, self).__init__()

        # Compare the value to a text value
        self.methods['exact'] = sppasAttributeCompare.exact
        self.methods['iexact'] = sppasAttributeCompare.iexact
        self.methods['startswith'] = sppasAttributeCompare.startswith
        self.methods['istartswith'] = sppasAttributeCompare.istartswith
        self.methods['endswith'] = sppasAttributeCompare.endswith
        self.methods['iendswith'] = sppasAttributeCompare.iendswith
        self.methods['contains'] = sppasAttributeCompare.contains
        self.methods['icontains'] = sppasAttributeCompare.icontains
        self.methods['regexp'] = sppasAttributeCompare.regexp

        # Compare the value to a numeric value
        self.methods['equal'] = sppasAttributeCompare.equals
        self.methods['iequal'] = sppasAttributeCompare.iequals
        self.methods['fequal'] = sppasAttributeCompare.fequals
        self.methods['gt'] = sppasAttributeCompare.gt
        self.methods['ge'] = sppasAttributeCompare.ge
        self.methods['lt'] = sppasAttributeCompare.lt
        self.methods['le'] = sppasAttributeCompare.le

    # -----------------------------------------------------------------------
    # Reference sppasAttribute
    # -----------------------------------------------------------------------

    @staticmethod
    def exact(att, value):
        """Test if the attribute value strictly matches value.

        :param att: (sppasAttribute) 
        :param value: (str) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value() == value

    # -----------------------------------------------------------------------

    @staticmethod
    def iexact(att, value):
        """Test if the att matches value without case sensitive.

        :param att: (sppasAttribute) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value().lower() == value.lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def startswith(att, value):
        """Test if the att starts with the characters of the value.

        :param att: (sppasAttribute)
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value().startswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def istartswith(att, value):
        """Case-insensitive startswith.

        :param att: (sppasAttribute) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value().lower().startswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def endswith(att, value):
        """Test if the att ends with the characters of the value.

        :param att: (sppasAttribute) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value().endswith(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iendswith(att, value):
        """Case-insensitive endswith.

        :param cat: (Category) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return att.get_value().lower().endswith(value.lower())

    # -----------------------------------------------------------------------

    @staticmethod
    def contains(att, value):
        """Test if the att contains the value.

        :param att: (sppasAttribute) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value in att.get_value()

    # -----------------------------------------------------------------------

    @staticmethod
    def icontains(att, value):
        """Case-insensitive contains.

        :param att: (sppasAttribute) 
        :param value: (unicode) Unicode string to be compared with.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, text_type):
            raise sppasTypeError(value, text_type)

        return value.lower() in att.get_value().lower()

    # -----------------------------------------------------------------------

    @staticmethod
    def regexp(att, pattern):
        """Test if att matches pattern.

        :param att: (sppasAttribute) 
        :param pattern: (unicode) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        text = att.get_value()

        return True if re.match(pattern, text) else False

    # -----------------------------------------------------------------------

    @staticmethod
    def equals(att, value):
        """Test if att equals the given numerical value.

        :param att: (sppasAttribute)
        :param value: (number) The value to compare
        :returns: (bool)
        :raises: sppasTypeError

        """
        return sppasAttributeCompare.iequals(att, value) or \
               sppasAttributeCompare.fequals(att, value)

    # -----------------------------------------------------------------------

    @staticmethod
    def iequals(att, value):
        """Test if att equals the given value.

        :param att: (sppasAttribute) 
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, int):
            raise sppasTypeError(value, "int")

        return att.get_typed_value() == value

    # -----------------------------------------------------------------------

    @staticmethod
    def fequals(att, value, precision):
        """Test if att equals the given value.

        :param att: (sppasAttribute) 
        :param value: (number) Pattern to search.
        :param precision: (number) Vagueness around the value
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, float):
            raise sppasTypeError(value, "float")

        return value - precision < att.get_typed_value() < value + precision

    # -----------------------------------------------------------------------

    @staticmethod
    def gt(att, value):
        """Test if att is strictly greater than the given value.

        :param att: (sppasAttribute) 
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, int) or not isinstance(value, float):
            raise sppasTypeError(value, "number")

        return att.get_typed_value() > value

    # -----------------------------------------------------------------------

    @staticmethod
    def ge(att, value):
        """Test if att is greater than or equal to the given value.

        :param att: (sppasAttribute) 
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, int) or not isinstance(value, float):
            raise sppasTypeError(value, "number")

        return att.get_typed_value() >= value

    # -----------------------------------------------------------------------

    @staticmethod
    def lt(att, value):
        """Test if att is less than the given value.

        :param att: (sppasAttribute) 
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, int) or not isinstance(value, float):
            raise sppasTypeError(value, "number")

        return att.get_typed_value() < value

    # -----------------------------------------------------------------------

    @staticmethod
    def le(att, value):
        """Test if att is less than or equal to the given value.

        :param att: (sppasAttribute) 
        :param value: (number) Pattern to search.
        :returns: (bool)
        :raises: sppasTypeError

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")
        if not isinstance(value, int) or not isinstance(value, float):
            raise sppasTypeError(value, "number")

        return att.get_typed_value() <= value

