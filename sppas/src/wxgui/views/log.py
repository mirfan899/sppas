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
# File: log.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# General libraries import
import sys
import os
import os.path
import shutil
import codecs
import wx

from wxgui.cutils.imageutils import spBitmap
from wxgui.sp_icons import REPORT_ICON
from wxgui.sp_icons import SAVE_FILE
from wxgui.sp_icons import CANCEL_ICON
from wxgui.sp_icons import APP_ICON
from wxgui.cutils.ctrlutils import CreateGenButton

from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE
from wxgui.sp_consts import MAIN_FONTSIZE

from wxgui.sp_consts import ERROR_COLOUR
from wxgui.sp_consts import INFO_COLOUR
from wxgui.sp_consts import IGNORE_COLOUR
from wxgui.sp_consts import WARNING_COLOUR
from wxgui.sp_consts import OK_COLOUR


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

ENCODING = 'utf-8'
ID_SAVE   = wx.NewId()
ID_CLOSE  = wx.NewId()


# ----------------------------------------------------------------------------
# class LogDialog
# ----------------------------------------------------------------------------

class LogDialog( wx.Dialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Frame allowing to show/save the procedure outcome report.

    """

    def __init__(self, parent, preferences, filename):
        """
        Constructor.

        @param parent is the sppas main frame (must contains preferences and
        parameters members).

        """
        wx.Dialog.__init__(self, parent, -1, title=FRAME_TITLE+" - Report", style=FRAME_STYLE)

        self.filename    = filename
        self.preferences = preferences
        self._create_gui()

        # Events of this frame
        #wx.EVT_CLOSE(self, self.OnClose)

    # End __init__
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------


    def _create_gui(self):
        self._init_infos()
        self._create_title_label()
        self._create_save_button()
        self._create_close_button()
        self._create_text_content() # after the creation of save button (to disable it if problem)
        self._layout_components()
        self._set_focus_component()


    def _init_infos( self ):
        wx.GetApp().SetAppName( "log" )
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
        bmp = wx.BitmapButton(self, bitmap=spBitmap(REPORT_ICON, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label = wx.StaticText(self, label="Procedure outcome report", style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)
        self.title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)


    def _create_text_content(self):
        try:
            with codecs.open(self.filename, 'r', ENCODING) as fp:
                logcontent = fp.read()
        except Exception as e:
            logcontent = "No report available...\n* * * Probably you don't have permission to write in the directory. Change the access rigth to solve the problem. * * *\n\nError is: %s"%str(e)
            self.btn_save.Enable(False)
        self.log_txt = wx.TextCtrl(self, -1, size=(620, 480), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)
        self.log_txt.SetDefaultStyle( wx.TextAttr( wx.BLACK,wx.WHITE ))
        self.log_txt.SetFont(wx.Font(MAIN_FONTSIZE, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New'))
        self.log_txt.SetValue(logcontent)
        i=0
        oldi=0
        while i>=0:
            i = logcontent.find("[ ", oldi)
            if logcontent.find("OK", i,i+14)>-1:
                self.log_txt.SetStyle(i,i+12, wx.TextAttr( OK_COLOUR ) )
            elif logcontent.find("ERROR", i,i+14)>-1:
                self.log_txt.SetStyle(i,i+12, wx.TextAttr( ERROR_COLOUR ) )
            elif logcontent.find("WARNING", i,i+14)>-1:
                self.log_txt.SetStyle(i,i+12, wx.TextAttr( WARNING_COLOUR ) )
            elif logcontent.find("INFO", i,i+14)>-1:
                self.log_txt.SetStyle(i,i+12, wx.TextAttr( INFO_COLOUR ) )
            elif logcontent.find("IGNORED", i,i+14)>-1:
                self.log_txt.SetStyle(i,i+12, wx.TextAttr( IGNORE_COLOUR ) )
            oldi=i+13


    def _create_save_button(self):
        bmp = spBitmap(SAVE_FILE, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_save = CreateGenButton(self, ID_SAVE, bmp, text="Save report as...", tooltip="Save the procedure outcome report", colour=color)
        self.btn_save.SetFont( self.preferences.GetValue('M_FONT'))
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.btn_save, ID_SAVE)


    def _create_close_button(self):
        bmp = spBitmap(CANCEL_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_close = CreateGenButton(self, wx.ID_CLOSE, bmp, text=" Close", tooltip="Close this frame and apply changes", colour=color)
        self.btn_close.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_close.SetDefault()
        self.btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)


    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_save,  flag=wx.RIGHT, border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_close, flag=wx.RIGHT, border=5)
        return button_box


    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout, 0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.log_txt, 1, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self._create_button_box(), 0, flag=wx.ALL|wx.EXPAND, border=5)
        self.SetSizerAndFit(vbox)


    def _set_focus_component(self):
        self.log_txt.SetFocus()


    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------


    def OnSave(self, evt):
        """
        Save the content in a text file.
        """
        filesel = None
        wildcard = "SPPAS log files (*-sppas.log)|*-sppas.log"
        fileName, fileExtension = os.path.splitext(self.filename)
        defaultDir  = os.path.dirname(self.filename)
        defaultFile = os.path.basename("Annotations-sppas.log")

        dlg = wx.FileDialog(
            self, message = "Save as...",
            defaultDir  = defaultDir,
            defaultFile = defaultFile,
            wildcard = wildcard,
            style = wx.FD_SAVE | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response.
        # If it is the OK response, process the data.
        if dlg.ShowModal() == wx.ID_OK:
            filesel = dlg.GetPath()
        dlg.Destroy()

        if filesel:
            # OK. We have a filename...
            # but if this is the default, don't do anything!
            if self.filename == filesel:
                return
            # or copy the file!
            try:
                shutil.copy(self.filename, filesel)
            # eg. src and dest are the same file
            except shutil.Error as e:
                dlg = wx.MessageDialog(self.GetParent(), 'Error: %s'%e, "Error while saving", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            # eg. source or destination doesn't exist
            except IOError as e:
                dlg = wx.MessageDialog(self.GetParent(), 'Error: %s'%e, "Error while saving", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

# ----------------------------------------------------------------------------
