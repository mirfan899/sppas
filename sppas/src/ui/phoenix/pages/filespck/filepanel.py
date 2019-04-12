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

import os
import wx
import wx.dataview as dv

from sppas.src.ui.phoenix import sppasSwissKnife
from sppas.src.ui.phoenix import sppasPanel
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
        self.tb = wx.ToolBar(self)
        self.tb.SetBackgroundColour(wx.Colour(230, 230, 230))
        self.tb.AddTool(wx.ID_ADD, 'Add', sppasSwissKnife.get_bmp_icon('add.png'))
        self.tb.AddTool(wx.ID_REMOVE, 'Remove', sppasSwissKnife.get_bmp_icon('remove.png'))
        self.tb.Realize()

        self.Bind(wx.EVT_TOOL, self.OnButtonClick)
        self.GetTopLevelParent().Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)

        self.fv = FileTreeCtrl(self, data)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(self.fv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)

        self.SetMinSize((320, 200))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

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

        ide = event.GetId()
        if ide == wx.ID_ADD:
            self._add_file()

        elif ide == wx.ID_REMOVE:
            self.fv.Remove()

        elif ide == wx.ID_DELETE:
            self._delete()
        elif ide == wx.ID_SAVEAS:
            self._copy()
        elif ide == wx.ID_SAVE:
            self._export()

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
