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

    src.ui.phoenix.page_files.wksmanager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Main panel to manage the workspaces.

"""

import os
import logging
import wx
import wx.lib.newevent

from sppas import sppasTypeError
from sppas.src.files.filedata import FileData
from sppas.src.ui import sppasWorkspaces

from ..dialogs import Confirm, Error
from ..windows import sppasStaticLine
from ..windows import sppasPanel
from ..windows.button import CheckButton

from .btntxttoolbar import BitmapTextToolbar
from .filesevent import DataChangedEvent

# ---------------------------------------------------------------------------
# Internal use of an event, when the workspace has changed.

WkpChangedEvent, EVT_WKP_CHANGED = wx.lib.newevent.NewEvent()
WkpChangedCommandEvent, EVT_WKP_CHANGED_COMMAND = wx.lib.newevent.NewCommandEvent()


# ----------------------------------------------------------------------------
# List of displayed messages:


# ----------------------------------------------------------------------------

class WorkspacesManager(sppasPanel):
    """Manage the workspaces and actions to perform on them.

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
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        self.__data = FileData()
        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to access the data saved in the workspace files
    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data of the current workspace."""
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this panel.

        :param data: (FileData)

        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        logging.debug('New data to set in the workspace.')
        self.__data = data

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
        tb.AddButton("workspace_pin", "Pin & Save")
        tb.AddButton("workspace_rename", "Rename")
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
        # The user pressed a key of its keyboard
        self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked (LeftDown - LeftUp) an action button of the toolbar
        self.Bind(wx.EVT_BUTTON, self._process_action)

        # The workspaces has changed.
        # This event is sent by the 'wkpslist' child window.
        self.Bind(EVT_WKP_CHANGED, self._process_wkp_changed)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        logging.debug('Workspaces manager received the key event {:d}'
                      ''.format(key_code))
        logging.debug('Key event skipped by the workspace manager.')
        event.Skip()

    # ------------------------------------------------------------------------

    def _process_wkp_changed(self, event):
        """Process a change of workspace event: the active workspace changed.

        The event must contain 'from_wkp' and 'to_wkp' integer members.

        :param event: (wx.Event) WkpChangedEvent

        """
        logging.debug('Workspaces manager processes a change of workspace '
                      'from {:d} to {:d}'.format(event.from_wkp, event.to_wkp))
        wkpslist = event.GetEventObject()
        wkp_name = wkpslist.get_wkp_name(event.to_wkp)
        # Save the currently displayed data (they correspond to the previous wkp)
        if self.__data.has_locked_files() or \
                (event.from_wkp == 0 and self.__data.is_empty() is False):

            # User must confirm to really switch
            title = "Confirm switch of workspace?"
            message = "The current workspace contains not saved work that " \
                      "will be lost. Are you sure you want to change workspace?"
            response = Confirm(message, title)
            if response == wx.ID_CANCEL:
                # the workspace panel has to switch back to the current
                wkpslist.switch_to(event.from_wkp)
                return

        # The user really intended to switch workspace.
        # Update the current data.
        if event.from_wkp > 0:
            # the 'Blank' workspace can't be saved... the others can
            try:
                wkpslist.save(self.__data, event.from_wkp)
            except Exception as e:

                # User must confirm to really switch
                title = "Confirm switch of workspace?"
                message = "The current workspace can not be saved due to " \
                          "the following error: {:s}\nAre you sure you want " \
                          "to change workspace?".format(str(e))
                response = Confirm(message, title)
                if response == wx.ID_CANCEL:
                    # the workspace panel has to switch back to the current
                    wkpslist.switch_to(event.from_wkp)
                    return

        try:
            # Load the data of the workspace from its file
            d = wkpslist.load_data()
            self.__data = d

            # the parent has to be informed of this change of content
            evt = DataChangedEvent(data=self.__data)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

        except Exception as e:
            # the workspace panel has to switch back to the current
            wkpslist.switch_to(event.from_wkp)

            # Propose to the user to remove the failing wkp
            title = "Confirm delete of workspace?"
            message = "Data of the workspace {:s} can't be loaded due to " \
                      "the following error: {:s}.\nDo you want to delete it?" \
                      "".format(wkp_name, str(e)),
            response = Confirm(message, title)
            if response == wx.ID_YES:
                wkpslist.remove(event.to_wkp)

    # ------------------------------------------------------------------------

    def _process_action(self, event):
        """Process a button event: an action has to be performed.

        :param event: (wx.Event)

        """
        name = event.GetButtonObj().GetName()

        if name == "workspace_import":
            self.import_wkp()

        elif name == "workspace_export":
            self.export_wkp()

        elif name == "workspace_pin":
            self.pin_save()

        elif name == "workspace_rename":
            self.rename_wkp()

        event.Skip()

    # ------------------------------------------------------------------------
    # Actions to perform on the workspaces
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
                message = "File '{:s}' can't be imported due to the following" \
                          " error:\n{!s:s}".format(pathname, str(e))
                Error(message, "Import error")

    # ------------------------------------------------------------------------

    def export_wkp(self):
        """Export a workspace file to a folder.

        It is different of a "save as...": here we export the workspace file,
        not the currently displayed data.

        """
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
            message = "A file with name {:s} is already existing. Override it?".format(pathname)
            title = "Confirm workspace name?"
            response = Confirm(message, title)
            if response == wx.ID_CANCEL:
                return

        try:
            self.FindWindow("wkpslist").export_to(pathname)
        except Exception as e:
            message = "File '{:s}' can't be exported due to the following" \
                      " error: {!s:s}".format(pathname, str(e))
            Error(message, "Export error")

    # ------------------------------------------------------------------------

    def pin_save(self):
        """Pin and/or save the currently displayed data into a workspace.

        """
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
                message = "Pin of workspace '{:s}' is not possible due to the following error: {!s:s}".format(wkp_name, str(e))
                Error(message, "Save error")
        else:
            wkp_name = wkps.get_wkp_name()

        try:
            print('TO BE SAVED DATA, IN WKPSMANAGER.PY:')
            print(self.__data.id)
            for fp in self.__data:
                print(fp)
                for fr in fp:
                    print(fr)
                    for fn in fr:
                        print(fn)
            wkps.save(self.__data)
        except Exception as e:
            message = "Workspace '{:s}' can't be saved due to the following error: {!s:s}".format(wkp_name, str(e))
            Error(message, "Save error")

    # ------------------------------------------------------------------------

    def rename_wkp(self):
        """Rename the currently displayed workspace.

        """
        current_name = self.FindWindow("wkpslist").get_wkp_name()
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
            message = "Workspace can't be renamed to '{:s}' due to the " \
                      "following error: {!s:s}".format(new_name, str(e))
            Error(message, "Rename error")

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

    The parent has to handle EVT_WKP_CHANGED event to be informed that a
    workspace changed.

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

    def load_data(self, index=None):
        """Return the data saved in the current workspace.

        If the file of the workspace does not exists, return an empty
        instance of FileData.

        :param index: (int) Index of the workspace to get data
        :returns: (FileData)
        :raises: IndexError

        """
        if index is None:
            index = self.__current
        return self.__wkps.load_data(index)

    # -----------------------------------------------------------------------

    def get_wkp_name(self, index=None):
        """Return the name of the current workspace.

        :param index: (int) Index of the workspace to get name
        :returns: (str)

        """
        if index is None:
            index = self.__current
        return self.__wkps[index]

    # -----------------------------------------------------------------------

    def get_wkp_current_index(self):
        """Return the index of the current workspace.

        :returns: (int)

        """
        return self.__current

    # -----------------------------------------------------------------------

    def switch_to(self, index):
        """Set the current workspace at the given index.

        Save current data then switch to the given workspace.
        The data of the new workspace are not loaded. We're join pointing
        on their filename.

        :param index: (int) Index of the workspace to switch on

        """
        # check if the given index is a valid one
        wkp_name = self.__wkps[index]

        # the currently displayed button
        cur_btn = self.GetSizer().GetItem(self.__current).GetWindow()
        # the one we want to switch on
        idx_btn = self.GetSizer().GetItem(index).GetWindow()

        # set the current button in a normal state
        self.__btn_set_state(cur_btn, False)
        # assign the new workspace
        self.__current = index
        self.__btn_set_state(idx_btn, True)

    # -----------------------------------------------------------------------

    def pin(self, new_name):
        """Append a new empty workspace and set it the current one.

        :param new_name: (str) Name of the new workspace.

        """
        wkp_name = self.__wkps.new(new_name)
        index = self.__append_wkp(wkp_name)
        self.switch_to(index)
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def import_from(self, filename):
        """Append a new imported workspace.

        A ".wjson" extension is expected.

        :param filename: (str) Name of the file to import.

        """
        try:
            with open(filename, 'r'):
                pass
        except IOError:
            raise  # TODO: raise a sppasIOError (to get translation!)
        wkp_name = self.__wkps.import_from_file(filename)
        self.__append_wkp(wkp_name)
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def export_to(self, filename):
        """Save the current workspace into an external file.

        A ".wjson" extension is expected but not verified.

        :param filename: (str) Name of the exported file.

        """
        self.__wkps.export_to_file(self.__current, filename)

    # -----------------------------------------------------------------------

    def rename(self, new_name):
        """Set a new name to the current workspace.

        Changing the name of a workspace implies to change both its filename
        and the label of the button.

        :param new_name: (str) New name to assign to the workspace.

        """
        # rename the workspace
        u_name = self.__wkps.rename(self.__current, new_name)
        # rename the button
        btn = self.GetSizer().GetItem(self.__current).GetWindow()
        btn.SetLabel(u_name)
        btn.Refresh()

    # -----------------------------------------------------------------------

    def save(self, data, index=None):
        """Save the given data to the active workspace or to the given one.

        :param data: (FileData)
        :param index: (int) Save data to the workspace with this index
        :raises: IndexError, IOError

        """
        if index is None:
            index = self.__current
        self.__wkps.save_data(data, index)

    # -----------------------------------------------------------------------

    def remove(self, index):
        """Remove a workspace of the list and delete the corresponding file.

        :param index: (int)

        """
        if index == self.__current:
            raise IndexError("The currently displayed workspace can't be removed")

        if index == 0:
            raise IndexError("The 'Blank' workspace can't be removed")

        # Delete of the list
        self.__wkps.delete(index)

        # Remove of the sizer
        self.GetSizer().Remove(index)

        self.Layout()
        self.Refresh()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        for w in self.__wkps:
            self.__append_wkp(w)
        self.SetMinSize(wx.Size(128, 32*len(self.__wkps)))

    # -----------------------------------------------------------------------

    def __append_wkp(self, name):
        """Add a button corresponding to the name of a workspace.

        :param name: (str)
        :return: index of the newly created workspace

        """
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
        return i

    # -----------------------------------------------------------------------

    def __set_normal_btn_style(self, button):
        """Set a normal style to a button."""
        button.BorderWidth = 1
        button.BorderColour = self.GetForegroundColour()
        button.BorderStyle = wx.PENSTYLE_SOLID
        button.FocusColour = wx.Colour(128, 196, 96, 128)  # yellow-green

    # -----------------------------------------------------------------------

    def __set_active_btn_style(self, button):
        """Set a special style to the button."""
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
        self.Bind(wx.EVT_CHECKBOX, self.__process_checked)

    # -----------------------------------------------------------------------

    def __process_checked(self, event):
        """Process a checkbox event.

        Skip the event in order to allow the parent to handle it: it's to
        update the other windows with data of the new selected workspace.

        :param event: (wx.Event)

        """
        # the button we want to switch on
        wkp_btn = event.GetButtonObj()
        wkp_name = wkp_btn.GetLabel()
        wkp_index = self.__wkps.index(wkp_name)

        # the current button
        cur_btn = self.GetSizer().GetItem(self.__current).GetWindow()

        # user clicked a different workspace
        if cur_btn != wkp_btn:

            evt = WkpChangedEvent(from_wkp=self.__current, to_wkp=wkp_index)
            evt.SetEventObject(self)

            # set the current button in a normal state
            self.__btn_set_state(cur_btn, False)
            # assign the new workspace
            self.__current = wkp_index
            self.__btn_set_state(wkp_btn, True)

            # the parent will decide what to exactly do with this change
            wx.PostEvent(self.GetParent(), evt)

        else:
            # user clicked the current workspace
            logging.info('Workspace {:s} is already active.'
                         ''.format(wkp_btn.GetLabel()))
            wkp_btn.SetValue(True)

    # -----------------------------------------------------------------------
    # Private methods to manage the data/displayed button
    # -----------------------------------------------------------------------

    def __btn_set_state(self, btn, state):
        if state is True:
            self.__set_active_btn_style(btn)
        else:
            self.__set_normal_btn_style(btn)
        btn.SetValue(state)
        btn.Refresh()
        logging.debug('Workspace {:s} is checked: {:s}'
                      ''.format(btn.GetLabel(), str(state)))

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(WorkspacesManager):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        self.SetBackgroundColour(wx.Colour(128, 128, 128))

