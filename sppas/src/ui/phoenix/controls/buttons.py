import wx

from wx.lib.buttons import GenBitmapTextButton, GenButton
from ..tools import sppasSwissKnife

# ---------------------------------------------------------------------------


class sppasTextButton(GenButton):
    """Create a simple text button. Inherited from the wx.Button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent, label, name):

        super(sppasTextButton, self).__init__(
           parent,
           wx.ID_ANY,
           label,
           style=wx.BORDER_NONE,
           name=name)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetForegroundColour(settings.button_fg_color)
        self.SetBackgroundColour(settings.button_bg_color)
        self.SetFont(settings.button_text_font)
        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

# ---------------------------------------------------------------------------


class sppasBitmapTextButton(GenBitmapTextButton):
    """Create a simple text button. Inherited from the wx.Button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Create a button with bitmap and text. A tooltip can optionally be added.

    >>> button = sppasBitmapTextButton(None, "Exit", "exit")
    >>> button.SetToolTipString("Quit the application")

    """

    def __init__(self, parent, label, name):
        settings = wx.GetApp().settings
        btn_height = int(settings.action_height * 0.6)
        super(sppasBitmapTextButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bitmap(name, height=btn_height),
            label="   "+label,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS,
            name=name
        )

        self.SetBackgroundColour(settings.button_bg_color)
        self.SetForegroundColour(settings.button_fg_color)
        self.SetFont(settings.button_text_font)
        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)
