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

    src.ui.phoenix.filespck.catsmanager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Main panel to manage the catalogues.

"""

import logging
import os
import wx

from sppas.src.ui.phoenix.windows.panel import sppasPanel
from .btntxttoolbar import BitmapTextToolbar

# ----------------------------------------------------------------------------


class CataloguesManager(sppasPanel):
    """Manage the catalogues and actions on perform on them.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, data=None, name=wx.PanelNameStr):
        super(CataloguesManager, self).__init__(
            parent, id=wx.ID_ANY,
            pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.NO_BORDER, name=name)

        self._create_content(data)
        self.Layout()

    # ------------------------------------------------------------------------

    def _create_content(self, data):
        """"""
        tb = self.__create_toolbar()
        cv = sppasPanel(self, name="catsview")  #, data)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(cv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)

        self.SetMinSize((220, 200))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = BitmapTextToolbar(self)
        tb.AddText("Catalogues: ")
        tb.AddButton("add", "Add")
        tb.AddButton("delete", "Delete")
        tb.AddButton("edit", "Edit")
        tb.Bind(wx.EVT_BUTTON, self.OnButtonClick)
        return tb

    # ------------------------------------------------------------------------

    def OnButtonClick(self, event):

        name = event.GetButtonObj().GetName()
        if name == "add":
            # create a reference
            pass  # self._add_catalogue()

        elif name == "delete":
            # delete a reference
            pass  # self._delete()

        elif name == "edit":
            # add/remove attributes
            pass  # self._delete()

        event.Skip()

