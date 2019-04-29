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
from .catsviewmodel import CataloguesTreeViewModel


# ----------------------------------------------------------------------------
# Control to store the data matching the model
# ----------------------------------------------------------------------------


class CataloguesTreeViewCtrl(BaseTreeViewCtrl):
    """A control to display catalogues in a tree-spreadsheet style.

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
        super(CataloguesTreeViewCtrl, self).__init__(parent, data, name)

        # Create an instance of our model and associate to the view.
        self._model = CataloguesTreeViewModel(data)
        self.AssociateModel(self._model)
        self._model.DecRef()

        # Create the columns that the model wants in the view.
        for i in range(self._model.GetColumnCount()):
            col = BaseTreeViewCtrl._create_column(self._model, i)
            if i == self._model.GetExpanderColumn():
                self.SetExpanderColumn(col)
            wx.dataview.DataViewCtrl.AppendColumn(self, col)

    # ------------------------------------------------------------------------

    def Add(self, filename):
        """Add a file in the tree.

        The given filename must include its absolute path.

        :param filename: (str) Name of a file or a directory.

        """