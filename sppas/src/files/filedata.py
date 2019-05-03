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
        >>>      (cmp.state, True, False)],
        >>>     logic_bool="and")


    :Example: Search if a FileRoot() is exactly matching "my_path/toto":

        >>> cmp = sppasRootCompare()
        >>> fr.match([(cmp.exact, "my_path", False)])

    :Example: Search if a FileRoot() is starting with "my_path/toto"
    and is checked:

        >>> fr.match(
        >>>     [(cmp.startswith, "my_path/toto", False),
        >>>      (cmp.state, True, False)],
        >>>     logic_bool="and")

    :Example: Search if a FileName() is starting with "toto" and is not
    a TextGrid and is checked:

        >>> cmpn = sppasNameCompare()
        >>> cmpe = sppasExtensionCompare()
        >>> cmpp = sppasFileCompare()
        >>> fn.match(
        >>>    [(cmpn.startswith, "toto", False),
        >>>     (cmpe.iexact, "textgrid", True),
        >>>     (cmpp.state, True, False)],
        >>>    logic_bool="and")

"""

import json
import pickle

from os.path import isfile, isdir, exists
from os.path import basename, dirname

from sppas import sppasTypeError, sppasValueError

from .filebase import FileBase, States
from .fileref import Reference
from .filestructure import FileName, FileRoot, FilePath

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
        self.__refs = list()
        self.states = States()

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

    def add_ref(self, ref):
        """Add a reference in the list from its file name.

        :param ref: (Reference) Reference to add

        """
        if isinstance(ref, Reference):
            if ref not in self.__refs:
                self.__refs.append(ref)
        else:
            raise sppasTypeError(ref, 'Reference')

    # -----------------------------------------------------------------------

    def remove_checked_ref(self):
        """Remove all checked ref from the list"""
        for ref in self.__refs:
            if ref.state == Reference.States.CHECKED:
                del self.__refs[self.__refs.index(ref)]

    # -----------------------------------------------------------------------

    def get_refs(self):
        """Return the current ref list"""
        return self.__refs

    # -----------------------------------------------------------------------

    def update(self):
        """Update the data: missing files, properties changed.

        TODO: Update states too

        """
        for fp in self.__data:
            for fr in reversed(fp):
                for fn in reversed(fr):
                    if exists(fn.id):
                        fn.update_properties()
                    else:
                        fp.remove(fn)
                if len(fr) == 0:
                    fp.remove(fr)

        # Remove empty FilePath
        for fp in reversed(self.__data):
            if len(fp) == 0:
                self.__data.remove(fp)

    # -----------------------------------------------------------------------

    def remove_files(self, state=FileName.States.CHECKED):
        """Remove all files of the given state.

        Do not update: empty roots or paths are not removed.

        :param state: (States)

        """
        for fp in self.__data:
            for fr in reversed(fp):
                for fn in reversed(fr):
                    if fn.state == state:
                        fr.remove(fn)

    # -----------------------------------------------------------------------

    def get_files(self, value=FileName.States.CHECKED):
        """Return the list of file names of the given state.

        :param value: (bool) Toggle state
        :return: (list of str)

        """
        checked = list()
        for fp in self.__data:
            for fr in fp:
                for fn in fr:
                    if fn.state == value:
                        checked.append(fn.id)
        return checked

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

    def get_state(self, file_obj):
        """Return the state of any File within the FileData.

        :param file_obj: (FileBase) The object which one enquire the state
        :return: FilePath.States, FileRoot.States, FileName.States

        """
        if not isinstance(file_obj, FilePath)\
            and not isinstance(file_obj, FileRoot)\
                and not isinstance(file_obj, FileName):
            raise sppasTypeError(file_obj, 'FilePath or FileRoot or FileName')
        else:
            return file_obj.get_state()

    # -----------------------------------------------------------------------

    def set_state(self, state, file_obj=None):
        """Set the state of any File within FileData.

        The default case is to set the state to all FilePath.

        :param state: (FilePath.States, FileRoot.States, FileName.States) state to set the file to
        :param file_obj: (FileBase) the specific file to set the state to

        """
        if file_obj is None:
            for fp in self.__data:
                if not fp.state == FilePath.States.AT_LEAST_ONE_LOCKED:
                    if isinstance(state, FilePath.States):
                        fp.state = state
                    else:
                        raise sppasTypeError(state, 'FilePath.States')
                else:
                    raise sppasValueError(fp.state, 'not AT_LEAST_ONE_LOCKED or ALL_LOCKED')
        else:
            if issubclass(file_obj, FileBase):
                if isinstance(state, (FilePath.States, FileRoot.States, FileName.States)):
                    file_obj.state = state
                else:
                    raise sppasTypeError(state, 'FilePath.State or FileRoot.State or FileName.State')
            else:
                raise sppasTypeError(file_obj, 'inherited from FileBase')

    # -----------------------------------------------------------------------

    def save(self, file_name):
        """Save the current FileData in a serialized file.

        TODO: json ASCII file

        :param file_name: (str) the name of the save file.

        """
        with open(file_name, 'wb') as save:
            pickle.dump(self.__data, save)

    # -----------------------------------------------------------------------

    def has_locked_files(self):
        for fp in self.__data:
            if fp.state == FilePath.States.AT_LEAST_ONE_LOCKED\
                    or fp.state == FilePath.States.ALL_LOCKED:
                return True
        return False

    # -----------------------------------------------------------------------

    def load(self, file_name, force=False):
        """Load a saved FileData object from a save file.

        :param file_name: (str) the name of the save file.
        :param force:  (bool) permit to the user to load a new FileData object even if there is locked files within.

        """
        at_least_one_fp_is_locked = self.has_locked_files()

        if force is True or at_least_one_fp_is_locked is False:
            self.__data.clear()
            with open(file_name, 'rb') as save:
                save = pickle.load(save)
                self.__data = save

        else:
            raise ValueError('Locked files')
            # TODO : make a SPPAS exception in fileexc

    # -----------------------------------------------------------------------

    def associate(self):
        ref_checked = list()
        for ref in self.__refs:
            if ref.state == Reference.States.CHECKED:
                ref_checked.append(ref)

        for fp in self.__data:
            for fr in fp:
                if fr.state == FileRoot.States.AT_LEAST_ONE_CHECKED\
                        or fr.state == FileRoot.States.ALL_CHECKED:
                    if fr.references is not None:
                        fr.references = set(fr.references.extend(ref_checked))
                    else:
                        fr.references = ref_checked

    # -----------------------------------------------------------------------

    def dissociate(self):
        ref_checked = list()
        for ref in self.__refs:
            if ref.state == Reference.States.CHECKED:
                ref_checked.append(ref)

        for fp in self.__data:
            for fr in fp:
                if fr.state == FileRoot.States.AT_LEAST_ONE_CHECKED \
                        or fr.state == FileRoot.States.ALL_CHECKED:
                    for ref in ref_checked:
                        if ref in fr.references:
                            fr.references.remove(ref)

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
