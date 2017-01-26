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

from sppas.src.wxgui.sp_images import WIZARD_WELCOME_MAIN_BMP
from sppas.src.wxgui.cutils.imageutils import ScaleImage

from .PointCtrlDemo import PointCtrlDemo
from .LabelCtrlDemo import LabelCtrlDemo
from .TierCtrlDemo import TierCtrlDemo
from .TrsCtrlDemo import TrsCtrlDemo
from .WaveCtrlDemo import WaveCtrlDemo
from .RulerCtrlDemo import RulerCtrlDemo
from .DisplayCtrlDemo import DisplayCtrlDemo


# ----------------------------------------------------------------------------

class WizardDisplayDemo( wx.wizard.Wizard ):

    def __init__(self, parent):
        wx.wizard.Wizard.__init__(self, parent, -1, "SppasEdit Main Demo")
        self.parent = parent

        page0 = WelcomePage(self, "Welcome")
        page1 = PointPage(self,   "Page 1")
        page2 = LabelPage(self,   "Page 2")
        page3 = TierPage(self,    "Page 3")
        page4 = TrsPage(self,     "Page 4")
        page5 = WavePage(self,    "Page 5")
        page6 = RulerPage(self,   "Page 6")
        page7 = DisplayPage(self, "Page 7")

        wx.wizard.WizardPageSimple.Chain(page0, page1)
        wx.wizard.WizardPageSimple.Chain(page1, page2)
        wx.wizard.WizardPageSimple.Chain(page2, page3)
        wx.wizard.WizardPageSimple.Chain(page3, page4)
        wx.wizard.WizardPageSimple.Chain(page4, page5)
        wx.wizard.WizardPageSimple.Chain(page5, page6)
        wx.wizard.WizardPageSimple.Chain(page6, page7)

        wx.CallAfter(self.SetSize,(480,400))
        #self.FitToPage(page0)
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

        img = ScaleImage( wx.Image(WIZARD_WELCOME_MAIN_BMP, wx.BITMAP_TYPE_ANY), 460, 280)
        bmp = img.ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, bmp, (0, 0))

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)


#----------------------------------------------------------------------


class PointPage(wx.wizard.WizardPageSimple):
    """ TimePoint Demo. """

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        w = PointCtrlDemo(self, -1)
        sizer.Add(w, 1, wx.ALL|wx.EXPAND, border=5)

#----------------------------------------------------------------------


class LabelPage(wx.wizard.WizardPageSimple):
    """ Label Demo. """

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        w = LabelCtrlDemo(self, -1)
        sizer.Add(w, 1, wx.ALL|wx.EXPAND, border=5)

#----------------------------------------------------------------------


class TierPage(wx.wizard.WizardPageSimple):
    """ Tier Demo. """

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        w = TierCtrlDemo(self, -1)
        sizer.Add(w, 1, wx.ALL|wx.EXPAND, border=5)

#----------------------------------------------------------------------


class TrsPage(wx.wizard.WizardPageSimple):
    """ Trs Demo. """

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        w = TrsCtrlDemo(self, -1)
        sizer.Add(w, 1, wx.ALL|wx.EXPAND, border=5)

#----------------------------------------------------------------------


class WavePage(wx.wizard.WizardPageSimple):
    """ Wave Demo. """

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        w = WaveCtrlDemo(self, -1)
        sizer.Add(w, 1, wx.ALL|wx.EXPAND, border=5)


#----------------------------------------------------------------------


class RulerPage(wx.wizard.WizardPageSimple):
    """ Ruler Demo. """

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        w = RulerCtrlDemo(self, -1)
        sizer.Add(w, 1, wx.ALL|wx.EXPAND, border=5)


#----------------------------------------------------------------------


class DisplayPage(wx.wizard.WizardPageSimple):
    """ Display Demo. """

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        w = DisplayCtrlDemo(self, -1)
        sizer.Add(w, 1, wx.ALL|wx.EXPAND, border=5)

#----------------------------------------------------------------------
