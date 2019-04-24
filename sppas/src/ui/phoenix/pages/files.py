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

from ..windows import sppasPanel
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
            name="page_files",
            style=wx.BORDER_NONE
        )
        self._create_content()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.Layout()

    # ------------------------------------------------------------------------

    def _create_content(self):
        """"""
        wp = self.__create_workspace_panel()
        fm = FilesManager(self, name="files")
        ap = self.__create_associate_panel()
        cm = CataloguesManager(self, name="catalogues")

        # Organize the title and message
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wp, 0, wx.EXPAND, 0)
        sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.EXPAND, 0)
        sizer.Add(fm, 2, wx.EXPAND, 0)
        sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.EXPAND, 0)
        sizer.Add(ap, 0, wx.EXPAND, 0)
        sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.EXPAND, 0)
        sizer.Add(cm, 1, wx.EXPAND, 0)

        self.SetSizer(sizer)
        self.SetMinSize((680, 380))   # width = 128 + 320 + 32 + 200
        self.SetAutoLayout(True)

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

    def __create_workspace_panel(self):
        wp = sppasPanel(self, name="wokspace")

        open = self.__create_button("Import...", "open_book")
        pin = self.__create_button("Pin&Save", "pin")
        ren = self.__create_button("Rename", "rename")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="Workspaces: "), 0, wx.LEFT | wx.TOP | wx.BOTTOM, 8)
        sizer.Add(open, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP)
        sizer.Add(pin, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP)
        sizer.Add(ren, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP)
        sizer.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), 0, wx.EXPAND, 0)

        wp.SetSizer(sizer)
        wp.SetMinSize((128, -1))
        return wp

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