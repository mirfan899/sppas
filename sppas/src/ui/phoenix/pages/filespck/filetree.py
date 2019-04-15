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

    src.ui.lib.filetree.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import logging
import wx
import wx.dataview as dv

from sppas import sppasLogSetup
from sppas.src.files.fileexc import FileAttributeError

from .filemodel import fileTreeModel

# ----------------------------------------------------------------------------
# Control to store the data matching the model
# ----------------------------------------------------------------------------


class FileTreeCtrl(wx.dataview.DataViewCtrl):
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
    
    default_renderers = {
        "string": wx.dataview.DataViewTextRenderer,
        "bool": wx.dataview.DataViewToggleRenderer,
        "datetime": wx.dataview.DataViewDateRenderer,
        "wxBitmap": wx.dataview.DataViewBitmapRenderer,
        "wxDataViewIconText": wx.dataview.DataViewIconTextRenderer
    }
    
    def __init__(self, parent, data=None):
        """Constructor of the FileTreeCtrl.

        :param `parent`: (wx.Window) 
        :param `data`: (FileData)

        """
        super(FileTreeCtrl, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.dataview.DV_MULTIPLE  # wx.dataview.DV_VERT_RULES |
            )

        # Create an instance of our model and associate to the view.
        self._model = fileTreeModel(data)
        self.AssociateModel(self._model)
        self._model.DecRef()

        # Create the columns that the model wants in the view.
        for i in range(self._model.GetColumnCount()):
            col = FileTreeCtrl.__create_column(self._model, i)
            if i == self._model.GetExpanderColumn():
                self.SetExpanderColumn(col)
            wx.dataview.DataViewCtrl.AppendColumn(self, col)

        # Bind events.
        # Used to remember the expend/collapse status of items after a refresh.
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_EXPANDED, self.__onExpanded)        
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_COLLAPSED, self.__onCollapsed)

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def GetChecked(self):
        """Return checked filenames."""
        return self._model.GetCheckedFiles(True)

    # ------------------------------------------------------------------------

    def GetUnChecked(self):
        """Return un-checked filenames."""
        return self._model.GetCheckedFiles(False)

    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------

    def Add(self, filename):
        """Add a file in the tree.
        
        The given filename must include its absolute path.

        :param filename: (str) Name of a file or a directory.

        """
        do_refresh = False
        if os.path.isdir(filename):
            for f in os.listdir(filename):
                fullname = os.path.join(filename, f)
                try:
                    self._model.AddFile(fullname)
                    do_refresh = True  
                except OSError:
                    logging.info('{:s} not added.'.format(fullname))

        elif os.path.isfile(filename):
            try:
                self._model.AddFile(filename)
                do_refresh = True  
            except OSError:
                logging.error('{:s} not added.'.format(filename))

        else:
            logging.error('{:s} not added.'.format(filename))
        
        if do_refresh:
            self.RefreshData()
        logging.debug('{:s} added.'.format(filename))

    # ------------------------------------------------------------------------

    def Remove(self):
        """Remove all checked files."""
        self._model.RemoveCheckedFiles()
        self.RefreshData()

    # ------------------------------------------------------------------------

    def ExpandAll(self):
        self._model.Expand(True)
        for item in self._model.GetExpandedItems(True):
            self.Expand(item)

    # ------------------------------------------------------------------------

    def CollapseAll(self):
        self._model.Expand(False)
        for item in self._model.GetExpandedItems(False):
            self.Expand(item)

    # ------------------------------------------------------------------------

    def __update_expand(self):
        for item in self._model.GetExpandedItems(True):
            self.Expand(item)
        for item in self._model.GetExpandedItems(False):
            self.Collapse(item)

    # ------------------------------------------------------------------------

    def RefreshData(self):
        # Update the data and clear the tree
        self._model.UpdateFiles()
        # But clearing the tree means to forget which are the expanded items!
        # so, re-expand/re-collapse properly.
        self.__update_expand()

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def __onExpanded(self, evt):
        """Happens when the user cliched a '+' button of the tree.

        We have to update the corresponding object 'expand' value to True.
        
        """
        self._model.Expand(True, evt.GetItem())
        evt.Skip()

    # ------------------------------------------------------------------------

    def __onCollapsed(self, evt):
        """Happens when the user cliched a '-' button of the tree.

        We have to update the corresponding object 'expand' value to False.
        
        """
        self._model.Expand(False, evt.GetItem())
        evt.Skip()

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

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    @staticmethod
    def __create_column(model, index):
        """Return the DataViewColumn matching the given index in the model.

        :param index: (int) Index of the column to create. It must match an
        existing column number of the model.
        :return: (wx.dataview.DataViewColumn)

        """
        logging.debug('Create column: {:d}: {:s}'
                      ''.format(index, model.GetColumnName(index)))

        stype = model.GetColumnType(index)
        render = model.GetColumnRenderer(index)
        if render is None:
            if stype not in FileTreeCtrl.default_renderers:
                stype = "string"
            render = FileTreeCtrl.default_renderers[stype](
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