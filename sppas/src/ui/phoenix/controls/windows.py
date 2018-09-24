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

    src.ui.phoenix.controls.windows.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx

# ---------------------------------------------------------------------------


class sppasNotebook(wx.Notebook):
    """A notebook is a control, which manages multiple pages with tabs.

    Possible constructors:
        - sppasNotebook()
        - sppasNotebook(parent, id=ID_ANY, pos=DefaultPosition,
            size=DefaultSize, style=0, name=NotebookNameStr)

    """
    def __init_(self, *args, **kw):
        super(sppasNotebook, self).__init__(*args, **kw)
        s = wx.GetApp().settings
        self.SetBackgroundColour(s.bg_color)
        self.SetForegroundColour(s.fg_color)
        self.SetFont(s.text_font)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override."""
        wx.Notebook.SetBackgroundColour(self, colour)
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            page.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override."""
        wx.Notebook.SetForegroundColour(self, colour)
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            page.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        wx.Notebook.SetFont(self, font)
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            page.SetFont(font)


# ---------------------------------------------------------------------------


class sppasSimplebook(wx.Simplebook):
    """A simple is a control, which manages multiple pages.

    It is showing exactly one of its several pages.

    Possible constructors:
        - sppasSimplebook()
        - sppasSimplebook(parent, id=ID_ANY, pos=DefaultPosition,
            size=DefaultSize, style=0, name=NotebookNameStr)

    >>> n = sppasSimplebook()
    >>> n.ShowNewPage(page)

    """
    def __init_(self, *args, **kw):
        super(sppasSimplebook, self).__init__(*args, **kw)
        s = wx.GetApp().settings
        self.SetBackgroundColour(s.bg_color)
        self.SetForegroundColour(s.fg_color)
        self.SetFont(s.text_font)
        # self.SetEffects(showEffect, hideEffect)
        # self.SetEffectsTimeouts(showTimeout, hideTimeout)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override."""
        wx.Simplebook.SetBackgroundColour(self, colour)
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            page.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override."""
        wx.Simplebook.SetForegroundColour(self, colour)
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            page.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        wx.Simplebook.SetFont(self, font)
        for i in range(self.GetPageCount()):
            page = self.GetPage(i)
            page.SetFont(font)
