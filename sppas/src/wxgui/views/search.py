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
# File: search.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import wx.lib.newevent as newevent

#import logging
from wxgui.cutils.imageutils import spBitmap
from wxgui.cutils.textutils import TextValidator
from wxgui.cutils.ctrlutils import CreateGenButton

from wxgui.sp_icons  import TIER_SEARCH
from wxgui.sp_icons  import BROOM_ICON
from wxgui.sp_icons  import APP_ICON
from wxgui.sp_icons import BACKWARD_ICON
from wxgui.sp_icons import FORWARD_ICON
from wxgui.sp_icons import CANCEL_ICON

from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE

# ----------------------------------------------------------------------------

DEFAULT_LABEL = 'label1, label2, etc'

SearchedEvent, spEVT_SEARCHED = newevent.NewEvent()
SearchedCommandEvent, spEVT_SEARCHED_COMMAND = newevent.NewCommandEvent()

# ----------------------------------------------------------------------------

class Search( wx.Dialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to display a Search dialog.

    Open a frame to search patterns in a transcription.
    """

    def __init__(self, parent, prefsIO, trs):
        """ Constructor. """
        wx.Dialog.__init__(self, parent, title=FRAME_TITLE+" - Search", style=FRAME_STYLE)

        # Members
        self._trs  = trs
        self._pmin = 0.
        self._pmax = 0.
        self.preferences = prefsIO

        self._create_gui()

    # End __init__
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_gui(self):
        self._init_infos()
        self._create_title_label()
        self._create_content()
        self._create_next_button()
        self._create_previous_button()
        self._create_close_button()
        self._layout_components()
        self._set_focus_component()


    def _init_infos( self ):
        wx.GetApp().SetAppName( "search" )
        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(APP_ICON) )
        self.SetIcon(_icon)
        # colors
        self.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont( self.preferences.GetValue('M_FONT'))


    def _create_title_label(self):
        self.title_layout = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.BitmapButton(self, bitmap=spBitmap(TIER_SEARCH, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label = wx.StaticText(self, label="Search patterns in a tier", style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)
        self.title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)


    def _create_content(self):
        label = wx.StaticText(self, label="Search for:", pos=wx.DefaultPosition, size=wx.DefaultSize)
        label.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        label.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )

        self.text = wx.TextCtrl(self, size=(150, -1), validator=TextValidator())
        self.text.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.text.SetForegroundColour(wx.Colour(128,128,128))
        self.text.SetValue(DEFAULT_LABEL)
        self.text.Bind(wx.EVT_TEXT, self.OnTextChanged)
        self.text.Bind(wx.EVT_SET_FOCUS, self.OnTextClick)

        self.broom = wx.BitmapButton(self, bitmap=spBitmap(BROOM_ICON, 16, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        self.broom.Bind(wx.EVT_BUTTON, self.OnTextErase)

        self.pattern_layout = wx.BoxSizer(wx.HORIZONTAL)
        self.pattern_layout.Add(label, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.pattern_layout.Add(self.text, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        self.pattern_layout.Add(self.broom, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)

        self.tp = TierPanel(self, self._trs)
        self.lp = LabelPanel(self)
        self.sh_layout = wx.BoxSizer(wx.HORIZONTAL)
        self.sh_layout.Add(self.lp, 1, wx.EXPAND|wx.LEFT,  0)
        self.sh_layout.Add(self.tp, 2, wx.EXPAND|wx.RIGHT, 0)


    def _create_previous_button(self):
        bmp = spBitmap(BACKWARD_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_previous = CreateGenButton(self, wx.ID_BACKWARD, bmp, text=" Search backward", tooltip="Search before the current position.", colour=color)
        self.btn_previous.SetFont( self.preferences.GetValue('M_FONT'))
        self.Bind(wx.EVT_BUTTON, self.OnFind, self.btn_previous, wx.ID_BACKWARD)

    def _create_next_button(self):
        bmp = spBitmap(FORWARD_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_next = CreateGenButton(self, wx.ID_FORWARD, bmp, text=" Search forward", tooltip="Search after the current position.", colour=color)
        self.btn_next.SetFont( self.preferences.GetValue('M_FONT'))
        self.Bind(wx.EVT_BUTTON, self.OnFind, self.btn_next, wx.ID_FORWARD)

    def _create_close_button(self):
        bmp = spBitmap(CANCEL_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_close = CreateGenButton(self, wx.ID_CLOSE, bmp, text=" Close", tooltip="Close this frame", colour=color)
        self.btn_close.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_close.SetDefault()
        self.btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)

    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_previous,  flag=wx.LEFT, border=5)
        button_box.Add(self.btn_next,      flag=wx.LEFT, border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_close, flag=wx.RIGHT, border=5)

        return button_box


    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout,   0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.pattern_layout, 0, wx.EXPAND|wx.ALL, border=5)
        vbox.Add(self.sh_layout,      2, flag=wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, border=5)
        vbox.Add(self._create_button_box(), 0, flag=wx.ALL|wx.EXPAND, border=5)
        self.SetMinSize((420,300))
        self.SetSizer( vbox )
        self.Centre()
        self.Enable()
        self.SetAutoLayout(True)
        self.SetFocus()
        self.Layout()
        self.Show(True)


    def _set_focus_component(self):
        self.btn_next.SetFocus()

    #-------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------------

    def OnClose(self, event):
        self.Destroy()


    def OnTextClick(self, event):
        self.text.SetForegroundColour( wx.BLACK )
        if self.text.GetValue() == DEFAULT_LABEL:
            self.OnTextErase(event)
        event.Skip()
        #self.text.SetFocus()


    def OnTextChanged(self, event):
        self.text.SetFocus()
        self.text.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.text.Refresh()


    def OnTextErase(self, event):
        self.text.SetValue('')
        self.text.SetFocus()
        self.text.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.text.Refresh()


    #-------------------------------------------------------------------------
#
#     def SetPeriod(self, pmin, pmax):
#         self._pmin = pmin
#         self._pmax = pmax

    #-------------------------------------------------------------------------


    def OnFind(self, event):
        """
        Search after or before the current position.
        """

        # Firstly, check if a text to find is given!
        success = self.text.GetValidator().Validate(self.text)
        if success is False:
            return

        ruler = self.GetParent()._display.GetRuler()
        self._pmin = ruler.GetSelectionIndicatorMinValue()
        self._pmax = ruler.GetSelectionIndicatorMaxValue()

        # Get search criteria
        criteria  = self.lp.GetCriteria()
        patterns  = self.text.GetValue().split(',')

        # Get search direction
        forward   = True
        direction = 1
        if event.GetId() == wx.ID_BACKWARD:
            forward = False
            direction = -1

        # Convert criteria into "functions"
        function = criteria['function']
        if criteria['case_sensitive'] is False and function != "regexp":
            function = "i"+function

        # Search... On which tier?
        tieridx  = self.tp.GetSelection()
        tier = self._trs[tieridx]
        if forward is True:
            annidx = tier.Near(self._pmax, direction)
        else:
            annidx = tier.Near(self._pmin, direction)

        # Now, can search the next/previous occurrence
        #logging.debug(' Search %s in %s with function %s in forward direction=%d'%(patterns,tier.GetName(),function,forward))
        annidx = tier.Search(patterns,function,annidx,forward,criteria['reverse'])

        # Show the search result
        if annidx == -1:
            self.text.SetForegroundColour(wx.RED)
            #self.text.SetFocus()
            self.text.Refresh()
            #logging.debug(' ... no occurrence. ')
        else:
            self.text.SetForegroundColour( wx.BLACK )
            ann = tier[annidx]
            #logging.debug(' ... success: %s '%ann)
            if ann.GetLocation().IsPoint():
                radius = ann.GetLocation().GetPointRadius()
                s = ann.GetLocation().GetPointMidpoint() - radius
                e = ann.GetLocation().GetPointMidpoint() + radius
            else:
                s = ann.GetLocation().GetBeginMidpoint()
                e = ann.GetLocation().GetEndMidpoint()
                evt = SearchedEvent(start=s,end=e)
                evt.SetEventObject(self)
                wx.PostEvent(self.GetParent(), evt)

    #-------------------------------------------------------------------------



    #-------------------------------------------------------------------------
    # Getters and Setters
    #-------------------------------------------------------------------------


    def SetTranscription(self, trs):
        """ Set a new transcription. """

        if trs != self._trs:
            self._trs = trs
            self.sh.Remove(1)
            self.tp.Destroy()

            self.tp = TierPanel(self, self._trs)
            self.sh.Add(self.tp, 0, wx.ALL|wx.EXPAND, 5)

            self.Layout()
            self.Refresh()

    #-------------------------------------------------------------------------


#-----------------------------------------------------------------------------


class LabelPanel(wx.Panel):
    """ A panel with the search modes. """

    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        #self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        #self.SetBackgroundColour( FRAME_BG_COLOR )

        self.modes = (
                   ("exact", "exact"),
                   ("not exact", "exact"),
                   ("contains", "contains"),
                   ("not contains", "contains"),
                   ("starts with", "startswith"),
                   ("not starts with", "startswith"),
                   ("ends with", "endswith"),
                   ("not ends with", "endswith"),
                   ("match (regexp)", "regexp"),
                   ("not match", "regexp")
                   )

        choices = []
        for choice in self.modes:
            choices.append(choice[0])

        self.radiobox = wx.RadioBox(self, label="Search mode:",
                                    choices=choices, majorDimension=2)
        self.radiobox.SetForegroundColour(wx.Colour(3,3,87))

        self.checkbox = wx.CheckBox(self, label="Case Sensitive")
        self.checkbox.SetValue(True)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.radiobox, 1, wx.EXPAND|wx.ALL, border=2)
        vbox.Add(self.checkbox, 0, wx.EXPAND|wx.ALL, border=2)
        self.SetSizer(vbox)
        self.SetAutoLayout(True)
        self.Layout()


    def GetCriteria(self):
        criteria = {}
        idx = self.radiobox.GetSelection()
        criteria['name']      = self.modes[idx][0]
        criteria['function']  = self.modes[idx][1]
        criteria['case_sensitive'] = self.checkbox.GetValue()
        criteria['reverse']   = idx % 2 != 0
        return criteria


#-----------------------------------------------------------------------------


class TierPanel(wx.Panel):
    """ A panel with the radiolist of tiers of the given transcription. """

    def __init__(self, parent, trs):

        wx.Panel.__init__(self, parent)
        #self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        #self.SetBackgroundColour( FRAME_BG_COLOR )

        choices = []
        for t in trs:
            choices.append( t.GetName() )

        self.radiobox = wx.RadioBox(self, label="Tier:",
                                    choices=choices, majorDimension=1)
        self.radiobox.SetForegroundColour(wx.Colour(87,3,3))
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.radiobox, 1, wx.EXPAND|wx.ALL, border=2)

        self.SetSizer(vbox)
        self.SetAutoLayout(True)
        self.Layout()

    def GetSelection(self):
        return self.radiobox.GetSelection()


#-----------------------------------------------------------------------------
