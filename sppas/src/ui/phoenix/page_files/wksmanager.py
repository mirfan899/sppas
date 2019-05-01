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

    src.ui.phoenix.filespck.wksmanager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Main panel to manage the workspaces.

"""

import logging
import wx

from sppas.src.ui.wkps import sppasWorkspaces

from sppas.src.ui.phoenix.windows import sppasStaticLine
from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows.button import CheckButton

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

    def __init__(self, parent, name=wx.PanelNameStr):
        super(WorkspacesManager, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN,
            name=name)

        # manager of the list of available workspaces in the software
        self.__wkps = sppasWorkspaces()
        self.__data = self.__wkps.get_data(0)
        self.__current = 0

        self._create_content()

        self.Bind(wx.EVT_KEY_DOWN, self.on_key_press)
        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to access the data
    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data of the currently displayed workspace."""
        return self.__data

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        tb = self.__create_toolbar()

        cv = sppasPanel(self, name="wksview")
        s = wx.BoxSizer(wx.VERTICAL)
        for i, w in enumerate(self.__wkps):
            btn = CheckButton(cv, label=w, name=w)
            btn.SetSpacing(12)
            btn.SetMinSize(wx.Size(-1, 32))
            btn.SetSize(wx.Size(-1, 32))
            s.Add(btn, 0, wx.EXPAND | wx.ALL, 2)
            btn.Bind(wx.EVT_CHECKBOX, self.on_wkp_changed)
            if i == 0:
                btn.SetValue(True)
            else:
                btn.SetValue(False)
        cv.SetSizer(s)

        # current workspace is the blank one
        #font = self.GetFont().MakeBold().Scale(1.4)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(cv, proportion=1, flag=wx.EXPAND, border=0)

        self.SetMinSize((128, 200))
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __set_current_wkp(self, index):
        """Set the current workspace at the given index.

        Switch to the corresponding workspace and load the new data.

        """
        wkp_name = self.__wkps[index]

        # un-check the current button
        p = self.FindWindow('wksview')
        c = p.GetSizer().GetItem(self.__current).GetWindow()
        # TODO: verify if data where not saved (some locked files)
        # if len(self.__data.get_state(state=FileData.LOCKED) > 0:
        # If the state of some of the data is not ok (files locked)
        #     c = p.GetSizer().GetItem(index).GetWindow()
        #     c.SetValue(False)
        #     return

        # save the data of the current wkp
        if self.__current > 0:
            self.__wkps.save(self.__data, self.__current)

        c.SetValue(False)
        c.Refresh()
        logging.debug('Workspace {:s} un-checked'.format(c.GetLabel()))

        # load the data of the new workspace
        self.__data = self.__wkps.get_data(index)
        self.__current = index

        # check the one we want to switch on
        # c = p.GetSizer().GetItem(self.__current).GetWindow()
        # c.SetValue(True)
        # c.Refresh()

        # send the new data to the parent
        try:
            self.GetParent().set_data()
        except AttributeError:
            # the parent is not of the expected type
            logging.error('Data of the current workspace not sent to the parent.')
            pass

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = BitmapTextToolbar(self, orient=wx.VERTICAL)
        tb.set_focus_color(wx.Colour(128, 196, 96, 128))  # yellow-green

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

    # ------------------------------------------------------------------------

    def on_wkp_changed(self, event):

        # which workspace is clicked
        btn = event.GetButtonObj()

        if btn.GetLabel() != self.__wkps[self.__current]:
            wkp_name = btn.GetLabel()
            wkp_index = self.__wkps.index(wkp_name)
            logging.debug(' ... Workspace {:s} clicked'.format(wkp_name))
            self.__set_current_wkp(wkp_index)

        else:
            # user clicked the current one!
            logging.warning('Workspace {:s} is already active.'
                            ''.format(btn.GetLabel()))
            btn.SetValue(True)

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(WorkspacesManager):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        self.add_test_data()
        self.SetBackgroundColour(wx.Colour(128, 128, 128))

    # ------------------------------------------------------------------------

    def add_test_data(self):
        pass
        # self.FindWindow('catsview').Add(cat)
