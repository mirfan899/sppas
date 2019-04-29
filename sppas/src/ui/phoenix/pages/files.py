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

    ui.phoenix.pages.files.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import logging

from ..windows import sppasPanel
from ..windows import sppasStaticLine
from .filespck.wksmanager import WorkspacesManager
from .filespck.filesmanager import FilesManager
from .filespck.catsmanager import CataloguesManager
from ..windows.button import sppasBitmapButton
from ..windows.button import BitmapTextButton
from ..windows.button import sppasBitmapTextButton

# ---------------------------------------------------------------------------


class sppasFilesPanel(sppasPanel):
    """Create a panel to browse and select files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasFilesPanel, self).__init__(
            parent=parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN,
            name="page_files"
        )
        self._create_content()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.Bind(wx.EVT_KEY_DOWN, self.on_key_press)
        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def GetFileData(self):
        """Return the data of the current workspace."""
        wp = self.FindWindow("workspaces")
        return wp.get_data()

    def SetFileData(self):
        """Set the data of the current workspace to the other panels."""
        data = self.GetFileData()
        fm = self.FindWindow("files")
        fm.set_data(data)
        cm = self.FindWindow("catalogues")
        cm.set_data(data)

    # ------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------

    def _create_content(self):
        """"""
        wp = WorkspacesManager(self, name='workspaces')
        fm = FilesManager(self, name="files")
        ap = self.__create_associate_panel()
        cm = CataloguesManager(self, name="catalogues")

        # Organize the title and message
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wp, 0, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(fm, 2, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(ap, 0, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(cm, 1, wx.EXPAND, 0)

        self.SetSizer(sizer)
        self.SetMinSize((680, 380))   # width = 128 + 320 + 32 + 200
        self.SetAutoLayout(True)

    # ------------------------------------------------------------------------

    def __create_vline(self):
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(2, -1))
        line.SetSize(wx.Size(2, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(2)
        line.SetForegroundColour(wx.Colour(128, 128, 128))
        return line

    # ------------------------------------------------------------------------

    def __create_associate_panel(self):
        ap = sppasPanel(self, name="associate")

        filter = sppasBitmapButton(ap, "check_filter")
        check = sppasBitmapButton(ap, "checklist")
        link = sppasBitmapButton(ap, "link_add")
        unlink = sppasBitmapButton(ap, "link_del")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(4)
        sizer.Add(filter, 1, wx.TOP | wx.ALIGN_CENTRE)
        sizer.Add(check, 1, wx.TOP | wx.ALIGN_CENTRE)
        sizer.AddStretchSpacer(2)
        sizer.Add(link, 1, wx.ALIGN_CENTRE)
        sizer.Add(unlink, 1, wx.ALIGN_CENTRE)
        sizer.AddStretchSpacer(4)

        ap.SetSizer(sizer)
        ap.SetMinSize((32, -1))
        return ap

    # ------------------------------------------------------------------------

    def __create_button(self, text, icon):
        btn = sppasBitmapTextButton(self, label=text, name=icon)
        """btn.FocusStyle = wx.PENSTYLE_SOLID
        btn.FocusWidth = 1
        btn.FocusColour = wx.Colour(200, 20, 20)
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = 12
        btn.BorderWidth = 0
        # btn.BitmapColour = wx.Colour(200, 20, 20)"""
        btn.SetMinSize((-1, 32))
        return btn

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def on_key_press(self, event):
        """Respond to a keypress event."""
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()

        if key_code == wx.WXK_F5 and cmd_down is False and shift_down is False:
            logging.debug('Refresh all the files [F5 keys pressed]')
            self.FindWindow("files").RefreshData()

        event.Skip()
