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

from wxgui.sp_images import WIZARD_WELCOME_SOUND_BMP
from wxgui.cutils.imageutils import ScaleImage


# ----------------------------------------------------------------------------

class WizardSoundDemo( wx.wizard.Wizard ):

    def __init__(self, parent):
        wx.wizard.Wizard.__init__(self, parent, -1, "SppasEdit Sound Demo")
        self.parent = parent

        page0 = WelcomePage(self, "Welcome")
        page1 = SorryPage(self, "Sorry")

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

        img = ScaleImage( wx.Image(WIZARD_WELCOME_SOUND_BMP, wx.BITMAP_TYPE_ANY), 460, 280)
        bmp = img.ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, bmp, (0, 0))

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)


#----------------------------------------------------------------------

class SorryPage(wx.wizard.WizardPageSimple):
    """ Welcome to the Demo. """

    def __init__(self, parent, title):
        """
        Constructor.
        """
        wx.wizard.WizardPageSimple.__init__(self, parent)

        wx.StaticText(self, -1, "Sorry... but no demo available!")

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

#----------------------------------------------------------------------
