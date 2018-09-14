import wx

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
