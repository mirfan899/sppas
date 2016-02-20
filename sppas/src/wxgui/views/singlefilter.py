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
#from _dbus_bindings import Boolean

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os
import wx
import re
import operator
import logging

from annotationdata.filter.predicate import Sel

from wxgui.sp_icons import DATAFILTER_APP_ICON
from wxgui.sp_icons import FILTER_SINGLE
from wxgui.sp_icons import APPLY_ICON
from wxgui.sp_icons import CANCEL_ICON
from wxgui.sp_icons import FILTER_ADD_LABEL
from wxgui.sp_icons import FILTER_ADD_DURATION
from wxgui.sp_icons import FILTER_ADD_TIME
from wxgui.sp_icons import FILTER_REMOVE

from wxgui.sp_consts import TB_ICONSIZE
from wxgui.sp_consts import TB_FONTSIZE

from wxgui.cutils.imageutils import spBitmap
from wxgui.cutils.ctrlutils import CreateGenButton
from wxgui.cutils.textutils import TextValidator

from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE

from wxgui.ui.CustomListCtrl import CheckListCtrl

from sp_glob import ICONS_PATH


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



# ----------------------------------------------------------------------------
# class SingleFilterDialog
# ----------------------------------------------------------------------------

class SingleFilterDialog( wx.Dialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to fix a set of filters for a tier.

    Dialog for the user to fix a set of filters to be applied to a tier, thanks
    to the predicate Sel.

    """

    def __init__(self, parent, prefsIO):
        """
        Create a new dialog.

        """

        wx.Dialog.__init__(self, parent, title=FRAME_TITLE+" - SingleFilter", style=FRAME_STYLE)

        # Members
        self.preferences = prefsIO
        self.match_all = False
        self._create_gui()

        # Events of this frame
        wx.EVT_CLOSE(self, self.onClose)

    # End __init__
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------


    def _create_gui(self):
        self._init_infos()
        self._create_title_label()
        self._create_content()
        self._create_cancel_button()
        self._create_applyall_button()
        self._create_applyany_button()
        self._layout_components()
        self._set_focus_component()


    def _init_infos( self ):
        wx.GetApp().SetAppName( "singlefilter" )
        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(DATAFILTER_APP_ICON) )
        self.SetIcon(_icon)
        # colors
        self.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont( self.preferences.GetValue('M_FONT'))


    def _create_title_label(self):
        self.title_layout = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.BitmapButton(self, bitmap=spBitmap(FILTER_SINGLE, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label = wx.StaticText(self, label="Filter annotations of a tier", style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)


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


    def _create_cancel_button(self):
        bmp = spBitmap(CANCEL_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_cancel = CreateGenButton(self, wx.ID_CLOSE, bmp, text=" Cancel ", tooltip="Close this frame", colour=color)
        self.btn_cancel.SetFont( self.preferences.GetValue('M_FONT'))
        self.SetEscapeId(wx.ID_CLOSE)


    def _create_applyany_button(self):
        bmp = spBitmap(APPLY_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_applyany = CreateGenButton(self, wx.ID_OK, bmp, text=" Apply any ", tooltip="Apply any of the filters and close the frame", colour=color)
        self.btn_applyany.SetFont( self.preferences.GetValue('M_FONT'))


    def _create_applyall_button(self):
        bmp = spBitmap(APPLY_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_applyall = CreateGenButton(self, wx.ID_OK, bmp, text=" Apply all ", tooltip="Apply all filters and close the frame", colour=color)
        self.btn_applyall.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_applyall.SetDefault()
        self.btn_applyall.SetFocus()


    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_cancel,   flag=wx.LEFT,  border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_applyany, flag=wx.RIGHT, border=5)
        button_box.Add(self.btn_applyall, flag=wx.RIGHT, border=5)

        self.btn_applyall.Bind(wx.EVT_BUTTON, self.onButtonAll)

        return button_box


    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout, 0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.filterpanel,  1, flag=wx.ALL|wx.EXPAND, border=0)
        vbox.Add(self.tiername_layout, 0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self._create_button_box(), 0, flag=wx.ALL|wx.EXPAND, border=5)
        self.SetSizerAndFit(vbox)


    def _set_focus_component(self):
        self.filterpanel.SetFocus()


    #-------------------------------------------------------------------------
    # Callbacks
    #-------------------------------------------------------------------------

    def onClose(self, event):
        self.SetEscapeId( wx.ID_CANCEL )

    def onButtonAll(self, event):
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

    #-------------------------------------------------------------------------


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

        # Members
        self.preferences = prefsIO
        self.data = []

        self._create_gui()


    def _create_gui(self):
        self._create_toolbar()
        self._create_filterlist()
        self._layout_components()
        self._set_focus_component()


    def _create_toolbar(self):
        """ Creates a toolbar panel. """

        # Define the size of the icons and buttons
        iconSize = (TB_ICONSIZE, TB_ICONSIZE)
        self.toolbar = wx.ToolBar( self, -1, style=wx.TB_TEXT)

        # Set the size of the buttons
        self.toolbar.SetToolBitmapSize(iconSize)
        self.toolbar.SetFont( self.preferences.GetValue('M_FONT') )

        self.toolbar.AddLabelTool(ID_ADD_LABEL, 'Label Filter',
                             spBitmap(FILTER_ADD_LABEL,TB_ICONSIZE,theme=self.preferences.GetValue('M_ICON_THEME')),
                             shortHelp="Add a filter on the content of each annotation of the tier")
        self.toolbar.AddLabelTool(ID_ADD_TIME, 'Time Filter',
                             spBitmap(FILTER_ADD_TIME,TB_ICONSIZE,theme=self.preferences.GetValue('M_ICON_THEME')),
                             shortHelp="Add a filter to fix the time to start or to end to filter")
        self.toolbar.AddLabelTool(ID_ADD_DURATION, 'Duration Filter',
                             spBitmap(FILTER_ADD_DURATION,TB_ICONSIZE,theme=self.preferences.GetValue('M_ICON_THEME')),
                             shortHelp="Add a filter on the duration of each annotations of the tier")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(ID_CLEAR, 'Remove Filter',
                             spBitmap(FILTER_REMOVE,TB_ICONSIZE,theme=self.preferences.GetValue('M_ICON_THEME')),
                             shortHelp="Remove checked filters of the list")
        self.toolbar.Realize()

        # events
        eventslist = [ ID_ADD_LABEL, ID_ADD_TIME, ID_ADD_DURATION, ID_CLEAR ]
        for event in eventslist:
            wx.EVT_TOOL(self, event, self.ProcessEvent)


    def _create_filterlist(self):
        self.filterlist = CheckListCtrl(self, -1, style=wx.LC_REPORT|wx.BORDER_NONE)

        self.filterlist.SetFont( self.preferences.GetValue('M_FONT') )
        cols = ("Filter", "Function", "Value", "Option")
        for i, col in enumerate(cols):
            self.filterlist.InsertColumn(i, col)
            self.filterlist.SetColumnWidth(i, 120)


    def _layout_components(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, proportion=0, flag=wx.EXPAND|wx.ALL, border=1 )
        sizer.Add(self.filterlist, 1, flag=wx.ALL|wx.EXPAND, border=10)
        self.SetSizer(sizer)
        self.SetAutoLayout( True )


    def _set_focus_component(self):
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
            self.OnClear(event)
            return True

        return wx.GetApp().ProcessEvent(event)

    # End ProcessEvent
    # ------------------------------------------------------------------------


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
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetData()
            self._add_filter( data )
            self.data.append( data )
        dlg.Destroy()


    def OnClear(self, event):
        sellist = self.filterlist.GetFirstSelected()
        while sellist != -1:
            next = self.filterlist.GetNextSelected( sellist )
            self.filterlist.DeleteItem( sellist )
            self.data.pop( sellist )
            sellist = next


    # ----------------------------------------------------------------------
    # Public Methods
    # ----------------------------------------------------------------------


    def GetPredicates(self):
        """
        Return a predicate, constructed from the data.
        """
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
        """
        Add a filter in the list.
        """
        row = self._format_data(data)
        index = self.filterlist.GetItemCount()

        self.filterlist.InsertStringItem( index, row[0] )
        for i in range(1,len(row)):
            self.filterlist.SetStringItem( index, i, row[i] )
        self.filterlist.Select( index,on=True )


    def _format_data(self, data):
        """
        Format data to be included in the list.
        """
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

    # ----------------------------------------------------------------------


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

        pred  = reduce(operator.or_, preds)

        if self.reverse:
            return ~pred
        return pred

    # ----------------------------------------------------------------------


# ----------------------------------------------------------------------------


class LabelFilterDialog(wx.Dialog):
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
        wx.Dialog.__init__(self, parent, -1, title=FRAME_TITLE+" - Label Filter", style=FRAME_STYLE)

        self.preferences = preferences
        self._create_gui()

        # Events of this frame
        wx.EVT_CLOSE(self, self.OnClose)

    # End __init__
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_gui(self):
        self._init_infos()
        self._create_title_label()
        self._create_notebook()
        self._create_apply_button()
        self._create_close_button()
        self._layout_components()
        self._set_focus_component()

    def _init_infos( self ):
        wx.GetApp().SetAppName( "label" )
        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(DATAFILTER_APP_ICON) )
        self.SetIcon(_icon)
        # colors
        self.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont( self.preferences.GetValue('M_FONT'))

    def _create_title_label(self):
        self.title_layout = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.BitmapButton(self, bitmap=spBitmap(FILTER_ADD_LABEL, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label = wx.StaticText(self, label="Label-based filter", style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT|wx.wx.ALIGN_CENTER_VERTICAL, border=5)
        self.title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)


    def _create_notebook(self):
        self.notebook = wx.Notebook(self)
        page1 = LabelString(self.notebook, self.preferences)
        page2 = LabelNumber(self.notebook, self.preferences)
        page3 = LabelBoolean(self.notebook, self.preferences)
        # add the pages to the notebook with the label to show on the tab
        self.notebook.AddPage(page1, "  String  ")
        self.notebook.AddPage(page2, "  Number  ")
        self.notebook.AddPage(page3, "  Boolean ")

        self.checkbox = wx.CheckBox(self, label="Search also in alternative labels")
        self.checkbox.SetValue(False)


    def _create_apply_button(self):
        bmp = spBitmap(APPLY_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_apply = CreateGenButton(self, wx.ID_OK, bmp, text=" Apply ", tooltip="Add filters and close this frame", colour=color)
        self.btn_apply.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_apply.SetDefault()
        self.btn_apply.SetFocus()
        self.SetAffirmativeId(wx.ID_OK)

    def _create_close_button(self):
        bmp = spBitmap(CANCEL_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_close = CreateGenButton(self, wx.ID_CLOSE, bmp, text=" Cancel", tooltip="Close this frame", colour=color)
        self.btn_close.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_close.SetDefault()
        self.btn_close.SetFocus()
        self.SetEscapeId(wx.ID_CLOSE)

    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_close, flag=wx.LEFT, border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_apply, flag=wx.RIGHT, border=5)
        return button_box

    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout,         0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.notebook,             1, flag=wx.ALL|wx.EXPAND, border=0)
        vbox.Add(self.checkbox,             0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self._create_button_box(), 0, flag=wx.ALL|wx.EXPAND, border=5)
        self.SetSizerAndFit(vbox)
#         self.SetMinSize((420,380))
#         self.SetSizer( vbox )
#         self.Centre()
#         self.Enable()
#         self.SetAutoLayout(True)
#         self.SetFocus()
#         self.Layout()
        self.Show(True)


    def _set_focus_component(self):
        self.notebook.SetFocus()

    # -----------------------------------------------------------------------

    def OnClose(self, event):
        self.SetEscapeId(wx.ID_CANCEL)


    def GetData(self):
        pageidx = self.notebook.GetSelection()
        data = self.notebook.GetPage(pageidx).GetData()
        if self.checkbox.GetValue() is True:
            data['opt'] = "any"
        else:
            data['opt'] = "best"
        return data

    # -----------------------------------------------------------------------



class LabelString( wx.Panel ):
    """
    Search into a label of type string.
    """

    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)
        self.preferences = prefsIO

        # Widgets
        msg = "Patterns to find (separated by commas):"
        self.label = wx.StaticText(self, label=msg)
        self.text = wx.TextCtrl(self, value="", validator=TextValidator())
        self.text.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))

        choices = [row[0] for row in LabelFilterDialog.choices]
        self.radiobox = wx.RadioBox(self, label="Functions",
                                    choices=choices, majorDimension=2)
        self.checkbox = wx.CheckBox(self, label="Case Sensitive")
        self.checkbox.SetValue(True)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label,     flag=wx.EXPAND|wx.ALL, border=5)
        sizer.Add(self.text,      flag=wx.EXPAND|wx.ALL, border=5)
        sizer.Add(self.radiobox,  flag=wx.EXPAND|wx.ALL, border=5)
        sizer.Add(self.checkbox,  flag=wx.EXPAND|wx.ALL, border=5)

        self.SetSizer( sizer )

    # End __init__
    # ------------------------------------------------------------------------


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

    # End GetData
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
        sizer.Add(self.radiobox, 1, flag=wx.EXPAND|wx.ALL, border=5)
        sizer.Add(hbox, 0, flag=wx.EXPAND|wx.ALL, border=5)
        self.SetSizer( sizer )

    def GetData(self):
        data = {}
        idx = self.radiobox.GetSelection()
        data['name']     = LabelNumber.choices[idx][0]
        data['function'] = LabelNumber.choices[idx][1]
        data['value']    = [ float(self.ctrl.GetValue()) ]
        data['type']     = "Label (number)"
        data['reverse']  = False
        return data

    # End GetData
    # -----------------------------------------------------------------------


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

        choices = [choice[0] for choice in LabelBoolean.choices]
        self.radiobox = wx.RadioBox(self, label="The label ",
                                    choices=choices, majorDimension=1, style=wx.RA_SPECIFY_COLS)


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

    # End GetData
    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------

class TimeFilterDialog(wx.Dialog):
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
        wx.Dialog.__init__(self, parent, -1, title=FRAME_TITLE+" - Time Filter", style=FRAME_STYLE)

        self.preferences = preferences
        self._create_gui()

        # Events of this frame
        wx.EVT_CLOSE(self, self.OnClose)

    # End __init__
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_gui(self):
        self._init_infos()
        self._create_title_label()
        self._create_content()
        self._create_apply_button()
        self._create_close_button()
        self._layout_components()
        self._set_focus_component()

    def _init_infos( self ):
        wx.GetApp().SetAppName( "time" )
        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(DATAFILTER_APP_ICON) )
        self.SetIcon(_icon)
        # colors
        self.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont( self.preferences.GetValue('M_FONT'))

    def _create_title_label(self):
        self.title_layout = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.BitmapButton(self, bitmap=spBitmap(FILTER_ADD_TIME, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label = wx.StaticText(self, label="Time-based filter", style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT|wx.wx.ALIGN_CENTER_VERTICAL, border=5)
        self.title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)

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
        self.content_layout = wx.BoxSizer(wx.VERTICAL)
        self.content_layout.Add(self.radiobox,1, flag=wx.EXPAND|wx.ALL, border=5)
        self.content_layout.Add(hbox,         0, flag=wx.EXPAND|wx.ALL, border=5)

    def _create_apply_button(self):
        bmp = spBitmap(APPLY_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_apply = CreateGenButton(self, wx.ID_OK, bmp, text=" Apply ", tooltip="Add filters and close this frame", colour=color)
        self.btn_apply.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_apply.SetDefault()
        self.btn_apply.SetFocus()
        self.SetAffirmativeId(wx.ID_OK)

    def _create_close_button(self):
        bmp = spBitmap(CANCEL_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_close = CreateGenButton(self, wx.ID_CLOSE, bmp, text=" Cancel", tooltip="Close this frame", colour=color)
        self.btn_close.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_close.SetDefault()
        self.btn_close.SetFocus()
        self.SetEscapeId(wx.ID_CLOSE)

    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_close, flag=wx.LEFT, border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_apply, flag=wx.RIGHT, border=5)
        return button_box

    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout,         0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.content_layout,       1, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self._create_button_box(), 0, flag=wx.ALL|wx.EXPAND, border=5)
        self.SetMinSize((320,280))
        self.SetSizer( vbox )
        self.Centre()
        self.Enable()
        self.SetAutoLayout(True)
        self.SetFocus()
        self.Layout()
        self.Show(True)

    def _set_focus_component(self):
        self.btn_apply.SetFocus()

    # -----------------------------------------------------------------------

    def OnClose(self, event):
        self.SetEscapeId(wx.ID_CANCEL)

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

    # End GetData
    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------


class DurationFilterDialog(wx.Dialog):
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
        wx.Dialog.__init__(self, parent, -1, title=FRAME_TITLE+" - Duration Filter", style=FRAME_STYLE)

        self.preferences = preferences
        self._create_gui()

        # Events of this frame
        wx.EVT_CLOSE(self, self.OnClose)

    # End __init__
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_gui(self):
        self._init_infos()
        self._create_title_label()
        self._create_content()
        self._create_apply_button()
        self._create_close_button()
        self._layout_components()
        self._set_focus_component()

    def _init_infos( self ):
        wx.GetApp().SetAppName( "duration" )
        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(DATAFILTER_APP_ICON) )
        self.SetIcon(_icon)
        # colors
        self.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont( self.preferences.GetValue('M_FONT'))

    def _create_title_label(self):
        self.title_layout = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.BitmapButton(self, bitmap=spBitmap(FILTER_ADD_DURATION, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label = wx.StaticText(self, label="Duration-based filter", style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT|wx.wx.ALIGN_CENTER_VERTICAL, border=5)
        self.title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)

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

        self.content_layout = wx.BoxSizer(wx.VERTICAL)
        self.content_layout.Add(self.radiobox, 1, flag=wx.EXPAND|wx.ALL, border=5)
        self.content_layout.Add(hbox,          0, flag=wx.EXPAND|wx.ALL, border=5)

    def _create_apply_button(self):
        bmp = spBitmap(APPLY_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_apply = CreateGenButton(self, wx.ID_OK, bmp, text=" Apply ", tooltip="Add filters and close this frame", colour=color)
        self.btn_apply.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_apply.SetDefault()
        self.btn_apply.SetFocus()
        self.SetAffirmativeId(wx.ID_OK)

    def _create_close_button(self):
        bmp = spBitmap(CANCEL_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_close = CreateGenButton(self, wx.ID_CLOSE, bmp, text=" Cancel", tooltip="Close this frame", colour=color)
        self.btn_close.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_close.SetDefault()
        self.btn_close.SetFocus()
        self.SetEscapeId(wx.ID_CLOSE)

    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_close, flag=wx.LEFT, border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_apply, flag=wx.RIGHT, border=5)
        return button_box

    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout,         0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.content_layout,       1, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self._create_button_box(), 0, flag=wx.ALL|wx.EXPAND, border=5)
        self.SetMinSize((380,340))
        self.SetSizer( vbox )
        self.Centre()
        self.Enable()
        self.SetAutoLayout(True)
        self.SetFocus()
        self.Layout()
        self.Show(True)

    def _set_focus_component(self):
        self.btn_apply.SetFocus()

    # -----------------------------------------------------------------------

    def OnClose(self, event):
        self.SetEscapeId(wx.ID_CANCEL)

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

    # End GetData
    # -----------------------------------------------------------------------


