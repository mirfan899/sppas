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
# File: descriptivestats.py
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

from annotationdata.utils.tierstats import TierStats
from utils import fileutils

from wxgui.sp_icons import STATISTICS_APP_ICON
from wxgui.sp_icons import SPREADSHEETS
from wxgui.sp_icons import CANCEL_ICON
from wxgui.sp_icons import SAVE_AS_FILE
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


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# class DescriptivesStatsDialog
# ----------------------------------------------------------------------------

class DescriptivesStatsDialog( wx.Dialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to display descriptives stats of tiers.

    Dialog for the user to display and save various descriptive statistics
    of a set of tiers.

    """

    def __init__(self, parent, prefsIO, filemanager):
        """
        Create a new dialog.

        """

        wx.Dialog.__init__(self, parent, title=FRAME_TITLE+" - Descriptives Statistics", style=FRAME_STYLE)

        # Members
        self.preferences = prefsIO
        self._data = {}
        # Options to evaluate stats:
        self.n=1
        self.withradius=0
        self.withalt=False

        self._create_tierstats( filemanager )
        self._create_gui()

        # Events of this frame
        wx.EVT_CLOSE(self, self.onClose)

    # End __init__
    # ------------------------------------------------------------------------

    def _create_tierstats(self, filemanager):
        self._data = {}
        for i in range(filemanager.GetSize()):
            # obj is a TrsList instance
            obj = filemanager.GetObject(i)
            trs = obj.GetTranscription()
            for tier in trs:
                logging.debug(' ... ... tier %s...'%tier.GetName())
                if obj.IsSelected(tier.GetName()):
                    logging.debug(' ... ... is added to the selection')
                    ts = TierStats( tier, self.n, self.withradius, self.withalt )
                    self._data[ts]=filemanager.GetFilename(i)
                    # remark: statistics are not estimated yet.

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
        wx.GetApp().SetAppName( "descriptivesstats" )
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
        bmp = wx.BitmapButton(self, bitmap=spBitmap(SPREADSHEETS, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label = wx.StaticText(self, label="Descriptives Statistics of a set of tiers", style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)


    def _create_toolbar(self):
        iconSize = (TB_ICONSIZE, TB_ICONSIZE)
        self.toolbar = wx.ToolBar( self, -1, style=wx.TB_TEXT )
        self.toolbar.SetToolBitmapSize(iconSize)
        self.toolbar.SetFont( self.preferences.GetValue('M_FONT') )

        self.toolbar.AddControl(wx.StaticText(self.toolbar, label="N-gram:"))
        self.ngrambox = wx.ComboBox(self.toolbar, -1, choices=['1','2','3','4','5'], style=wx.CB_READONLY)
        self.ngrambox.SetSelection(0)
        self.toolbar.AddControl(self.ngrambox)
        self.toolbar.Bind( wx.EVT_COMBOBOX, self.OnNgram, self.ngrambox )
        self.toolbar.AddStretchableSpace()

        lablist = ['Use only the label with the best score', 'Include also alternative labels']
        self.withaltbox = wx.RadioBox(self.toolbar, -1, label="Annotation labels:", choices=lablist, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.toolbar.AddControl(self.withaltbox)
        self.toolbar.Bind(wx.EVT_RADIOBOX, self.OnWithAlt, self.withaltbox)

        durlist = ['Use only Midpoint value', 'Add the radius value', 'Deduct the radius value']
        self.withradiusbox = wx.RadioBox(self.toolbar, -1, label="Annotation durations:", choices=durlist, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.toolbar.AddControl(self.withradiusbox)
        self.toolbar.Bind(wx.EVT_RADIOBOX, self.OnWithRadius, self.withradiusbox)

        self.toolbar.Realize()


    def _create_content(self):
        self.notebook = wx.Notebook(self)

        page1 = SummaryPanel(self.notebook,  self.preferences, "summary")
        page2 = DetailedPanel(self.notebook, self.preferences, "occurrences")
        page3 = DetailedPanel(self.notebook, self.preferences, "total")
        page4 = DetailedPanel(self.notebook, self.preferences, "mean")
        page5 = DetailedPanel(self.notebook, self.preferences, "median")
        page6 = DetailedPanel(self.notebook, self.preferences, "stdev")

        # add the pages to the notebook with the label to show on the tab
        self.notebook.AddPage(page1, "   Summary   " )
        self.notebook.AddPage(page2, " Occurrences " )
        self.notebook.AddPage(page3, "Total durations"  )
        self.notebook.AddPage(page4, "Mean durations"  )
        self.notebook.AddPage(page5, "Median durations"  )
        self.notebook.AddPage(page6, "Std dev. durations"  )

        page1.ShowStats( self._data )
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
        button_box.Add(self.btn_save,  flag=wx.LEFT, border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_close, flag=wx.RIGHT, border=5)
        self.btn_save.Bind(wx.EVT_BUTTON, self.onButtonSave)
        return button_box


    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout, 0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.toolbar,      0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.notebook,     1, flag=wx.ALL|wx.EXPAND, border=5)
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

    def OnNgram(self, event):
        # get new n value of the N-gram
        self.n = int(event.GetSelection()+1)
        # update infos of TierStats objects
        for ts in self._data:
            ts.set_ngram( self.n )
        page = self.notebook.GetPage( self.notebook.GetSelection() )
        page.ShowStats( self._data )

    def OnWithAlt(self, event):
        newvalue = bool(event.GetSelection())
        if self.withalt == newvalue:
            return
        # update infos of TierStats objects
        for ts in self._data:
            ts.set_withalt( self.withalt )
        page = self.notebook.GetPage( self.notebook.GetSelection() )
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

    #-------------------------------------------------------------------------


# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Base Stat Panel
# ----------------------------------------------------------------------------

class BaseStatPanel( wx.Panel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Base stat panel.

    """

    def __init__(self, parent, prefsIO, name):

        wx.Panel.__init__(self, parent)
        self.preferences = prefsIO
        self.name = name.lower()
        self.rowdata = []

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.ShowNothing()
        self.sizer.Fit(self)

    # End __init__
    # ------------------------------------------------------------------------


    def ShowNothing(self):
        """
        Method to show a message in the panel.

        """
        self.sizer.DeleteWindows()
        self.sizer.Add(wx.StaticText(self, -1, "Nothing to view!"), 1, flag=wx.ALL|wx.EXPAND, border=5)

    # ------------------------------------------------------------------------


    def ShowStats(self, tier):
        """
        Base method to show a tier in the panel.

        """
        self.ShowNothing()

    # ------------------------------------------------------------------------


    def SaveAs(self):
        dlg = wx.FileDialog(self,
                           "Save as",
                           "Save as",
                           "stats.csv",
                           "Excel UTF-16 (*.csv)|*.csv |Excel UTF-8 (*.csv)|*.csv",
                           wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        path, index = dlg.GetPath(), dlg.GetFilterIndex()
        dlg.Destroy()
        encoding = "utf-16" if index == 0 else "utf-8"

        self.rowdata.insert(0, self.cols)
        fileutils.writecsv(path, self.rowdata, separator=";", encoding=encoding)
        self.rowdata.pop(0)

    # ------------------------------------------------------------------------

    def AppendRow(self, i, row, listctrl):
        # append the row in the list
        pos = self.statctrl.InsertStringItem(i, row[0])
        for j in range(1,len(row)):
            s = row[j]
            if isinstance(s, float):
                s = str(round(s,4))
            elif isinstance(s, int):
                s = str(s)
            listctrl.SetStringItem(pos, j, s)

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# First tab: summary
# ----------------------------------------------------------------------------

class SummaryPanel( BaseStatPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Summary of descriptive stats of all merged-tiers.

    """

    def __init__(self, parent, prefsIO, name):
        BaseStatPanel.__init__(self, parent, prefsIO, name)
        self.cols = ("Label", "Occurrences", "Total durations", "Mean durations", "Median durations", "Std dev. durations")

    # End __init__
    # ------------------------------------------------------------------------


    def ShowStats(self, data):
        """
        Show descriptive statistics of set of tiers as list.

        """
        if not data or len(data)==0:
            self.ShowNothing()
            return
        logging.debug('Summary show stats')

        self.statctrl = SortListCtrl(self, size=(-1,400))

        for i,col in enumerate(self.cols):
            self.statctrl.InsertColumn(i,col)
            self.statctrl.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
        self.statctrl.SetColumnWidth(0, 200)

        # create a TierStats (with durations of all tiers)
        ts = self.__get_ts(data)

        # estimates descriptives statistics
        ds = ts.ds()
        occurrences = ds.len()
        total = ds.total()
        mean = ds.mean()
        median = ds.median()
        stdev = ds.stdev()

        # fill rows
        self.rowdata = []
        for i,item in enumerate(occurrences):
            row = [ item[0], occurrences[i][1], total[i][1], mean[i][1], median[i][1], stdev[i][1] ]
            # add the data content in rowdata
            self.rowdata.append( row )
            # add into the listctrl
            self.AppendRow(i, row, self.statctrl)

        self.sizer.DeleteWindows()
        self.sizer.Add(self.statctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.Fit(self)

    # ------------------------------------------------------------------------


    def __get_ts(self, data):
        tiers=[]
        n = 1
        withalt=False
        withradius=0
        for ts,f in data.items():
            if not isinstance( ts.tier,list ):
                tiers.append( ts.tier )
            else:
                tiers.extend( ts.tier )
            # TODO:check if all n/withalt/withradius are the same
            # (it can happen for now, so it's a todo!)
            n          = ts.get_ngram()
            withalt    = ts.get_withalt()
            withradius = ts.get_withradius()
        return TierStats(tiers, n, withradius, withalt)

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Other tabs: details of each file
# ----------------------------------------------------------------------------

class DetailedPanel( BaseStatPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Details of descriptive stats: either occurrences, or durations of each tier.

    """

    def __init__(self, parent, prefsIO, name):
        BaseStatPanel.__init__(self, parent, prefsIO, name)
        self.cols = ('',)

    # End __init__
    # ------------------------------------------------------------------------


    def ShowStats(self, data):
        """
        Show descriptive statistics of set of tiers as list.

        """
        if not data or len(data)==0:
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
        for ts,f in data.items():
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
        items = []
        for t in statvalues:
            # t is a tuple of tuples, representing the stats of each item of a tier
            for s in t:
                if not s[0] in items:
                    items.append(s[0])

        # fill rows
        self.rowdata = []
        for i,item in enumerate(items):
            # add the data content in rowdata
            row = [item] + [0]*len(data.values())
            for j,t in enumerate(statvalues):
                for s in t:
                    if s[0] == item:
                        row[j+1] = s[1]
            self.rowdata.append(row)

            self.AppendRow(i, row, self.statctrl)

        self.sizer.DeleteWindows()
        self.sizer.Add(self.statctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.Fit(self)


    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------
