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

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import wx.wizard

from sppas.src.ui.wxgui.sp_images import WIZARD_WELCOME_ZOOM_BMP
from sppas.src.ui.wxgui.sp_images import WIZARD_ZOOM_PANEL_BMP
from sppas.src.ui.wxgui.sp_images import WIZARD_ZOOM_KEYBOARD_BMP
from sppas.src.ui.wxgui.sp_images import WIZARD_ZOOM_MOUSE_BMP

from sppas.src.ui.wxgui.cutils.imageutils import ScaleImage

# ----------------------------------------------------------------------------


class WizardZoomDemo( wx.wizard.Wizard ):

    def __init__(self, parent):
        wx.wizard.Wizard.__init__(self, parent, -1, "DataViewer Zoom Demo")
        self.parent = parent

        page0 = WelcomePage(self, "Welcome")
        page1 = MainPage(self, "Main")
        page2 = KeyboardPage(self, "Keyboard")
        page3 = MouseMotionPage(self, "MouseMotion")
        page4 = ToolbarPage(self, "Toolbar")

        wx.wizard.WizardPageSimple.Chain(page0, page1)
        wx.wizard.WizardPageSimple.Chain(page1, page2)
        wx.wizard.WizardPageSimple.Chain(page2, page3)
        wx.wizard.WizardPageSimple.Chain(page3, page4)

        #self.FitToPage(page0)
        wx.CallAfter(self.SetSize,(480,400))
        self.RunWizard(page0)
        self.Destroy()

    def GetStatusBar(self):
        return self.parent.GetTopLevelParent().GetStatusBar()


# ----------------------------------------------------------------------------


class WelcomePage(wx.wizard.WizardPageSimple):
    """Welcome to the Demo."""

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        img = ScaleImage( wx.Image(WIZARD_WELCOME_ZOOM_BMP, wx.BITMAP_TYPE_ANY), 460, 280)
        bmp = img.ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, bmp, (0, 0))

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.bitmap, 0, wx.TOP|wx.ALIGN_CENTRE)
        self.SetSizer(sizer)


#----------------------------------------------------------------------


class MainPage(wx.wizard.WizardPageSimple):
    """Presentation of the main ways to zoom."""

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        panel = wx.Panel(self,-1, style=wx.NO_BORDER)
        panel.SetBackgroundColour("WHITE")

        wx.StaticText(panel, -1, "Three solutions for zooming: ", pos=(10,10))
        wx.StaticText(panel, -1, "   1 - using keyboard short-cuts ", pos=(10,40))
        wx.StaticText(panel, -1, "   2 - using mouse motion ", pos=(10,70))
        wx.StaticText(panel, -1, "   3 - clicking on icons ", pos=(10,100))

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(panel, 1, wx.EXPAND|wx.ALIGN_CENTRE, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

#----------------------------------------------------------------------


class KeyboardPage(wx.wizard.WizardPageSimple):
    """Presentation of the keyboard ways to zoom."""

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        panel1 = wx.Panel(self,-1, style=wx.NO_BORDER)
        panel1.SetBackgroundColour("WHITE")
        panel2 = wx.Panel(self,-1, style=wx.NO_BORDER)
        panel2.SetBackgroundColour("WHITE")

        wx.StaticText(panel1, -1,  "Zooming with Keyboard shortcuts: ", pos=(10,10))
        wx.StaticText(panel1, -1, "  - Ctrl+i allows to zoom in (time period is smaller).", pos=(10,40))
        wx.StaticText(panel1, -1, "  - Ctrl+o allows to zoom out (time period is greater).", pos=(10,70))

        bmp = wx.Image(WIZARD_ZOOM_KEYBOARD_BMP, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.StaticBitmap(panel2, -1, bmp, (10, 10))

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(panel1, 1, wx.EXPAND|wx.TOP|wx.ALIGN_CENTRE, 5)
        box.Add(panel2, 1, wx.EXPAND|wx.BOTTOM|wx.ALIGN_CENTRE, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

#----------------------------------------------------------------------


class MouseMotionPage(wx.wizard.WizardPageSimple):
    """Presentation of the keyboard ways to zoom."""

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        panel1 = wx.Panel(self,-1, style=wx.NO_BORDER)
        panel1.SetBackgroundColour("WHITE")
        panel2 = wx.Panel(self,-1, style=wx.NO_BORDER)
        panel2.SetBackgroundColour("WHITE")

        wx.StaticText(panel1, -1,  "Zooming with mouse motion: ", pos=(10,10))
        wx.StaticText(panel1, -1, "  - Shift + Mouse Motion allows to zoom vertically.", pos=(10,40))
        wx.StaticText(panel1, -1, "  - Ctrl + Mouse Motion allows to zoom time period.", pos=(10,70))

        bmp = wx.Image(WIZARD_ZOOM_MOUSE_BMP, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.StaticBitmap(panel2, -1, bmp, (10, 10))

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(panel1, 1, wx.EXPAND|wx.TOP|wx.ALIGN_CENTRE, 5)
        box.Add(panel2, 1, wx.EXPAND|wx.BOTTOM|wx.ALIGN_CENTRE, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

#----------------------------------------------------------------------


class ToolbarPage(wx.wizard.WizardPageSimple):
    """Presentation of the toolbar."""

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        panel1 = wx.Panel(self,-1, style=wx.NO_BORDER)
        panel2 = wx.Panel(self,-1, style=wx.NO_BORDER)
        panel1.SetBackgroundColour("WHITE")
        panel2.SetBackgroundColour("WHITE")

        bmp = wx.Image(WIZARD_ZOOM_PANEL_BMP, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(panel1, -1, bmp, (0, 0))

        wx.StaticText(panel2, -1, "Icons for zooming and scrolling are BLUE", pos=(10,10))

        box = wx.BoxSizer(wx.VERTICAL)

        box.Add(panel2, 1, wx.EXPAND|wx.BOTTOM|wx.ALIGN_CENTRE, 5)
        box.Add(panel1, 2, wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

#----------------------------------------------------------------------


