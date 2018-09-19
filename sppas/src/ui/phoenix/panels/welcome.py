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

    ui.phoenix.panels.welcome.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx

from sppas.src.config import sg
from ..controls.texts import sppasTitleText, sppasMessageText
from ..tools import sppasSwissKnife

# ---------------------------------------------------------------------------


class sppasWelcomePanel(wx.Panel):
    """Create a panel to display a welcome message.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasWelcomePanel, self).__init__(
            parent=parent,
            name="welcome"
        )
        self.SetBackgroundColour(parent.GetBackgroundColour())

        # Create a title
        st = sppasTitleText(
            parent=self,
            label="Installation issue...",
            style=wx.ALIGN_CENTER_HORIZONTAL)
        st.SetBackgroundColour(parent.GetBackgroundColour())

        # Create the welcome message
        message = \
            "The Graphical User Interface can't work because "\
            "{:s} requires WxPython version 3 but version 4 is installed.\n" \
            "Yet the Command-Line User Interface still works.\n\n"\
            "For any help, see the web page for installation instructions " \
            "and chapter 2 of the documentation.\n\n"\
            "{:s}".format(sg.__name__, sg.__url__)
        txt = sppasMessageText(self, message)

        bmp = sppasSwissKnife.get_bmp_image('splash_transparent', 100)
        sbmp = wx.StaticBitmap(self, wx.ID_ANY, bmp)
        sbmp.SetBackgroundColour(parent.GetBackgroundColour())

        # Organize the title and message
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sbmp, 2, wx.ALL | wx.EXPAND, 0)
        sizer.AddStretchSpacer(1)
        sizer.Add(st, 0, wx.ALL | wx.EXPAND, 0)
        sizer.AddStretchSpacer(1)
        sizer.Add(txt, 6, wx.ALL | wx.EXPAND, 0)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
