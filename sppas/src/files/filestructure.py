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

    src.files.filestructure.py
    ~~~~~~~~~~~~~~~~~~~~~

"""

import mimetypes
from datetime import datetime

from os.path import splitext, abspath, join
from os.path import getsize, getmtime
from os.path import isfile, isdir, exists
from os.path import basename, dirname

from sppas import sppasTypeError
from .fileref import Reference
from .fileexc import FileOSError, FileTypeError, PathTypeError
from .fileexc import FileRootValueError
from .filebase import FileBase, States

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

    def __init__(self, identifier):
        """Constructor of a FileName.

        From the identifier, the following properties are extracted:

            0. id (str) Identifier - the absolute identifier (from FileBase)
            1. identifier (str) The base name of the file, without path nor ext
            2. ext (str) The extension of the file, or the mime type
            3. date (str) Time of the last modification
            4. filesize (str) Size of the file

        Some states of the file are also stored.

        :param `identifier`: (str) Full name of a file (from FileBase)
        :raise: OSError if identifier does not match a file (not dir/link)

        """
        super(FileName, self).__init__(identifier)
        if exists(identifier) is False:
            raise FileOSError(identifier)
        if isfile(self.get_id()) is False:
            raise FileTypeError(identifier)

        # Properties of the file (protected)
        # ----------------------------------

        # The displayed identifier (no path, no extension)
        fn, ext = splitext(self.get_id())
        self.__name = basename(fn)

        # The extension is forced to be in upper case
        self.__extension = ext.upper()

        # Modified date/time and file size
        self.__date = " -- "
        self.__filesize = 0
        self.update_properties()

        self.states = (States().UNUSED, States().CHECKED, States().LOCKED)

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
        if filesize > (1024 * 1024):
            filesize /= 1024
            unit = " Mo"

        return str(int(filesize)) + unit

    # -----------------------------------------------------------------------

    def set_state(self, value):
        """Set a value to represent one of the states.

        :param value: (bool)

        """
        if value in self.states:
            self._state = value
        else:
            raise sppasTypeError(value, 'States')

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

    statefn = property(FileBase.get_state, set_state)
    size = property(get_size, None)
    date = property(get_date, None)
    extension = property(get_extension, None)
    name = property(get_name, None)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __hash__(self):
        return hash((self.__name,
                     self.__date,
                     self.__extension,
                     self.__filesize,
                     self._state,
                     self.id))

    def __eq__(self, other):
        if other is not None:
            return self.id == other.id

        return False

    def __ne__(self, other):
        if other is not None:
            return self.id != other.id

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

        # References
        self.__references = None

        self.states = (States().UNUSED,
                       States().CHECKED,
                       States().LOCKED,
                       States().ALL_CHECKED,
                       States().ALL_LOCKED
                       )

        # A free to use dictionary to expand the class
        self.subjoined = dict()

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
                fn = fn[:len(fn) - len(pattern)]
        return fn

    # -----------------------------------------------------------------------

    def set_state(self, value):
        """Set a value to represent a toggle meaning the fileroot is checked.

        :param value: (int) A state of FileRoot.

        """
        if isinstance(value, int):
            self._state = value
        else:
            raise sppasTypeError(value, 'States')

        for fn in self.__files:
            if value == States().UNUSED:
                fn.set_state(States().UNUSED)
            elif value == States().ALL_CHECKED:
                fn.set_state(States().CHECKED)
            elif value == States().ALL_LOCKED:
                fn.set_state(States().LOCKED)

    statefr = property(FileBase.get_state, set_state)

    # -----------------------------------------------------------------------

    def get_references(self):
        """If the reference catalog is not set yet, instead of returning None the method returns an empty list."""
        if self.__references is None:
            return list()
        return self.__references

    def set_references(self, list_of_references):
        """In order to set the references one must provide a list of category or an empty list.

        :param list_of_references: (list)

        """
        self.__references = list()
        if isinstance(list_of_references, list):
            if len(list_of_references) > 0:
                for reference in list_of_references:
                    if not isinstance(reference, Reference):
                        raise sppasTypeError(reference, 'Reference')

            self.__references = list_of_references
        else:
            raise sppasTypeError(list_of_references, 'list')

    references = property(get_references, set_references)

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

    def update_state(self):
        """Modify state depending on the checked filenames."""
        if len(self.__files) == 0:
            self.set_state(States().UNUSED)
            return

        checked = 0
        locked = 0
        for fn in self.__files:
            if fn.get_state() == States().CHECKED:
                checked += 1
            elif fn.get_state() == States().LOCKED:
                locked += 1

        if locked == len(self.__files):
            self.set_state(States().ALL_LOCKED)
        elif locked > 1:
            self.set_state(States().AT_LEAST_ONE_LOCKED)
        elif checked == len(self.__files):
            self.set_state(States().ALL_CHECKED)
        elif checked > 1:
            self.set_state(States().AT_LEAST_ONE_CHECKED)
        else:
            self.set_state(States().UNUSED)

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

        self.states = (States().UNUSED,
                       States().CHECKED,
                       States().LOCKED,
                       States().ALL_CHECKED,
                       States().ALL_LOCKED,
                       States().AT_LEAST_ONE_CHECKED,
                       States().AT_LEAST_ONE_LOCKED
                       )

        # a free to use dictionary to expand the class
        self.subjoined = dict()

    # -----------------------------------------------------------------------

    def set_state(self, value):
        if isinstance(value, int):
            self._state = value
        else:
            raise sppasTypeError(value, 'States')

        for fr in self.__roots:
            if value in self.states:
                fr.set_state(value)

    statefp = property(FileBase.get_state, set_state)

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

        # Append this file to the root
        return fr.append(filename)

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

    def update_state(self):
        """Modify state depending on the checked root names."""
        if len(self.__roots) == 0:
            self._state = States().UNUSED
            return

        checked = 0
        locked = 0
        for fr in self.__roots:
            if fr.get_state() == States().AT_LEAST_ONE_CHECKED\
                    or fr.get_state() == States().ALL_CHECKED:
                checked += 1
            elif fr.get_state() == States().AT_LEAST_ONE_LOCKED\
                    or fr.get_state() == States().ALL_LOCKED:
                locked += 1

        if locked == len(self.__roots):
            self.set_state(States().ALL_LOCKED)
        elif locked > 1:
            self.set_state(States().AT_LEAST_ONE_LOCKED)
        elif checked == len(self.__roots):
            self.set_state(States().ALL_CHECKED)
        elif checked > 1:
            self.set_state(States().AT_LEAST_ONE_CHECKED)
        else:
            self.set_state(States().UNUSED)

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
