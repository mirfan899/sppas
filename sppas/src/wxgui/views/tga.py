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
# File: tga.py
# ----------------------------------------------------------------------------

import sys
import os.path
sys.path.append( os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import wx
import logging
import os.path

import annotationdata.aio

from wxgui.dialogs.basedialog import spBaseDialog

from calculus.descriptivesstats import DescriptiveStatistics
from presenters.tiertga import TierTGA
from utils import fileutils

from wxgui.sp_icons  import TIMEANALYSIS
from wxgui.sp_icons  import BROOM_ICON
from wxgui.sp_icons  import APPLY_ICON
from wxgui.sp_icons  import EXPORT_ICON

from wxgui.cutils.imageutils import spBitmap

from wxgui.ui.CustomListCtrl import SortListCtrl
from wxgui.panels.basestats import BaseStatPanel
from wxgui.views.processprogress import ProcessProgressDialog

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

DEFAULT_SEP = 'sep1, sep2, etc'

# ----------------------------------------------------------------------------


class TGADialog(spBaseDialog):
    """
    :author:  Brigitte Bigi
    :contact: brigitte.bigi@gmail.com
    :license: GPL, v3
    :summary: This class is used to display TGA results of tiers.

    Dialog for the user to display and save Time Group Analysis results
    of a set of tiers.

    """
    def __init__(self, parent, preferences, tiers={}):
        """ Create a new dialog.

        :param parent:
        :param preferences: (structs.Preferences)
        :param tiers: a dictionary with key=filename, value=list of selected tiers

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Time Group Analysis")
        wx.GetApp().SetAppName("tga")

        # Members
        # Options to evaluate stats:
        self.withradius = 0

        self._data = {}  # to store stats
        for k, v in tiers.items():
            for tier in v:
                ts = TierTGA(tier, self.withradius)
                self._data[ts] = k
                # remark: TGA are not estimated yet.

        titlebox = self.CreateTitle(TIMEANALYSIS, "Time Group Analysis of a set of tiers")
        contentbox = self._create_content()
        buttonbox = self._create_buttons()

        self.LayoutComponents(titlebox,
                              contentbox,
                              buttonbox)

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_export = self.CreateButton(EXPORT_ICON, "Export", tooltip="Show a random tip")
        btn_save = self.CreateSaveButton()
        btn_close = self.CreateCloseButton()
        self.Bind(wx.EVT_BUTTON, self._on_save, btn_save)
        self.Bind(wx.EVT_BUTTON, self._on_export, btn_export)
        return self.CreateButtonBox([btn_save, btn_export], [btn_close])

        self._create_toolbar()
        self._create_content()

        self._create_close_button()
        self._create_save_button()
        self._create_export_button()
        self._layout_components()
        self._set_focus_component()

    # ------------------------------------------------------------------------

    def _create_toolbar(self):
        """ Simulate a toolbar."""

        font = self.preferences.GetValue('M_FONT')
        font.SetPointSize(font.GetPointSize() - 2)

        sep_label = wx.StaticText(self, label="Time group separators:", style=wx.ALIGN_CENTER)
        sep_label.SetFont(font)

        self.septext = wx.TextCtrl(self, -1, size=(150,24))
        self.septext.SetFont(font)
        self.septext.SetInsertionPoint(0)
        self.septext.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.septext.SetForegroundColour(wx.Colour(128,128,128))
        self.septext.SetValue(DEFAULT_SEP)

        broomb = wx.BitmapButton(self,
                                 bitmap=spBitmap(BROOM_ICON, 24, theme=self.preferences.GetValue('M_ICON_THEME')),
                                 style=wx.NO_BORDER)
        applyb = wx.BitmapButton(self,
                                 bitmap=spBitmap(APPLY_ICON, 24, theme=self.preferences.GetValue('M_ICON_THEME')),
                                 style=wx.NO_BORDER)

        durlist = ['Use only Midpoint value', 'Add the Radius value', 'Deduct the Radius value']
        withradiusbox = wx.RadioBox(self, -1,
                                    label="Annotation durations:",
                                    choices=durlist,
                                    majorDimension=1,
                                    style=wx.RA_SPECIFY_COLS)
        withradiusbox.SetFont(font)

        self.AddToolbar([sep_label, broomb, self.septext, applyb], [withradiusbox])

        self.septext.Bind(wx.EVT_TEXT, self.OnTextChanged)
        self.septext.Bind(wx.EVT_SET_FOCUS, self.OnTextClick)
        self.Bind(wx.EVT_BUTTON, self.OnTextErase, broomb)
        self.Bind(wx.EVT_BUTTON, self.OnSeparatorChanged, applyb)
        self.Bind(wx.EVT_RADIOBOX, self.OnWithRadius, withradiusbox)

    def _create_content(self):
        self._create_toolbar()
        self.notebook = wx.Notebook(self)
        page1 = TotalPanel( self.notebook, self.preferences, "total")
        page2 = MeansPanel(self.notebook, self.preferences, "means")
        page3 = DeltaDurationsPanel(self.notebook, self.preferences, "delta")
        # add the pages to the notebook with the label to show on the tab
        self.notebook.AddPage(page1, "   Total   ")
        self.notebook.AddPage(page2, "   Means  ")
        self.notebook.AddPage(page3, " DeltaDurations ")
        page1.ShowStats(self._data)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChanged)
        return self.notebook

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def _on_save(self, event):
        idx = self.notebook.GetSelection()
        page = self.notebook.GetPage(idx)
        page.SaveAs(outfilename="tga-%s.csv" % page.name)

    def _on_export(self, event):
        # Create the progress bar then run the annotations
        wx.BeginBusyCursor()
        p = ProcessProgressDialog(self, self.preferences, "Time Group Analysis...")
        p.set_header("Annotation generation")
        p.update(0, "")
        total = len(self._data.items())
        i = 0
        # Work: Generate TGA annotations for each of the given files
        for tg, filename in self._data.items():
            p.set_text(filename)
            # estimates TGA
            trs = tg.tga_as_transcription()
            # save as file
            infile, ext = os.path.splitext(filename)
            outfile = infile + "-tga" + ext
            logging.info('Export file: %s' % outfile)
            annotationdata.aio.write(outfile, trs)
            # uppdate progress bar
            i += 1
            p.set_fraction(float((i+1))/float(total))
        # Close progress bar
        p.close()
        wx.EndBusyCursor()

    def OnNotebookPageChanged(self, event):
        oldselection = event.GetOldSelection()
        newselection = event.GetSelection()
        if oldselection != newselection:
            page = self.notebook.GetPage(newselection)
            page.ShowStats(self._data)

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
        # update infos of TierTGA objects
        for ts in self._data:
            ts.set_withradius(self.withradius)
        page = self.notebook.GetPage(self.notebook.GetSelection())
        page.ShowStats(self._data)


    def OnTextClick(self, event):
        self.septext.SetForegroundColour(wx.BLACK)
        if self.septext.GetValue() == DEFAULT_SEP:
            self.OnTextErase(event)
        event.Skip()
        #self.text.SetFocus()

    def OnTextChanged(self, event):
        logging.debug('Text changed event: %s'%self.septext.GetValue())
        self.septext.SetFocus()
        self.septext.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.septext.Refresh()

    def OnSeparatorChanged(self, event):
        logging.debug('Enter event: %s'%self.septext.GetValue())
        seps = self.septext.GetValue().strip().split()
        # update infos of TierTGA objects
        for ts in self._data:
            ts.remove_separators()
            for sep in seps:
                ts.append_separator(sep)
        page = self.notebook.GetPage(self.notebook.GetSelection())
        page.ShowStats(self._data)

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

class TotalPanel(BaseStatPanel):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: TGA of all tiers, in details.

    """

    def __init__(self, parent, prefsIO, name):
        BaseStatPanel.__init__(self, parent, prefsIO, name)
        self.cols = ("Filename", "Tier", "TG name", "TG segments", "Length", "Total", "Mean", "Median", "Std dev.", "nPVI", "Intercept-Pos","Slope-Pos", "Intercept-Time","Slope-Time")

    # ------------------------------------------------------------------------

    def ShowStats(self, data):
        """
        Show TGA of set of tiers as list.

        """
        if not data or len(data)==0:
            self.ShowNothing()
            return

        self.statctrl = SortListCtrl(self, size=(-1,-1))

        for i,col in enumerate(self.cols):
            self.statctrl.InsertColumn(i,col)
            self.statctrl.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
        self.statctrl.SetColumnWidth(0, 200)

        self.rowdata = []
        i = 0
        for tg,filename in data.items():
            # estimates TGA
            ds = tg.tga()    # durations data
            ls = tg.labels() # labels data
            occurrences = ds.len()
            total       = ds.total()
            mean        = ds.mean()
            median      = ds.median()
            stdev       = ds.stdev()
            npvi        = ds.nPVI()
            regressp    = ds.intercept_slope_original()
            regresst    = ds.intercept_slope()

            # fill rows
            for key in occurrences.keys():
                # create the row, as a list of column items
                segs = " ".join(ls[key])
                row = [ filename, tg.tier.GetName(), key, segs, occurrences[key], total[key], mean[key], median[key], stdev[key], npvi[key], regressp[key][0], regressp[key][1], regresst[key][0], regresst[key][1] ]
                # add the data content in rowdata
                self.rowdata.append(row)
                # add into the listctrl
                self.AppendRow(i, row, self.statctrl)
                i = i+1

        self.sizer.DeleteWindows()
        self.sizer.Add(self.statctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.FitInside(self)
        self.SendSizeEvent()

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class MeansPanel(BaseStatPanel):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: The means of TGA for each tier.

    """

    def __init__(self, parent, prefsIO, name):
        BaseStatPanel.__init__(self, parent, prefsIO, name)
        self.cols = ("Filename", "Tier", "Length", "Total", "Mean", "Median", "Std dev.", "nPVI", "Intercept-Pos","Slope-Pos", "Intercept-Time","Slope-Time")

    # ------------------------------------------------------------------------

    def ShowStats(self, data):
        """
        Show descriptive statistics of set of tiers as list.

        """
        if not data or len(data)==0:
            self.ShowNothing()
            return

        self.statctrl = SortListCtrl(self, size=(-1,480))

        # create columns
        for i,col in enumerate(self.cols):
            self.statctrl.InsertColumn(i,col)
            self.statctrl.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
        self.statctrl.SetColumnWidth(0, 200)

        self.rowdata = []
        i = 0
        # estimates TGA, store results in a dict
        for tg,filename in data.items():
            ds = tg.tga()
            tgdict = {'len':[], 'total':[], 'mean':[], 'median':[], 'stdev':[], 'npvi':[], 'interceptp':[], 'slopep':[], 'interceptt':[], 'slopet':[]}
            tgdict['len']    = list(ds.len().values())
            tgdict['total']  = list(ds.total().values())
            tgdict['mean']   = list(ds.mean().values())
            tgdict['median'] = list(ds.median().values())
            tgdict['stdev']  = list(ds.stdev().values())
            tgdict['npvi']   = list(ds.nPVI().values())
            regressp = ds.intercept_slope_original()
            regresst = ds.intercept_slope()
            tgdict['interceptp'] = [intercept for intercept,slope in list(regressp.values())]
            tgdict['slopep']     = [slope     for intercept,slope in list(regressp.values())]
            tgdict['interceptt'] = [intercept for intercept,slope in list(regresst.values())]
            tgdict['slopet']     = [slope     for intercept,slope in list(regresst.values())]

            stats = DescriptiveStatistics(tgdict)
            means = stats.mean()

            # fill rows
            row = [ filename, tg.tier.GetName(), means['len'], means['total'], means['mean'], means['median'], means['stdev'], means['npvi'], means['interceptp'], means['slopep'], means['interceptt'], means['slopet'] ]
            # add the data content in rowdata
            self.rowdata.append(row)
            # add into the listctrl
            self.AppendRow(i, row, self.statctrl)
            i = i+1


        self.sizer.DeleteWindows()
        self.sizer.Add(self.statctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.FitInside(self)
        self.SendSizeEvent()

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class DeltaDurationsPanel(BaseStatPanel):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: TGA related to delta durations.

    """

    def __init__(self, parent, prefsIO, name):
        BaseStatPanel.__init__(self, parent, prefsIO, name)
        self.cols = ("Filename", "Tier", "TG name", "Delta Durations")

    # ------------------------------------------------------------------------

    def ShowStats(self, data):
        """
        Show TGA of set of tiers as list.

        """
        if not data or len(data)==0:
            self.ShowNothing()
            return

        self.statctrl = SortListCtrl(self, size=(-1,-1))

        for i,col in enumerate(self.cols):
            self.statctrl.InsertColumn(i,col)
            self.statctrl.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
        self.statctrl.SetColumnWidth(0, 200)

        self.rowdata = []
        i = 0
        for tg,filename in data.items():
            # estimates TGA
            #ds = tg.tga()    # durations data
            #ls = tg.labels() # labels data
            dd = tg.deltadurations()
            # fill rows
            for key in dd.keys():
                # create the row, as a list of column items
                segs = " ".join("%10.3f" % x for x in dd[key])
                row = [ filename, tg.tier.GetName(), key, segs ]
                # add the data content in rowdata
                self.rowdata.append(row)
                # add into the listctrl
                self.AppendRow(i, row, self.statctrl)
                i = i+1

        self.sizer.DeleteWindows()
        self.sizer.Add(self.statctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.FitInside(self)
        self.SendSizeEvent()

# ----------------------------------------------------------------------------

def ShowTgaDialog(parent, preferences, tiers):
    dialog = TGADialog(parent, preferences, tiers)
    dialog.ShowModal()
    dialog.Destroy()

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.PySimpleApp()
    ShowTgaDialog(None,None,tiers={})
    app.MainLoop()

# ---------------------------------------------------------------------------
