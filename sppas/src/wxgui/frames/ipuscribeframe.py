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
# File: ipuscribeframe.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx

from wxgui.sp_icons   import IPUSCRIBE_APP_ICON
from wxgui.sp_icons   import SAVE_FILE
from wxgui.sp_icons   import SAVE_ALL_FILE
from wxgui.sp_consts  import TB_ICONSIZE

from baseframe                     import ComponentFrame
from wxgui.clients.ipuscribeclient import IPUscribeClient
from wxgui.cutils.imageutils       import spBitmap

SAVE_ALL_ID = wx.NewId()

# ----------------------------------------------------------------------------

class IPUscribeFrame( ComponentFrame ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: IPUscribe allows to transcribe manually speech files inside IPUs.

    """

    def __init__(self, parent, id, prefsIO):
        """
        Creates a new ComponentFrame instance for IPUscribe component.
        """
        arguments = {}
        arguments['files'] = []
        arguments['title'] = "SPPAS - IPUscriber"
        arguments['type']  = "SOUNDFILES"
        arguments['icon']  = IPUSCRIBE_APP_ICON
        arguments['prefs'] = prefsIO

        ComponentFrame.__init__(self, parent, id, arguments)

        self._append_in_menu()
        self._append_in_toolbar()
        self._add_accelerator()

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
        iconSize = (TB_ICONSIZE, TB_ICONSIZE)

        toolbar.InsertLabelTool(8, wx.ID_SAVE, "Save",      spBitmap(SAVE_FILE, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        toolbar.InsertLabelTool(9, SAVE_ALL_ID, "Save all", spBitmap(SAVE_ALL_FILE, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )

        toolbar.InsertSeparator(10)
        toolbar.Realize()

        # events
        eventslist = [ wx.ID_SAVE, SAVE_ALL_ID ]
        for event in eventslist:
            wx.EVT_TOOL(self, event, self.IPUscribeProcessEvent)

        # see documentation:
        # http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.ToolBar.html

    # ------------------------------------------------------------------------

    def _add_accelerator(self):
        """
        Replace the accelerator table.
        """

        # Save with CTRL+S
        accelS = wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('S'), wx.ID_SAVE)
        # Save all with CTRL+SHIFT+S
        accelSS = wx.AcceleratorEntry(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('S'), SAVE_ALL_ID)
        # Quit with ATL+F4
        accelQ = wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F4, wx.ID_EXIT)

        accel_tbl = wx.AcceleratorTable([ accelQ, accelS, accelSS ])
        self.SetAcceleratorTable(accel_tbl)

    # ------------------------------------------------------------------------

    def CreateClient(self, parent, prefsIO):
        """
        Override.
        """
        return IPUscribeClient(parent,prefsIO)

    # ------------------------------------------------------------------------

    def IPUscribeProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.
        """
        id = event.GetId()

        if id == wx.ID_SAVE:
            # add a file in the file manager
            self.OnSave(event)
            return True
        elif id == SAVE_ALL_ID:
            # add a file in the file manager
            self.OnSaveAll(event)
            return True

        return wx.GetApp().ProcessEvent(event)

    # ------------------------------------------------------------------------

    def OnSave(self, event):
        """
        Ask to save the current file.
        """
        self._clientpanel.Save()


    def OnSaveAll(self, event):
        """
        Ask to save all opened files.
        """
        self._clientpanel.SaveAll()

# ----------------------------------------------------------------------------
