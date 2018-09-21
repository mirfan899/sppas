import wx

from wx.lib.buttons import GenBitmapTextButton, GenButton, GenBitmapButton
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

        self.ShouldInheritColours()
        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

# ---------------------------------------------------------------------------


class sppasBitmapTextButton(GenBitmapTextButton):
    """Create a simple text button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Create a button with bitmap and text. A tooltip can optionally be added.

    >>> button = sppasBitmapTextButton(None, "Exit", "exit")
    >>> button.SetToolTipString("Quit the application")

    """

    def __init__(self, parent, label, name, style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS):

        btn_height = int(parent.GetSize()[1])
        super(sppasBitmapTextButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bmp_icon(name, height=btn_height),
            label=" "+label+" ",
            style=style,
            name=name
        )
        self.ShouldInheritColours()
        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)


# ---------------------------------------------------------------------------


class sppasBitmapButton(GenBitmapButton):
    """Create a simple text button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Create a button with bitmap. A tooltip can optionally be added.

    >>> button = sppasBitmapButton(None, "exit")
    >>> button.SetToolTipString("Quit the application")

    """

    def __init__(self, parent, name, style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS):

        btn_height = int(parent.GetSize()[1])
        super(sppasBitmapButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bmp_icon(name, height=btn_height),
            style=style,
            name=name
        )
        self.ShouldInheritColours()
        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

