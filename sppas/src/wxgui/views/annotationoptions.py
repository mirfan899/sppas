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
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import wx.lib.agw.floatspin
import wx.lib.scrolledpanel as scrolled

from wxgui.dialogs.basedialog import spBaseDialog

from wxgui.sp_icons import ANNOTATE_CONFIG_ICON
from wxgui.sp_icons import RESTORE_ICON

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

    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------

    def GetItems(self):
        return self.items

# ----------------------------------------------------------------------------

class spAnnotationConfig( spBaseDialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Dialog to configure the automatic annotation options.

    Parent must be a sppasFrame.

    """

    def __init__(self, parent, preferences, step, stepidx):
        """
        Constructor.

        @param parent must be the sppas main frame

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Options")
        wx.GetApp().SetAppName( "option"+str(stepidx) )

        self.step        = step
        self.stepid      = stepidx
        self.preferences = preferences

        titlebox   = self._create_title()
        contentbox = self._create_content()
        buttonbox  = self._create_buttons()

        self.LayoutComponents( titlebox,
                               contentbox,
                               buttonbox )

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_title(self):
        text = self.GetParent().parameters.get_step_name(self.stepid)+" Configuration"
        return self.CreateTitle(ANNOTATE_CONFIG_ICON, text)

    def _create_content(self):
        options_panel = optionsPanel(self, self.step.get_options())
        options_panel.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        options_panel.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        options_panel.SetFont( self.preferences.GetValue('M_FONT') )
        self.items = options_panel.GetItems()
        return options_panel

    def _create_buttons(self):
        btn_restore = self.CreateButton( RESTORE_ICON, " Restore defaults ", "Reset options to their default values" )
        btn_cancel  = self.CreateCancelButton()
        btn_okay    = self.CreateOkayButton()
        self.Bind(wx.EVT_BUTTON, self._on_restore, btn_restore)
        self.Bind(wx.EVT_BUTTON, self._on_cancel, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self._on_okay, btn_okay)
        return self.CreateButtonBox( [btn_restore],[btn_cancel,btn_okay] )

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _on_okay(self, evt):
        # Save options
        for i in range( len( self.step.get_options() ) ):
            self.step.get_option(i).set_value(self.items[i].GetValue())
        self.GetParent().Update()
        self.GetParent().Refresh()
        del self.GetParent().opened_frames[self.GetParent().ID_FRAME_ANNOTATION_CFG+self.stepid]
        self.Destroy()

    def _on_restore(self, evt):
        #restore options in the frame using the parameters
        for i in range(len( self.step.get_options() )):
            self.items[i].SetValue( self.step.get_option(i).get_value() )

    def _on_cancel(self, evt):
        del self.GetParent().opened_frames[self.GetParent().ID_FRAME_ANNOTATION_CFG+self.stepid]
        self.Destroy()

# ----------------------------------------------------------------------------
