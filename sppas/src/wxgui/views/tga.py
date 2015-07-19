#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------
# File: tga.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os
import wx
import logging
import os.path

from presenters.tiertga import TierTGA
from utils import fileutils

from wxgui.sp_icons  import STATISTICS_APP_ICON
from wxgui.sp_icons  import TIMEANALYSIS
from wxgui.sp_icons  import CANCEL_ICON
from wxgui.sp_icons  import SAVE_AS_FILE
from wxgui.sp_icons  import BROOM_ICON

from wxgui.sp_consts import TB_ICONSIZE
from wxgui.sp_consts import TB_FONTSIZE

from wxgui.sp_consts import TB_ICONSIZE
from wxgui.sp_consts import TB_FONTSIZE
from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE

from wxgui.cutils.imageutils import spBitmap
from wxgui.cutils.ctrlutils  import CreateGenButton

from wxgui.ui.CustomListCtrl import SortListCtrl
from sp_glob import ICONS_PATH

from descriptivestats import BaseStatPanel

# ----------------------------------------------------------------------------

DEFAULT_SEP = 'sep1, sep2, etc'

# ----------------------------------------------------------------------------

def compare(self, object):
    # Check if it has been modified
    if object.GetValue() == object.string:
        return 1
    else:
        return 0

# ----------------------------------------------------------------------------
# class TGADialog
# ----------------------------------------------------------------------------

