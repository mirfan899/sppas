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
# File: annotationoptions.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi, Cazembe Henry"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
from os.path import *

import re
import wx
import wx.lib.agw.floatspin
import wx.lib.scrolledpanel as scrolled

from wxgui.sp_icons import APP_ICON
from wxgui.sp_icons import ANNOTATE_CONFIG_ICON
from wxgui.sp_icons import APPLY_ICON
from wxgui.sp_icons import CANCEL_ICON
from wxgui.sp_icons import RESTORE_ICON

from wxgui.cutils.imageutils import spBitmap
from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE
from wxgui.cutils.ctrlutils import CreateGenButton

# ----------------------------------------------------------------------------

ID_RESTORE = wx.NewId()

# ----------------------------------------------------------------------------

class optionsPanel( scrolled.ScrolledPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Create dynamically a panel depending on a list of options.

    """

    def __init__(self, parent, options):
        """
        Constructor.

        @param options (list) List of options (see param.py).

        """
        scrolled.ScrolledPanel.__init__(self, parent, -1, size=(400,300), style=wx.NO_BORDER)

        self.option_sizer = wx.BoxSizer(wx.VERTICAL)

        # item list
        self.items = []

        # Adding options
        for opt in options:

            if opt.get_type() == bool:
                self.AddCheckbox( opt.get_text(), value=opt.get_value() )

            elif opt.get_type() == int:
                self.AddIntSpinner( opt.get_text(), value=opt.get_value() )

            elif opt.get_type() == float:
                self.AddFloatSpinner( opt.get_text(), value=opt.get_value() )

            elif opt.get_type() == unicode:
                self.AddTextctrl( opt.get_text(), value=opt.get_value() )

        self.SetSizer(self.option_sizer)
        self.SetupScrolling()


    def AddIntSpinner(self, label, smin=0, smax=2000, value=1, width=130):
        """
        Add a spinner to the panel.

        @param  label (String)
        @param  smin is the minimum value
        @param  smax is the maximum value
        @param  value is the current value

        """
        st = wx.StaticText(self, -1, label)

        sc = wx.SpinCtrl(self, -1, label, (30, 20), (width, -1))
        sc.SetRange(smin, smax)
        sc.SetValue(value)

        self.option_sizer.Add(st, 0, wx.LEFT, 3)
        self.option_sizer.Add(sc, 0, wx.BOTTOM, 8)

        self.items.append(sc)


    def AddFloatSpinner(self, label, smin=0, smax=2000, incr=0.01, value=1.0, width=130):
        """
        Add a float spinner to the panel.

        @param label (String)
        @param smin is the minimum value
        @param smax is the maximum value
        @param incr is increment for every evt_floatspin events
        @param value is the current value

        """
        st = wx.StaticText(self, -1, label)

        fsc = wx.lib.agw.floatspin.FloatSpin(self, -1, size=(width, -1), increment=incr, digits=3)
        fsc.SetRange(smin, smax)
        fsc.SetValue(value)
        self.option_sizer.Add(st, 0, wx.LEFT, 3)
        self.option_sizer.Add(fsc, 0, wx.BOTTOM, 8)

        self.items.append(fsc)


    def AddCheckbox(self, label, value=True):
        """
        Add a checkbox to the panel.

        @param label
        @param value is the current value

        """
        cb = wx.CheckBox(self, -1, label)
        cb.SetValue(value)
        self.option_sizer.Add(cb, 0, wx.BOTTOM, 8)

        self.items.append(cb)


    def AddTextctrl(self, label, value=""):
        """
        Add a TextCtrl to the panel.

        @param label
        @param value is the current value

        """
        st = wx.StaticText(self, -1, label)
        textctrl = wx.TextCtrl(self, -1, size=(300, -1))
        textctrl.SetValue(value)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(textctrl)

        self.option_sizer.Add(st, 0, wx.BOTTOM, 8)
        self.option_sizer.Add(sizer, 0, wx.BOTTOM, 8)

        self.items.append(textctrl)


    def GetItems(self):
        return self.items


# ----------------------------------------------------------------------------


class spAnnotationConfig( wx.Frame ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Frame allowing to configure the annotation' options.
    Parent must be a sppasFrame.

    """

    def __init__(self, parent, preferences, step, stepidx):
        """
        Constructor.

        @param parent is the sppas main frame

        """
        wx.Frame.__init__(self, parent, -1,  title=FRAME_TITLE+" - Options", style=FRAME_STYLE)

        self.step        = step
        self.stepid      = stepidx

        self.preferences = preferences
        self._create_gui()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    # End __init__
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------


    def _create_gui(self):
        self._init_infos()
        self._create_title_label()
        self._create_options()
        self._create_restore_button()
        self._create_cancel_button()
        self._create_close_button()
        self._layout_components()
        self._set_focus_component()


    def _init_infos( self ):
        wx.GetApp().SetAppName( "option"+str(self.stepid) )
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
        bmp = wx.BitmapButton(self, bitmap=spBitmap(ANNOTATE_CONFIG_ICON, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        text = self.GetParent().parameters.get_step_name(self.stepid)+" Configuration"
        self.title_label = wx.StaticText(self, label=text, style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)
        self.title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)


    def _create_options(self):
        self.options_panel = optionsPanel(self, self.step.get_options())
        self.options_panel.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        self.options_panel.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        self.options_panel.SetFont( self.preferences.GetValue('M_FONT') )
        self.items = self.options_panel.GetItems()


    def _create_restore_button(self):
        bmp = spBitmap(RESTORE_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        self.btn_restore = CreateGenButton(self, ID_RESTORE, bmp, text=" Restore defaults", tooltip="Reset options to their default values", colour=None)
        self.btn_restore.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        self.btn_restore.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        self.btn_restore.SetFont( self.preferences.GetValue('M_FONT') )
        self.Bind(wx.EVT_BUTTON, self.on_restore, self.btn_restore, ID_RESTORE)


    def _create_cancel_button(self):
        bmp = spBitmap(CANCEL_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        self.btn_cancel = CreateGenButton(self, wx.ID_CANCEL, bmp, text=" Cancel", tooltip="Reset options to their default values", colour=None)
        self.btn_cancel.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        self.btn_cancel.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        self.btn_restore.SetFont( self.preferences.GetValue('M_FONT') )
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.btn_cancel, wx.ID_CANCEL)


    def _create_close_button(self):
        bmp = spBitmap(APPLY_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        self.btn_close = CreateGenButton(self, wx.ID_CLOSE, bmp, text=" Close", tooltip="Close this frame", colour=None)
        self.btn_close.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        self.btn_close.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        self.btn_close.SetFont( self.preferences.GetValue('M_FONT') )
        self.btn_close.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.on_close, self.btn_close, wx.ID_CLOSE)


    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout,  flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.options_panel, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self._create_button_box(), flag=wx.EXPAND, border=5)
        self.SetSizerAndFit(vbox)
        self.Show(True)


    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_restore, flag=wx.RIGHT, border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_cancel, flag=wx.CENTRE, border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_close, flag=wx.LEFT, border=5)
        return button_box


    def _set_focus_component(self):
        self.btn_close.SetFocus()

    # -----------------------------------------------------------------------

    def on_close(self, evt):
        # Save options
        for i in range( len( self.step.get_options() ) ):
            self.step.get_option(i).set_value(self.items[i].GetValue())
        self.GetParent().Update()
        self.GetParent().Refresh()
        del self.GetParent().opened_frames[self.GetParent().ID_FRAME_ANNOTATION_CFG+self.stepid]
        self.Destroy()

    def on_restore(self, evt):
        #restore options in the frame using the parameters
        for i in range(len( self.step.get_options() )):
            self.items[i].SetValue( self.step.get_option(i).get_value() )

    def on_cancel(self, evt):
        del self.GetParent().opened_frames[self.GetParent().ID_FRAME_ANNOTATION_CFG+self.stepid]
        self.Destroy()

    # -----------------------------------------------------------------------
