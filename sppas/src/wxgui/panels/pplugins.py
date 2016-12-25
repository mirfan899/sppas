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
import os

from wxgui.cutils.imageutils import spBitmap
from wxgui.cutils.ctrlutils  import CreateGenButton

from wxgui.sp_icons import PLUGINS_ICON, PLUGIN_IMPORT_ICON, PLUGIN_REMOVE_ICON
from wxgui.sp_consts import BUTTON_ICONSIZE
from wxgui.panels.buttons      import ButtonPanel
from wxgui.dialogs.msgdialogs  import ShowInformation
from wxgui.dialogs.filedialogs import OpenSpecificFiles

from wxgui.panels.mainbuttons  import MainToolbarPanel

from plugins.manager import sppasPluginsManager

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

IMPORT_ID = wx.NewId()
REMOVE_ID = wx.NewId()

# ----------------------------------------------------------------------------

class PluginsPanel( wx.Panel ):
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
        self.SetBackgroundColour( preferences.GetValue('M_BG_COLOUR') )
        self._prefs = preferences

        try:
            self._manager = sppasPluginsManager()
        except Exception as e:
            self._manager = None
            logging.info('%s'%str(e))
            ShowInformation( self, preferences, "%s"%str(e), style=wx.ICON_ERROR)

        self._toolbar = self._create_toolbar()
        #pluginspanel = self.__create_buttons()

        _vbox = wx.BoxSizer(wx.VERTICAL)
        _vbox.Add(self._toolbar,   proportion=0, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=4)
        #_vbox.Add(pluginspanel, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=4)

        self.Bind(wx.EVT_BUTTON, self.ProcessEvent)
        self.SetSizerAndFit(_vbox)


    def _create_toolbar(self):
        """
        Creates a toolbar panel.

        """
        activated=True
        if self._manager is None:
            activated=False
        toolbar = MainToolbarPanel(self, self._prefs)
        toolbar.AddSpacer()
        toolbar.AddButton( IMPORT_ID, PLUGIN_IMPORT_ICON, 'Import', tooltip="Install a plugin in SPPAS plugins directory.", activated=activated)
        toolbar.AddButton( REMOVE_ID, PLUGIN_REMOVE_ICON, 'Remove', tooltip="Delete a plugin of SPPAS plugins directory.", activated=activated)
        toolbar.AddSpacer()
        return toolbar


    def __create_buttons(self):
        """ Create buttons to call plugins. """

        _box = wx.GridBagSizer()

#         annotateButton = ButtonPanel(self, ID_FRAME_DATAROAMER, self._prefs, DATAROAMER_APP_ICON,  "DataRoamer")
#         analyzeButton  = ButtonPanel(self, ID_FRAME_SNDROAMER,  self._prefs, AUDIOROAMER_APP_ICON, "AudioRoamer")
#         pluginsButton  = ButtonPanel(self, ID_FRAME_IPUSCRIBE,  self._prefs, IPUSCRIBE_APP_ICON,   "IPUscriber")
#         settingsButton = ButtonPanel(self, ID_FRAME_SPPASEDIT,  self._prefs, SPPASEDIT_APP_ICON,   "Vizualizer")
#         helpButton     = ButtonPanel(self, ID_FRAME_DATAFILTER, self._prefs, DATAFILTER_APP_ICON,  "DataFilter")
#         aboutButton    = ButtonPanel(self, ID_FRAME_STATISTICS, self._prefs, STATISTICS_APP_ICON,  "DataStats")
#
#         _box.Add( annotateButton, pos=(0, 0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
#         _box.Add( pluginsButton,  pos=(1, 1), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
#         _box.Add( analyzeButton,  pos=(0, 1), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
#         _box.Add( settingsButton, pos=(1, 0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
#         _box.Add( aboutButton,    pos=(2, 0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
#         _box.Add( helpButton,     pos=(2, 1), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
#
#         _box.AddGrowableCol(0)
#         _box.AddGrowableCol(1)
#         _box.AddGrowableRow(0)
#         _box.AddGrowableRow(1)
#         _box.AddGrowableRow(2)

        return _box

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
        afile = OpenSpecificFiles("Plugin archive", ['zip', "*.zip", "*.[zZ][iI][pP]"])
        if len(afile) > 0:
            try:
                # fix a name for the plugin directory
                pluginfolder = os.path.splitext(os.path.basename( afile ))[0]
                pluginfolder.replace(' ', "_")

                # install the plugin.
                pluginid = self._manager.install( afile, pluginfolder )

                ShowInformation( self, self._prefs, "Plugin %s successfully installed in %s folder."%(pluginid,pluginfolder), style=wx.ICON_INFORMATION)

            except Exception as e:
                logging.info('%s'%str(e))
                ShowInformation( self, self._prefs, "%s"%str(e), style=wx.ICON_ERROR)

    # -----------------------------------------------------------------------

    def Remove(self):
        """
        Remove and delete a plugin.

        """
        # get the list of installed plugins

    # -----------------------------------------------------------------------

#     def OnButtonClick(self, evt):
#         obj = evt.GetEventObject()
#         evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, obj.GetId())
#         evt.SetEventObject(self)
#         wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------