class TGADialog( wx.Dialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to display TGA results of tiers.

    Dialog for the user to display and save Time Group Analysis results
    of a set of tiers.

    """

    def __init__(self, parent, prefsIO, tiers={}):
        """
        Create a new dialog.

        @param tiers: a dictionary with key=filename, value=list of selected tiers
        """

        wx.Dialog.__init__(self, parent, title=FRAME_TITLE+" - Time Group Analysis", style=FRAME_STYLE)

        # Members
        self.preferences = prefsIO
        # Options to evaluate stats:
        self.withradius=0

        self._data = {} # to store stats
        for k,v in tiers.items():
            for tier in v:
                ts = TierTGA( tier, self.withradius)
                self._data[ts]=k
                # remark: TGA are not estimated yet.

        self._create_gui()

        # Events of this frame
        wx.EVT_CLOSE(self, self.onClose)

    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_gui(self):
        self._init_infos()
        self._create_title_label()
        self._create_toolbar()
        self._create_content()
        self._create_close_button()
        self._create_save_button()
        self._layout_components()
        self._set_focus_component()


    def _init_infos( self ):
        wx.GetApp().SetAppName( "tga" )
        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(STATISTICS_APP_ICON) )
        self.SetIcon(_icon)
        # colors
        self.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont( self.preferences.GetValue('M_FONT'))


    def _create_title_label(self):
        self.title_layout = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.BitmapButton(self, bitmap=spBitmap(TIMEANALYSIS, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        title_label = wx.StaticText(self, label="Time Group Analysis of a set of tiers", style=wx.ALIGN_CENTER)
        title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.title_layout.Add(title_label, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

    def _create_toolbar(self):
        self.toolbar_layout = wx.BoxSizer(wx.HORIZONTAL)
        font = self.preferences.GetValue('M_FONT')
        sep_label = wx.StaticText(self, label="Time group separators:", style=wx.ALIGN_CENTER)
        sep_label.SetFont( font )
        self.septext = wx.TextCtrl(self, -1)
        self.septext.SetInsertionPoint(0)
        self.septext.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.septext.SetForegroundColour(wx.Colour(128,128,128))
        self.septext.SetValue(DEFAULT_SEP)
        self.septext.Bind(wx.EVT_TEXT, self.OnTextChanged)
        self.septext.Bind(wx.EVT_SET_FOCUS, self.OnTextClick)
        self.septext.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)

        broom = wx.BitmapButton(self, bitmap=spBitmap(BROOM_ICON, 16, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        broom.Bind(wx.EVT_BUTTON, self.OnTextErase)

        font.SetPointSize(font.GetPointSize() - 2)
        durlist = ['Use only Midpoint value', 'Add the Radius value', 'Deduct the Radius value']
        withradiusbox = wx.RadioBox(self, -1, label="Annotation durations:", choices=durlist, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        withradiusbox.SetFont( font )
        self.Bind(wx.EVT_RADIOBOX, self.OnWithRadius, withradiusbox)

        self.toolbar_layout.Add(sep_label,    0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.toolbar_layout.Add(self.septext, 1, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.toolbar_layout.Add(broom, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.toolbar_layout.AddStretchSpacer()
        self.toolbar_layout.Add(withradiusbox, 0, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

    def _create_content(self):
        self.notebook = wx.Notebook(self)

        page1 = SummaryPanel(self.notebook, self.preferences, "summary")
        page2 = TotalPanel(  self.notebook, self.preferences, "total")

        # add the pages to the notebook with the label to show on the tab
        self.notebook.AddPage(page1, "  Summary  " )
        self.notebook.AddPage(page2, "   Total   " )

        page2.ShowStats( self._data )
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChanged)


    def _create_close_button(self):
        bmp = spBitmap(CANCEL_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_close = CreateGenButton(self, wx.ID_OK, bmp, text=" Close", tooltip="Close this frame", colour=color)
        self.btn_close.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_close.SetDefault()
        self.btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_OK)


    def _create_save_button(self):
        bmp = spBitmap(SAVE_AS_FILE, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_save = CreateGenButton(self, wx.ID_SAVE, bmp, text=" Save sheet ", tooltip="Save the currently displayed sheet", colour=color)
        self.btn_save.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_save.SetDefault()
        self.btn_save.SetFocus()


    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        #button_box.Add(self.btn_save,  flag=wx.LEFT, border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_close, flag=wx.RIGHT, border=5)
        self.btn_save.Bind(wx.EVT_BUTTON, self.onButtonSave)
        return button_box


    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout,   0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.toolbar_layout, 1, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.notebook,       2, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self._create_button_box(), 0, flag=wx.ALL|wx.EXPAND, border=5)
        self.SetSizerAndFit(vbox)


    def _set_focus_component(self):
        self.notebook.SetFocus()


    #-------------------------------------------------------------------------
    # Callbacks
    #-------------------------------------------------------------------------

    def onClose(self, event):
        self.SetEscapeId( wx.ID_CANCEL )

    def onButtonSave(self, event):
        page = self.notebook.GetPage( self.notebook.GetSelection() )
        page.SaveAs()

    def OnNotebookPageChanged(self, event):
        oldselection = event.GetOldSelection()
        newselection = event.GetSelection()
        if oldselection != newselection:
            page = self.notebook.GetPage( newselection )
            page.ShowStats( self._data )

    def OnWithRadius(self, event):
        if event.GetSelection()==0:
            if not self.withradius == 0:
                self.withradius = 0
            else:
                return
        elif event.GetSelection()==1:
            if not self.withradius == -1:
                self.withradius = -1
            else:
                return
        elif event.GetSelection()==2:
            if not self.withradius == 1:
                self.withradius = 1
            else:
                return
        # update infos of TierStats objects
        for ts in self._data:
            ts.set_withradius( self.withradius )
        page = self.notebook.GetPage( self.notebook.GetSelection() )
        page.ShowStats( self._data )


    def OnTextClick(self, event):
        self.septext.SetForegroundColour( wx.BLACK )
        if self.septext.GetValue() == DEFAULT_SEP:
            self.OnTextErase(event)
        event.Skip()
        #self.text.SetFocus()

    def OnTextChanged(self, event):
        self.septext.SetFocus()
        self.septext.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.septext.Refresh()

    def OnTextEnter(self, event):
        if self.compare(self.septext):
            return
        seps = self.septext.GetValue().strip().split()
        # update infos of TierTGA objects
        for ts in self._data:
            ts.remove_separators()
            for sep in seps:
                ts.append_separator( sep )
        page = self.notebook.GetPage( self.notebook.GetSelection() )
        page.ShowStats( self._data )

    def OnTextErase(self, event):
        self.septext.SetValue('')
        self.septext.SetFocus()
        self.septext.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.septext.Refresh()

    #-------------------------------------------------------------------------

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Panels
# ----------------------------------------------------------------------------

class SummaryPanel( BaseStatPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: The whole table with TG descriptions.

    """

    def __init__(self, parent, prefsIO, name):
        BaseStatPanel.__init__(self, parent, prefsIO, name)
        self.cols = ('',)

    # ------------------------------------------------------------------------

    def ShowStats(self, data):
        """
        Show descriptive statistics of set of tiers as list.

        """
        #if not data or len(data)==0:
        self.ShowNothing()
        return

        self.statctrl = SortListCtrl(self, size=(-1,400))

        # create columns
        self.cols = ("Labels",) + tuple( os.path.basename(v) for v in data.values() )
        for i,col in enumerate(self.cols):
            self.statctrl.InsertColumn(i,col)
            self.statctrl.SetColumnWidth(i, 120)
        self.statctrl.SetColumnWidth(0, 200)

        # estimates descriptives statistics
        statvalues = []
        for ts in data.keys():
            ds = ts.ds()
            if self.name == "occurrences":
                statvalues.append( ds.len() )
            elif self.name == "total":
                statvalues.append( ds.total() )
            elif self.name == "mean":
                statvalues.append( ds.mean() )
            elif self.name == "median":
                statvalues.append( ds.median() )
            elif self.name == "stdev":
                statvalues.append( ds.stdev() )

        # get the list of labels
        items = ds.len().keys()

        # fill rows
        self.rowdata = []
        for i,item in enumerate(items):
            row = [item] + [ statvalues[i].get(item,0) for i in range(len(statvalues)) ]
            self.rowdata.append(row)
            self.AppendRow(i, row, self.statctrl)

        self.sizer.DeleteWindows()
        self.sizer.Add(self.statctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.FitInside(self)
        self.SendSizeEvent()

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class TotalPanel( BaseStatPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Summary of descriptive stats of all merged-tiers.

    """

    def __init__(self, parent, prefsIO, name):
        BaseStatPanel.__init__(self, parent, prefsIO, name)
        self.cols = ("Label", "Occurrences", "Total durations", "Mean durations", "Median durations", "Std dev. durations")

    # ------------------------------------------------------------------------

    def ShowStats(self, data):
        """
        Show descriptive statistics of set of tiers as list.

        """
        if not data or len(data)==0:
            self.ShowNothing()
            return

        self.statctrl = SortListCtrl(self, size=(-1,400))

        for i,col in enumerate(self.cols):
            self.statctrl.InsertColumn(i,col)
            self.statctrl.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
        self.statctrl.SetColumnWidth(0, 200)

        # create a list of TierTGA
        tabts = self.__get_ts(data)

        # estimates descriptives statistics
        i = 0
        for ts in tabts:
            ds = ts.tga()
            occurrences = ds.len()
            total       = ds.total()
            mean        = ds.mean()
            median      = ds.median()
            stdev       = ds.stdev()

            # fill rows
            self.rowdata = []
            for key in occurrences.keys():
                row = [ key, occurrences[key], total[key], mean[key], median[key], stdev[key] ]
                # add the data content in rowdata
                self.rowdata.append( row )
                # add into the listctrl
                self.AppendRow(i, row, self.statctrl)
                i = i+1

        self.sizer.DeleteWindows()
        self.sizer.Add(self.statctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.FitInside(self)
        self.SendSizeEvent()

    # ------------------------------------------------------------------------

    def __get_ts(self, data):
        TGA=[]
        withradius=0
        for ts in data.keys():
            if not isinstance( ts.tier,list ):
                TGA.append( TierTGA(ts.tier,withradius) )
            else:
                for tier in ts.tier:
                    TGA.append( TierTGA(tier,withradius) )
            # TODO:check if all withradius are the same
            # (it can happen for now, so it's a todo!)
            withradius = ts.get_withradius()
        return TGA

# ----------------------------------------------------------------------------
