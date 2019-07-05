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

    ui.phoenix.page_plugins.plugins.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    One of the main pages of the wx4-based GUI of SPPAS.

    It manages the set of plugins: install, delete, run.

"""

import logging
import wx
import os

from sppas import sppasTypeError

from sppas.src.files import FileData, States
from sppas.src.plugins import sppasPluginsManager

from ..dialogs import Error, Information
from ..dialogs import sppasFileDialog

from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..windows import sppasToolbar
from ..dialogs import sppasChoiceDialog
from ..main_events import DataChangedEvent

# ---------------------------------------------------------------------------
# List of displayed messages:

PGS_TITLE = "Plugins: "
PGS_ACT_ADD = "Install"
PGS_ACT_DEL = "Delete"

PGS_ACT_ADD_ERROR = "Plugin '{:s}' can't be imported due to the following" \
                       " error:\n{!s:s}"
PGS_ACT_DEL_ERROR = "Plugin '{:s}' can't be deleted due to the following" \
                       " error:\n{!s:s}"

FLS_MSG_CONFIRM_DEL = "Are you sure you want to delete {:s} plugin?"

# ----------------------------------------------------------------------------


class sppasPluginsPanel(sppasPanel):
    """Create a panel to work with plugins on the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    HIGHLIGHT_COLOUR = wx.Colour(196, 128, 196, 196)

    def __init__(self, parent):
        super(sppasPluginsPanel, self).__init__(
            parent=parent,
            name="page_plugins",
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE,
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
        """Return the data currently displayed in the list of files.

        :returns: (FileData) data of the files-viewer model.

        """
        return self.FindWindow("pluginslist").get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (FileData)

        """
        self.FindWindow("pluginslist").set_data(data)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """"""
        tb = self.__create_toolbar()
        fv = PluginsList(self, name="pluginslist")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(fv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)

        self.SetMinSize(wx.Size(sppasPanel.fix_size(320), sppasPanel.fix_size(200)))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        """Create the toolbar."""
        tb = sppasToolbar(self)
        tb.set_focus_color(sppasPluginsPanel.HIGHLIGHT_COLOUR)
        tb.AddTitleText(PGS_TITLE, sppasPluginsPanel.HIGHLIGHT_COLOUR)
        tb.AddButton("plugin-import", PGS_ACT_ADD)
        tb.AddButton("plugin-delete", PGS_ACT_DEL)
        return tb

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

        # The user clicked (LeftDown - LeftUp) an action button of the toolbar
        self.Bind(wx.EVT_BUTTON, self._process_action)

    # ------------------------------------------------------------------------

    def notify(self):
        """Send the EVT_DATA_CHANGED to the parent."""
        if self.GetParent() is not None:
            data = self.get_data()
            data.set_state(States().CHECKED)
            evt = DataChangedEvent(data=data)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()
        logging.debug('Plugins page received a key event. key_code={:d}'.format(key_code))

        event.Skip()

    # ------------------------------------------------------------------------

    def _process_action(self, event):
        """Process an action of a button.

        :param event: (wx.Event)

        """
        name = event.GetButtonObj().GetName()
        logging.debug("Event received of button: {:s}".format(name))

        if name == "plugin-import":
            self.FindWindow("pluginslist").Install()

        elif name == "plugin-delete":
            w = self.FindWindow("pluginslist")
            w.Delete()

        event.Skip()

# -----------------------------------------------------------------------


class PluginsList(sppasScrolledPanel):
    """Create a panel to run a plugin.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    No data is given at the initialization.
    Use set_data() method.

    """

    def __init__(self, parent, name="page_plugins_list"):
        super(PluginsList, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE,
            name=name
        )

        # The workspace to work with
        self.__data = FileData()

        # The manager for the plugins
        try:
            self._manager = sppasPluginsManager()
        except Exception as e:
            self._manager = None
            Error("Plugin manager initialization: {:s}".format(str(e)))

        self._create_content()
        # self._setup_events()
        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (FileData) data of the files-viewer model.

        """
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (FileData)

        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        logging.debug('New data to set in the plugins page. '
                      'Id={:s}'.format(data.id))
        self.__data = data

    # -----------------------------------------------------------------------
    # Actions to perform with plugins
    # -----------------------------------------------------------------------

    def Install(self):
        """Import and install a plugin."""
        # Get the name of the file to be imported
        dlg = sppasFileDialog(self, title=PGS_ACT_ADD,
                              style=wx.FC_OPEN | wx.FC_NOSHOWHIDDEN)
        dlg.SetWildcard("ZIP files|*.zip")  # |*.[zZ][iI][pP]")
        if dlg.ShowModal() == wx.ID_OK:
            # Get the selected file name
            filename = dlg.GetPath()

            try:
                # fix a name for the plugin directory
                plugin_folder = os.path.splitext(os.path.basename(filename))[0]
                plugin_folder.replace(' ', "_")

                # install the plugin and display it in the list
                plugin_id = self._manager.install(filename, plugin_folder)
                self._append(self._manager.get_plugin(plugin_id))
                self.Layout()
                self.Refresh()

                Information("Plugin {:s} successfully installed in folder {:s}."
                            "".format(plugin_id, plugin_folder))

            except Exception as e:
                message = PGS_ACT_ADD_ERROR.format(filename, str(e))
                Error(message, "Import error")

        dlg.Destroy()

    # ------------------------------------------------------------------------

    def Delete(self):
        """Remove and delete a plugin."""
        logging.debug('User asked to delete a plugin')
        try:
            plugin_id = self._remove()
            if plugin_id is not None:
                logging.debug('User asked to delete the plugin {:s}'.format(plugin_id))

                self._manager.delete(plugin_id)
                Information("Plugin %s was successfully deleted." % plugin_id)

        except Exception as e:
            Error("%s" % str(e))

    # ------------------------------------------------------------------------
    # Create and manage the GUI
    # ------------------------------------------------------------------------

    def _create_content(self):
        """"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        if self._manager is not None:
            for plugin_id in self._manager.get_plugin_ids():
                plugin = self._manager.get_plugin(plugin_id)
                self._append(plugin)

        self.SetupScrolling(scroll_x=True, scroll_y=True)

    # -----------------------------------------------------------------------

    def _append(self, plugin):
        """Append a plugin into the panel.

        :param plugin (sppasPluginParam) The plugin to append

        """
        plugin_id = plugin.get_key()

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(wx.StaticText(self, label=plugin_id), proportion=0, flag=wx.LEFT | wx.EXPAND, border=2)
        self.GetSizer().Add(s)

    # ------------------------------------------------------------------------

    def _remove(self):
        """Ask for the plugin to be removed, remove of the list.

        :returns: plugin identifier of the plugin to be deleted.

        """
        keys = list(self._manager.get_plugin_ids())
        logging.debug('List of plugins: {:s}'.format(str(keys)))
        plugin_id = None
        dlg = sppasChoiceDialog("Which is the plugin to delete:", choices=keys)
        if dlg.ShowModal() == wx.ID_OK:

            # Remove of the sizer
            idx = dlg.GetSelection()
            self.GetSizer().Remove(idx)

            # Destroy the panel
            plugin_id = dlg.GetStringSelection()
            panel_name = plugin_id + "_panel"
            panel = self.FindWindow(panel_name)
            panel.Destroy()

            # Re-organize
            self.Layout()
            self.Refresh()

        dlg.Destroy()
        return plugin_id
