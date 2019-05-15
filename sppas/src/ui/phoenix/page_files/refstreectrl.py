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

    src.ui.lib.catstreectrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import logging
import wx
import wx.dataview

from .basectrls import BaseTreeViewCtrl
from .refsviewmodel import ReferencesTreeViewModel


# ----------------------------------------------------------------------------
# Control to store the data matching the model
# ----------------------------------------------------------------------------


class ReferencesTreeViewCtrl(BaseTreeViewCtrl):
    """A control to display references in a tree-spreadsheet style.

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

        :param `parent`: (wx.Window)

        """
        super(ReferencesTreeViewCtrl, self).__init__(parent, name)

        # Create an instance of our model and associate to the view.
        self._model = ReferencesTreeViewModel()
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
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_EXPANDED, self._on_item_expanded)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_COLLAPSED, self._on_item_collapsed)
        # self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self._on_item_activated)
        # self.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self._on_item_selection_changed)

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data of the model."""
        return self._model.get_data()

    # ------------------------------------------------------------------------

    def AddRefs(self, entries):
        """Add a list of references into the model.

        :param entries: (str) List of references.

        """
        items = self._model.add_refs(entries)
        if len(items) > 0:
            self.__refresh()
            return True
        return False

    # ------------------------------------------------------------------------

    def RemoveCheckedRefs(self):
        """Remove all checked files."""
        nb = self._model.remove_checked_refs()
        if nb > 0:
            self.__refresh()
            return True
        return False

    # ------------------------------------------------------------------------

    def update_data(self):
        """Overridden. Update the currently displayed data."""
        self._model.update()
        self.__refresh()

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _on_item_expanded(self, evt):
        """Happens when the user cliched a '+' button of the tree.

        We have to update the corresponding object 'expand' value to True.

        """
        self._model.expand(True, evt.GetItem())

    # ------------------------------------------------------------------------

    def _on_item_collapsed(self, evt):
        """Happens when the user cliched a '-' button of the tree.

        We have to update the corresponding object 'expand' value to False.

        """
        self._model.expand(False, evt.GetItem())

    # ------------------------------------------------------------------------

    def __refresh(self):
        for item in self._model.get_expanded_items(True):
            self.Expand(item)
        for item in self._model.get_expanded_items(False):
            self.Collapse(item)
