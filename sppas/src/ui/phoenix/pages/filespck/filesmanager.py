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

    src.ui.phoenix.filespck.filesmanager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Main panel to manage the tree of files.

"""

import logging
import os
import wx

from sppas.src.ui.phoenix.windows.panel import sppasPanel
from .filestreectrl import FilesTreeViewCtrl
from .btntxttoolbar import BitmapTextToolbar

# ----------------------------------------------------------------------------


class FilesManager(sppasPanel):
    """Manage the tree of files and actions on perform on them.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, data=None, name=wx.PanelNameStr):
        super(FilesManager, self).__init__(
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
        self.FindWindow('fileview').set_data(data)

    # ------------------------------------------------------------------------

    def _create_content(self, data):
        """"""
        tb = self.__create_toolbar()
        fv = FilesTreeViewCtrl(self, name="fileview")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(fv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)

        self.SetMinSize((320, 200))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = BitmapTextToolbar(self)
        tb.set_focus_color(wx.Colour(196, 128, 128))
        tb.AddText("Files: ")
        tb.AddButton("files-add", "Add")
        tb.AddButton("files-remove", "Remove checked")
        tb.AddButton("files-delete", "Delete checked")
        tb.Bind(wx.EVT_BUTTON, self.on_button_click)
        return tb

    # -----------------------------------------------------------------------

    def GetSelected(self, extension=""):
        """Get a list containing checked filenames.

        Selecting a folder item equals to select all its items.

        :param extension: Extension of the selected file
        :return: The fileroot of each selected regular file (not folders)
        from the data.

        """
        # TODO: return the checked files (or roots), not the selected ones
        checked = self.FindWindow("fileview").GetSelections()
        return checked

    # ------------------------------------------------------------------------

    def on_key_press(self, event):
        """Respond to a keypress event."""
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        if key_code == wx.WXK_F5 and cmd_down is True:
            logging.debug('Refresh the data files [CMD+F5 keys pressed]')
            self.FindWindow("fileview").RefreshData()

        event.Skip()

    # ------------------------------------------------------------------------

    def on_button_click(self, event):

        name = event.GetButtonObj().GetName()
        logging.debug("Event received of button: {:s}".format(name))

        if name == "files-add":
            self._add_file()

        elif name == "files-remove":
            self.FindWindow("fileview").Remove()

        elif name == "files-delete":
            self._delete()

        event.Skip()

    # ------------------------------------------------------------------------
    # Private
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
                self.FindWindow('fileview').Add(f)

    # ------------------------------------------------------------------------

    def _delete(self):
        logging.info('Not implemented')
        pass


# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(FilesManager):
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
            logging.info('add {:s}'.format(fullname))
            if os.path.isfile(fullname):
                self.FindWindow('fileview').Add(fullname)

        self.FindWindow('fileview').ExpandAll()
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_EXPANDED, self.__onExpanded)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_COLLAPSED, self.__onCollapsed)

    # ------------------------------------------------------------------------

    def __onExpanded(self, evt):
        print("fv expanded")

    def __onCollapsed(self, evt):
        print("fv collapsed")
