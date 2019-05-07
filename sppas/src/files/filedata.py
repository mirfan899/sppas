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

from os.path import exists
from os.path import dirname

from sppas import sppasTypeError, sppasValueError
from .fileutils import sppasGUID

from .filebase import FileBase, States
from .fileref import Reference
from .filestructure import FileName, FileRoot, FilePath

# ---------------------------------------------------------------------------


class FileData(FileBase):
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
        super().__init__(sppasGUID().get())
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

        for refe in self.__refs:
            if refe.id == ref.id:
                return

        if isinstance(ref, Reference):
            if ref not in self.__refs:
                self.__refs.append(ref)
        else:
            raise sppasTypeError(ref, 'Reference')

    # -----------------------------------------------------------------------

    def remove_checked_ref(self):
        """Remove all checked ref from the list."""
        for ref in self.__refs:
            if ref.stateref == States().CHECKED:
                del self.__refs[self.__refs.index(ref)]

    # -----------------------------------------------------------------------

    def get_refs(self):
        """Return the current ref list."""
        return self.__refs

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

        # Remove empty FilePath
        for fp in reversed(self.__data):
            if len(fp) == 0:
                self.__data.remove(fp)

        for fp in self.__data:
            for fr in reversed(fp):
                fr.update_state()
            fp.update_state()

    # -----------------------------------------------------------------------

    def remove_files(self, state=States().CHECKED):
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

    def get_files(self, value=States().CHECKED):
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
        :return: States

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

        :param state: (States) state to set the file to
        :param file_obj: (FileBase) the specific file to set the state to

        """
        if file_obj is None:
            for fp in self.__data:
                if not fp.statefp == States().AT_LEAST_ONE_LOCKED:
                    if isinstance(state, int):
                        fp.set_state(state)
                    else:
                        raise sppasTypeError(state, 'States')
                else:
                    raise sppasValueError(fp.state, 'not AT_LEAST_ONE_LOCKED or ALL_LOCKED')
        else:
            if issubclass(file_obj, FileBase):
                if isinstance(state, int):
                    file_obj.state = state
                else:
                    raise sppasTypeError(state, 'States')
            else:
                raise sppasTypeError(file_obj, 'inherited from FileBase')

    # -----------------------------------------------------------------------

    def toJSON(self):
        my_fp = dict()
        for fp in self.__data:
            my_fr = dict()
            for fr in fp:
                my_fn = list()
                my_ref = list()
                for fn in fr:
                    my_fn.append(fn.id)
                for ref in fr.references:
                    my_ref.append(ref)

                my_fr[fr.id] = (my_fn, my_ref)
            my_fp[fp.id] = my_fr
        return my_fp

    # -----------------------------------------------------------------------

    def save(self, file_name):
        """Save the current FileData in a serialized file.

        :param file_name: (str) the name of the save file.

        """
        with open(file_name, 'w') as save:
            json.dump(self.toJSON(), save)

    # -----------------------------------------------------------------------

    def has_locked_files(self):
        for fp in self.__data:
            if fp.statefp == States().AT_LEAST_ONE_LOCKED\
                    or fp.statefp == States().ALL_LOCKED:
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
            with open(file_name, 'r') as save_file:
                save = json.loads(save_file.read())
                for value in save.values():
                    for in_value in value.values():
                        for path in in_value[0]:
                            self.add_file(path)
                        for ref in in_value[1]:
                            self.add_ref(ref)

        else:
            raise ValueError('Locked files')
            # TODO : make a SPPAS exception in fileexc

    # -----------------------------------------------------------------------

    def associate(self):
        ref_checked = list()
        for ref in self.__refs:
            if ref.state == States().CHECKED:
                ref_checked.append(ref)

        for fp in self.__data:
            for fr in fp:
                if fr.state == States().AT_LEAST_ONE_CHECKED\
                        or fr.state == States().ALL_CHECKED:
                    if fr.get_references() is not None:
                        fr.set_references(set(fr.get_references().extend(ref_checked)))
                    else:
                        fr.set_references(ref_checked)

    # -----------------------------------------------------------------------

    def dissociate(self):
        ref_checked = list()
        for ref in self.__refs:
            if ref.stateref == States().CHECKED:
                ref_checked.append(ref)

        for fp in self.__data:
            for fr in fp:
                if fr.statefr == States().AT_LEAST_ONE_CHECKED \
                        or fr.statefr == States().ALL_CHECKED:
                    for ref in ref_checked:
                        if ref in fr.references:
                            fr.references.remove(ref)

    # -----------------------------------------------------------------------

    def is_empty(self):
        """Return if the instance contains information."""
        return len(self.__data) + len(self.__refs) == 0

    # -----------------------------------------------------------------------

    def get_filepath_from_state(self, state):
        """Return every FilePath in the given state."""
        for fp in self.__data:
            if fp.statefp == state:
                yield fp
    # -----------------------------------------------------------------------

    def get_fileroot_from_state(self, state):
        """Return every FileRoot in the given state."""
        for fp in self.__data:
            for fr in fp:
                if fr.statefr == state:
                    yield fr

    # -----------------------------------------------------------------------

    def get_filename_from_state(self, state):
        """Return every FileName in the given state."""
        for fp in self.__data:
            for fr in fp:
                for fn in fr:
                    if fn.statefn == state:
                        yield fn

    # -----------------------------------------------------------------------

    def get_reference_from_state(self, state):
        """Return every Reference in the given state."""
        for fp in self.__data:
            for fr in fp:
                for ref in fr:
                    if ref.stateref == state:
                        yield ref

    # -----------------------------------------------------------------------

    def unlock(self, list_of_files):
        """Unlocks the given list of file.

        :param list_of_files (list) the list of file to unlock

        """
        if isinstance(list_of_files, list):
            for file in list_of_files:
                file.set_state(States().UNUSED)

            for fp in self.__data:
                for fr in reversed(fp):
                    fr.update_state()
                fp.update_state()

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
