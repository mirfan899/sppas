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

import logging
import json

from os.path import exists
from os.path import dirname

from sppas import sppasTypeError
from .fileutils import sppasGUID

from .filebase import FileBase, States
from .fileref import FileReference
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

    def __init__(self, identifier=sppasGUID().get()):
        """Constructor of a FileData."""
        super().__init__(identifier)
        self.__data = list()
        self.__refs = list()

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

    def remove_file(self, filename):
        """Remove a file in the list from its file name.

        :param filename: (str) Absolute or relative name of a file
        :return: (FileName)
        :raises: OSError

        """
        given_fp = FilePath(dirname(filename))
        for fp in self.__data:
            if fp.id == given_fp.id:
                for fr in fp:
                    fr.remove(filename)

    # -----------------------------------------------------------------------

    def add_ref(self, ref):
        """Add a reference in the list from its file name.

        :param ref: (FileReference) Reference to add

        """
        if isinstance(ref, FileReference) is False:
            raise sppasTypeError(ref, 'FileReference')

        for refe in self.__refs:
            if refe.id == ref.id:
                logging.error("A reference with the identifier '{:s}' is"
                              "already in the data.".format(refe.id))
                return False

        self.__refs.append(ref)
        return True

    # -----------------------------------------------------------------------

    def remove_refs(self, state=States().CHECKED):
        """Remove all references of the given state.

        :param state: (States)
        :returns: (int) Number of removed refs

        """
        # Fix the list of references to be removed
        removes = list()
        for ref in self.__refs:
            if ref.stateref == state:
                removes.append(ref)

        # Remove these references of the roots
        for fp in self.__data:
            for fr in fp:
                for fc in removes:
                    fr.remove_ref(fc)

        # Remove these references of the list of existing references
        nb = len(removes)
        for ref in reversed(removes):
            self.__refs.remove(ref)

        return nb

    # -----------------------------------------------------------------------

    def get_refs(self):
        """Return the list of references."""
        return self.__refs

    # -----------------------------------------------------------------------

    def update(self):
        """Update the data: missing files, properties changed.

        Empty FileRoot and FilePath are removed.

        """
        for fp in self.__data:
            for fr in reversed(fp):
                for fn in reversed(fr):
                    if exists(fn.id):
                        fn.update_properties()
                    else:
                        fr.remove(fn)
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
        :returns: (int) Number of removed files

        """
        nb = 0
        for fp in self.__data:
            for fr in reversed(fp):
                for fn in reversed(fr):
                    if fn.get_state() == state:
                        fr.remove(fn)
                        nb += 1
                fr.update_state()
            fp.update_state()

        return nb

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
                    if fn.get_state() == value:
                        checked.append(fn.id)
        return checked

    # -----------------------------------------------------------------------

    def get_object(self, identifier):
        """Return the file object matching the given identifier.

        :param identifier: (str)
        :return: (FileData, FilePath, FileRoot, FileName, FileReference)

        """
        if self.id == identifier:
            return self

        for ref in self.get_refs():
            if ref.id == identifier:
                return ref

        for fp in self.__data:
            if fp.id == identifier:
                return fp
            for fr in fp:
                if fr.id ==  identifier:
                    return fr
                for fn in fr:
                    if fn.id == identifier:
                        return fn

        return None

    # -----------------------------------------------------------------------

    @staticmethod
    def get_object_state(file_obj):
        """Return the state of any FileBase within the FileData.

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

    def set_object_state(self, state, file_obj=None):
        """Set the state of any FileBase within FileData.

        The default case is to set the state to all FilePath.

        It is not allowed to manually assign one of the "AT_LEAST" states.
        They are automatically fixed here depending on the paths states.

        :param state: (States) state to set the file to
        :param file_obj: (FileBase) the specific file to set the state to
        :raises: sppasTypeError, sppasValueError

        """
        modified = False
        if file_obj is None:
            for fp in self.__data:
                modified = fp.set_state(state)

        else:
            if isinstance(file_obj, FilePath):
                modified = file_obj.set_state(state)

            elif isinstance(file_obj, (FileRoot, FileName)):
                # search for the FilePath matching with the file_obj
                for fp in self.__data:
                    # test if file_obj is a root or name in this fp
                    cur_obj = fp.get_object(file_obj.id)
                    if cur_obj is not None:
                        # this object is one of this fp
                        modified = fp.set_object_state(state, file_obj)
                        break

            else:
                raise sppasTypeError(file_obj, 'FileBase')

        return modified

    # -----------------------------------------------------------------------

    def set_state(self, value):
        """Set the state of this FileData instance.

        Actually we don't do anything with this state value!
        It overrides the FileBase method to not raise a NotImplementedError.

        :param value: (States)

        """
        self._state = int(value)

    # -----------------------------------------------------------------------

    def serialize(self):
        d = dict()
        d['id'] = self.id
        d['paths'] = list()
        d['catalogue'] = list()
        for fp in self.__data:
            d['paths'].append(fp.serialize())
        for ref in self.__refs:
            d['catalogue'].append(ref.serialize())
        return d

    # -----------------------------------------------------------------------

    @staticmethod
    def parse(d):
        data = FileData(d['id'])

        # Add all refs in the data
        for dictref in d['catalogue']:
            r = FileReference.parse(dictref)
            data.add_ref(r)

        # Add all files in the data,
        # but do not create roots/paths from "d"
        for path in d['paths']:
            fp = None
            for root in path['roots']:
                fr = None
                # append files
                for file in root['files']:
                    try:
                        fn = data.add_file(file['id'])
                        s = int(file['state'])
                        if s > 0:
                            fn.set_state(States().CHECKED)
                        else:
                            # it does not make sense to set state to LOCKED
                            fn.set_state(States().UNUSED)
                        if fr is None:
                            fr = data.get_parent(fn)
                    except Exception as e:
                        logging.error(
                            "The file {:s} can't be included in the workspace"
                            "due to the following error: {:s}"
                            "".format(file['id'], str(e)))

                if fr is not None:
                    # append refs
                    for ref_id in root['refids']:
                        ref = data.get_object(ref_id)
                        if ref is not None:
                            fr.add_ref(ref)

                    # append subjoined
                    fr.subjoined = json.loads(root['subjoin'])

                    if fp is not None:
                        fp = data.get_parent(fr)

            if fp is not None:
                # append subjoined
                fp.subjoined = json.loads(path['subjoin'])

        return data

    # -----------------------------------------------------------------------

    def save(self, filename):
        """Save the current FileData in a serialized file.

        :param filename: (str) the name of the save file.

        """
        with open(filename, 'w') as fd:
            json.dump(self.serialize(), fd, indent=4, separators=(',', ': '))

    # -----------------------------------------------------------------------

    @staticmethod
    def load(filename):
        """Load a saved FileData object from a save file.

        :param filename: (str) the name of the save file.
        :return: FileData

        """
        with open(filename, "r") as fd:
            d = json.load(fd)
            return FileData.parse(d)

    # -----------------------------------------------------------------------

    def associate(self):
        ref_checked = self.get_reference_from_state(States().CHECKED)
        if len(ref_checked) == 0:
            return 0

        associed = 0
        for fp in self.__data:
            for fr in fp:
                if fr.get_state() in (States().AT_LEAST_ONE_CHECKED, States().CHECKED):
                    associed += 1
                    if fr.get_references() is not None:
                        ref_extended = fr.get_references()
                        ref_extended.extend(ref_checked)
                        fr.set_references(list(set(ref_extended)))
                    else:
                        fr.set_references(ref_checked)

        return associed

    # -----------------------------------------------------------------------

    def dissociate(self):
        ref_checked = self.get_reference_from_state(States().CHECKED)
        if len(ref_checked) == 0:
            return 0

        dissocied = 0
        for fp in self.__data:
            for fr in fp:
                if fr.get_state() in (States().AT_LEAST_ONE_CHECKED, States().CHECKED):
                    for ref in ref_checked:
                        removed = fr.remove_ref(ref)
                        if removed is True:
                            dissocied += 1
        return dissocied

    # -----------------------------------------------------------------------

    def is_empty(self):
        """Return if the instance contains information."""
        return len(self.__data) + len(self.__refs) == 0

    # -----------------------------------------------------------------------

    def get_filepath_from_state(self, state):
        """Return every FilePath of the given state.

        """
        paths = list()
        for fp in self.__data:
            if fp.get_state() == state:
                paths.append(fp)
        return paths

    # -----------------------------------------------------------------------

    def get_fileroot_from_state(self, state):
        """Return every FileRoot in the given state."""
        roots = list()
        for fp in self.__data:
            for fr in fp:
                if fr.get_state() == state:
                    roots.append(fr)
        return roots

    # -----------------------------------------------------------------------

    def get_filename_from_state(self, state):
        """Return every FileName in the given state.

        """
        files = list()
        for fp in self.__data:
            for fr in fp:
                for fn in fr:
                    if fn.get_state() == state:
                        files.append(fn)
        return files

    # -----------------------------------------------------------------------

    def get_reference_from_state(self, state):
        """Return every Reference in the given state.

        """
        refs = list()
        for r in self.__refs:
            if r.get_state() == state:
                refs.append(r)
        return refs

    # -----------------------------------------------------------------------

    def has_locked_files(self):
        for fp in self.__data:
            if fp.get_state() in (States().AT_LEAST_ONE_LOCKED, States().LOCKED):
                return True
        return False

    # -----------------------------------------------------------------------

    def get_parent(self, filebase):
        """Return the parent of an object.

        :param filebase: (FileName or FileRoot).
        :returns: (FileRoot or FilePath)
        :raises: sppasTypeError

        """
        if isinstance(filebase, FileName):
            fr = FileRoot(filebase.id)
            return self.get_object(fr.id)

        if isinstance(filebase, FileRoot):
            fp = FilePath(filebase.id)
            return self.get_object(fp.id)

        raise sppasTypeError(filebase, "FileName, FileRoot")

    # -----------------------------------------------------------------------

    def unlock(self, entries=None):
        """Unlock the given list of files.

        :param entries: (list, None) List of FileName to unlock

        """
        if entries is None:
            for fp in self.__data:
                for fr in fp:
                    for fn in fr:
                        if fn.get_state() == States().LOCKED:
                            fn.set_state(States().UNUSED)
                    fr.update_state()
                fp.update_state()

        elif isinstance(entries, list):
            for fn in entries:
                if fn.get_state() == States().LOCKED:
                    self.set_object_state(States().UNUSED, fn)

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
