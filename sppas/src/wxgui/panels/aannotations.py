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
# File: aannotations.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi, Cazembe Henry"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import wx.lib.newevent
import wx.lib.scrolledpanel
import functools

from annotations.param import sppasParam

from wxgui.cutils.imageutils       import spBitmap
from wxgui.cutils.ctrlutils        import CreateGenButton
from wxgui.views.annotationoptions import spAnnotationConfig
from wxgui.process.annotateprocess import AnnotateProcess

from wxgui.sp_consts import MIN_PANEL_W
from wxgui.sp_consts import MIN_PANEL_H
from wxgui.sp_consts import BUTTON_ICONSIZE

from wxgui.sp_icons import LINK_ICON
from wxgui.sp_icons import UNLINK_ICON
from wxgui.sp_icons import ANNOTATE_ICON
import wxgui.ui.CustomCheckBox as CCB


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

LANG_NONE = "---"

RUN_ID  = wx.NewId()
LINK_ID = wx.NewId()


# ----------------------------------------------------------------------------
# Events
# ----------------------------------------------------------------------------

#event launched when a step is checked or unchecked
stepEvent, EVT_STEP_EVENT = wx.lib.newevent.NewEvent()

#event launched when a language is chosen
langEvent, EVT_LANG_EVENT = wx.lib.newevent.NewEvent()


# ----------------------------------------------------------------------------
# class sppasStepPanel
# ----------------------------------------------------------------------------

class sppasStepPanel( wx.Panel ):
    """
    @author:  Cazembe Henry, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Panel with an annotation and the language choice.

    Panel containing a checkbox and eventually a choice of languages for a
    given annotation.

    """
    def __init__(self, parent, parameters, preferences, index):

        wx.Panel.__init__(self, parent, size=wx.DefaultSize, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))

        # Members
        self.parameters  = parameters
        self.step_idx    = index
        self._prefsIO    = preferences
        choicelist       = self.parameters.get_langlist(index)
        self.choice      = None
        self.opened_frames = {}
        self.ID_FRAME_ANNOTATION_CFG = wx.NewId()

        step_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #create the checkbox allowing to select or unselect the step
        self.checkbox = CCB.CustomCheckBox(self, -1, self.parameters.get_step_name(index), CCB_TYPE="activecheck")
        self.checkbox.SetFont( self._prefsIO.GetValue( 'M_FONT'))
        self.checkbox.SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ))
        self.checkbox.SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ))
        self.checkbox.SetSpacing( self._prefsIO.GetValue( 'F_SPACING' ))

        self.checkbox.Bind(wx.EVT_CHECKBOX, functools.partial(self.on_check_changed, step_idx=index))
        step_sizer.Add(self.checkbox, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 8)

        #create the panel allowing to show configuration panel
        self.choice = None
        #if there are different languages available, add a choice to the panel
        if len(choicelist) > 0:
            choicelist.append( LANG_NONE )
            self.choice = wx.Choice(self, -1, choices = sorted(choicelist))
            self.choice.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )
            self.choice.SetForegroundColour( self._prefsIO.GetValue('M_FGD_COLOUR') )
            self.choice.SetFont( self._prefsIO.GetValue('M_FONT') )

            self.choice.SetSelection(self.choice.GetItems().index( LANG_NONE ))
            self.choice.Bind(wx.EVT_CHOICE, functools.partial(self.on_lang_changed, step_idx=index))
            step_sizer.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), proportion=1, flag=wx.ALIGN_CENTER_VERTICAL |wx.LEFT|wx.RIGHT, border=4)
            step_sizer.Add(self.choice, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)#, wx.ALIGN_RIGHT)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.text = wx.StaticText(self, -1, self.parameters.get_step_descr(index))
        self.text.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR'))
        self.text.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR'))
        self.text.SetFont( self._prefsIO.GetValue('M_FONT') )
        self.text.Wrap( 400 )

        self.link = wx.StaticText(self, -1, "Configure...")
        self.link.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR'))
        self.link.SetForegroundColour( wx.Colour(40,40,190) )
        self.link.SetFont( self._prefsIO.GetValue('M_FONT') )
        self.link.Bind(wx.EVT_LEFT_UP, self.on_click)

        sizer.Add(step_sizer, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer.Add(self.text,  0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer.Add(self.link,  0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.SetSizerAndFit(sizer)


    def on_check_changed(self, evt, step_idx):
        if hasattr(evt, 'IsChecked'):
            checked = evt.IsChecked()
        else:
            checked = True
        #create the a step event
        event = stepEvent(step_idx=step_idx, checked=checked)
        #post the event
        wx.PostEvent(self, event)


    def on_click(self, event):
        self.on_check_changed(event, self.step_idx)
        self.checkbox.SetValue(True)
        annotId = self.step_idx
        frameId = self.ID_FRAME_ANNOTATION_CFG + annotId
        if frameId not in self.opened_frames.keys():
            dlg = spAnnotationConfig(self, self._prefsIO, self.parameters.annotations[annotId], annotId)
            dlg.Show()
            self.opened_frames[frameId] = dlg
        else:
            self.opened_frames[frameId].SetFocus()
            self.opened_frames[frameId].Raise()

    def on_lang_changed(self, evt, step_idx):
        #create the a step event
        event = langEvent(step_idx=step_idx, lang=evt.GetString())
        #post the event
        wx.PostEvent(self, event)


    def set_lang(self, lang):
        if self.choice != None:
                if lang in self.choice.GetItems():
                    #select the language in parameter
                    self.choice.SetSelection(self.choice.GetItems().index(lang))
                else:
                    #empty the selection
                    self.choice.SetSelection(self.choice.GetItems().index( LANG_NONE ))
                    self.parameters.set_lang(None, self.step_idx)
                self.parameters.set_lang(lang, self.step_idx)


    def SetPrefs(self, prefs):
        """
        Fix new preferences.
        """
        self._prefsIO = prefs
        self.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )
        self.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )
        self.SetFont( self._prefsIO.GetValue('M_FONT') )

        self.checkbox.SetFont( self._prefsIO.GetValue( 'M_FONT'))
        self.checkbox.SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ))
        self.checkbox.SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ))
        self.text.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR'))
        self.text.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR'))
        self.text.SetFont( self._prefsIO.GetValue('M_FONT') )

        if self.choice:
            self.choice.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )
            self.choice.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )
            self.choice.SetFont( self._prefsIO.GetValue('M_FONT') )
            self.choice.Refresh()

        self.Refresh()



