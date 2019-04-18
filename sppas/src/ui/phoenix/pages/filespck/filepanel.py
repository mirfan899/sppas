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

from sppas.src.ui.phoenix.windows.panel import sppasPanel
from sppas.src.ui.phoenix.windows.button import BitmapTextButton
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
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)
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
        tb.AddButton("add", "Add")
        tb.AddButton("remove", "Remove")
        tb.AddButton("delete", "Delete")

        tb.AddSpacer(3)
        tb.Bind(wx.EVT_BUTTON, self.OnButtonClick)
        return tb

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


class MainToolbarPanel(sppasPanel):
    """Panel imitating the behaviors of a toolbar.

    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)

        self.buttons = []
        self.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        self.SetMinSize((32, -1))

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------

    def AddButton(self, icon, text, tooltip=None, activated=True):
        btn = self.create_button(icon, text)
        # btn.SetToolTip(tooltip)
        btn.Enable(activated)
        self.GetSizer().Add(btn, proportion=1, flag=wx.ALL, border=2)
        self.buttons.append(btn)
        return btn

    def AddSpacer(self, proportion=1):
        self.GetSizer().AddStretchSpacer(proportion)

    # -----------------------------------------------------------------------

    def create_button(self, icon, text):
        btn = BitmapTextButton(self, label=text, name=icon)
        btn.FocusStyle = wx.PENSTYLE_SOLID
        btn.FocusWidth = 3
        btn.FocusColour = wx.Colour(220, 220, 120)
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = 12
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        return btn

    # -----------------------------------------------------------------------

    def get_button(self, name):
        for b in self.GetSizer().GetChildren():
            if b.GetName() == name:
                return b

        return None

# ----------------------------------------------------------------------------
# Panel to test
# ----------------------------------------------------------------------------


class TestPanel(FileManager):
    MIN_WIDTH = 240
    MIN_HEIGHT = 64

    # ------------------------------------------------------------------------

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, data=None)
        self.add_test_data()

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
