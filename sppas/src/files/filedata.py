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

    src.files.filedata.py
    ~~~~~~~~~~~~~~~~~~~~~

    Description:
    ============

    Use instances of these classes to hold data related to a filename. 
    
    Files are structured in a fixed tree-like structure:
        - a FileData contains a list of FilePath,
        - a FilePath contains a list of FileRoot,
        - a FileRoot contains a list of FileName,
        - a FileName is limited to regular file names (no links, etc).

    Example:
    ========

    The file 'C:\\Users\\MyName\\Desktop\\myfile.pdf' and the file
    'C:\\Users\\MyName\\Desktop\\myfile.txt' will be in the following tree:

        + FileData:
            + FilePath: id='C:\\Users\\MyName\\Desktop'
                + FileRoot: id='C:\\Users\\MyName\\Desktop\\myfile'
                    + FileName: 
                        * id='C:\\Users\\MyName\\Desktop\\myfile.pdf'
                        * name='myfile'
                        * extension='.PDF'
                    + FileName: 
                        * id='C:\\Users\\MyName\\Desktop\\myfile.txt'
                        * name='myfile'
                        * extension='.TXT'
    

    Raised exceptions:
    ==================

        - FileOSError (error 9010)
        - FileTypeError (error 9012)
        - PathTypeError (error 9014)
        - FileRootValueError (error 9030)


    Tests:
    ======

        - python 2.7.15
        - python 3.7.0

        More tests should be implemented, particularly FileData is not tested
        at all.

    How to use these classes to filter data:
    ========================================

    A comparator must be implemented to define comparison functions. Then
    the method 'match' of the FileBase class can be invoked.
    The FileDataFilter() class is based on the use of this solution. It allows
    to combine results and is a simplified way to write a request.
    The use of the FileBase().match() is described in the next examples.

    :Example: Search if a FilePath() is exactly matching "my_path":

        >>> cmp = sppasPathCompare()
        >>> fp.match([(cmp.exact, "my_path", False)])

    :Example: Search if a FilePath() is starting with "my_path" and is checked:

        >>> fp.match(
        >>>     [(cmp.startswith, "my_path", False),
        >>>      (cmp.check, True, False)],
        >>>     logic_bool="and")


    :Example: Search if a FileRoot() is exactly matching "my_path/toto":

        >>> cmp = sppasRootCompare()
        >>> fr.match([(cmp.exact, "my_path", False)])

    :Example: Search if a FileRoot() is starting with "my_path/toto"
    and is checked:

        >>> fr.match(
        >>>     [(cmp.startswith, "my_path/toto", False),
        >>>      (cmp.check, True, False)],
        >>>     logic_bool="and")

    :Example: Search if a FileName() is starting with "toto" and is not
    a TextGrid and is checked:

        >>> cmpn = sppasNameCompare()
        >>> cmpe = sppasExtensionCompare()
        >>> cmpp = sppasFileCompare()
        >>> fn.match(
        >>>    [(cmpn.startswith, "toto", False),
        >>>     (cmpe.iexact, "textgrid", True),
        >>>     (cmpp.check, True, False)],
        >>>    logic_bool="and")

"""

import unittest
import random
import mimetypes

from os.path import isfile, isdir, exists
from os.path import splitext, abspath, join
from os.path import getsize, getmtime
from os.path import basename, dirname
from datetime import datetime

from .fileexc import FileOSError, FileTypeError, PathTypeError
from .fileexc import FileRootValueError

# -----------------------------------------------------------------------

    
class FileBase(object):
    """Represents any type of data linked to a filename.
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, filename):
        """Constructor of a FileBase.
        
        :param `filename`: (str) Full name of a file/directory
        :raise: OSError if filename does not match a file nor a directory
        
        The following members are stored:

            - id (str) Identifier - the absolute filename [private]

        """
        self.__id = filename

    # -----------------------------------------------------------------------

    def get_id(self):
        """Return the identifier of the file, i.e. the full name."""
        return self.__id

    # -----------------------------------------------------------------------

    def match(self, functions, logic_bool="and"):
        """Return True if the file matches all or any of the functions.

        Functions are defined in a comparator. They return a boolean.
        The type of the value depends on the function.
        The logical not is used to reverse the result of the function.

        :param functions: list of (function, value, logical_not)
        :param logic_bool: (str) Apply a logical "and" or a logical "or" between the functions.
        :returns: (bool)

        """
        matches = list()
        for func, value, logical_not in functions:
            if logical_not is True:
                matches.append(not func(self, value))
            else:
                matches.append(func(self, value))

        if logic_bool == "and":
            is_matching = all(matches)
        else:
            is_matching = any(matches)

        return is_matching

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    id = property(get_id, None)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    def __str__(self):
        return '{!s:s}'.format(self.__id)

    def __repr__(self):
        return 'File: {!s:s}'.format(self.__id)