# ----------------------------------------------------------------------------
# class AnnotationPanel
# ----------------------------------------------------------------------------

class AnnotationsPanel( wx.lib.scrolledpanel.ScrolledPanel ):
    """
    @author:  Cazembe Henry, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Panel allowing to select annotations and languages.

    """

    def __init__(self, parent, preferences):
        """
        Constructor.
        """
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, size=wx.DefaultSize, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))

        # Members
        self.activated = []
        self.step_panels = []
        self.linked = False
        self.parameters  = sppasParam()
        self._prefsIO = preferences
        self.parameters.set_output_format( self._prefsIO.GetValue('M_OUTPUT_EXT') )

        _contentbox = self.__create_content()

        # Button to annotate
        runBmp = spBitmap(ANNOTATE_ICON, BUTTON_ICONSIZE, self._prefsIO.GetValue('M_ICON_THEME'))
        self._brun = CreateGenButton(self, RUN_ID, runBmp, text="  Perform annotations  ", tooltip="Automatically annotate selected files.", colour=wx.Colour(220,100,80), SIZE=BUTTON_ICONSIZE, font=self._prefsIO.GetValue('M_FONT'))

        _vbox = wx.BoxSizer(wx.VERTICAL)
        _vbox.Add(_contentbox, proportion=2, flag=wx.EXPAND | wx.ALL, border=4)
        _vbox.Add(self._brun, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=20)

        self.Bind(wx.EVT_BUTTON, self.on_sppas_run, self._brun, RUN_ID)
        self.SetSizer(_vbox)
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.SetMinSize(wx.Size(MIN_PANEL_W,MIN_PANEL_H))


    def __create_content(self):
        """ Annotation and language choices."""
        _box = wx.BoxSizer(wx.HORIZONTAL)

        self.steplist_panel = wx.Panel(self)
        self.steplist_panel.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        sbox = wx.BoxSizer(wx.VERTICAL)
        for i in range( len(self.parameters.get_steplist()) ):
            p = sppasStepPanel( self.steplist_panel, self.parameters, self._prefsIO, i )
            p.Bind(EVT_STEP_EVENT, self.on_check_changed)
            p.Bind(EVT_LANG_EVENT, self.on_lang_changed)
            self.step_panels.append( p )
            self.activated.append(False)
            sbox.Add(p, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 1)
        self.steplist_panel.SetSizer(sbox)

        self.link_btn = CreateGenButton(self, LINK_ID, spBitmap(LINK_ICON, theme=self._prefsIO.GetValue('M_ICON_THEME')), tooltip="Link/Unlink language selection.", colour=self._prefsIO.GetValue('M_BG_COLOUR'), SIZE=16)
        self.Bind(wx.EVT_BUTTON, self.on_link, self.link_btn, LINK_ID)
        self.on_link(None)

        _box.Add(self.steplist_panel, 1, wx.EXPAND |wx.TOP, 2)
        _box.Add(self.link_btn, 0, wx.LEFT|wx.EXPAND, 4)
        return _box


    def on_link(self, evt):
        self.linked = not self.linked
        if self.linked:
            b=spBitmap(LINK_ICON, size=24, theme=self._prefsIO.GetValue('M_ICON_THEME'))
        else:
            b=spBitmap(UNLINK_ICON, size=24, theme=self._prefsIO.GetValue('M_ICON_THEME'))
        self.link_btn.SetBitmapLabel(b)


    def on_check_changed(self, evt):
        index = evt.step_idx
        self.activated[index] = evt.checked


    def on_lang_changed(self, evt):

        if evt.lang == LANG_NONE:
            l = None
        else:
            l = evt.lang

        if self.linked:
            for sp in self.step_panels:
                sp.set_lang(l)
        else:
            self.parameters.set_lang(l, evt.step_idx)


    def on_sppas_run(self, evt):
        """
        Execute the automatic annotations.
        """

        #self.GetTopLevelParent().annotate(self.activated)
        filelist = self.GetTopLevelParent().GetAudioSelection()
        self.annprocess = AnnotateProcess( self._prefsIO)
        self.annprocess.Run(self.GetParent(), filelist, self.activated, self.parameters)


    def SetPrefs(self, prefs):
        """
        Fix new preferences.
        """
        self._prefsIO = prefs
        self.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )
        self.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )
        self.SetFont( self._prefsIO.GetValue('M_FONT') )

        self._brun.SetFont( self._prefsIO.GetValue('M_FONT') )
        self.link_btn.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )

        self.steplist_panel.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        for sp in self.step_panels:
            sp.SetPrefs( prefs )

        self.parameters.set_output_format( self._prefsIO.GetValue('M_OUTPUT_EXT') )

# ----------------------------------------------------------------------------
