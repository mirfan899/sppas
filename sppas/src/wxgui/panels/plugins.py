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

__docformat__ = """epytext"""
__authors__   = """Tatsuya Watanabe"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import os
import shutil
import wx

from wxgui.process.pluginprocess   import PluginProcess
from wxgui.views.pluginimport      import ImportPluginDialog
from wxgui.structs.plugincfgparser import PluginConfigParser


# ---------------------------------------------------------------------------


class PluginPanel(wx.Panel):

    def __init__(self, preferences, plugin_dir, *args, **kwargs):

        wx.Panel.__init__(self, *args, **kwargs)
        self.preferences = preferences
        self.plugin_dir = plugin_dir
        self.cfgparser = PluginConfigParser()
        self.pluginList = []
        self.InitUI()
        self.InitPlugins()


    def InitUI(self):
        self._title = wx.StaticText(self, -1, 'Plugins:')
        if self.preferences:
            self._title.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
            font = self.preferences.GetValue('M_FONT')
            font.SetWeight( wx.BOLD )
            self._title.SetFont(font)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self._title, proportion=0, flag=wx.ALL, border=4)
        self.SetSizer(self.sizer)
        if self.preferences:
            self.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR') )


    def InitPluginDirectory(self):
        if os.path.exists(self.plugin_dir):
            return True
        try:
            os.makedirs(self.plugin_dir)
        except OSError as e:
            return False
        else:
            return True


    def InitPlugins(self):
        self.InitPluginDirectory()
        cfgfiles = [os.path.join(self.plugin_dir, d, "plugin.cfg") for d in os.listdir(self.plugin_dir)]
        for cfgfile in cfgfiles:
            try:
                self.AppendPlugin(cfgfile)
            except Exception as e:
                wx.MessageBox("%s" % e,
                              "Plugin Error",
                              wx.ICON_ERROR)


    def AppendPlugin(self, cfgfile):
        plugin = self.CreatePlugin(cfgfile)
        if plugin:
            self.pluginList.append(os.path.dirname(cfgfile))
            self.sizer.Add(plugin, flag=wx.ALL|wx.ALIGN_CENTER, border=4)
            self.Layout()


    def CopyPlugin(self, src, dst):
        shutil.copytree(src, dst)


    def CreatePlugin(self, cfgfile):
        config_data = self.cfgparser.read(cfgfile)
        if not config_data:
            return
        config = config_data[0]
        return PluginBitmapButton(parent=self,
                                  **config)


    def RemovePlugin(self, plugin_dir):
        shutil.rmtree(plugin_dir)
        index = self.pluginList.index(plugin_dir)
        self.pluginList.remove(plugin_dir)
        self.sizer.Remove(index+1)
        self.Layout()


    def Import(self):
        """ Open the plugin import frame.
            Return:      none
            Exceptions:  none
        """
        dlg = ImportPluginDialog(self)
        if not dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
            return
        src = dlg.GetPluginDir()
        dst = os.path.join(self.plugin_dir, os.path.basename(src))
        if os.path.exists(dst):
            self.RemovePlugin(dst)
        self.CopyPlugin(src, dst)
        cfgfile = os.path.join(dst, 'plugin.cfg')
        try:
            self.AppendPlugin(cfgfile)
        except Exception as e:
            wx.MessageBox("%s" % e,
                          "Plugin Error",
                          wx.ICON_ERROR)


    def SetPrefs(self, prefs):
        """
        Fix new preferences.
        """
        self._prefsIO = prefs
        self.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )
        self.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )
        self.SetFont( self._prefsIO.GetValue('M_FONT') )

        font = self._prefsIO.GetValue('M_FONT')
        font.SetWeight( wx.BOLD )
        self._title.SetFont( font )
        self._title.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )



    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------

class PluginBitmapButton(wx.BitmapButton):

    def __init__(self, parent, icon, name, command, iparam, types,
                 windows=None, mac=None, unix=None):
        """
        Initialize new PluginBitmapButton instance.
        Parameters:
            - parent (wx.Window)
            - icon (str): file name
            - name (str): tooltip
            - command (str)
            - iparam (str):
                     example '-i'
            - types (list): file types supported by this plugin.
                     example ['csv', 'textgrid', 'eaf', 'tag']
        """
        # Initialize Plugin
        self.plugin = PluginProcess(command, unix, windows, mac, iparam)
        # Initialize BitmapButton
        bitmap = self._createBitmap(icon)
        wx.BitmapButton.__init__(self, parent, id=wx.ID_ANY,
                                 bitmap=bitmap, style=wx.NO_BORDER)
        self.SetToolTipString (name)
        self.timer = wx.Timer(self)
        self.types = types
        self.selection = []

        self.timer.Start(1000)

        # Bind
        self.Bind(wx.EVT_BUTTON, self.OnLoadPlugin)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        self.Bind(wx.EVT_TIMER, self.OnTimer)


    # End __init__
    # ------------------------------------------------------------------------

    def _createBitmap(self, image):
        img = wx.Image(image)
        return img.Scale(30, 30).ConvertToBitmap()

    # End _createBitmap
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------------


    def OnLoadPlugin(self, event):
        if not self.plugin.IsRunning():
            self.selection = []
            for t in self.types:
                self.selection.extend(self.GetTopLevelParent().GetSelected(".%s" % t))

            try:
                self.plugin.Run(inputfiles=self.selection)
            except Exception as e:
                dialog = wx.MessageDialog(self,
                                       message=str(e),
                                       caption="Error",
                                       style=wx.ICON_ERROR)
                dialog.ShowModal()
                dialog.Destroy()

    # End OnLoadPlugin
    # ------------------------------------------------------------------------


    def OnTimer(self, event):
        if not self.selection or self.plugin.IsRunning():
            return
        self.GetTopLevelParent().RefreshTree(self.selection)
        self.selection = []


    def OnDestroy(self, event):
        self.plugin.Terminate()
        self.timer.Stop()

    # End OnDestroy
    # ------------------------------------------------------------------------
