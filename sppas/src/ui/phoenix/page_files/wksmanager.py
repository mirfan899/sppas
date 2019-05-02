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

import os
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
    # Public methods to access the data saved in the workspace files
    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data of the current workspace."""
        return self.FindWindow("wkpslist").get_data()

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
        event.Skip()

    # ------------------------------------------------------------------------

    def _process_wkp_changed(self, event):
        """Process a checkbox event: the active workspace changed.

        :param event: (wx.Event)

        """
        try:
            p = self.GetParent()
            p.set_data_from_workspace()
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
            self.export_wkp()

        elif name == "pin":
            self.pin_save()

        elif name == "rename":
            self.rename_wkp()

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

    def import_wkp(self):
        """Import a file and append into the list of workspaces."""
        # get the name of the file to be imported
        with wx.FileDialog(
            self,
            "Import workspace",
            wildcard="Workspace files (*.wjson)|*.wjson",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) \
                as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            pathname = dlg.GetPath()

            # import the selected file in the workspaces
            try:
                self.FindWindow("wkpslist").import_from(pathname)
            except Exception as e:
                wx.LogError("File '{:s}' can't be imported due to the following "
                            "error: {!s:s}".format(pathname, str(e)))

    # ------------------------------------------------------------------------

    def export_wkp(self):
        """Export a workspace file to a folder."""
        # get the name of the file to be exported in
        with wx.FileDialog(
            self,
            "Export workspace",
            wildcard="Workspace files (*.wjson)|*.wjson",
            style=wx.FD_SAVE) \
                as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            pathname = dlg.GetPath()

        if os.path.exists(pathname):
            dlg = wx.MessageDialog(
                self,
                'A file with name {:s} is already existing. Override it?'.format(pathname),
                caption="Confirm workspace name?",
                style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_QUESTION
            )
            if dlg.ShowModal() == wx.ID_CANCEL:
                return

        try:
            self.FindWindow("wkpslist").export_to(pathname)
        except Exception as e:
            wx.LogError("File '{:s}' can't be exported due to the following "
                        "error: {!s:s}".format(pathname, str(e)))

    # ------------------------------------------------------------------------

    def pin_save(self):
        """Pin and save the currently displayed workspace."""
        # Ask for a name if current is the Blank one
        wkps = self.FindWindow("wkpslist")
        if wkps.get_wkp_current_index() == 0:
            dlg = wx.TextEntryDialog(
                self,
                "New name of the workspace: ",
                caption=wx.GetTextFromUserPromptStr,
                value="Corpus",
                style=wx.OK | wx.CANCEL)
            dlg.SetMaxLength(24)
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            wkp_name = dlg.GetValue()
            dlg.Destroy()

            try:
                wkps.pin(wkp_name)
            except Exception as e:
                wx.LogError("Pin of workspace '{:s}' is not possible due to the "
                            "following error: {!s:s}".format(wkp_name, str(e)))

        else:
            wkp_name = wkps.get_wkp_current_name()

        try:
            wkps.save()
        except Exception as e:
            wx.LogError("Workspace '{:s}' can't be saved due to the "
                        "following error: {!s:s}".format(wkp_name, str(e)))

    # ------------------------------------------------------------------------

    def rename_wkp(self):
        """Rename the currently displayed workspace."""
        current_name = self.FindWindow("wkpslist").get_wkp_current_name()
        dlg = wx.TextEntryDialog(
            self,
            "New name of the workspace: ",
            caption=wx.GetTextFromUserPromptStr,
            value=current_name,
            style=wx.OK | wx.CANCEL)
        dlg.SetMaxLength(24)
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
        self.__current = 0

        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to access the data
    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data saved in the current workspace."""
        return self.__wkps.get_data(self.__current)

    # -----------------------------------------------------------------------

    def get_wkp_current_name(self):
        """Return the name of the current workspace."""
        return self.__wkps[self.__current]

    def get_wkp_current_index(self):
        """Return the index of the current workspace."""
        return self.__current

    # -----------------------------------------------------------------------

    def pin(self, new_name):
        """Append a new empty workspace.

        """
        wkp_name = self.__wkps.new(new_name)
        self.__add_wkp(wkp_name)
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def import_from(self, filename):
        """Append a new imported workspace."""
        try:
            with open(filename, 'r'):
                pass
        except IOError:
            raise  # TODO: raise a sppasIOError (to get translation!)
        wkp_name = self.__wkps.import_from_file(filename)
        self.__add_wkp(wkp_name)
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def export_to(self, filename):
        """Save the current workspace into an external file."""
        self.__wkps.export_to_file(self.__current, filename)

    # -----------------------------------------------------------------------

    def rename(self, new_name):
        """Set a new name to the current workspace."""
        # rename the workspace
        u_name = self.__wkps.rename(self.__current, new_name)
        # rename the button
        btn = self.GetSizer().GetItem(self.__current).GetWindow()
        btn.SetLabel(u_name)
        btn.Refresh()

    # -----------------------------------------------------------------------

    def save(self):
        """Save the currently displayed data to the active workspace."""
        data = self.__get_displayed_data()
        if data is None:
            logging.warning('Currently displayed data not found.')
        else:
            # TODO: verify if data contain locked files
            # if len(data.get_state(state=FileData.LOCKED) > 0:
            #   # switch back the clicked button
            #   idx_btn.SetValue(False)
            #   raise ValueError('Current workspace has locked files.')
            if self.__current > 0:
                self.__wkps.save(data, self.__current)
                logging.info('Currently displayed data of workspace {:s}'
                             'were successfully saved.'
                             ''.format(self.__wkps[self.__current]))

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
        """Add a button corresponding to the name of a workspace."""
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
        button.FocusColour = wx.Colour(128, 196, 96, 128)  # yellow-green

    # -----------------------------------------------------------------------

    def __set_active_btn_style(self, button):
        """Set a special style to the currently checked button."""
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

        Skip the event in order to allow the parent to handle it: it's to
        update the other windows with data of the new selected workspace.

        :param event: (wx.Event)

        """
        # which workspace is clicked
        btn = event.GetButtonObj()

        if btn.GetLabel() != self.__wkps[self.__current]:
            # user clicked a different workspace
            wkp_name = btn.GetLabel()
            wkp_index = self.__wkps.index(wkp_name)
            logging.debug(' ... Workspace {:s} clicked'.format(wkp_name))
            self.__set_current_wkp(wkp_index)
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

    def __get_displayed_data(self):
        """Get the data displayed in another panel."""
        data = None
        try:
            w = self.GetParent().GetParent()
            data = w.get_data()
        except AttributeError:
            logging.warning("Windows {:s} doesn't have a get_data() method"
                            "".format(w.GetName()))
        return data

    # -----------------------------------------------------------------------

    def __set_current_wkp(self, index):
        """Set the current workspace at the given index.

        Save current data then switch to the given workspace.
        The data of the new workspace are not loaded. We're join pointing
        on their filename.

        """
        # the currently displayed button
        cur_btn = self.GetSizer().GetItem(self.__current).GetWindow()
        # the one we want to switch on
        idx_btn = self.GetSizer().GetItem(index).GetWindow()

        # save the data of the current wkp
        self.save()

        # set the current button in a normal state
        self.__set_normal_btn_style(cur_btn)
        cur_btn.SetValue(False)
        cur_btn.Refresh()
        logging.debug('Workspace {:s} un-checked'.format(cur_btn.GetLabel()))

        # assign the new workspace
        self.__current = index
        self.__set_active_btn_style(idx_btn)
        # n.SetValue(True)
        idx_btn.Refresh()
        logging.debug('Workspace {:s} checked'.format(idx_btn.GetLabel()))

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
