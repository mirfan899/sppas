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
# File: settings.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os
import wx
from wx.lib import stattext

from annotationdata.io import extensions_out_multitiers as extensions_out

from wxgui.sp_icons import BG_COLOR_ICON
from wxgui.sp_icons import FG_COLOR_ICON
from wxgui.sp_icons import FONT_ICON

from wxgui.sp_icons import SETTINGS_ICON
from wxgui.sp_icons import SAVE_FILE
from wxgui.sp_icons import APPLY_ICON
from wxgui.sp_icons import CANCEL_ICON
from wxgui.sp_icons import APP_ICON

from wxgui.cutils.imageutils import spBitmap
from wxgui.cutils.ctrlutils import CreateGenButton

from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE

from sp_glob import ICONS_PATH


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

ID_SAVE   = wx.NewId()


# ----------------------------------------------------------------------------
# class SettingsDialog
# ----------------------------------------------------------------------------

class SettingsDialog( wx.Dialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to fix all user's settings, with a Dialog.

    Dialog for the user to fix all preferences.

    """

    def __init__(self, parent, prefsIO):
        """
        Create a new dialog fo fix preferences, sorted in a notebook.

        """

        wx.Dialog.__init__(self, parent, title=FRAME_TITLE+" - Settings", style=FRAME_STYLE)

        # Members
        self.preferences = prefsIO
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
        self._create_notebook()
        self._create_save_button()
        self._create_cancel_button()
        self._create_close_button()
        self._layout_components()
        self._set_focus_component()


    def _init_infos( self ):
        wx.GetApp().SetAppName( "settings" )
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
        bmp = wx.BitmapButton(self, bitmap=spBitmap(SETTINGS_ICON, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label = wx.StaticText(self, label="User settings", style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)
        self.title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)


    def _create_notebook(self):
        self.notebook = wx.Notebook(self)
        page1 = PrefsGeneralPanel(self.notebook, self.preferences)
        page2 = PrefsThemePanel(self.notebook, self.preferences)
        page3 = PrefsAnnotationPanel(self.notebook, self.preferences)
        # add the pages to the notebook with the label to show on the tab
        self.notebook.AddPage(page1, "General")
        self.notebook.AddPage(page2, "Icons Theme")
        self.notebook.AddPage(page3, "Annotation")


    def _create_save_button(self):
        bmp = spBitmap(SAVE_FILE, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_save = CreateGenButton(self, wx.ID_SAVE, bmp, text="Save", tooltip="Save the settings", colour=color)
        self.btn_save.SetFont( self.preferences.GetValue('M_FONT'))
        self.Bind(wx.EVT_BUTTON, self.onSave, self.btn_save, wx.ID_SAVE)


    def _create_cancel_button(self):
        bmp = spBitmap(CANCEL_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_cancel = CreateGenButton(self, wx.ID_CANCEL, bmp, text=" Cancel", tooltip="Close this frame", colour=color)
        self.btn_cancel.SetFont( self.preferences.GetValue('M_FONT'))
        self.SetEscapeId(wx.ID_CANCEL)


    def _create_close_button(self):
        bmp = spBitmap(APPLY_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_close = CreateGenButton(self, wx.ID_OK, bmp, text=" Close", tooltip="Close this frame", colour=color)
        self.btn_close.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_close.SetDefault()
        self.btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_OK)


    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(self.btn_save, flag=wx.RIGHT, border=5)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_cancel, flag=wx.RIGHT, border=5)
        button_box.Add(self.btn_close, flag=wx.RIGHT, border=5)
        return button_box


    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout, 0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.notebook, 1, flag=wx.ALL|wx.EXPAND, border=0)
        vbox.Add(self._create_button_box(), 0, flag=wx.ALL|wx.EXPAND, border=5)
        self.SetSizerAndFit(vbox)


    def _set_focus_component(self):
        self.notebook.SetFocus()


    #-------------------------------------------------------------------------
    # Callbacks
    #-------------------------------------------------------------------------


    def onSave(self, event):
        """ Save preferences in a file. """
        self.preferences.Write()

    #-------------------------------------------------------------------------

    def onClose(self, event):
        self.SetEscapeId(wx.ID_CANCEL)

    #-------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Getters...
    #-------------------------------------------------------------------------

    def GetPreferences(self):
        """ Return the preferences. """
        return self.preferences

    #-------------------------------------------------------------------------


# ----------------------------------------------------------------------------


class PrefsGeneralPanel( wx.Panel ):
    """
    Main Frame settings: background color, foreground color and font, etc.
    """

    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)
        self.preferences = prefsIO

        gbs = self.__create_sizer()

        self.UpdateUI()
        self.SetSizer(gbs)

    # End __init__
    # ------------------------------------------------------------------------


    def __create_sizer(self):

        gbs = wx.GridBagSizer(hgap=5, vgap=5)

        # ---------- Background color

        txt_bg = wx.StaticText(self, -1, "Background color: ")
        gbs.Add(txt_bg, (0,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        self.btn_color_bg = wx.BitmapButton(self, -1, spBitmap( BG_COLOR_ICON, 24, theme=self.preferences.GetValue('M_ICON_THEME')))
        self.btn_color_bg.Bind(wx.EVT_BUTTON, self.onColorDlg, self.btn_color_bg)
        gbs.Add(self.btn_color_bg, (0,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        # ---------- Foreground color

        txt_fg = wx.StaticText(self, -1, "Foreground color: ")
        gbs.Add(txt_fg, (1,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        self.btn_color_fg = wx.BitmapButton(self, -1, spBitmap( FG_COLOR_ICON, 24, theme=self.preferences.GetValue('M_ICON_THEME') ))
        self.btn_color_fg.Bind(wx.EVT_BUTTON, self.onColorDlg, self.btn_color_fg)
        gbs.Add(self.btn_color_fg, (1,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        # ---------- Font

        txt_font = wx.StaticText(self, -1, "Font: ")
        gbs.Add(txt_font, (2,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        btn_font = wx.BitmapButton(self, -1, spBitmap( FONT_ICON, 24, theme=None ))
        self.Bind(wx.EVT_BUTTON, self.onSelectFont, btn_font)
        gbs.Add(btn_font, (2,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        # ---------- Sample text

        self.sampleText = stattext.GenStaticText(self, -1, u"  This is a sample text.?!§+={}[]#&$€%éèàù")
        self.sampleText.SetFont( self.preferences.GetValue('M_FONT') )
        self.sampleText.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        self.sampleText.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )

        gbs.Add(self.sampleText, (3,0), (1,2), flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, border=5)

        # ---------- tips

        txt_tips = wx.StaticText(self, -1, "Show tips at start-up: ")
        gbs.Add(txt_tips, (4,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        btn_tips = wx.CheckBox(self, -1, "")
        btn_tips.SetValue( self.preferences.GetValue('M_TIPS'))
        self.Bind(wx.EVT_CHECKBOX, self.onTipsChecked, btn_tips)
        gbs.Add(btn_tips, (4,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        # ----------

        gbs.AddGrowableCol(1)

        return gbs

    # ------------------------------------------------------------------------


    def UpdateUI(self):
        """
        Update the sample to look like the chosen decoration.
        """
        self.sampleText.SetFont( self.preferences.GetValue('M_FONT') )
        self.sampleText.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        self.sampleText.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )

        self.Layout()

    # End UpdateUI
    #-------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Callbacks
    #-------------------------------------------------------------------------

    def onColorDlg(self, event):
        """
        Open a dialog to choose a color, then fix it.
        """
        # get the button that was clicked
        button = event.GetEventObject()

        # open the dialog
        dlg = wx.ColourDialog(self)

        # Ensure the full colour dialog is displayed,
        # not the abbreviated version.
        dlg.GetColourData().SetChooseFull(True)

        if dlg.ShowModal() == wx.ID_OK:
            data  = dlg.GetColourData()
            color = data.GetColour()
            if button == self.btn_color_bg:
                self.preferences.SetValue( 'M_BG_COLOUR', 'wx.Colour', color )
            else:
                self.preferences.SetValue( 'M_FG_COLOUR', 'wx.Colour', color )
            self.UpdateUI()

        dlg.Destroy()

    # End onColorDlg
    #-------------------------------------------------------------------------


    def onSelectFont(self, event):
        """
        Open a dialog to choose a font, then fix it.
        """
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour( self.preferences.GetValue('M_FG_COLOUR') ) # set font colour
        data.SetInitialFont( self.preferences.GetValue('M_FONT') ) # set font

        dlg = wx.FontDialog(self, data)

        if dlg.ShowModal() == wx.ID_OK:
            data   = dlg.GetFontData()
            font   = data.GetChosenFont()
            color  = data.GetColour()
            self.preferences.SetValue( 'M_FONT', 'wx.Font', font )
            self.preferences.SetValue( 'M_FG_COLOUR', 'wx.Colour', color )
            self.UpdateUI()

        dlg.Destroy()

    # End onSelectFont
    #-------------------------------------------------------------------------


    def onTipsChecked(self, event):
        """ Tips at start-up. """
        self.preferences.SetValue( 'M_TIPS', 'bool', event.GetEventObject().GetValue() )

    # End onTipsChecked
    #-------------------------------------------------------------------------


#-----------------------------------------------------------------------------


# ----------------------------------------------------------------------------


class PrefsAnnotationPanel( wx.Panel ):
    """ Panel to fix prefs for annotations. """

    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)

        self.preferences = prefsIO

        # ---------- Annotations file extensions

        currentext = self.preferences.GetValue('M_OUTPUT_EXT')
        currentchoice = extensions_out.index(currentext)

        self.radiobox = wx.RadioBox(self, label="Annotations file format: ",
                                    choices=extensions_out, majorDimension=1) # majorDimension is the nb max of columns
        # check the current theme
        self.radiobox.SetSelection( currentchoice )
        # bind any theme change
        self.Bind(wx.EVT_RADIOBOX, self.onOutputFormat, self.radiobox)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.radiobox, 0, flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5)
        self.SetSizer(s)

    #-------------------------------------------------------------------------

    def onOutputFormat(self, event):
        """ File format of automatic annotations."""
        idx = self.radiobox.GetSelection()
        self.preferences.SetValue( 'M_OUTPUT_EXT', 'str', extensions_out[idx] )

    # End onOutputFormat
    #-------------------------------------------------------------------------


# ----------------------------------------------------------------------------


class PrefsThemePanel( wx.Panel ):
    """ Panel with a radiobox to choose the theme of the icons. """

    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)

        self.preferences = prefsIO

        self.iconthemes = os.listdir(ICONS_PATH)
        currenttheme = self.preferences.GetValue('M_ICON_THEME')
        currentchoice = self.iconthemes.index(currenttheme)

        self.radiobox = wx.RadioBox(self, label="Theme of the icons: ",
                                    choices=self.iconthemes, majorDimension=1)
        # check the current theme
        self.radiobox.SetSelection( currentchoice )

        # bind any theme change
        self.Bind(wx.EVT_RADIOBOX, self.onIconThemeClick, self.radiobox)

        text = "To apply the theme change,\nclick on Save button, then Close and re-start SPPAS."
        txt = wx.StaticText(self, -1, text, style=wx.ALIGN_CENTER|wx.NO_BORDER)
        font = wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.NORMAL)
        txt.SetFont(font)
        txt.SetForegroundColour( wx.RED )

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.radiobox, 2, flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5)
        s.Add(txt, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.SetSizer(s)

    #-------------------------------------------------------------------------


    def onIconThemeClick(self, event):
        """ Set the new theme. """
        idxtheme = self.radiobox.GetSelection()
        self.preferences.SetValue( 'M_ICON_THEME', 'str', self.iconthemes[idxtheme] )

    #-------------------------------------------------------------------------

# ----------------------------------------------------------------------------
