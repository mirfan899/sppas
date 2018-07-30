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
# File: useraggreement.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# General libraries import
import wx
import wx.richtext

from sppas.src.calculus.kappa import sppasKappa
from sppas.src.annotationdata.utils.tierutils import TierConverter

from sppas.src.ui.wxgui.dialogs.basedialog import spBaseDialog
from sppas.src.ui.wxgui.sp_icons import USERCHECK

# ----------------------------------------------------------------------------
# class UserAgreementDialog
# ----------------------------------------------------------------------------

class UserAgreementDialog(spBaseDialog):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Frame allowing to show user agreements between 2 tiers.

    """
    def __init__(self, parent, preferences, tiers={}):
        """
        Constructor.

        @param parent is a wx.Window or wx.Frame or wx.Dialog
        @param preferences (Preferences or Preferences_IO)
        @param tiers: a dictionary with key=filename, value=list of selected tiers

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - User Agreement")
        wx.GetApp().SetAppName("useragreement")

        self.tiers = tiers

        titlebox   = self.CreateTitle(USERCHECK, "User agreement of 2 tiers")
        contentbox = self._create_content()
        buttonbox  = self._create_buttons()

        self.LayoutComponents(titlebox,
                               contentbox,
                               buttonbox)

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_close = self.CreateCloseButton()
        return self.CreateButtonBox([],[btn_close])

    def _create_content(self):
        self.notebook = wx.Notebook(self)

        page1 = InformationPanel(self.notebook, self.preferences)
        page2 = KappaPanel(self.notebook, self.preferences)

        # add the pages to the notebook with the label to show on the tab
        self.notebook.AddPage(page1, "Information")
        self.notebook.AddPage(page2, "Cohen's Kappa")

        page1.ShowContent(self.tiers)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChanged)

        return self.notebook

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def OnNotebookPageChanged(self, event):
        oldselection = event.GetOldSelection()
        newselection = event.GetSelection()
        if oldselection != newselection:
            page = self.notebook.GetPage(newselection)
            page.ShowContent(self.tiers)


# ----------------------------------------------------------------------------
# Base Tier Panel
# ----------------------------------------------------------------------------

class BaseTierPanel(wx.Panel):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Base tier panel.

    """

    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)
        self.preferences = prefsIO

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.ShowNothing()
        self.sizer.FitInside(self)

    # ------------------------------------------------------------------------

    def ShowNothing(self):
        """
        Method to show a message in the panel.
        """
        self.sizer.DeleteWindows()
        self.sizer.Add(wx.StaticText(self, -1, "Nothing to view!"), 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.Refresh()

    # ------------------------------------------------------------------------

    def ShowContent(self, tiers):
        """
        Base method to show a content in the panel.
        """
        self.ShowNothing()

# ----------------------------------------------------------------------------
# First tab: information
# ----------------------------------------------------------------------------

class InformationPanel(BaseTierPanel):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: General information about tiers and their annotations.

    """

    def __init__(self, parent, prefsIO):
        BaseTierPanel.__init__(self, parent, prefsIO)

    # ------------------------------------------------------------------------

    def ShowContent(self, tiers):
        """
        Show a tier as list.

        """
        if not tiers:
            self.ShowNothing()
            return

        self.text_ctrl = wx.richtext.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
        self.text_ctrl.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        self.text_ctrl.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        self.text_ctrl.SetMinSize((600, 380))
        self.text_ctrl.SetEditable(False)
        self._create_text_content(tiers)

        self.sizer.DeleteWindows()
        self.sizer.Add(self.text_ctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.FitInside(self)
        self.SendSizeEvent()

    # ------------------------------------------------------------------------

    def _create_text_content(self, tiers):
        """
        Add the content in the RichTextCtrl.

        """
        if not tiers:
            self.text_ctrl.WriteText("Nothing to view!")
            return

        self.text_ctrl.WriteText("Selected tiers:\n")
        i = 0
        for filename,tiers in tiers.items():
            for t in tiers:
                self.text_ctrl.WriteText("    "+str(i)+". "+filename+" - "+t.GetName()+"\n")
                i = i+1
        self.text_ctrl.WriteText("\n")

        self.text_ctrl.WriteText("Confusion matrix:\n")
        self.text_ctrl.WriteText("\n")


# ----------------------------------------------------------------------------
# Second tab: Details of each annotation
# ----------------------------------------------------------------------------

class KappaPanel(BaseTierPanel):
    """Detailed-view of a tiers.

    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL

    """

    def __init__(self, parent, prefsIO):
        BaseTierPanel.__init__(self, parent, prefsIO)

    # ------------------------------------------------------------------------

    def ShowContent(self, tiers):
        """
        Show the Cohen's Kappa result, with detailed information.

        """
        self.text_ctrl = wx.richtext.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
        self.text_ctrl.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        self.text_ctrl.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        self.text_ctrl.SetMinSize((600, 380))
        self.text_ctrl.SetEditable(False)
        self._create_text_content(tiers)

        self.sizer.DeleteWindows()
        self.sizer.Add(self.text_ctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.FitInside(self)
        self.SendSizeEvent()

    # ------------------------------------------------------------------------

    def _create_text_content(self, tiers):
        """
        Add the content of the tier in the RichTextCtrl.
        """
        if not tiers:
            self.text_ctrl.WriteText("Nothing to view!")
            return

        self.text_ctrl.WriteText("Cohen's Kappa on labels of tiers:\n")
        tier = []
        for filename,tiers in tiers.items():
            for t in tiers:
                tier.append(t)
        self.text_ctrl.WriteText("\n")

        if len(tier) != 2:
            self.text_ctrl.WriteText("Cohen's Kappa can be estimated only with exactly 2 tiers. Got %d\n" % len(tier))
            return
        if tier[0].GetSize() != tier[1].GetSize():
            self.text_ctrl.WriteText("Cohen's Kappa on labels of tiers can be estimated only if the 2 tiers have the same number of annotations. "
                                     "Got %d and %d\n"%(len(tier[0]),len(tier[1])))
            return

        # Create the list of items in both tiers 1 and 2
        d1 = TierConverter(tier[0])
        items1 = d1.tier_to_items()
        d2 = TierConverter(tier[1])
        items2 = d2.tier_to_items()
        items = sorted(list(set(items1+items2)))

        p = d1.labels_to_vector(items)
        q = d2.labels_to_vector(items)

        kappa = sppasKappa(p, q)
        v = kappa.evaluate()
        self.text_ctrl.WriteText("value = "+str(v)+"\n")
