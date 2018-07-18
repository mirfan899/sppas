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
# File: singlefilter.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os
import wx
import re
import operator
import functools

from sppas.src.annotationdata.filter.predicate import Sel

from sppas.src.ui.wxgui.dialogs.basedialog import spBaseDialog
from sppas.src.ui.wxgui.sp_icons import FILTER_SINGLE
from sppas.src.ui.wxgui.sp_icons import APPLY_ICON
from sppas.src.ui.wxgui.sp_icons import FILTER_ADD_LABEL
from sppas.src.ui.wxgui.sp_icons import FILTER_ADD_DURATION
from sppas.src.ui.wxgui.sp_icons import FILTER_ADD_TIME
from sppas.src.ui.wxgui.sp_icons import FILTER_REMOVE
from sppas.src.ui.wxgui.panels.mainbuttons import MainToolbarPanel
from sppas.src.ui.wxgui.cutils.textutils import TextValidator
from sppas.src.ui.wxgui.ui.CustomListCtrl import CheckListCtrl

try:
    from agw import floatspin as FS
except ImportError:
    import wx.lib.agw.floatspin as FS

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

ID_ADD_LABEL    = wx.NewId()
ID_ADD_TIME     = wx.NewId()
ID_ADD_DURATION = wx.NewId()
ID_CLEAR        = wx.NewId()

DEFAULT_TIERNAME = "Filtered tier"
DEFAULT_LABEL = "label1, label2..."

# ----------------------------------------------------------------------------
# class SingleFilterDialog
# ----------------------------------------------------------------------------

