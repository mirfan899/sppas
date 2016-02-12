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
#       Copyright (C) 2011-2016  Brigitte Bigi
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
# File: dataroamerframe.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx

from baseframe import ComponentFrame

from wxgui.sp_icons   import DATAROAMER_APP_ICON
from wxgui.sp_icons   import NEW_FILE
from wxgui.sp_icons   import SAVE_FILE
from wxgui.sp_icons   import SAVE_AS_FILE
from wxgui.sp_icons   import SAVE_ALL_FILE
from wxgui.sp_consts  import TB_ICONSIZE

from wxgui.cutils.imageutils        import spBitmap
from wxgui.clients.dataroamerclient import DataRoamerClient

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

NEW_ID      = wx.NewId()
SAVE_AS_ID  = wx.NewId()
SAVE_ALL_ID = wx.NewId()

# ----------------------------------------------------------------------------

class DataRoamerFrame( ComponentFrame ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: DataRoamer allows to manipulate annotated files.

    """

    def __init__(self, parent, id, args={}):
        """
        Creates a new ComponentFrame instance for DataRoamer component.
        """
        ComponentFrame.__init__(self, parent, id, args)

        self._update_about()
        self._append_in_menu()
        self._append_in_toolbar()

    # ------------------------------------------------------------------------

    def _update_about(self):
        """
        Update information of the about dialog box.
        """
        description = """DataRoamer is a component to play and get information about speech files."""
        self._about.SetName('DataRoamer')
        self._about.SetVersion('2.0')
        self._about.SetDescription(description)
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(DATAROAMER_APP_ICON) )
        self._about.SetIcon(_icon)

    # ------------------------------------------------------------------------

    def _append_in_menu(self):
        """
        Append new items in a menu or a new menu in the menubar.
        """
        menubar = self.GetMenuBar()
        menus = menubar.GetMenus()
        # nothing to add for now! but it's possible and it works (tested).
        # see documentation:
        # http://www.wxpython.org/docs/api/wx.MenuBar-class.html
        # http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.Menu.html

    # ------------------------------------------------------------------------

    def _append_in_toolbar(self):
        """
        Append new items in the toolbar.
        """
        toolbar = self.GetToolBar()

        # Define the size of the icons and buttons
        #iconSize = (TB_ICONSIZE, TB_ICONSIZE)

        toolbar.InsertLabelTool(8, NEW_ID,       "New",      spBitmap(NEW_FILE,      TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        toolbar.InsertLabelTool(9, wx.ID_SAVE,   "Save",     spBitmap(SAVE_FILE,     TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        toolbar.InsertLabelTool(10, SAVE_AS_ID,  "Save as",  spBitmap(SAVE_AS_FILE,  TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        toolbar.InsertLabelTool(11, SAVE_ALL_ID, "Save all", spBitmap(SAVE_ALL_FILE, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )

        toolbar.InsertSeparator(12)
        toolbar.Realize()

        # events
        eventslist = [ NEW_ID, wx.ID_SAVE, SAVE_AS_ID, SAVE_ALL_ID ]
        for event in eventslist:
            wx.EVT_TOOL(self, event, self.DataRoamerProcessEvent)

    # ------------------------------------------------------------------------

    def _add_accelerator(self):
        """
        Replace the accelerator table.
        """

        # New with CTRL+N
        accelN = wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('N'), NEW_ID)
        # Save with CTRL+S
        accelS = wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('S'), wx.ID_SAVE)
        # Save all with CTRL+SHIFT+S
        accelSS = wx.AcceleratorEntry(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('S'), SAVE_ALL_ID)
        # Quit with ATL+F4
        accelQ = wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F4, wx.ID_EXIT)

        accel_tbl = wx.AcceleratorTable([ accelQ, accelN, accelS, accelSS ])
        self.SetAcceleratorTable(accel_tbl)

    # ------------------------------------------------------------------------

    def CreateClient(self, parent, prefsIO):
        """
        Override.
        """
        return DataRoamerClient( parent,prefsIO )

    # ------------------------------------------------------------------------

    def DataRoamerProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.
        """
        ide = event.GetId()

        if ide == NEW_ID:
            self.OnNew(event)
            return True
        elif ide == wx.ID_SAVE:
            self.OnSave(event)
            return True
        elif ide == SAVE_AS_ID:
            self.OnSaveAs(event)
            return True
        elif ide == SAVE_ALL_ID:
            self.OnSaveAll(event)
            return True

        return wx.GetApp().ProcessEvent(event)

    # ------------------------------------------------------------------------

    def OnNew(self, event):
        """
        Ask the client to add a new file.
        """
        self._clientpanel.New()

    def OnSave(self, event):
        """
        Ask the client to save the current file.
        """
        self._clientpanel.Save()

    def OnSaveAs(self, event):
        """
        Ask the client to save the current file, propose to change the name.
        """
        self._clientpanel.SaveAs()

    def OnSaveAll(self, event):
        """
        Ask the client to save all opened files.
        """
        self._clientpanel.SaveAll()

# ----------------------------------------------------------------------------
