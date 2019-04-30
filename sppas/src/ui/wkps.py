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

    ui.wkps.py
    ~~~~~~~~~~

    Management of the workspaces of the software.

"""

import os
import logging

from sppas.src.files.filedata import FileData
from sppas import paths
from sppas import sppasIndexError
from sppas.src.utils.makeunicode import sppasUnicode

# ---------------------------------------------------------------------------


class sppasWorkspaces(object):
    """Manage the set of workspaces.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    A workspace is made of:

        - a file in which data are saved and loaded when needed;
        - a name, matching the filename without path nor extension.

    The extension of a workspace JSON files is: wjson

    """

    ext = ".wjson"

    def __init__(self):
        """Create a sppasWorkspaces instance.

        Load the list of existing wjson file names of the workspaces folder
        of the software.

        """
        wkp_dir = paths.wkps
        if os.path.exists(wkp_dir) is False:
            os.mkdir(wkp_dir)

        self.__wkps = list()
        self.__wkps.append("Blank")

        self.set_workspaces()

    # -----------------------------------------------------------------------

    def set_workspaces(self):
        """Fix the list of existing workspaces in the software.

        Reset the current list of workspaces.

        """
        for fn in os.listdir(paths.wkps):
            if fn.endswith(sppasWorkspaces.ext):
                # remove path and extension to set the name of the workspace
                wkp_name = os.path.basename(os.path.splitext(fn)[0])
                # append in the list
                self.__wkps.append(wkp_name)
                logging.debug('Founded workspace {:s}'.format(wkp_name))

    # -----------------------------------------------------------------------

    def new(self, name):
        """Create and append a new empty workspace.

        :param name: (str) Name of the workspace to create.
        :returns: The real name used to save the workspace
        :raises: IOError, ValueError

        """
        # set the name in unicode and with the appropriate extension
        su = sppasUnicode(name)
        u_name = su.to_strip()
        if u_name in self.__wkps:
            raise ValueError('A workspace with name {:s} is already existing.'
                             ''.format(u_name))

        # create the empty workspace data & save
        fn = os.path.join(paths.wkps, u_name) + sppasWorkspaces.ext
        data = FileData()
        # data.save(fn)

        self.__wkps.append(u_name)
        return u_name

    # -----------------------------------------------------------------------

    def save(self, data, index=-1):
        """Save data into a workspace.

        The data can already match an existing workspace or a new workspace
        is created.

        :param data: (FileData) Data of a workspace to save
        :param index: (int) Index of the workspace to save data in
        :returns: The real name used to save the workspace
        :raises: IOError, IndexError

        """
        if index == 0:
            raise IOError('It is not allowed to save the Blank workspace.')

        if index == -1:
            u_name = self.new("New workspace")
        else:
            u_name = self[index]

        fn = os.path.join(paths.wkps, u_name) + sppasWorkspaces.ext
        # data.save(fn)

        return u_name

    # -----------------------------------------------------------------------

    def delete(self, index):
        """Delete the workspace with the given index.

        :param index: (int) Index of the workspace
        :raises: IndexError

        """
        if index == 0:
            raise IOError('It is not allowed to delete the Blank workspace.')

        try:
            fn = self.check_filename(index)
        except OSError:
            # The file was not existing.
            return

        os.remove(fn)
        self.__wkps.pop(index)

    # -----------------------------------------------------------------------

    def index(self, name):
        """Return the index of the workspace with the given name."""
        su = sppasUnicode(name)
        u_name = su.to_strip()
        if u_name not in self.__wkps:
            raise ValueError('Name {:s} not found.')

        i = 0
        while self.__wkps[i] != u_name:
            i += 1

        return i

    # -----------------------------------------------------------------------

    def check_filename(self, index):
        """Get the filename of the workspace at the given index.

        In case the filename is not existing, the workspace is removed.

        :param index: (int) Index of the workspace
        :returns: (str)
        :raises: IndexError, OSerror

        """
        fn = os.path.join(paths.wkps, self[index]) + sppasWorkspaces.ext
        if os.path.exists(fn) is False:
            self.__wkps.pop(index)
            raise OSError('The file matching the workspace {:s} is not '
                          'existing'.format(fn[:-4]))

        return fn

    # -----------------------------------------------------------------------

    def get_data(self, index):
        """Return the data of the workspace at the given index.

        In case the filename is not existing, the workspace is removed.

        :param index: (int) Index of the workspace
        :returns: (str)
        :raises: IndexError, OSError

        """
        if index == 0:
            return FileData()  #"Blank")

        fn = self.check_filename(index)
        data = FileData()
        #data.load(fn)
        return data

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of workspaces."""
        return len(self.__wkps)

    def __iter__(self):
        for a in self.__wkps:
            yield a

    def __getitem__(self, i):
        try:
            item = self.__wkps[i]
        except IndexError:
            raise sppasIndexError(i)
        return item
