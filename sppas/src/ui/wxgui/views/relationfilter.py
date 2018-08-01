# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    wxgui.views.relationfilter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx

from sppas.src.ui.wxgui.dialogs.basedialog import spBaseDialog
from sppas.src.ui.wxgui.sp_icons import FILTER_RELATION

from sppas.src.ui.wxgui.cutils.textutils import TextValidator
from sppas.src.ui.wxgui.panels.relationstable import AllensRelationsTable

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

DEFAULT_TIERNAME = "Filtered tier"
# ----------------------------------------------------------------------------


class RelationFilterDialog(spBaseDialog):
    """Dialog for the user to fix a set of filters to be applied to a tier.
    
    :author:  Brigitte Bigi
    :contact: brigitte.bigi@gmail.com
    :license: GPL, v3

    """
    
    def __init__(self, parent, preferences, tierX=[], tierY=[]):
        """Create a new dialog."""
        
        spBaseDialog.__init__(self, parent, preferences, title=" - RelationFilter")
        wx.GetApp().SetAppName("relationfilter")

        # Members
        self.tierX = tierX
        self.tierY = tierY

        titlebox = self.CreateTitle(FILTER_RELATION,
                                    "Filter a tier X, depending on time-relations with a tier Y")
        contentbox = self._create_content()
        buttonbox = self._create_buttons()

        self.LayoutComponents(titlebox,
                              contentbox,
                              buttonbox)

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_cancel = self.CreateCancelButton()
        btn_okay = self.CreateOkayButton()
        return self.CreateButtonBox([btn_cancel],[btn_okay])

    def _create_content(self):
        self.xy_layout = self._create_xy_layout()
        self.filterpanel = RelationFilterPanel(self, self.preferences)
        self.tiername_layout = self._create_tiername_layout()

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.xy_layout, 0, flag=wx.ALL | wx.EXPAND, border=0)
        vbox.Add(self.filterpanel, 1, flag=wx.ALL | wx.EXPAND, border=4)
        vbox.Add(self.tiername_layout, 0, flag=wx.ALL | wx.EXPAND, border=0)
        return vbox

    def _create_tiername_layout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_tiername = wx.StaticText(self,
                                       label="Name of filtered tier: ",
                                       style=wx.ALIGN_CENTER)
        title_tiername.SetFont(self.preferences.GetValue('M_FONT'))
        self.text_outtiername = wx.TextCtrl(self,
                                            size=(250, -1),
                                            validator=TextValidator())
        self.text_outtiername.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.text_outtiername.SetForegroundColour(wx.Colour(128, 128, 128))
        self.text_outtiername.SetValue(DEFAULT_TIERNAME)
        self.text_outtiername.Bind(wx.EVT_TEXT, self.OnTextChanged)
        self.text_outtiername.Bind(wx.EVT_SET_FOCUS, self.OnTextClick)

        sizer.Add(title_tiername,
                  flag=wx.ALL | wx.wx.ALIGN_CENTER_VERTICAL,
                  border=5)
        sizer.Add(self.text_outtiername,
                  flag=wx.EXPAND | wx.ALL | wx.wx.ALIGN_CENTER_VERTICAL,
                  border=5)
        return sizer

    def _create_xy_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        x = self._createX()
        y = self._createY()
        sizer.Add(x, proportion=1, flag=wx.EXPAND | wx.RIGHT | wx.LEFT, border=5)
        sizer.Add(y, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        return sizer

    def _createX(self):
        textX = wx.StaticText(self, -1, label="Tier X: ")
        tiersX = wx.TextCtrl(self, -1, size=(250, 24), style=wx.TE_READONLY)
        tiersX.SetValue(", ".join(self.tierX))
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(textX,  0, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=4)
        s.Add(tiersX, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, border=0)
        return s

    def _createY(self):
        textY = wx.StaticText(self, -1, label="Tier Y: ")
        self.texttierY = wx.TextCtrl(self, size=(250, 24), validator=TextValidator())
        self.texttierY.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.texttierY.SetForegroundColour(wx.Colour(128, 128, 128))
        self.texttierY.SetValue('')
        self.texttierY.Bind(wx.EVT_TEXT, self.OnTextChanged)
        self.texttierY.Bind(wx.EVT_SET_FOCUS, self.OnTextClick)
        btn = wx.Button(self, 1, 'Fix name', (50, 24))
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(textY, 0, wx.ALIGN_CENTER_VERTICAL,   border=0)
        s.Add(self.texttierY, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, border=0)
        s.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL, border=0)
        btn.Bind(wx.EVT_BUTTON, self.OnChooseY)
        return s

    # ------------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------------

    def OnChooseY(self, event):
        dlg = wx.SingleChoiceDialog(self,
                                    "Fix Y tier from this list:",
                                    "RelationFilter", self.tierY)

        if dlg.ShowModal() == wx.ID_OK:
            selection = dlg.GetSelection()
            self.texttierY.SetValue(self.tierY[selection])

        dlg.Destroy()

    def OnTextClick(self, event):
        text = event.GetEventObject()
        text.SetForegroundColour(wx.BLACK)
        if text.GetValue().strip() == "":
            self.OnTextErase(event)
        event.Skip()

    def OnTextChanged(self, event):
        text = event.GetEventObject()
        text.SetFocus()
        text.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        text.Refresh()

    def OnTextErase(self, event):
        text = event.GetEventObject()
        text.SetValue('')
        text.SetFocus()
        text.SetBackgroundColour(wx.Colour(245, 220, 240))
        text.Refresh()

    # ------------------------------------------------------------------------
    # Getters...
    # ------------------------------------------------------------------------

    def GetSelectedData(self):
        """Return the content of the checklist as a list of data."""
        return self.filterpanel.GetSelectedData()

    def GetFiltererdTierName(self):
        """Return the future name for the filtered tier."""
        return self.text_outtiername.GetValue().strip()

    def GetRelationTierName(self):
        """Return the name for the Y tier."""
        return self.texttierY.GetValue().strip()

    def GetAnnotationFormat(self):
        return self.filterpanel.opt.GetValue()

# ----------------------------------------------------------------------------


class RelationFilterPanel(wx.Panel):
    """Panel to fix filters to be used with rel method of 'sppasFilter()'.

    :author:  Brigitte Bigi
    :contact: brigitte.bigi@gmail.com
    :license: GPL

    """

    def __init__(self, parent, prefsIO):
        wx.Panel.__init__(self, parent, size=(580, 320))
        self.SetBackgroundColour(prefsIO.GetValue('M_BG_COLOUR'))

        # Members
        self.preferences = prefsIO
        self.data = []

        self.relTable = AllensRelationsTable(self)
        self.opt = wx.CheckBox(self, label='Replace label of X by the relation name.')
        self.opt.SetBackgroundColour(prefsIO.GetValue('M_BG_COLOUR'))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.relTable, proportion=1, flag=wx.EXPAND | wx.BOTTOM, border=5)
        sizer.Add(self.opt, flag=wx.EXPAND | wx.TOP, border=5)
        self.SetSizer(sizer)
        self.SetMinSize((380, 280))
        self.Center()

    # ----------------------------------------------------------------------
    # Public Methods
    # ----------------------------------------------------------------------

    def GetSelectedData(self):
        """Return a predicate, constructed from the data."""
        return self.relTable.GetData()