# ---------------------------------------------------------------------------

    
class FileName(FileBase):
    """Represent the data linked to a filename.

    Use instances of this class to hold data related to a filename.
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, filename):
        """Constructor of a FileName.

        From the filename, the following properties are extracted:

            0. id (str) Identifier - the absolute filename (from FileBase)
            1. filename (str) The base name of the file, without path nor ext
            2. ext (str) The extension of the file, or the mime type
            3. date (str) Time of the last modification
            4. filesize (str) Size of the file
        
        Some states of the file are also stored:

            - check (bool) File is selected or not
            - lock (bool) File is locked or not (enable/disable)

        :param `filename`: (str) Full name of a file (from FileBase)
        :raise: OSError if filename does not match a file (not dir/link)

        """
        super(FileName, self).__init__(filename)
        if exists(filename) is False:
            raise FileOSError(filename)
        if isfile(self.get_id()) is False:
            raise FileTypeError(filename)

        # Properties of the file (protected)
        # ----------------------------------

        # The displayed filename (no path, no extension) 
        fn, ext = splitext(self.get_id())
        self.__name = basename(fn)

        # The extension is forced to be in upper case
        self.__extension = ext.upper()

        # Modified date/time and file size
        self.__date = " -- "
        self.__filesize = 0
        self.update_properties()
        
        # States of the file
        # ------------------

        self.__check = False
        self.lock = False

    # -----------------------------------------------------------------------

    def folder(self):
        """Return the name of the directory of this file."""
        return dirname(self.get_id())

    # -----------------------------------------------------------------------

    def get_name(self):
        """Return the short name of the file., i.e. without path nor extension."""
        return self.__name

    # -----------------------------------------------------------------------

    def get_extension(self):
        """Return the extension of the file."""
        return self.__extension

    def get_mime(self):
        """Return the mime type of the file."""
        m = mimetypes.guess_type(self.id)
        if m[0] is not None:
            return m[0]
        
        return "unknown"

    # -----------------------------------------------------------------------

    def get_date(self):
        """Return a string representing the date of the last modification."""
        return self.__date
    
    # -----------------------------------------------------------------------

    def get_size(self):
        """Return a string representing the size of the file."""
        unit = " Ko"
        filesize = self.__filesize / 1024
        if filesize > (1024*1024):
            filesize /= 1024
            unit = " Mo"

        return str(int(filesize)) + unit
    
    # -----------------------------------------------------------------------

    def get_check(self):
        """Return true if the file is checked."""
        return self.__check
    
    def set_check(self, value):
        """Set a value to represent a toggle meaning the file is checked.
        
        :param value: (bool)

        """
        self.__check = bool(value)

    # -----------------------------------------------------------------------

    def update_properties(self):
        """Update properties of the file (modified, filesize).
        
        :raise: FileTypeError if the file is not existing

        """
        # test if the file is still existing
        if isfile(self.get_id()) is False:
            raise FileTypeError(self.get_id())

        # get time and size
        self.__date = datetime.fromtimestamp(getmtime(self.get_id()))
        self.__filesize = getsize(self.get_id())

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    check = property(get_check, set_check)
    size = property(get_size, None)
    date = property(get_date, None)
    extension = property(get_extension, None)
    name = property(get_name, None)

# ---------------------------------------------------------------------------


class FileRoot(FileBase):
    """Represent the data linked to the basename of a file.

    We'll use instances of this class to hold data related to the root
    base name of a file. The root of a file is its name without the pattern.
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    # if we create dynamically this list from the existing annotations, we'll
    # have circular imports.
    # solutions to implement are either:
    #     - add this info in each annotation json file (preferred), or
    #     - add this information in the sppasui.json file
    FilePatterns = (
        "-token", "-phon", "-palign", "-syll", "-tga", 
        "-momel", "-intsint", "-ralign")

    # -----------------------------------------------------------------------

    def __init__(self, name):
        """Constructor of a FileRoot.
        
        :param `name`: (str) Filename or rootname
        :raise: OSError if filepath does not match a directory (not file/link)

        """
        root_name = FileRoot.root(name)
        super(FileRoot, self).__init__(root_name)
    
        # A list of FileName instances, i.e. files sharing this root.
        self.__files = list()

        # States of the path
        # ------------------

        self.__check = False
        self.expand = True
        self.__bgcolor = (30, 30, 30)

    # -----------------------------------------------------------------------

    @staticmethod
    def pattern(filename):
        """Return the pattern of the given filename."""
        fn = basename(filename)
        fn = splitext(fn)[0]
        for pattern in FileRoot.FilePatterns:
            if fn.endswith(pattern) is True:
                return pattern
        return ""
    
    # -----------------------------------------------------------------------

    @staticmethod
    def root(filename):
        """Return the root of the given filename."""
        fn = splitext(filename)[0]
        for pattern in FileRoot.FilePatterns:
            if fn.endswith(pattern) is True:
                fn = fn[:len(fn)-len(pattern)]
        return fn

    # -----------------------------------------------------------------------

    def get_bgcolor(self):
        return self.__bgcolor
    
    def set_bgcolor(self, r, g, b):
        # we should check values (0-255)
        self.__bgcolor = (r, g, b)

    bg_color = property(get_bgcolor, set_bgcolor)

    # -----------------------------------------------------------------------

    def get_check(self):
        """Return true if the fileroot is checked."""
        return self.__check
    
    def set_check(self, value):
        """Set a value to represent a toggle meaning the fileroot is checked.
        
        :param value: (bool)

        """
        self.__check = bool(value)
        for fn in self.__files:
            fn.check = value

    check = property(get_check, set_check)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def get_object(self, filename):
        """Return the instance matching the given filename.

        Return self if filename is matching the id.

        :param filename: Full name of a file

        """
        fr = FileRoot.root(filename)

        # Does this filename matches this root
        if fr != self.id:
            return None
        
        # Does it match only the root (no file name)
        if fr == filename:
            return self
        
        # Check if this file is in the list of known files
        for fn in self.__files:
            if fn.id == filename:
                return fn
        
        return None

    # -----------------------------------------------------------------------

    def append(self, filename):
        """Append a filename in the list of files.

        Given filename must be the absolute name of a file or an instance
        of FileName.

        :param filename: (str, FileName) Absolute name of a file
        :return: (FileName) the appended FileName or None

        """
        # Get or create the FileName instance
        fn = filename
        if isinstance(filename, FileName) is False:
            fn = FileName(filename)
        
        # Check if root is ok
        if self.id != FileRoot.root(fn.id):
            raise FileRootValueError(fn.id, self.id)

        # Check if this filename is not already in the list
        for efn in self.__files:
            if efn.id == fn.id:
                return efn
        
        # Nothings wrong. filename is appended
        self.__files.append(fn)
        return fn

    # -----------------------------------------------------------------------

    def remove(self, filename):
        """Remove a filename of the list of files.

        Given filename must be the absolute name of a file or an instance
        of FileName.

        :param filename: (str, FileName) Absolute name of a file
        :return: (int) Index of the removed FileName or -1 if nothing removed.

        """
        idx = -1
        if isinstance(filename, FileName):
            try:
                idx = self.__files.index(filename)
            except ValueError:
                idx = -1
        else:
            # Search for this filename in the list
            for i, fn in enumerate(self.__files):
                if fn.id == filename:
                    idx = i
                    break

        if idx != -1:
            self.__files.pop(idx)
        
        return idx

    # -----------------------------------------------------------------------

    def do_check(self, value=True, filename=None):
        """Check or uncheck all or any file.

        :param filename: (str) Absolute name of a file
        :param value: (bool) Toggle value

        """
        if filename is None:
            for fn in self.__files:
                fn.check = bool(value)
        else:
            root_id = FileRoot.root(filename)
            if root_id != self.id:
                raise FileRootValueError(filename, root_id)
            for fn in self.__files:
                if fn.id == filename:
                    fn.check = bool(value)
                    self.update_check()

    # -----------------------------------------------------------------------

    def update_check(self):
        """Modify check depending on the checked filenames."""
        if len(self.__files) == 0:
            self.check = False
            return
        all_checked = True
        all_unchecked = True
        for fn in self.__files:
            if fn.check is True:
                all_unchecked = False
            else:
                all_checked = False

        if all_checked:
            self.check = True
        if all_unchecked:
            self.check = False

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return 'Root: ' + self.id + \
               ' contains ' + str(len(self.__files)) + ' files\n'

    def __iter__(self):
        for a in self.__files:
            yield a

    def __getitem__(self, i):
        return self.__files[i]

    def __len__(self):
        return len(self.__files)
    
    def __contains__(self, value):
        # The given value is a FileName instance
        if isinstance(value, FileName):
            return value in self.__files
        
        # The given value is a filename
        for fn in self.__files:
            if fn.id == value:
                return True

        # nothing is matching this value
        return False

