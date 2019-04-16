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

    src.ui.phoenix.filespck.filetree.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import os
import wx
import wx.dataview as dv

from sppas.src.ui.phoenix import sppasSwissKnife
from sppas.src.ui.phoenix.windows.panel import sppasPanel
from sppas.src.ui.phoenix.windows.button import BitmapTextButton, sppasBitmapTextButton
from .filetree import FileTreeCtrl

# ----------------------------------------------------------------------------


class FileManager(sppasPanel):
    """

    """

    def __init__(self, parent, data=None):
        super(FileManager, self).__init__(
            parent, id=wx.ID_ANY,
            pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.NO_BORDER, name=wx.PanelNameStr)

        self._create_content(data)
        self.Layout()

    # ------------------------------------------------------------------------

    def _create_content(self, data):
        """"""
        self.tb = self.__create_toolbar()
        self.fv = FileTreeCtrl(self, data)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(self.fv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)

        self.SetMinSize((320, 200))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = MainToolbarPanel(self)
        add = tb.AddButton("add", "Add")
        add.FocusStyle = wx.PENSTYLE_SOLID
        add.FocusWidth = 1
        add.BorderWidth = 0
        add.FocusColour = wx.Colour(220, 220, 120)

        tb.AddButton("remove", "Remove")
        tb.AddButton("delete", "Delete")

        tb.AddSpacer(3)
        tb.Bind(wx.EVT_BUTTON, self.OnButtonClick)
        return tb

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        self.tb.SetForegroundColour(colour)
        self.fv.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        self.tb.SetBackgroundColour(colour)
        self.fv.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        self.tb.SetFont(font)
        self.fv.SetFont(font)
        self.Layout()

    # -----------------------------------------------------------------------

    def GetSelected(self, extension=""):
        """Get a list containing checked filenames.

        Selecting a folder item equals to select all its items.

        :param extension: Extension of the selected file
        :return: The filepath of each selected regular file (not folders)
        from the data.

        """
        checked = self.fv.GetSelections()
        return checked

    # ------------------------------------------------------------------------

    def OnKeyPress(self, event):
        """Respond to a keypress event."""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_F5:
            print('Refresh the data')
            self.fv.RefreshData()

        event.Skip()

    # ------------------------------------------------------------------------

    def OnButtonClick(self, event):

        name = event.GetButtonObject().GetName()
        if name == "add":
            self._add_file()

        elif name == "remove":
            self.fv.Remove()

        elif name == "delete":
            self._delete()

        event.Skip()

    # ------------------------------------------------------------------------

    def _add_file(self):
        filenames = list()
        with wx.Dialog(self, style=wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.STAY_ON_TOP, size=(640, 480)) as dlg:
            fc = wx.FileCtrl(dlg,  # defaultDirectory="", defaultFilename="", wildCard="",
                             style=wx.FC_OPEN | wx.FC_MULTIPLE | wx.FC_NOSHOWHIDDEN)
            fc.SetSize((500, 350))
            fc.SetBackgroundColour(self.GetBackgroundColour())
            fc.SetForegroundColour(self.GetForegroundColour())

            ok = wx.Button(dlg, id=wx.ID_OK, label='OK')
            dlg.SetAffirmativeId(wx.ID_OK)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(fc, 1, wx.EXPAND, 0)
            sizer.Add(ok, 0, wx.ALL | wx.EXPAND, 4)
            dlg.SetSizer(sizer)

            if dlg.ShowModal() == wx.ID_OK:
                filenames = fc.GetPaths()

        if len(filenames) > 0:
            for f in filenames:
                self.fv.Add(f)

    # ------------------------------------------------------------------------

    def _delete(self):
        logging.info('Not implemented')
        pass


# ----------------------------------------------------------------------------


class MainToolbarPanel(wx.Panel):
    """Panel imitating the behaviors of a toolbar.

    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)

        self.buttons = []
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.SetSizer(self.sizer)
        self.SetMinSize((32, -1))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick)

    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):
        evt.Skip()
        """obj = evt.GetEventObject()
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, obj.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)"""

    def AddButton(self, icon, text, tooltip=None, activated=True):
        btn = self.create_button(icon, text)
        btn.SetToolTip(tooltip)
        btn.Enable(activated)
        self.sizer.Add(btn, proportion=1, flag=wx.ALL, border=2)
        self.buttons.append(btn)
        #self.Layout()
        return btn

    def AddSpacer(self, proportion=1):
        self.sizer.AddStretchSpacer(proportion)

    # -----------------------------------------------------------------------

    def create_button(self, icon, text):
        print(icon)
        btn = BitmapTextButton(self, label=text, name=icon)
        btn.SetBorderWidth(0)
        return btn

# ----------------------------------------------------------------------------
# Panel to test
# ----------------------------------------------------------------------------


class TestPanel(FileManager):
    MIN_WIDTH = 240
    MIN_HEIGHT = 64

    # ------------------------------------------------------------------------

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, data=None)

    # ------------------------------------------------------------------------

    def add_test_data(self):
        here = os.path.abspath(os.path.dirname(__file__))

        for f in os.listdir(here):
            fullname = os.path.join(here, f)
            print('add {:s}'.format(fullname))
            if os.path.isfile(fullname):
                self.fv.Add(fullname)

        self.fv.ExpandAll()
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_EXPANDED, self.__onExpanded)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_COLLAPSED, self.__onCollapsed)

    # ------------------------------------------------------------------------

    def __onExpanded(self, evt):
        print("fv expanded")

    def __onCollapsed(self, evt):
        print("fv collapsed")
