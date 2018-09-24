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

    src.ui.phoenix.controls.texts.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx

# ---------------------------------------------------------------------------


class sppasStaticText(wx.StaticText):
    """Create a static text.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Font, foreground and background are taken from the application settings.

    """

    def __init__(self, *args, **kw):
        """Create a static text for a content panel.

        Possible constructors:
            - sppasStaticText()
            - sppasStaticText(parent, id=ID_ANY, label="",
                pos=DefaultPosition, size=DefaultSize, style=0,
                name=StaticTextNameStr)

        """
        super(sppasStaticText, self).__init__(*args, **kw)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetFont(settings.text_font)
        self.SetBackgroundColour(settings.bg_color)
        self.SetForegroundColour(settings.fg_color)

# ---------------------------------------------------------------------------


class sppasTextCtrl(wx.TextCtrl):
    """A text control allows text to be displayed and edited.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Possible constructors:
        - sppasTextCtrl()
        - sppasTextCtrl(parent, id=ID_ANY, value="", pos=DefaultPosition,
                 size=DefaultSize, style=0, validator=DefaultValidator,
                 name=TextCtrlNameStr)

    Font, foreground and background are taken from the application settings.

    """

    def __init__(self, *args, **kw):
        super(sppasTextCtrl, self).__init__(*args, **kw)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetFont(settings.text_font)
        self.SetBackgroundColour(settings.bg_color)
        self.SetForegroundColour(settings.fg_color)

        # Fix Look&Feel for the new text to be added
        attr = wx.TextAttr()
        attr.SetTextColour(settings.fg_color)
        attr.SetBackgroundColour(settings.bg_color)
        attr.SetFont(settings.text_font)
        self.SetDefaultStyle(attr)

# ---------------------------------------------------------------------------


class sppasTitleText(wx.StaticText):
    """Create a static title.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Font, foreground and background are taken from the application settings.

    """

    def __init__(self, *args, **kw):
        """Create a static text for a header panel.

        Possible constructors:

            - StaticText()

            - StaticText(parent, id=ID_ANY, label="", pos=DefaultPosition,
                         size=DefaultSize, style=0, name=StaticTextNameStr)

        """
        super(sppasTitleText, self).__init__(*args, **kw)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetFont(settings.header_text_font)
        self.SetBackgroundColour(settings.header_bg_color)
        self.SetForegroundColour(settings.header_fg_color)

# ---------------------------------------------------------------------------


class sppasMessageText(sppasTextCtrl):
    """Create a multi-lines message text, centered.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Font, foreground and background are taken from the application settings.

    """
    text_style = wx.TAB_TRAVERSAL | \
                 wx.TE_MULTILINE | \
                 wx.TE_READONLY | \
                 wx.TE_BESTWRAP | \
                 wx.TE_AUTO_URL | \
                 wx.TE_CENTRE | \
                 wx.NO_BORDER

    def __init__(self, parent, message):
        super(sppasMessageText, self).__init__(
            parent=parent,
            value=message,
            style=sppasMessageText.text_style)
