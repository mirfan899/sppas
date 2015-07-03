# coding=UTF8
# Copyright (C) 2014  Brigitte Bigi
#
# This file is part of DataEditor.
#
# DataEditor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DataEditor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DataEditor.  If not, see <http://www.gnu.org/licenses/>.
#


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import wx.wizard
import os
import os.path

from wxgui.sp_images import WIZARD_WELCOME_SCROLL_BMP
from wxgui.sp_images import WIZARD_SCROLL_PANEL_BMP
from wxgui.cutils.imageutils import ScaleImage


# ----------------------------------------------------------------------------


class WizardScrollDemo( wx.wizard.Wizard ):

    def __init__(self, parent):
        wx.wizard.Wizard.__init__(self, parent, -1, "SppasEdit Scroll Demo")
        self.parent = parent

        page0 = WelcomePage(self, "Welcome")
        page1 = ToolbarPage(self, "Toolbar")

        wx.wizard.WizardPageSimple.Chain(page0, page1)

        #self.FitToPage(page0)
        wx.CallAfter(self.SetSize,(480,400))
        self.RunWizard(page0)
        self.Destroy()

    def GetStatusBar(self):
        return self.parent.GetTopLevelParent().GetStatusBar()


# ----------------------------------------------------------------------------


class WelcomePage(wx.wizard.WizardPageSimple):
    """ Welcome to the Demo. """

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        img = ScaleImage( wx.Image(WIZARD_WELCOME_SCROLL_BMP, wx.BITMAP_TYPE_ANY), 460, 280)
        bmp = img.ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, bmp, (0, 0))

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)


#----------------------------------------------------------------------


class ToolbarPage(wx.wizard.WizardPageSimple):
    """ Presentation of the toolbar. """

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        panel1 = wx.Panel(self,-1, style=wx.NO_BORDER)
        panel2 = wx.Panel(self,-1, style=wx.NO_BORDER)
        panel1.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        panel2.SetBackgroundColour("WHITE")

        img = wx.Image(WIZARD_SCROLL_PANEL_BMP, wx.BITMAP_TYPE_ANY)
        bmp = img.ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(panel1, -1, bmp, (0, 0))

        wx.StaticText(panel2, -1, "Icons for zooming and scrolling are BLUE", pos=(10,10))

        box = wx.BoxSizer(wx.VERTICAL)

        box.Add(panel1, 1, wx.BOTTOM|wx.ALIGN_CENTRE, 5)
        box.Add(panel2, 2, wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

#----------------------------------------------------------------------

