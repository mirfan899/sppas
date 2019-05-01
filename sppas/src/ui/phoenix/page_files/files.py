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

    ui.phoenix.page_files.files.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import logging

from ..windows import sppasPanel
from ..windows import sppasStaticLine

from sppas.src.ui.phoenix.page_files.wksmanager import WorkspacesManager
from sppas.src.ui.phoenix.page_files.filesmanager import FilesManager
from sppas.src.ui.phoenix.page_files.catsmanager import CataloguesManager
from sppas.src.ui.phoenix.page_files.associate import AssociatePanel

# ---------------------------------------------------------------------------


class sppasFilesPanel(sppasPanel):
    """Main panel to browse and select workspaces and their content.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This panel is managing 4 areas:

        1. the workspaces;
        2. the files;
        3. an association toolbar to link files and catalogues;
        4. the catalogues.

    """

    def __init__(self, parent):
        super(sppasFilesPanel, self).__init__(
            parent=parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE,
            name="page_files"
        )
        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data of the current workspace."""
        wp = self.FindWindow("workspaces")
        return wp.get_data()

    def set_data(self):
        """Set the data of the current workspace to the other panels."""
        data = self.get_data()
        fm = self.FindWindow("files")
        fm.set_data(data)
        cm = self.FindWindow("catalogues")
        cm.set_data(data)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        wp = WorkspacesManager(self, name='workspaces')
        fm = FilesManager(self, name="files")
        ap = AssociatePanel(self, name="associate")
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

        # self.SetMinSize((680, 380))   # width = 128 + 320 + 32 + 200
        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_vline(self):
        """Create a vertical line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(2, -1))
        line.SetSize(wx.Size(2, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(2)
        line.SetForegroundColour(wx.Colour(128, 128, 128))
        return line

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()
        logging.debug('Files page received a key event. key_code={:d}'.format(key_code))

        #if key_code == wx.WXK_F5 and cmd_down is False and shift_down is False:
        #    logging.debug('Refresh all the files [F5 keys pressed]')
        #    self.FindWindow("files").RefreshData()