class SingleFilterDialog( spBaseDialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to fix a set of filters for a tier.

    Dialog for the user to fix a set of filters to be applied to a tier, thanks
    to the predicate Sel.

    """

    def __init__(self, parent, preferences):
        """
        Create a new dialog.

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - SingleFilter")
        wx.GetApp().SetAppName( "singlefilter" )

        # Members
        self.match_all = False

        titlebox   = self.CreateTitle(FILTER_SINGLE,"Filter annotations of a tier")
        contentbox = self._create_content()
        buttonbox  = self._create_buttons()

        self.LayoutComponents( titlebox,
                               contentbox,
                               buttonbox )
        self.SetMinSize((540,460))

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_cancel   = self.CreateCancelButton( )
        btn_applyany = self.CreateButton(APPLY_ICON, "Apply ANY", btnid=wx.ID_OK )
        btn_applyall = self.CreateButton(APPLY_ICON, "Apply ALL", btnid=wx.ID_OK )
        self.SetAffirmativeId(wx.ID_OK)
        btn_applyall.SetDefault()
        btn_applyall.Bind(wx.EVT_BUTTON, self._on_button_all, btn_applyall)
        return self.CreateButtonBox( [btn_cancel],[btn_applyany,btn_applyall] )

    def _create_content(self):
        self.filterpanel = SingleFilterPanel(self, self.preferences)

        self.tiername_layout = wx.BoxSizer(wx.HORIZONTAL)
        title_tiername = wx.StaticText(self, label="Name of filtered tier: ", style=wx.ALIGN_CENTER)
        title_tiername.SetFont( self.preferences.GetValue('M_FONT') )
        self.text_tiername = wx.TextCtrl(self, size=(250, -1), validator=TextValidator())
        self.text_tiername.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.text_tiername.SetForegroundColour(wx.Colour(128,128,128))
        self.text_tiername.SetValue(DEFAULT_TIERNAME)
        self.text_tiername.Bind(wx.EVT_TEXT, self.OnTextChanged)
        self.text_tiername.Bind(wx.EVT_SET_FOCUS, self.OnTextClick)
        self.tiername_layout.Add(title_tiername,  flag=wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)
        self.tiername_layout.Add(self.text_tiername, flag=wx.EXPAND|wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.filterpanel,     1, flag=wx.ALL|wx.EXPAND, border=0)
        vbox.Add(self.tiername_layout, 0, flag=wx.ALL|wx.EXPAND, border=0)
        return vbox

    #-------------------------------------------------------------------------
    # Callbacks
    #-------------------------------------------------------------------------

    def _on_button_all(self, event):
        self.match_all = True
        event.Skip()

    def OnTextClick(self, event):
        self.text_tiername.SetForegroundColour( wx.BLACK )
        if self.text_tiername.GetValue().strip() == "":
            self.OnTextErase(event)
        event.Skip()

    def OnTextChanged(self, event):
        self.text_tiername.SetFocus()
        self.text_tiername.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.text_tiername.Refresh()

    def OnTextErase(self, event):
        self.text_tiername.SetValue('')
        self.text_tiername.SetFocus()
        self.text_tiername.SetBackgroundColour( wx.Colour(245,220,240) )
        self.text_tiername.Refresh()

    #-------------------------------------------------------------------------

    #-------------------------------------------------------------------------
    # Getters...
    #-------------------------------------------------------------------------

    def GetPredicates(self):
        """
        Convert the content in a list of Sel predicates and return it.
        """
        return self.filterpanel.GetPredicates()

    def GetFiltererdTierName(self):
        """
        Return the future name for the filtered tier.
        """
        return self.text_tiername.GetValue().strip()

    def GetMatchAll(self):
        """
        Return True if all predicates must match.
        """
        return self.match_all

# ----------------------------------------------------------------------------

class SingleFilterPanel(wx.Panel):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Panel to fix filters to be used with Sel predicate.

    """

    def __init__(self, parent, prefsIO):
        wx.Panel.__init__(self, parent, size=(580, 320))
        self.SetBackgroundColour(prefsIO.GetValue('M_BG_COLOUR'))

        # Members
        self.preferences = prefsIO
        self.data = []

        self._create_toolbar()
        self._create_filterlist()
        self.Bind(wx.EVT_BUTTON, self.ProcessEvent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar,     proportion=0, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=4)
        sizer.Add(self.filterlist,  proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=4)
        self.SetSizer(sizer)
        self.SetAutoLayout( True )


    def _create_toolbar(self):

        self.toolbar = MainToolbarPanel(self, self.preferences)
        self.toolbar.AddButton( ID_ADD_LABEL, FILTER_ADD_LABEL, "Label", tooltip="Add a filter on the content of each annotation of the tier.")
        self.toolbar.AddButton( ID_ADD_TIME, FILTER_ADD_TIME,   "Time",  tooltip="Add a filter to fix the time to start or to end to filter.")
        self.toolbar.AddButton( ID_ADD_DURATION, FILTER_ADD_DURATION, "Duration", tooltip="Add a filter on the duration of each annotations of the tier.")
        self.toolbar.AddSpacer()
        self.toolbar.AddButton( ID_CLEAR, FILTER_REMOVE, "Remove", tooltip="Remove checked filters of the list.")


    def _create_filterlist(self):

        self.filterlist = CheckListCtrl(self, -1, style=wx.LC_REPORT|wx.BORDER_NONE)
        self.filterlist.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        self.filterlist.SetFont( self.preferences.GetValue('M_FONT') )

        cols = ("Filter", "Function", "Value", "Option")
        for i, col in enumerate(cols):
            self.filterlist.InsertColumn(i, col)
            self.filterlist.SetColumnWidth(i, 120)
        self.filterlist.SetFocus()

    # ------------------------------------------------------------------------
    # Callbacks to any kind of event
    # ------------------------------------------------------------------------

    def ProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.
        """
        id = event.GetId()

        if id == ID_ADD_LABEL:
            self.OnAddLabel(event)
            return True

        elif id == ID_ADD_TIME:
            self.OnAddTime(event)
            return True

        elif id == ID_ADD_DURATION:
            self.OnAddDuration(event)
            return True

        elif id == ID_CLEAR:
            self.OnRemove(event)
            return True

        return wx.GetApp().ProcessEvent(event)

    # ----------------------------------------------------------------------
    # Callbacks
    # ----------------------------------------------------------------------

    def OnAddLabel(self, event):
        dlg = LabelFilterDialog(self, self.preferences)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetData()
            self._add_filter( data )
            self.data.append( data )
        dlg.Destroy()

    def OnAddTime(self, event):
        dlg = TimeFilterDialog(self, self.preferences)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetData()
            self._add_filter( data )
            self.data.append( data )
        dlg.Destroy()

    def OnAddDuration(self, event):
        dlg = DurationFilterDialog(self, self.preferences)
        dlg.Show()
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetData()
            self._add_filter( data )
            self.data.append( data )
        dlg.Destroy()

    def OnRemove(self, event):
        # fix a list of selected idem indexes
        selected = []
        currentf = self.filterlist.GetFirstSelected()
        while currentf != -1:
            nextf = self.filterlist.GetNextSelected( currentf )
            selected.append( currentf )
            currentf = nextf

        # remove selected items (starting from end!)
        for index in reversed(selected):
            self.data.pop( index )
            self.filterlist.DeleteItem( index )

    # ----------------------------------------------------------------------
    # Public Methods
    # ----------------------------------------------------------------------

    def GetPredicates(self):
        """ Return a predicate, constructed from the data. """

        predicates = []
        sellist = self.filterlist.GetFirstSelected()
        while sellist != -1:
            d = self.data[sellist]
            p = _genPredicateSel( **d ).generate()
            predicates.append( p )
            sellist = self.filterlist.GetNextSelected( sellist )

        return predicates

    # ----------------------------------------------------------------------
    # Private methods
    # ----------------------------------------------------------------------

    def _add_filter(self, data):
        """ Add a filter in the list. """

        row = self._format_data(data)
        index = self.filterlist.GetItemCount()

        self.filterlist.InsertStringItem( index, row[0] )
        for i in range(1,len(row)):
            self.filterlist.SetStringItem( index, i, row[i] )
        self.filterlist.Select( index,on=True )


    def _format_data(self, data):
        """ Format data to be included in the list. """

        opt = ""
        if "label" in data['type'].lower() and 'string' in data['type'].lower():
            values = ", ".join( data['value'] )
            if data['case_sensitive'] is True:
                opt = "Case-sensitive"
            else:
                opt = "Case-insensitive"
        else:
            values = str(data['value'][0])

        if 'opt' in data.keys() and data['opt'] == "any":
            opt += " Alternatives"

        return (data['type'], data['name'], values, opt)

# --------------------------------------------------------------------------

class _genPredicateSel(object):
    """
    Generate a Sel predicate from data.
    """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def generate(self):
        """
        Returns:
            (Predicate)
        """
        preds = []
        for v in self.value:
            kwargs = {}
            kwargs[ self.function ] = v
            if 'opt' in kwargs.keys():
                kwargs[ 'opt' ] = self.opt
            preds.append( Sel(**kwargs) )

        pred  = functools.reduce(operator.or_, preds)

        if self.reverse:
            return ~pred
        return pred

# ----------------------------------------------------------------------------


class LabelFilterDialog( spBaseDialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to display a Label filter dialog.

    Open a frame to fix the list of patterns and mode to filter labels
    of annotations.

    """
    choices = (
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

    def __init__(self, parent, preferences):
        """
        Constructor.

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Label Filter")
        wx.GetApp().SetAppName( "labelfilter" )

        titlebox   = self.CreateTitle(FILTER_ADD_LABEL,"Label-based single filter")
        contentbox = self._create_content()
        buttonbox  = self._create_buttons()

        self.LayoutComponents( titlebox,
                               contentbox,
                               buttonbox )

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_cancel = self.CreateCancelButton( )
        btn_okay   = self.CreateOkayButton( )
        return self.CreateButtonBox( [btn_cancel],[btn_okay] )

    def _create_content(self):
        self.notebook = wx.Notebook(self)
        self.notebook.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))

        page1 = LabelString(self.notebook, self.preferences)
        page2 = LabelNumber(self.notebook, self.preferences)
        page3 = LabelBoolean(self.notebook, self.preferences)
        # add the pages to the notebook with the label to show on the tab
        self.notebook.AddPage(page1, "  String  ")
        self.notebook.AddPage(page2, "  Number  ")
        self.notebook.AddPage(page3, "  Boolean ")

        self.checkbox = wx.CheckBox(self, label="Search also in alternative labels")
        self.checkbox.SetValue(False)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.notebook, 1, flag=wx.ALL|wx.EXPAND, border=0)
        vbox.Add(self.checkbox, 0, flag=wx.ALL|wx.EXPAND, border=0)
        return vbox

    # -----------------------------------------------------------------------

    def GetData(self):
        pageidx = self.notebook.GetSelection()
        data = self.notebook.GetPage(pageidx).GetData()
        if self.checkbox.GetValue() is True:
            data['opt'] = "any"
        else:
            data['opt'] = "best"
        return data

