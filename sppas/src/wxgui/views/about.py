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
# File: about.py
# ----------------------------------------------------------------------------

import wx

from wxgui.dialogs.basedialog import spBaseDialog
from wxgui.sp_icons import ABOUT_ICON
from wxgui.panels.about import AboutSPPAS

# ----------------------------------------------------------------------------

class AboutDialog( spBaseDialog ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      This class is used to display an about frame.

    """
    def __init__(self, parent, preferences):
        spBaseDialog.__init__(self, parent, preferences, title="About")
        wx.GetApp().SetAppName( "about" )

        titlebox   = self.CreateTitle(ABOUT_ICON,"About")
        contentbox = AboutSPPAS( self,preferences )
        buttonbox  = self.CreateButtonBox( [],[self.CreateOkayButton()] )

        self.LayoutComponents( titlebox,
                               contentbox,
                               buttonbox )

# ------------------------------------------------------------------------

def ShowAboutDialog(parent, preferences):
    dialog = AboutDialog(parent, preferences)
    dialog.SetMinSize((520,580))
    dialog.ShowModal()
    dialog.Destroy()
