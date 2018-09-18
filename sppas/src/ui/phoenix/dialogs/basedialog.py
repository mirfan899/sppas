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

    src.ui.phoenix.dialogs.basedialog.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      This is a base class for dialogs.

"""
import wx

from sppas.src.config import sg
from ..tools import sppasSwissKnife
from ..controls import sppasBitmapTextButton

# ---------------------------------------------------------------------------


class sppasDialog(wx.Dialog):
    """Base class for dialogs in SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi

    """
    def __init__(self, *args, **kw):
        """Create a dialog.

        :param parent: (wx.Window)
        :param title: String to append to the title of the dialog frame.

        """
        super(sppasDialog, self).__init__(*args, **kw)
        self._init_infos()
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
        # Fix frame properties
        self.SetMinSize(wx.Size(320, 200))
        self.SetName('{:s}-{:d}'.format(sg.__name__, self.GetId()))

        # icon
        _icon = wx.Icon()
        bmp = sppasSwissKnife.get_bmp_icon("sppas_32", height=32, colorize=False)
        _icon.CopyFromBitmap(bmp)
        self.SetIcon(_icon)

        # colors & font
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------
    # Override existing but un-useful methods
    # -----------------------------------------------------------------------

    def CreateButtonSizer(self, flags):
        """Override to disable."""
        pass

    def CreateSeparatedButtonSizer(self, flags):
        """Override to disable."""
        pass

    def CreateSeparatedSizer(self, sizer):
        """Override to disable."""
        pass

    def CreateStdDialogButtonSizer(self, flags):
        """Override to disable."""
        pass

    def CreateTextSizer(self, message):
        """Override to disable.
        
        Splits text up at newlines and places the lines into wx.StaticText 
        objects in a vertical wx.BoxSizer.
            Parameters:	message (string) –
            Return type:	wx.Sizer
        
        """
        pass

    # -----------------------------------------------------------------------

    def GetContentWindow(self):
        """Override.

        Return a window containing the main content of the dialog.

        """
        return self.FindWindow("content")

    # -----------------------------------------------------------------------
    # Methods to add header/toolbar/buttons
    # -----------------------------------------------------------------------

    def CreateHeader(self, title, icon_name=None):
        """Create a panel including a nice bold-title with an optional icon.

        :param title: (str) The message in the header
        :param icon_name: (str) Name of the icon.

        """
        settings = wx.GetApp().settings

        # Create the header panel and sizer
        header = wx.Panel(self, name="header")
        header.SetMinSize((-1, settings.title_height))
        header.SetBackgroundColour(settings.title_bg_color)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add the icon, at left
        if icon_name is not None:
            bitmap = sppasSwissKnife.get_bmp_icon(
                icon_name,
                height=settings.title_height * 0.6)
            sBmp = wx.StaticBitmap(header, wx.ID_ANY, bitmap)
            sizer.Add(sBmp, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=4)

        # Add the title, in a panel (required for vertical centering)
        panel_text = wx.Panel(header, style=wx.NO_BORDER, name="headertext")
        panel_text.SetBackgroundColour(header.GetBackgroundColour())
        sizer_text = wx.BoxSizer()
        text = wx.StaticText(panel_text, label=title, style=wx.ALIGN_CENTER)
        text.SetFont(settings.title_text_font)
        text.SetBackgroundColour(settings.title_bg_color)
        text.SetForegroundColour(settings.title_fg_color)
        sizer_text.Add(text, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        panel_text.SetSizer(sizer_text)
        sizer.Add(panel_text, 1, wx.EXPAND | wx.LEFT, border=10)

        # This header panel properties
        header.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def CreateToolbar(self):
        """Create a customized toolbar panel."""
        pass

    # -----------------------------------------------------------------------

    def CreateButtons(self, left_flags, right_flags=[]):
        """Create a customized buttons panel.

        flags is a bit list of the following flags:
            - wx.ID_OK,
            - wx.ID_CANCEL,
            - wx.ID_YES,
            - wx.ID_NO,
            - wx.ID_APPLY,
            - wx.ID_CLOSE,
            - wx.ID_SAVE.

        :param left_flags: (list) Buttons to put at left
        :param right_flags: (list) Buttons to put at right

        """
        settings = wx.GetApp().settings

        # Create the action panel and sizer
        actions = wx.Panel(self, name="actions")
        actions.SetMinSize(wx.Size(-1, settings.action_height))
        actions.SetBackgroundColour(settings.button_bg_color)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        if len(left_flags) > 0:
            for i, flag in enumerate(left_flags):
                button = self.__create_button(actions, flag)
                sizer.Add(button, 2, flag=wx.LEFT | wx.EXPAND, border=0)
                if len(right_flags) > 0 or i+1 < len(left_flags):
                    line = wx.StaticLine(actions, style=wx.LI_VERTICAL)
                    sizer.Add(line, 0, wx.EXPAND, 0)

        if len(right_flags) > 0:
            if len(left_flags) > 0:
                sizer.AddStretchSpacer(1)

            for flag in right_flags:
                button = self.__create_button(actions, flag)
                line = wx.StaticLine(actions, style=wx.LI_VERTICAL)
                sizer.Add(line, 0, wx.EXPAND, 0)
                sizer.Add(button, 2, flag=wx.RIGHT | wx.EXPAND, border=0)

        # This action panel properties
        actions.SetSizer(sizer)

    # ---------------------------------------------------------------------------

    def _process_event(self, event):
        """Must be overriden to process any kind of events.

        This method is invoked when a button is clicked.

        :param event: (wx.Event)

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------
    # Put the whole content of the dialog in a sizer
    # ---------------------------------------------------------------------------

    def LayoutComponents(self):
        """Layout the components of the dialog.

            - header at the top
            - then eventually the toolbar
            - then a panel with name 'content' (if any)
            - and eventually a button box at the bottom.

        """
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add header
        header = self.FindWindow("header")
        if header is not None:
            sizer.Add(header, 1, flag=wx.ALL | wx.EXPAND, border=0)
            h_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
            sizer.Add(h_line, 0, wx.ALL | wx.EXPAND, 0)

        # Add toolbar
        toolbar = self.FindWindow("toolbar")
        if toolbar is not None:
            sizer.Add(toolbar, 1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=0)
            h_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
            sizer.Add(h_line, 0, wx.ALL | wx.EXPAND, 0)

        # Add content
        content = self.FindWindow("content")
        if content is not None:
            sizer.Add(content, 8, flag=wx.ALL | wx.EXPAND, border=10)
        else:
            sizer.AddSpacer(2)

        # Add action buttons
        actions = self.FindWindow("actions")
        if actions is not None:
            h_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
            sizer.Add(h_line, 0, wx.ALL | wx.EXPAND, 0)
            # proportion is 0 to ask the sizer to never hide the buttons
            sizer.Add(actions, 0, flag=wx.ALL | wx.EXPAND, border=2)

        # Since Layout doesn't happen until there is a size event, you will
        # sometimes have to force the issue by calling Layout yourself. For
        # example, if a frame is given its size when it is created, and then
        # you add child windows to it, and then a sizer, and finally Show it,
        # then it may not receive another size event (depending on platform)
        # in order to do the initial layout. Simply calling self.Layout from
        # the end of the frame's __init__ method will usually resolve this.
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()

    # ---------------------------------------------------------------------------
    # Private
    # ---------------------------------------------------------------------------

    def __create_button(self, parent, flag):
        btns = {
            wx.ID_OK: ("Okay", "ok"),
            wx.ID_CANCEL: ("Cancel", "cancel"),
            wx.ID_YES: ("Yes", "yes"),
            wx.ID_NO: ("No", "no"),
            wx.ID_APPLY: ("Apply", "apply"),
            wx.ID_CLOSE: ("Close", "close"),
            wx.ID_SAVE: ("Save", "save"),
        }
        btn = sppasBitmapTextButton(parent, btns[flag][0], btns[flag][1])
        btn.SetId(flag)
        btn.Bind(wx.EVT_BUTTON, self._process_event, btn)

        if flag == wx.CANCEL:
            self.SetAffirmativeId(wx.ID_CANCEL)
        elif flag in (wx.CLOSE, wx.OK):
            btn.SetDefault()
            btn.SetFocus()
            self.SetAffirmativeId(flag)
        elif flag == wx.YES:
            self.SetAffirmativeId(wx.ID_YES)
        elif flag == wx.OK:
            btn.SetDefault()

        return btn