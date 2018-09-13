import wx

# ---------------------------------------------------------------------------


class sppasTitleText(wx.StaticText):
    """Create a title."""

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
