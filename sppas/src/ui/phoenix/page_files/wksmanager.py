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

        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to access the data
    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data of the currently displayed workspace."""
        return self.FindWindow("wkslist").get_data()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        tb = self.__create_toolbar()
        cv = WorkspacesPanel(self, name="wkpslist")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, 0, wx.EXPAND, 0)
        sizer.Add(self.__create_hline(), 0, wx.EXPAND, 0)
        sizer.Add(cv, 1, wx.EXPAND, 0)

        self.SetMinSize(wx.Size(128, -1))
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = BitmapTextToolbar(self, orient=wx.VERTICAL)
        tb.set_focus_color(wx.Colour(128, 196, 96, 128))  # yellow-green

        tb.AddText("Workspaces: ")
        tb.AddButton("workspace_import", "Import from")
        tb.AddButton("workspace_export", "Export to")
        tb.AddButton("pin", "Pin & Save")
        tb.AddButton("rename", "Rename")
        return tb

    # ------------------------------------------------------------------------

    def __create_hline(self):
        """Create an horizontal line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, 20))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        line.SetForegroundColour(self.GetForegroundColour())
        return line

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)
        self.Bind(wx.EVT_CHECKBOX, self._process_wkp_changed)
        self.Bind(wx.EVT_BUTTON, self._process_action)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        shift_down = event.ShiftDown()
        if key_code == wx.WXK_F5 and shift_down is True:
            logging.debug('Refresh the workspaces [SHIFT+F5 keys pressed]')
            #self.FindWindow("wkpslist").RefreshData()

        event.Skip()

    # ------------------------------------------------------------------------

    def _process_wkp_changed(self, event):
        """Process a checkbox event: the active workspace changed.

        :param event: (wx.Event)

        """
        try:
            self.GetParent().set_data()
        except AttributeError:
            # the parent is not of the expected type
            logging.error('Data of the current workspace not sent to the parent.')
            pass

    # ------------------------------------------------------------------------

    def _process_action(self, event):
        """Process a button event: an action has to be performed.

        :param event: (wx.Event)

        """
        name = event.GetButtonObj().GetName()
        event.Skip()

        if name == "workspace_import":
            self.import_wkp()

        elif name == "workspace_export":
            pass

        elif name == "pin":
            pass

        elif name == "rename":
            self.rename_wkp()

    # ------------------------------------------------------------------------

    def import_wkp(self):
        """Import a file and append into the list of workspaces."""
        # get the name of the file to be imported
        dlg = wx.FileDialog(
            self,
            "Import workspace",
            wildcard="Workspace files (*.wjson)|*.wjson",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        pathname = dlg.GetPath()
        dlg.Destroy()

        # import the selected file in the workspaces
        try:
            self.FindWindow("wkpslist").import_file(pathname)
        except Exception as e:
            wx.LogError("File '{:s}' can't be imported due to the following "
                        "error: {!s:s}".format(pathname, str(e)))

    # ------------------------------------------------------------------------

    def rename_wkp(self):
        """"""
        current_name = self.FindWindow("wkpslist").get_wkp_current_name()
        dlg = wx.TextEntryDialog(
            self,
            "New name of the workspace: ",
            caption=wx.GetTextFromUserPromptStr,
            value=current_name,
            style=wx.OK | wx.CANCEL)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return

        new_name = dlg.GetValue()
        dlg.Destroy()

        if new_name == current_name:
            return

        try:
            self.FindWindow("wkpslist").rename(new_name)
        except Exception as e:
            wx.LogError("Workspace can't be renamed to '{:s}' due to the following "
                        "error: {!s:s}".format(new_name, str(e)))

# ----------------------------------------------------------------------------
# Panel to display the existing workspaces
# ----------------------------------------------------------------------------


class WorkspacesPanel(sppasPanel):
    """Manager of the list of available workspaces in the software.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """
    def __init__(self, parent, name=wx.PanelNameStr):
        super(WorkspacesPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.__wkps = sppasWorkspaces()
        self.__data = self.__wkps.get_data(0)
        self.__current = 0

        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to access the data
    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data of the currently displayed workspace."""
        return self.__data

    # -----------------------------------------------------------------------

    def get_wkp_current_name(self):
        """Return the name of the current workspace."""
        return self.__wkps[self.__current]

    # -----------------------------------------------------------------------

    def import_file(self, filename):
        """Append a new imported workspace."""
        try:
            with open(filename, 'r'):
                pass
        except IOError:
            raise  # TODO: raise a sppasIOError (to get translation!)
        wkp_name = self.__wkps.import_file(filename)
        self.__add_wkp(wkp_name)
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def rename(self, new_name):
        """Set a new name to the current workspace."""
        # rename the workspace
        u_name = self.__wkps.rename(self.__current, new_name)
        # rename the button
        btn = self.GetSizer().GetItem(self.__current).GetWindow()
        btn.SetLabel(u_name)
        btn.Refresh()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        for w in self.__wkps:
            self.__add_wkp(w)

        self.SetMinSize(wx.Size(128, 32*len(self.__wkps)))

    # -----------------------------------------------------------------------

    def __add_wkp(self, name):
        btn = CheckButton(self, label=name, name=name)
        btn.SetSpacing(12)
        btn.SetMinSize(wx.Size(-1, 32))
        btn.SetSize(wx.Size(-1, 32))
        i = self.__wkps.index(name)
        if i == self.__current:
            self.__set_active_btn_style(btn)
            btn.SetValue(True)
        else:
            self.__set_normal_btn_style(btn)
            btn.SetValue(False)
        self.GetSizer().Add(btn, 0, wx.EXPAND | wx.ALL, 2)

    # -----------------------------------------------------------------------

    def __set_normal_btn_style(self, button):
        """Set a normal style to a button."""
        button.BorderWidth = 1
        button.BorderColour = self.GetForegroundColour()
        button.BorderStyle = wx.PENSTYLE_SOLID

    # -----------------------------------------------------------------------

    def __set_active_btn_style(self, button):
        """Set style to the currently checked button."""
        button.BorderWidth = 2
        button.BorderColour = self.GetForegroundColour()
        button.BorderStyle = wx.PENSTYLE_SOLID

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_CHECKBOX, self.__process_wkp_changed)

    # -----------------------------------------------------------------------

    def __process_wkp_changed(self, event):
        """Process a checkbox event.

        :param event: (wx.Event)

        """
        # which workspace is clicked
        btn = event.GetButtonObj()

        if btn.GetLabel() != self.__wkps[self.__current]:
            # user clicked a different workspace
            wkp_name = btn.GetLabel()
            wkp_index = self.__wkps.index(wkp_name)
            logging.debug(' ... Workspace {:s} clicked'.format(wkp_name))
            r = self.__set_current_wkp(wkp_index)
            if r == 0:
                # everything went normally. Say it to the parent.
                event.Skip()

        else:
            # user clicked the current one!
            logging.warning('Workspace {:s} is already active.'
                            ''.format(btn.GetLabel()))
            btn.SetValue(True)

    # -----------------------------------------------------------------------
    # Private methods to manage the data/displayed button
    # -----------------------------------------------------------------------

    def __set_current_wkp(self, index):
        """Set the current workspace at the given index.

        Switch to the corresponding workspace and load the new data.

        """
        wkp_name = self.__wkps[index]

        # un-check the current button
        c = self.GetSizer().GetItem(self.__current).GetWindow()
        # TODO: verify if data where not saved (some locked files)
        # if len(self.__data.get_state(state=FileData.LOCKED) > 0:
        # If the state of some of the data is not ok (files locked)
        #     c = p.GetSizer().GetItem(index).GetWindow()
        #     c.SetValue(False)
        #     return -1

        # save the data of the current wkp
        if self.__current > 0:
            self.__wkps.save(self.__data, self.__current)

        self.__set_normal_btn_style(c)
        c.SetValue(False)
        c.Refresh()
        logging.debug('Workspace {:s} un-checked'.format(c.GetLabel()))

        # load the data of the new workspace
        self.__data = self.__wkps.get_data(index)
        self.__current = index

        # check the one we want to switch on
        n = self.GetSizer().GetItem(self.__current).GetWindow()
        self.__set_active_btn_style(n)
        # n.SetValue(True)
        n.Refresh()
        logging.debug('Workspace {:s} checked'.format(n.GetLabel()))

        return 0

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
