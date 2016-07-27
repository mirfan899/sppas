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

from structs.tips import Tips

from wxgui.panels.buttons import ButtonPanel, ButtonMenuPanel, ImgPanel, ButtonCreator
from sp_glob import program, title

from wxgui.sp_icons import ANNOTATIONS_ICON
from wxgui.sp_icons import COMPONENTS_ICON
from wxgui.sp_icons import PLUGIN_ICON
from wxgui.sp_icons import ABOUT_ICON
from wxgui.sp_icons import HELP_ICON
from wxgui.sp_icons import SETTINGS_ICON

from wxgui.sp_icons import EXIT_ICON
from wxgui.sp_icons import BUG_ICON
from wxgui.sp_icons import FEEDBACK_ICON
from wxgui.sp_icons import WEB_ICON
from wxgui.sp_icons import BUG_ICON
from wxgui.sp_icons import BACKWARD_ICON
from wxgui.sp_icons import FORWARD_ICON
from wxgui.sp_icons import CLOSE_ICON

from wxgui.sp_consts import ID_ANNOTATIONS
from wxgui.sp_consts import ID_COMPONENTS
from wxgui.sp_consts import ID_PLUGINS
from wxgui.sp_consts import ID_FEEDBACK
from wxgui.sp_consts import ID_EXT_BUG
from wxgui.sp_consts import ID_EXT_HOME
from wxgui.sp_consts import ID_ACTIONS

from wxgui.sp_consts import MENU_ICONSIZE

# ----------------------------------------------------------------------------

class MainMenuPanel( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Main frame menu panel.

    """
    def __init__(self, parent, preferences):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BGM_COLOUR') )

        exitButton     = ButtonMenuPanel(self, wx.ID_EXIT,  preferences, EXIT_ICON, None)
        bugButton      = ButtonMenuPanel(self, ID_EXT_BUG,  preferences, BUG_ICON, None)
        feedbackButton = ButtonMenuPanel(self, ID_FEEDBACK, preferences, FEEDBACK_ICON, None)

        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( exitButton, proportion=0, flag=wx.ALL, border=2)
        sizer.AddStretchSpacer(2)
        sizer.Add( bugButton,  proportion=0, flag=wx.ALL, border=2)
        sizer.Add( feedbackButton, proportion=0, flag=wx.ALL, border=2)

        self.SetSizer( sizer )
        self.SetMinSize((MENU_ICONSIZE+4, -1))
        self.Bind( wx.EVT_BUTTON, self.OnButtonClick )

    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):
        obj = evt.GetEventObject()
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, obj.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

class MainTitlePanel( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Main frame buttons panel.

    """
    def __init__(self, parent, preferences):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BGD_COLOUR') )

        font = preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)

        s = wx.BoxSizer()
        text = wx.StaticText(self, label=program+" - "+title, style=wx.ALIGN_CENTER)
        text.SetFont( font )
        text.SetForegroundColour( preferences.GetValue('M_FONT_COLOUR') )
        text.Bind(wx.EVT_LEFT_UP, self.OnButtonClick)
        s.Add(text, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=10)

        self.SetSizer(s)
        self.SetMinSize((-1,MENU_ICONSIZE+4))

        self.Bind(wx.EVT_LEFT_UP, self.OnButtonClick)

    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, ID_EXT_HOME)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ----------------------------------------------------------------------------