# ---------------------------------------------------------------------------

class LabelString( wx.Panel ):
    """
    Search into a label of type string.
    """

    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)
        self.preferences = prefsIO
        self.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))

        # Widgets
        msg = "Patterns to find (separated by commas):"
        self.label = wx.StaticText(self, label=msg)
        self.text = wx.TextCtrl(self, value=DEFAULT_LABEL, validator=TextValidator())
        self.text.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))

        choices = [row[0] for row in LabelFilterDialog.choices]
        self.radiobox = wx.RadioBox(self, label="Functions",
                                    choices=choices, majorDimension=2)
        self.checkbox = wx.CheckBox(self, label="Case Sensitive")
        self.checkbox.SetValue(True)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label,     flag=wx.EXPAND|wx.ALL, border=4)
        sizer.Add(self.text,      flag=wx.EXPAND|wx.ALL, border=4)
        sizer.Add(self.radiobox,  flag=wx.EXPAND|wx.ALL, border=4)
        sizer.Add(self.checkbox,  flag=wx.EXPAND|wx.ALL, border=4)

        self.SetSizer( sizer )

    # ------------------------------------------------------------------------

    def OnTextClick(self, event):
        self.text.SetForegroundColour( wx.BLACK )
        if self.text.GetValue() == DEFAULT_LABEL:
            self.OnTextErase(event)
        event.Skip()
        #self.text.SetFocus()

    def OnTextChanged(self, event):
        self.text.SetFocus()
        self.text.Refresh()

    def OnTextErase(self, event):
        self.text.SetValue('')
        self.text.SetFocus()
        self.text.Refresh()

    # -----------------------------------------------------------------------

    def GetData(self):
        """
        Returns:
             (dict):
               name (str)
               type (str)
               function (str)
               patterns (list) patterns to find
               reverse (bool)
        """
        data = {}
        idx = self.radiobox.GetSelection()
        data['type'] = "Label (string)"
        data['name'] = LabelFilterDialog.choices[idx][0]
        data['function'] = LabelFilterDialog.choices[idx][1]
        data['reverse'] = idx % 2 != 0
        case_sensitive = self.checkbox.GetValue()
        data['case_sensitive'] = case_sensitive
        if not case_sensitive and data['function'] != "regexp":
            data['function'] = 'i' + data['function']

        if data['function'] == "regexp":
            data['value'] = [self.text.GetValue()]
        else:
            patterns = re.split(',', self.text.GetValue())
            patterns = [" ".join(p.split()) for p in patterns]
            data['value'] = patterns

        return data

    # -----------------------------------------------------------------------

