import wx
import logging

from wx.lib.buttons import GenBitmapTextButton, GenButton, GenBitmapButton
from ..tools import sppasSwissKnife
from .images import ColorizeImage

# ---------------------------------------------------------------------------

DEFAULT_STYLE = wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS

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
           style=DEFAULT_STYLE,
           name=name)

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

    def __init__(self, parent, label, name, style=DEFAULT_STYLE):

        btn_height = int(parent.GetSize()[1])
        super(sppasBitmapTextButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bmp_icon(name, height=btn_height),
            label=" "+label+" ",
            style=style,
            name=name
        )
        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to both the image and the text.

        :param colour: (wx.Colour)

        """
        current = self.GetForegroundColour()
        try:
            bmp = self.GetBitmapLabel()
            img = bmp.ConvertToImage()
            ColorizeImage(img, current, colour)
            self.SetBitmapLabel(wx.Bitmap(img))
        except:
            logging.debug('SetForegroundColour not applied to image'
                          'for button {:s}'.format(self.GetName()))

        GenBitmapTextButton.SetForegroundColour(self, colour)

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

    def __init__(self, parent, name, style=DEFAULT_STYLE):

        btn_height = int(parent.GetSize()[1])
        super(sppasBitmapButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bmp_icon(name, height=btn_height),
            style=style,
            name=name
        )
        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to the image.

        :param colour: (wx.Colour)

        """
        try:
            bmp = self.GetBitmapLabel()
            img = bmp.ConvertToImage()
            current = self.GetForegroundColour()
            ColorizeImage(img, current, colour)
            self.SetBitmapLabel(wx.Bitmap(img))
        except:
            logging.debug('SetForegroundColour not applied to image'
                          'for button {:s}'.format(self.GetName()))

        GenBitmapButton.SetForegroundColour(self, colour)