class MainActionsPanel( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Main frame buttons panel.

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

        annotateButton = ButtonPanel(self, ID_ANNOTATIONS,   self._prefs, ANNOTATIONS_ICON,"Annotate", "Segment speech, normalize text, ...")
        analyzeButton  = ButtonPanel(self, ID_COMPONENTS,    self._prefs, COMPONENTS_ICON, "Analyze",  "Statistics, data managers, ...")
        pluginsButton  = ButtonPanel(self, ID_PLUGINS,       self._prefs, PLUGIN_ICON,     "Plugins",  "External tools")
        settingsButton = ButtonPanel(self, wx.ID_PREFERENCES,self._prefs, SETTINGS_ICON,   "Settings", "Configuration, preferences")
        helpButton     = ButtonPanel(self, wx.ID_HELP,       self._prefs, HELP_ICON,       "Help",     "Documentation")
        aboutButton    = ButtonPanel(self, wx.ID_ABOUT,      self._prefs, ABOUT_ICON,      "About",    "Know more, give feedback, ...")

        _box = wx.GridBagSizer()
        _box.Add( annotateButton, pos=(0, 0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
        _box.Add( pluginsButton,  pos=(1, 1), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
        _box.Add( analyzeButton,  pos=(0, 1), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
        _box.Add( settingsButton, pos=(1, 0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
        _box.Add( aboutButton,    pos=(2, 0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
        _box.Add( helpButton,     pos=(2, 1), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)

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

class MainActionsMenuPanel( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Main actions menu panel.

    """
    def __init__(self, parent, preferences, icon=BACKWARD_ICON):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BGM_COLOUR') )
        self._prefs = preferences

        self.backButton = ImgPanel(self, MENU_ICONSIZE, icon)
        font = preferences.GetValue('M_FONT')

        self.text = wx.TextCtrl( self, -1, style=wx.NO_BORDER )
        self.text.SetEditable(False)
        font.SetWeight( wx.BOLD )
        self.text.SetFont( font )
        self.text.SetBackgroundColour( self.GetBackgroundColour() )
        self.text.SetForegroundColour( preferences.GetValue('M_FONTM_COLOUR') )

        sizer = wx.BoxSizer( wx.HORIZONTAL )
        sizer.Add( self.backButton, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTRE_VERTICAL, border=2)
        sizer.Add( self.text, proportion=1, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTRE_VERTICAL, border=0)
        self.SetSizer( sizer )
        self.SetMinSize((-1, MENU_ICONSIZE+4))

        self.Bind(wx.EVT_LEFT_UP, self.OnButtonClick)

    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, ID_ACTIONS)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def ShowBack(self, state=True, text=""):
        self.text.SetValue(text)
        if state is True:
            self.backButton.Show()
        else:
            self.backButton.Hide()
        self.Refresh()

    # -----------------------------------------------------------------------

# ----------------------------------------------------------------------------

class MainTooltips( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Main tooltips panel.

    """
    def __init__(self, parent, preferences):
        wx.Panel.__init__(self, parent, -1, style=wx.RAISED_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BGD_COLOUR') )
        self._prefs = preferences
        self.tips = Tips()

        menu   = self._create_menu()
        self.text = self._create_content()
        button = self._create_button()

        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( menu, proportion=0, flag=wx.EXPAND, border=0 )
        sizer.Add( self.text, proportion=2, flag=wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, border=10 )
        sizer.Add( button, proportion=0, flag=wx.ALIGN_CENTER, border=0 )
        self.SetSizerAndFit( sizer )

        self.Bind(wx.EVT_BUTTON, self.OnClose)

    # -----------------------------------------------------------------------

    def _create_menu(self):
        return MainActionsMenuPanel(self, self._prefs, icon=CLOSE_ICON)

    def _create_content(self):
        txt = wx.TextCtrl(self, wx.ID_ANY, value=self.tips.get(), style=wx.TE_READONLY|wx.TE_MULTILINE|wx.NO_BORDER)
        font = self._prefs.GetValue('M_FONT')
        txt.SetFont(font)
        txt.SetForegroundColour( self._prefs.GetValue('M_FG_COLOUR') )
        txt.SetBackgroundColour( self._prefs.GetValue('M_BGD_COLOUR') )
        txt.SetMinSize((300,48))
        return txt

    def _create_button(self):
        btncreator = ButtonCreator(self._prefs)
        btn = btncreator.CreateButton(self, FORWARD_ICON, " Next tip", "Show a random tip", wx.NewId())
        btn.SetBackgroundColour( self._prefs.GetValue('M_BG_COLOUR') )
        btn.Bind(wx.EVT_BUTTON, self.OnNext)
        return btn

    # -----------------------------------------------------------------------

    def OnClose(self, event):
        self.Hide()
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, ID_ACTIONS)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def OnNext(self, event):
        self.text.SetValue( self.tips.get() )
        self.Refresh()

    # -----------------------------------------------------------------------