class LabelNumber( wx.Panel ):
    """
    Search into a label of type string.
    """
    choices = (
               (" is equal to...",     "equal"),
               (" is greater than...", "greater"),
               (" is less than...",    "lower"),
              )

    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)
        self.preferences = prefsIO
        self.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))

        # Widgets
        label = wx.StaticText(self, label="... this value: ")
        choices = [choice[0] for choice in LabelNumber.choices]
        self.radiobox = wx.RadioBox(self, label="The label ",
                                    choices=choices, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.ctrl = FS.FloatSpin(self, min_val=0.0, increment=0.01, value=0, digits=3)

        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label,     flag=wx.EXPAND|wx.ALL, border=5)
        hbox.Add(self.ctrl, flag=wx.EXPAND|wx.ALL, border=5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.radiobox, 1, flag=wx.EXPAND|wx.ALL, border=4)
        sizer.Add(hbox,          0, flag=wx.EXPAND|wx.ALL, border=4)
        self.SetSizer( sizer )

    # -----------------------------------------------------------------------

    def GetData(self):
        data = {}
        idx = self.radiobox.GetSelection()
        data['name']     = LabelNumber.choices[idx][0]
        data['function'] = LabelNumber.choices[idx][1]
        data['value']    = [ float(self.ctrl.GetValue()) ]
        data['type']     = "Label (number)"
        data['reverse']  = False
        return data

# ---------------------------------------------------------------------------

class LabelBoolean( wx.Panel ):
    """
    Search into a label of type string.
    """
    choices = (
               (" is False", "bool"),
               (" is True",  "bool"),
              )
    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)
        self.preferences = prefsIO
        self.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))

        choices = [choice[0] for choice in LabelBoolean.choices]
        self.radiobox = wx.RadioBox(self, label="The label ",
                                    choices=choices, majorDimension=1, style=wx.RA_SPECIFY_COLS)

    # -----------------------------------------------------------------------

    def GetData(self):
        data = {}
        idx = self.radiobox.GetSelection()
        val = bool(idx)
        data['name']     = LabelBoolean.choices[idx][0]
        data['function'] = LabelBoolean.choices[idx][1]
        data['value']    = [ val ]
        data['type']     = "Label (Boolean)"
        data['reverse']  = False
        return data

# ---------------------------------------------------------------------------

