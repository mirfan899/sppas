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
# File: mainbuttons.py
# ----------------------------------------------------------------------------

import wx

from wxgui.panels.buttons import ButtonPanel

from wxgui.sp_icons import ANNOTATIONS_ICON
from wxgui.sp_icons import COMPONENTS_ICON
from wxgui.sp_icons import PLUGIN_ICON
from wxgui.sp_icons import ABOUT_ICON
from wxgui.sp_icons import HELP_ICON
from wxgui.sp_icons import SETTINGS_ICON

from wxgui.views.about        import AboutBox
from wxgui.views.settings     import SettingsDialog
from wxgui.frames.helpbrowser import HelpBrowser

# ----------------------------------------------------------------------------

ID_ANNOTATE   = wx.NewId()
ID_COMPONENTS = wx.NewId()
ID_PLUGINS    = wx.NewId()

# ----------------------------------------------------------------------------

class MainButtonsPanel( wx.Panel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Main frame buttons panel.

    """
    def __init__(self, parent, preferences):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BG_COLOUR') )
        self._prefs = preferences

        content = self.__create_buttons()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(content, proportion=1, flag=wx.EXPAND | wx.ALL, border=0)

        self.Bind(wx.EVT_BUTTON, self.OnButtonClick)
        self.SetSizerAndFit(sizer)


    def __create_buttons(self):
        """ Create buttons to call tools. """

        annotateButton = ButtonPanel(self, ID_ANNOTATE,      self._prefs, ANNOTATIONS_ICON,"Annotate", "Segment speech, normalize text, ...")
        analyzeButton  = ButtonPanel(self, ID_COMPONENTS,    self._prefs, COMPONENTS_ICON, "Analyze",  "Statistics, data managers, ...")
        pluginsButton  = ButtonPanel(self, ID_PLUGINS,       self._prefs, PLUGIN_ICON,     "Plugins",  "External tools")
        settingsButton = ButtonPanel(self, wx.ID_PREFERENCES,self._prefs, SETTINGS_ICON,   "Settings", "Configuration, preferences")
        helpButton     = ButtonPanel(self, wx.ID_HELP,       self._prefs, HELP_ICON,       "Help",     "Documentation")
        aboutButton    = ButtonPanel(self, wx.ID_ABOUT,      self._prefs, ABOUT_ICON,      "About",    "Know more, give feedback, ...")

        _box = wx.GridBagSizer()
        _box.Add( annotateButton, pos=(0, 0), flag=wx.ALL, border=2)
        _box.Add( pluginsButton,  pos=(1, 1), flag=wx.ALL, border=2)
        _box.Add( analyzeButton,  pos=(0, 1), flag=wx.ALL, border=2)
        _box.Add( settingsButton, pos=(1, 0), flag=wx.ALL, border=2)
        _box.Add( aboutButton,    pos=(2, 0), flag=wx.ALL, border=2)
        _box.Add( helpButton,     pos=(2, 1), flag=wx.ALL, border=2)

        _box.AddGrowableCol(0)
        _box.AddGrowableCol(1)
        _box.AddGrowableRow(0)
        _box.AddGrowableRow(1)
        _box.AddGrowableRow(2)

        return _box

    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):
        obj = evt.GetEventObject()
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, obj.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------

