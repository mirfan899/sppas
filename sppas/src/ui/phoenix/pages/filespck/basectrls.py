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

    src.ui.phoenix.filespck.basectrls.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Base classes to manage a workspace and utilities.

"""

import wx
import wx.dataview
import logging

from sppas.src.files.fileexc import FileAttributeError

# ----------------------------------------------------------------------------


default_renderers = {
    "string": wx.dataview.DataViewTextRenderer,
    "bool": wx.dataview.DataViewToggleRenderer,
    "datetime": wx.dataview.DataViewDateRenderer,
    "wxBitmap": wx.dataview.DataViewBitmapRenderer,
    "wxDataViewIconText": wx.dataview.DataViewIconTextRenderer
}


# ----------------------------------------------------------------------------
# Control to store the data matching the model
# ----------------------------------------------------------------------------


class BaseTreeViewCtrl(wx.dataview.DataViewCtrl):
    """A control to display data files in a tree-spreadsheet style.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Columns of this class are defined by the model and created by the
    constructor. No parent nor children will have the possibility to
    Append/Insert/Prepend/Delete columns: such methods are disabled.

    """

    def __init__(self, parent, data=None, name=wx.PanelNameStr):
        """Constructor of the FileTreeCtrl.

        :param `parent`: (wx.Window)
        :param `data`: (FileData)

        """
        super(BaseTreeViewCtrl, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.dataview.DV_MULTIPLE,  # wx.dataview.DV_VERT_RULES |
            name=name
        )

        # Create an instance of our model and associate to the view.
        self._model = None

        # Colors&font
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetForegroundColour(parent.GetForegroundColour())

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        wx.Window.SetBackgroundColour(self, color)
        if self._model is not None:
            self._model.SetBackgroundColour(color)
            self.RefreshData()

    # ------------------------------------------------------------------------

    def SetForegroundColour(self, color):
        wx.Window.SetForegroundColour(self, color)
        if self._model is not None:
            self._model.SetForegroundColour(color)
            self.RefreshData()

    # ------------------------------------------------------------------------

    def RefreshData(self):
        """To be overridden."""
        return

    # ------------------------------------------------------------------------
    # For sub-classes only (private)
    # ------------------------------------------------------------------------

    @staticmethod
    def _create_column(model, index):
        """Return the DataViewColumn matching the given index in the model.

        :param model:
        :param index: (int) Index of the column to create. It must match an
        existing column number of the model.
        :return: (wx.dataview.DataViewColumn)

        """
        logging.debug('Create column: {:d}: {:s}'
                      ''.format(index, model.GetColumnName(index)))

        stype = model.GetColumnType(index)
        render = model.GetColumnRenderer(index)
        if render is None:
            if stype not in default_renderers:
                stype = "string"
            render = default_renderers[stype](
                varianttype=stype,
                mode=model.GetColumnMode(index),
                align=model.GetColumnAlign(index))

        col = wx.dataview.DataViewColumn(
            model.GetColumnName(index),
            render,
            index,
            width=model.GetColumnWidth(index))
        col.Reorderable = True
        col.Sortable = False
        if stype in ("string", "datetime"):
            col.Sortable = True

        return col

    # ------------------------------------------------------------------------
    # Override methods to manage columns. No parent nor children will have the
    # possibility to Append/Insert/Prepend/Delete columns.
    # ------------------------------------------------------------------------

    def DeleteColumn(self, column):
        raise FileAttributeError(self.__class__.__format__, "DeleteColumn")

    def ClearColumns(self):
        raise FileAttributeError(self.__class__.__format__, "ClearColumns")

    def AppendColumn(self, col):
        raise FileAttributeError(self.__class__.__format__, "AppendColumn")

    def AppendBitmapColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendBitmapColumn")

    def AppendDateColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendDateColumn")

    def AppendIconTextColumn(self,*args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendIconTextColumn")

    def AppendProgressColumn(self,*args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendProgressColumn")

    def AppendTextColumn(self,*args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendTextColumn")

    def AppendToggleColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendToggleColumn")

    def InsertColumn(self, pos, col):
        raise FileAttributeError(self.__class__.__format__, "InsertColumn")

    def PrependBitmapColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependBitmapColumn")

    def PrependColumn(self, col):
        raise FileAttributeError(self.__class__.__format__, "PrependColumn")

    def PrependDateColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependDateColumn")

    def PrependIconTextColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependIconTextColumn")

    def PrependProgressColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependProgressColumn")

    def PrependTextColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependTextColumn")

    def PrependToggleColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependToggleColumn")

