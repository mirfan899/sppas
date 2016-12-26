#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: plugins.py
# ----------------------------------------------------------------------------

import logging
import wx
import wx.lib.scrolledpanel
import os

from plugins.manager import sppasPluginsManager

from wxgui.sp_icons import PLUGIN_IMPORT_ICON, PLUGIN_REMOVE_ICON
from wxgui.panels.buttons      import ButtonToolbarPanel
from wxgui.dialogs.msgdialogs  import ShowInformation
from wxgui.dialogs.msgdialogs  import Choice
from wxgui.dialogs.filedialogs import OpenSpecificFiles
from wxgui.panels.mainbuttons  import MainToolbarPanel

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

IMPORT_ID = wx.NewId()
REMOVE_ID = wx.NewId()

# ----------------------------------------------------------------------------


class PluginsPanel(wx.Panel):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Tools for calling a plugin.

    """
    def __init__(self, parent, preferences):

        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))
        self._prefs = preferences

        try:
            self._manager = sppasPluginsManager()
        except Exception as e:
            self._manager = None
            logging.info('%s' % str(e))
            ShowInformation(self, preferences, "%s" % str(e), style=wx.ICON_ERROR)

        self._toolbar = self._create_toolbar()
        self._pluginspanel = PluginsListPanel(self, preferences, self._manager)

        _vbox = wx.BoxSizer(wx.VERTICAL)
        _vbox.Add(self._toolbar,      proportion=0, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=4)
        _vbox.Add(self._pluginspanel, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4)

        self.Bind(wx.EVT_BUTTON, self.ProcessEvent)
        self.SetSizerAndFit(_vbox)

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """
        Creates a toolbar panel.

        """
        activated = True
        if self._manager is None:
            activated = False
        toolbar = MainToolbarPanel(self, self._prefs)
        toolbar.AddSpacer()
        toolbar.AddButton(IMPORT_ID, PLUGIN_IMPORT_ICON, 'Import', tooltip="Install a plugin in SPPAS plugins directory.", activated=activated)
        toolbar.AddButton(REMOVE_ID, PLUGIN_REMOVE_ICON, 'Remove', tooltip="Delete a plugin of SPPAS plugins directory.", activated=activated)
        toolbar.AddSpacer()
        return toolbar

    # -----------------------------------------------------------------------

    def ProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.

        """
        ide = event.GetId()

        if ide == IMPORT_ID:
            self.Import()
            return True
        elif ide == REMOVE_ID:
            self.Remove()
            return True

        return wx.GetApp().ProcessEvent(event)

    # -----------------------------------------------------------------------

    def Import(self):
        """
        Import and install a plugin.

        """
        filename = OpenSpecificFiles("Plugin archive", ['zip', "*.zip", "*.[zZ][iI][pP]"])
        if len(filename) > 0:
            try:
                # fix a name for the plugin directory
                plugin_folder = os.path.splitext(os.path.basename(filename))[0]
                plugin_folder.replace(' ', "_")

                # install the plugin.
                plugin_id = self._manager.install(filename, plugin_folder)

                ShowInformation( self, self._prefs, "Plugin %s successfully installed in %s folder."%(plugin_id,plugin_folder), style=wx.ICON_INFORMATION)

                self._pluginspanel.Append(plugin_id, self._manager)
                self._pluginspanel.Layout()
                self._pluginspanel.Refresh()

            except Exception as e:
                logging.info('%s' % str(e))
                ShowInformation(self, self._prefs, "%s" % str(e), style=wx.ICON_ERROR)

    # -----------------------------------------------------------------------

    def Remove(self):
        """
        Remove and delete a plugin.

        """
        self._pluginspanel.Remove(self._manager)
        self._pluginspanel.Layout()
        self._pluginspanel.Refresh()


# ---------------------------------------------------------------------------


class PluginsListPanel( wx.lib.scrolledpanel.ScrolledPanel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      List of buttons to call a plugin.

    """

    def __init__(self, parent, preferences, manager):
        """
        Constructor.

        @param manager (sppasPluginsManager) Plugins manager.

        """
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))

        self._prefs = preferences
        self._plugins = {}

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        for plugin_id in manager.get_plugin_ids():
            self.Append(plugin_id,manager)

        self.Bind(wx.EVT_BUTTON, self.OnButtonClick)
        self.SetAutoLayout(True)
        self.Layout()
        self.SetupScrolling()

    # -----------------------------------------------------------------------

    def Append(self, plugin_id, manager):
        """
        Append a plugin into the panel.

        :param plugin_id (string) Identifier of the plugin
        :param manager (sppasPluginsManager)

        """
        # Create the button
        plugin       = manager.get_plugin(plugin_id)
        button_id    = wx.NewId()
        button_icon  = os.path.join(plugin.get_directory(),plugin.get_icon())
        button_descr = plugin.get_descr()
        button = ButtonToolbarPanel(self, button_id, self._prefs, button_icon,
                                    plugin_id, activated=False)

        txt = wx.TextCtrl(self, wx.ID_ANY, value=button_descr,
                          style=wx.TE_READONLY | wx.TE_MULTILINE | wx.NO_BORDER)
        font = self._prefs.GetValue('M_FONT')
        txt.SetFont(font)
        txt.SetForegroundColour(self._prefs.GetValue('M_FG_COLOUR'))
        txt.SetBackgroundColour(self._prefs.GetValue('M_BG_COLOUR'))

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(button,
                proportion=0,
                flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL,
                border=4)
        box.Add(txt, proportion=1,
                flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER,
                border=4)

        # Add to the main sizer
        self.GetSizer().Add(box, flag=wx.ALL | wx.EXPAND, border=2)
        self._plugins[plugin_id] = (button_id, box)

    # -----------------------------------------------------------------------

    def Remove(self, manager):
        """
        Ask for the plugin to be removed, remove of the list, then delete of
        the manager.

        :param manager: (sppasPluginsManager)
        :return: plugin identifier of the plugin to be deleted.

        """
        # Ask to select one
        dlg = Choice(self, self._prefs, "Choose the plugin to delete:",
                     self._plugins.keys())
        if dlg.ShowModal() == wx.ID_OK:
            plugin_idx = dlg.GetSelection()
            plugin_id = self._plugins.keys()[plugin_idx]
            try:
                manager.delete(plugin_id)
                plugin_box = self._plugins[plugin_id][1]
                sizer = self.GetSizer()
                sizer.Hide(plugin_box)
                sizer.Remove(plugin_box)
                del self._plugins[plugin_id]

                ShowInformation(self, self._prefs,
                                "Plugin %s was successfully deleted." % plugin_id,
                                style=wx.ICON_INFORMATION)
            except Exception as e:
                logging.info('%s' % str(e))
                ShowInformation(self, self._prefs,
                                "%s deletion error: %s" % (plugin_id, str(e)),
                                style=wx.ICON_ERROR)
        dlg.Destroy()


    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):

        # Which button? then, which plugin?
        obj = evt.GetEventObject()
        button_id = obj.GetId()
        #plugin_id = self._buttons[button_id]

        # Send the plugin identifier to the parent
        # evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, plugin_id)
        # evt.SetEventObject(self)
        # wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------
