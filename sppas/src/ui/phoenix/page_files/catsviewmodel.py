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

    src.ui.phoenix.filespck.catsviewmodel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This model acts as a bridge between a DataViewCtrl and a FileData instance.

"""

import unittest
import os
import logging
import wx
import wx.dataview

from sppas.src.files.filedata import FileData
from sppas import sppasTypeError
from .basectrls import ColumnProperties

# ----------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------


class CataloguesTreeViewModel(wx.dataview.PyDataViewModel):
    """A class that is a DataViewModel combined with an object mapper.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This model mapper provides these data columns identifiers:

        0. icon:     wxBitmap
        1. file:     string
        2. check:    bool
        3. type:     string
        4. data:     string
        5. size:     string

    """

    def __init__(self, data=FileData()):
        """Constructor of a fileTreeModel.

        :param data: (FileData) Workspace to be managed by the mapper

        """
        wx.dataview.PyDataViewModel.__init__(self)
        try:  # wx4 only
            self.UseWeakRefs(True)
        except AttributeError:
            pass

        # The workspace to display
        if data is None:
            data = FileData()
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        self.__data = data

        # Map between displayed columns and workspace
        self.__mapper = dict()
        self.__mapper[0] = CataloguesTreeViewModel.__create_col('ref')
        self.__mapper[1] = CataloguesTreeViewModel.__create_col('value')
        self.__mapper[2] = CataloguesTreeViewModel.__create_col('descr')

        # GUI information which can be managed by the mapper
        self._bgcolor = None
        self._fgcolor = None

    # -----------------------------------------------------------------------

    def set_data(self, data):
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        logging.debug('New data to set in the catsview.')
        self.__data = data
        self.Cleared()

    # -----------------------------------------------------------------------

    @staticmethod
    def __create_col(name):
        col = ColumnProperties(name, name)
        col.width = 100
        return col

    # -----------------------------------------------------------------------

    def IsContainer(self, item):
        """Return True if the item has children, False otherwise.

        :param item: (wx.dataview.DataViewItem)

        """
        return False

    # -----------------------------------------------------------------------
    # Manage column properties
    # -----------------------------------------------------------------------

    def GetColumnCount(self):
        """Override. Report how many columns this model provides data for."""
        return len(self.__mapper)

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------

    def GetColumnType(self, col):
        """Override. Map the data column number to the data type.

        :param col: (int)

        """
        return self.__mapper[col].stype

    # -----------------------------------------------------------------------

    def GetColumnName(self, col):
        """Map the data column number to the data name.

        :param col: (int)

        """
        return self.__mapper[col].name

    # -----------------------------------------------------------------------

    def GetColumnMode(self, col):
        """Map the data column number to the cell mode.

        :param col: (int)

        """
        return self.__mapper[col].mode

    # -----------------------------------------------------------------------

    def GetColumnWidth(self, col):
        """Map the data column number to the col width.

        :param col: (int)

        """
        return self.__mapper[col].width

    # -----------------------------------------------------------------------

    def GetColumnRenderer(self, col):
        """Map the data column numbers to the col renderer.

        :param col: (int)

        """
        return self.__mapper[col].renderer

    # -----------------------------------------------------------------------

    def GetColumnAlign(self, col):
        """Map the data column numbers to the col alignment.

        :param col: (int)

        """
        return self.__mapper[col].align

    # -----------------------------------------------------------------------
    # Manage the tree
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        self._bgcolor = color

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        self._fgcolor = color
