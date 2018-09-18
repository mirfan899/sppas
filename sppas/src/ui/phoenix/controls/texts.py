import wx

# ---------------------------------------------------------------------------


class sppasStaticText(wx.StaticText):
    """Create a static text.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Font and foreground color are taken from the application settings but
    background color is the one of the parent.

    """

    def __init__(self, parent, label):
        super(sppasStaticText, self).__init__(
            parent,
            label=label,
            style=wx.ALIGN_CENTER)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetFont(settings.text_font)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetForegroundColour(settings.fg_color)

# ---------------------------------------------------------------------------

class sppasTitleText(wx.StaticText):
    """Create a title.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Font and foreground color are taken from the application settings but
    background color is the one of the parent.

    """

    def __init__(self, parent, label):
        super(sppasTitleText, self).__init__(
            parent,
            label=label,
            style=wx.ALIGN_CENTER)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetFont(settings.title_text_font)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetForegroundColour(settings.title_fg_color)

# ---------------------------------------------------------------------------


class sppasMessageText(wx.TextCtrl):
    """Create a multi-lines message text, centered.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Font and foreground color are taken from the application settings but
    background color is the one of the parent.

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
        settings = wx.GetApp().settings
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetForegroundColour(settings.fg_color)
        self.SetFont(settings.text_font)

        # Fix Look&Feel for the new text to be added
        attr = wx.TextAttr()
        attr.SetTextColour(settings.fg_color)
        attr.SetBackgroundColour(parent.GetBackgroundColour())
        attr.SetFont(settings.text_font)

        self.SetDefaultStyle(attr)
