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
# File: sndroamerframe.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import logging

from baseframe                  import ComponentFrame
from wxgui.sp_icons                import SNDROAMER_APP_ICON
from wxgui.cutils.imageutils       import spBitmap
from wxgui.clients.sndroamerclient import SndRoamerClient

# ----------------------------------------------------------------------------

class SndRoamerFrame( ComponentFrame ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: SndRoamer allows to manipulate speech files.

    """

    def __init__(self, parent, id, args={}):
        """
        Creates a new ComponentFrame instance for SndRoamer component.
        """
        ComponentFrame.__init__(self, parent, id, args)

        self._update_about()
        self._append_in_menu()
        self._append_in_toolbar()

    # End __init__
    # ------------------------------------------------------------------------


    def _update_about(self):
        """
        Update information of the about dialog box.
        """
        description = """SndRoamer is a component to play and get information about speech files."""
        self._about.SetName('SndRoamer')
        self._about.SetVersion('1.0')
        self._about.SetDescription(description)

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(SNDROAMER_APP_ICON) )
        self._about.SetIcon(_icon)

    # End _update_about
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

    # End _append_in_menu
    # ------------------------------------------------------------------------


    def _append_in_toolbar(self):
        """
        Append new items in the toolbar.
        """
        toolbar = self.GetToolBar()

        # nothing to add for now! but it's possible and it works (tested).
        # see documentation:
        # http://xoomer.virgilio.it/infinity77/wxPython/Widgets/wx.ToolBar.html

        toolbar.Realize()

    # End _append_in_toolbar
    # ------------------------------------------------------------------------


    def CreateClient(self, parent, prefsIO):
        """
        Override.
        """
        return SndRoamerClient(parent,prefsIO)

    # End CreateClient
    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------