class TimeFilterDialog( spBaseDialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to display a Time filter dialog.

    Open a frame to fix the list of modes and values to filter time(s)
    of annotations.

    """
    choices = (
               (" is starting at...", "begin_ge"),
               (" is ending at...",   "end_le")
               )

    def __init__(self, parent, preferences):
        """ Constructor. """
        spBaseDialog.__init__(self, parent, preferences, title=" - Time Filter")
        wx.GetApp().SetAppName( "timefilter" )

        titlebox   = self.CreateTitle(FILTER_ADD_TIME,"Time-based single filter")
        contentbox = self._create_content()
        buttonbox  = self._create_buttons()

        self.LayoutComponents( titlebox,
                               contentbox,
                               buttonbox )

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_cancel = self.CreateCancelButton( )
        btn_okay   = self.CreateOkayButton( )
        return self.CreateButtonBox( [btn_cancel],[btn_okay] )

    def _create_content(self):
        # Widgets
        label = wx.StaticText(self, label="... this time value in seconds: ")
        choices = [choice[0] for choice in TimeFilterDialog.choices]
        self.radiobox = wx.RadioBox(self, label="The time ",
                                    choices=choices, majorDimension=1)
        self.ctrl = FS.FloatSpin(self, min_val=0.0, increment=0.001, value=0, digits=3)
        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label, flag=wx.EXPAND|wx.ALL, border=5)
        hbox.Add(self.ctrl, flag=wx.EXPAND|wx.ALL, border=5)

        content_layout = wx.BoxSizer(wx.VERTICAL)
        content_layout.Add(self.radiobox,1, flag=wx.EXPAND|wx.ALL, border=0)
        content_layout.Add(hbox,         0, flag=wx.EXPAND|wx.ALL, border=0)
        return content_layout

    # -----------------------------------------------------------------------

    def GetData(self):
        """
        Returns:
            (dict):
               name (str)
               type (str)
               function (str)
               value (float) time value in seconds
        """
        data = {}
        idx = self.radiobox.GetSelection()
        data['name']     = TimeFilterDialog.choices[idx][0]
        data['function'] = TimeFilterDialog.choices[idx][1]
        data['value']    = [self.ctrl.GetValue()]
        data['type']     = "Time"
        data['reverse']  = False
        return data

# ---------------------------------------------------------------------------

class DurationFilterDialog( spBaseDialog):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to display a Duration filter dialog.

    Open a frame to fix the list of modes and values to filter duration(s)
    of annotations.

    """
    choices = (
               (" is equal to...",   "duration_eq"),
               (" is greater than...",   "duration_gt"),
               (" is less than...",    "duration_lt"),
               (" is greater or equal to...", "duration_ge"),
               (" is lesser or equal to...", "duration_le")
              )

    def __init__(self, parent, preferences):
        """ Constructor. """
        spBaseDialog.__init__(self, parent, preferences, title=" - Duration Filter")
        wx.GetApp().SetAppName( "durationfilter" )

        titlebox   = self.CreateTitle(FILTER_ADD_DURATION,"Duration-based single filter")
        contentbox = self._create_content()
        buttonbox  = self._create_buttons()

        self.LayoutComponents( titlebox,
                               contentbox,
                               buttonbox )
    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_cancel = self.CreateCancelButton( )
        btn_okay   = self.CreateOkayButton( )
        return self.CreateButtonBox( [btn_cancel],[btn_okay] )

    def _create_content(self):
        # Widgets
        label = wx.StaticText(self, label="... this value in seconds: ")
        choices = [choice[0] for choice in DurationFilterDialog.choices]
        self.radiobox = wx.RadioBox(self, label="The duration",
                                    choices=choices, majorDimension=1)
        self.ctrl = FS.FloatSpin(self, min_val=0.0, increment=0.01, value=0, digits=3)
        # Layout
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(label,     flag=wx.EXPAND|wx.ALL, border=5)
        hbox.Add(self.ctrl, flag=wx.EXPAND|wx.ALL, border=5)

        content_layout = wx.BoxSizer(wx.VERTICAL)
        content_layout.Add(self.radiobox, 1, flag=wx.EXPAND|wx.ALL, border=0)
        content_layout.Add(hbox,          0, flag=wx.EXPAND|wx.ALL, border=0)
        return content_layout

    # -----------------------------------------------------------------------

    def GetData(self):
        """
        Returns:
            (dict):
               name (str)
               type (str)
               function (str)
               value (float) duration value in seconds
        """
        data = {}
        idx = self.radiobox.GetSelection()
        data['name']     = DurationFilterDialog.choices[idx][0]
        data['function'] = DurationFilterDialog.choices[idx][1]
        data['value']    = [self.ctrl.GetValue()]
        data['type']     = "Duration"
        data['reverse']  = False
        return data

    # -----------------------------------------------------------------------
