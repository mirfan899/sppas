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

            - StaticText()

            - StaticText(parent, id=ID_ANY, label="", pos=DefaultPosition,
                         size=DefaultSize, style=0, name=StaticTextNameStr)

        """
        super(sppasStaticText, self).__init__(*args, **kw)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetFont(settings.text_font)
        self.SetBackgroundColour(settings.bg_color)
        self.SetForegroundColour(settings.fg_color)

# ---------------------------------------------------------------------------


class sppasTextCtrl(wx.TextCtrl):
    """Create a static text.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

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
    """Create a title.

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
        self.SetFont(settings.title_text_font)
        self.SetBackgroundColour(settings.title_bg_color)
        self.SetForegroundColour(settings.title_fg_color)

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
