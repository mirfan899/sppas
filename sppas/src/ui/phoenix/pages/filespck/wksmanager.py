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


class WorkspacesManager(sppasPanel):
    """Manage the workspaces and actions on perform on them.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, data=None, name=wx.PanelNameStr):
        super(WorkspacesManager, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN,
            name=name)

        self._create_content(data)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_press)
        self.Layout()

    # ------------------------------------------------------------------------

    def _create_content(self, data):
        """"""
        tb = self.__create_toolbar()
        cv = sppasPanel(self, name="wksview")  #, data)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(cv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)
        self.SetMinSize((196, 200))
        self.SetSize((196, -1))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = BitmapTextToolbar(self, orient=wx.VERTICAL)
        tb.set_focus_color(wx.Colour(128, 128, 196))

        tb.AddText("Workspaces: ")
        tb.AddButton("workspace_import", "Import from")
        tb.AddButton("workspace_export", "Export to")
        tb.AddButton("pin", "Pin & Save")
        tb.AddButton("rename", "Rename")
        tb.Bind(wx.EVT_BUTTON, self.on_button_click)
        return tb

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def on_key_press(self, event):
        """Respond to a keypress event."""
        key_code = event.GetKeyCode()
        shift_down = event.ShiftDown()
        if key_code == wx.WXK_F5 and shift_down is True:
            logging.debug('Refresh the data catalogs [SHIFT+F5 keys pressed]')
            self.FindWindow("catsview").RefreshData()

        event.Skip()

    # ------------------------------------------------------------------------

    def on_button_click(self, event):

        name = event.GetButtonObj().GetName()
        if name == "workspace_import":
            pass

        elif name == "workspace_export":
            pass

        elif name == "pin":
            pass

        elif name == "rename":
            pass

        event.Skip()

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(WorkspacesManager):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, data=None)
        self.add_test_data()
        self.SetBackgroundColour(wx.Colour(128, 128, 128))

    # ------------------------------------------------------------------------

    def add_test_data(self):
        pass
        # self.FindWindow('catsview').Add(cat)
