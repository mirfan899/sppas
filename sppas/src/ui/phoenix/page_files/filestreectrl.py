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

    src.ui.lib.filestreectrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx
import wx.dataview

from .filesviewmodel import FilesTreeViewModel
from .basectrls import BaseTreeViewCtrl

# ----------------------------------------------------------------------------
# Control to store the data matching the model
# ----------------------------------------------------------------------------


class FilesTreeViewCtrl(BaseTreeViewCtrl):
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

    def __init__(self, parent, name=wx.PanelNameStr):
        """Constructor of the FileTreeCtrl.

        :param parent: (wx.Window)
        :param name: (str)

        """
        super(FilesTreeViewCtrl, self).__init__(parent, name)

        # Create an instance of our model and associate to the view.
        self._model = FilesTreeViewModel()
        self.AssociateModel(self._model)
        self._model.DecRef()

        # Create the columns that the model wants in the view.
        for i in range(self._model.GetColumnCount()):
            col = BaseTreeViewCtrl._create_column(self._model, i)
            if i == self._model.GetExpanderColumn():
                self.SetExpanderColumn(col)
            wx.dataview.DataViewCtrl.AppendColumn(self, col)

        # Bind events.
        # Used to remember the expend/collapse status of items after a refresh.
        # self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_EXPANDED, self.__onExpanded)
        # self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_COLLAPSED, self.__onCollapsed)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self._on_item_activated)
        self.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self._on_item_selection_changed)

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data of the model."""
        return self._model.get_data()

    # ------------------------------------------------------------------------

    def AddFiles(self, entries):
        """Add a list of files in the model.
        
        The given filenames must include theirs absolute path.

        :param entries: (list of str) Filenames or folder with absolute path.

        """
        items = self._model.add_files(entries)
        for i in items:
            self.EnsureVisible(i)

    # ------------------------------------------------------------------------

    def RemoveCheckedFiles(self):
        """Remove all checked files."""
        self._model.remove_checked_files()

    # ------------------------------------------------------------------------

    def DeleteCheckedFiles(self):
        """Delete all checked files."""
        self._model.delete_checked_files()

    # ------------------------------------------------------------------------

    def GetCheckedFiles(self):
        """Return the list of checked files.

        :returns: List of FileName

        """
        return self._model.get_checked_files()

    # ------------------------------------------------------------------------

    def LockFiles(self, entries):
        """Lock a list of files.

        :param entries: (list of str/FileName) Filenames with absolute path or FileName instance.

        """
        self._model.lock(entries)

    # ------------------------------------------------------------------------

    # def ExpandAll(self):
    #    self._model.Expand(True)
    #     for item in self._model.GetExpandedItems(True):
    #         self.Expand(item)

    # ------------------------------------------------------------------------

    # def CollapseAll(self):
    #     self._model.Expand(False)
    #     for item in self._model.GetExpandedItems(False):
    #         self.Expand(item)

    # ------------------------------------------------------------------------

    # def __update_expand(self):
    #     for item in self._model.GetExpandedItems(True):
    #         self.Expand(item)
    #     for item in self._model.GetExpandedItems(False):
    #         self.Collapse(item)

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    # def __onExpanded(self, evt):
    #    """Happens when the user cliched a '+' button of the tree.
    #
    #    We have to update the corresponding object 'expand' value to True.
    #
    #    """
    #    self._model.Expand(True, evt.GetItem())
    #    evt.Skip()

    # ------------------------------------------------------------------------

    # def __onCollapsed(self, evt):
    #    """Happens when the user cliched a '-' button of the tree.
    #
    #    We have to update the corresponding object 'expand' value to False.
    #
    #    """
    #    self._model.Expand(False, evt.GetItem())
    #    evt.Skip()

    # ------------------------------------------------------------------------

    def _on_item_activated(self, event):
        """Happens when the user activated a cell (double-click).

        This event is triggered by double clicking an item or pressing some
        special key (usually “Enter”) when it is focused.

        """
        self._model.change_value(event.GetColumn(), event.GetItem())

    # ------------------------------------------------------------------------

    def _on_item_selection_changed(self, event):
        """Happens when the user simple-click a cell.

        """
        item = event.GetItem()
        self._model.change_value(event.GetColumn(), item)