# ---------------------------------------------------------------------------


class FilePath(FileBase):
    """Represent the data linked to a folder name.

    We'll use instances of this class to hold data related to the path of
    a filename. Items in the tree will get associated back to the 
    corresponding FileName and this FilePath object.
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, filepath):
        """Constructor of a FilePath.
        
        :param `filepath`: (str) Absolute or relative name of a folder
        :raise: OSError if filepath does not match a directory (not file/link)

        """
        super(FilePath, self).__init__(abspath(filepath))
        if exists(filepath) is False:
            raise FileOSError(filepath)
        if isdir(self.get_id()) is False:
            raise PathTypeError(filepath)

        # A list of FileRoot instances
        self.__roots = list()

        # States of the path
        # ------------------

        self.__check = False
        self.expand = True
        self.fgcolor = (
            random.randint(180, 240),
            random.randint(180, 240),
            random.randint(180, 240))
        self.__bgcolor = (
            random.randint(15, 30),
            random.randint(15, 30),
            random.randint(15, 30))

    # -----------------------------------------------------------------------

    def get_check(self):
        return self.__check
    
    def set_check(self, value):
        self.__check = value
        for fr in self.__roots:
            fr.check = value

    check = property(get_check, set_check)
    
    # -----------------------------------------------------------------------

    def get_bgcolor(self):
        return self.__bgcolor
    
    def set_bgcolor(self, r, g, b):
        # we should check values (0-255)
        self.__bgcolor = (r, g, b)
        for fr in self.__roots:
            self.set_root_bgcolor(fr)

    bg_color = property(get_bgcolor, set_bgcolor)

    # -----------------------------------------------------------------------

    def get_object(self, filename):
        """Return the instance matching the given filename.

        :param filename: Name of a file (absolute of relative)

        Notice that it returns `self` if filename is a directory matching 
        self.id.

        """
        fp = abspath(filename)
        if isdir(fp) and fp == self.id:
            return self
        
        elif isfile(filename):
            idt = self.identifier(filename)
            for fr in self.__roots:
                fn = fr.get_object(idt)
                if fn is not None:
                    return fn

        return None

    # -----------------------------------------------------------------------

    def identifier(self, filename):
        """Return the identifier, i.e. the full name of the file.

        :param filename: (str) Absolute or relative name of a file
        :return: (str) Identifier for this filename
        :raise: FileOSError if filename does not match a regular file

        """
        f = abspath(filename)

        if isfile(f) is False:
            f = join(self.id, filename)

        if isfile(f) is False:
            raise FileOSError(filename)

        return f

    # -----------------------------------------------------------------------

    def get_root(self, name):
        """Return the FileRoot matching the given id (root or file).
        
        :param name: (str) Identifier name of a root or a file.
        :return: FileRoot or None
 
        """
        for fr in self.__roots:
            if fr.id == name:
                return fr

        for fr in self.__roots:
            for fn in fr:
                if fn.id == name:
                    return fr

        return None

    # -----------------------------------------------------------------------

    def append(self, filename):
        """Append a filename in the list of files.

        Given filename can be either an absolute or relative name of a file
        or an instance of FileName.

        :param filename: (str, FileName) Absolute or relative name of a file
        :return: (FileName) the appended FileName of None

        """
        if isinstance(filename, FileName):
            file_id = filename.id
        else:
            file_id = self.identifier(filename)
            filename = FileName(file_id)
        root_id = FileRoot.root(file_id)

        # Get or create the corresponding FileRoot
        fr = self.get_root(root_id)
        if fr is None:
            fr = FileRoot(root_id)
            self.__roots.append(fr)
            self.set_root_bgcolor(fr)
        
        # Append this file to the root
        return fr.append(filename)

    # -----------------------------------------------------------------------

    def set_root_bgcolor(self, root):
        """Fix the bgcolor of a root."""
        index = self.__roots.index(root)
        if index % 2:
            r = max(10, min(245, self.__bgcolor[0] + 4))
            g = max(10, min(245, self.__bgcolor[1] + 4))
            b = max(10, min(245, self.__bgcolor[2] + 4))
            root.bgcolor = (r, g, b)
        else:
            r = max(10, min(245, self.__bgcolor[0] - 4))
            g = max(10, min(245, self.__bgcolor[1] - 4))
            b = max(10, min(245, self.__bgcolor[2] - 4))
            root.bgcolor = (r, g, b)

    # -----------------------------------------------------------------------

    def remove(self, fileroot):
        """Remove a fileroot of the list of roots.

        Given fileroot can be either the identifier of a root or an instance 
        of FileRoot.

        :param fileroot: (str or FileRoot)
        :return: (int) Index of the removed FileRoot or -1 if nothing removed.
        
        """
        if isinstance(fileroot, FileRoot):
            root = fileroot
        else:
            root = self.get_root(fileroot)

        try:
            idx = self.__roots.index(root)
            self.__roots.pop(idx)
        except ValueError:
            idx = -1

        return idx

    # -----------------------------------------------------------------------

    def do_check(self, value=True, entry=None):
        """Check or uncheck all or any file.

        :param value: (bool) Toggle value
        :param entry: (str) Absolute or relative name of a file or a file root

        """
        change = False
        if entry is None:
            for fr in self.__roots:
                fr.check = bool(value)
            change = True

        elif isinstance(entry, FileRoot):
            if entry in self.__roots:
                entry.check = bool(value)
                change = True

        else:
            fr = self.get_root(entry)
            if fr is not None:
                fr.do_check(value, entry)
                change = True

        if change:    
            self.update_check()
    
    # -----------------------------------------------------------------------

    def update_check(self):
        """Modify check depending on the checked root names."""
        if len(self.__roots) == 0:
            self.check = False
            return
        all_checked = True
        all_unchecked = True
        for fr in self.__roots:
            if fr.check is True:
                all_unchecked = False
            else:
                all_checked = False

        if all_checked:
            self.check = True
        if all_unchecked:
            self.check = False

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return 'Path: ' + self.get_id() + \
               ' contains ' + str(len(self.__roots)) + ' file roots\n'

    def __iter__(self):
        for a in self.__roots:
            yield a

    def __getitem__(self, i):
        return self.__roots[i]

    def __len__(self):
        return len(self.__roots)
    
    def __contains__(self, value):
        # The given value is a FileRoot instance
        if isinstance(value, FileRoot):
            return value in self.__roots
        
        # The given value is a FileName instance or a string
        for fr in self.__roots:
            x = value in fr
            if x is True:
                return True

        # Value could be the name of a root
        root_id = FileRoot.root(value)
        fr = self.get_root(root_id)
        if fr is not None:
            return True

        # nothing is matching this value
        return False

# ---------------------------------------------------------------------------


class FileData(object):
    """Represent the data linked to a list of files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    FileData is the manager of a list of file names.
    It organizes them hierarchically as a collection of FilePath instances, 
    each of which is a collection of FileRoot instances, each of which is a 
    collection of FileName. 

    """

    def __init__(self):
        """Constructor of a FileData."""
        self.__data = list()

    # -----------------------------------------------------------------------

    def add_file(self, filename):
        """Add a file in the list from its file name.

        :param filename: (str) Absolute or relative name of a file
        :return: (FileName)
        :raises: OSError

        """
        new_fp = FilePath(dirname(filename))
        for fp in self.__data:
            if fp.id == new_fp.id:
                new_fp = fp
        
        if new_fp not in self.__data:
            # this is a new path to add
            self.__data.append(new_fp)

        return new_fp.append(filename)

    # -----------------------------------------------------------------------

    def update(self):
        """Update the data: missing files, properties changed."""
        for fp in self.__data:
            for fr in reversed(fp):
                for fn in reversed(fr):
                    if exists(fn.id):
                        fn.update_properties()
                    else:
                        fp.remove(fn)
                if len(fr) == 0:
                    fp.remove(fr)
            # reset bg colors of the roots
            for fr in fp:
                fp.set_root_bgcolor(fr)

        # Remove empty FilePath
        for fp in reversed(self.__data):
            if len(fp) == 0:
                self.__data.remove(fp)
    
    # -----------------------------------------------------------------------

    def remove_checked_files(self):
        """Remove all checked files.
        
        Do not update: empty roots or paths are not removed.

        """
        for fp in self.__data:
            for fr in reversed(fp):
                for fn in reversed(fr):
                    if fn.check is True:
                        fr.remove(fn)
 
    # -----------------------------------------------------------------------

    def get_checked_files(self, value=True):
        """Return the list of checked or unchecked file names.

        :param value: (bool) Toggle state
        :return: (list of str)

        """
        checked = list()
        for fp in self.__data:
            for fr in fp:
                for fn in fr:
                    if fn.check == value:
                        checked.append(fn.id)
        return checked

    # -----------------------------------------------------------------------

    def check(self, value=True, entry=None):
        """Check or uncheck all or any entry.

        If no entry is given, this method toggles all the data.

        :param value: (bool) Toggle value
        :param entry: (str) Absolute or relative name of a file or a file root

        """
        if entry is not None:
            try:
                path = dirname(entry)
            except TypeError:
                raise FileOSError(entry)

            new_fp = FilePath(path)
            for fp in self.__data:
                if fp.id == new_fp.id:
                    fp.do_check(value, entry)
        else:
            for fp in self.__data:
                fp.do_check(value)

    # -----------------------------------------------------------------------

    def get_expanded_objects(self, value=True):
        """Return the list of expanded or collapsed FilePath and FileRoot.

        :param value: (bool) Toggle state
        :return: (list of FilePath and FileRoot objects)

        """
        expanded = list()
        for fp in self.__data:
            if fp.expand == value:
                expanded.append(fp)
            for fr in fp:
                if fr.expand == value:
                    expanded.append(fr)
        return expanded

    # -----------------------------------------------------------------------

    def expand(self, value=True):
        """Expand or collapse all the FilePath instances."""
        for fp in self.__data:
            fp.expand = bool(value)

    # -----------------------------------------------------------------------

    def expand_all(self, value=True):
        """Expand or collapse all the FilePath and FileRoot instances."""
        for fp in self.__data:
            fp.expand = bool(value)
            for fr in fp:
                fr.expand = bool(value)

    # -----------------------------------------------------------------------

    def get_object(self, entry):
        """Return the file object matching the given entry.
        
        :return: (FilePath, FileRoot, FileName)

        """
        try:
            path = dirname(entry)
            new_fp = FilePath(path)
        except TypeError:
            return None

        for fp in self.__data:
            if fp.id == new_fp.id:
                return fp.get_object(entry)
        
        return None

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __iter__(self):
        for a in self.__data:
            yield a

    def __getitem__(self, i):
        return self.__data[i]

    def __len__(self):
        return len(self.__data)
    
# ---------------------------------------------------------------------------
