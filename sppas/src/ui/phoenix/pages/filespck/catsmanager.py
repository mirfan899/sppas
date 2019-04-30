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
import wx

from sppas.src.ui.phoenix.windows.panel import sppasPanel
from .btntxttoolbar import BitmapTextToolbar
from .catstreectrl import CataloguesTreeViewCtrl

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

    def set_data(self, data):
        """Assign new data to display to this panel.

        :param data: (FileData)

        """
        pass  # self.FindWindow('catsview').set_data(data)

    # ------------------------------------------------------------------------

    def _create_content(self, data):
        """"""
        tb = self.__create_toolbar()
        cv = CataloguesTreeViewCtrl(self, name="catsview")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(cv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)

        self.SetMinSize((220, 200))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = BitmapTextToolbar(self)
        tb.set_focus_color(wx.Colour(64, 64, 196, 128))
        tb.AddText("Catalogues: ")
        tb.AddButton("cats-add", "Create")
        tb.AddButton("cats-edit", "Edit")
        tb.AddButton("cats-delete", "Delete")
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
        if name == "cats-add":
            # create a reference
            pass  # self._add_catalogue()

        elif name == "cats-delete":
            # delete a reference
            pass  # self._delete()

        elif name == "cats-edit":
            # add/remove attributes of the selected references
            pass  # self._delete()

        event.Skip()

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(CataloguesManager):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, data=None)
        self.add_test_data()

    # ------------------------------------------------------------------------

    def add_test_data(self):
        pass
        # self.FindWindow('catsview').Add(cat)
