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

    # ---------------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
        # Fix frame properties
        self.SetMinSize(wx.Size(480, 200))
        self.SetName('{:s}-{:d}'.format(sg.__name__, self.GetId()))

        # icon
        _icon = wx.Icon()
        _icon.CopyFromBitmap(sppasSwissKnife.get_bmp_icon("sppas"))
        self.SetIcon(_icon)

        # colors & font
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ---------------------------------------------------------------------------
    # Override existing but un-useful methods
    # ---------------------------------------------------------------------------

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

    # ---------------------------------------------------------------------------

    def GetContentWindow(self):
        """Override.

        Return a window containing the main content of the dialog.

        """
        return self.FindWindow("content")

    # ---------------------------------------------------------------------------
    # Methods to add header/toolbar/buttons
    # ---------------------------------------------------------------------------

    def CreateHeader(self, title, icon_name=None):
        """Create a panel including a nice bold-title with an optional icon.

        :param title: (str) The title
        :param icon_name: (str) Name of the icon.
        :returns: wx.Panel of a customized header title

        """
        settings = wx.GetApp().settings

        header = wx.Panel(self, name="header")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        header.SetMinSize((-1, settings.title_height))
        header.SetBackgroundColour(settings.title_bg_color)

        if icon_name is not None:
            bitmap = sppasSwissKnife.get_bmp_icon(icon_name)
            sBmp = wx.StaticBitmap(header, wx.ID_ANY, bitmap)
            sizer.Add(sBmp, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=4)

        panel_text = wx.Panel(header, style=wx.NO_BORDER)
        panel_text.SetBackgroundColour(settings.title_bg_color)
        sizer_text = wx.BoxSizer()
        text = wx.StaticText(panel_text, label=title, style=wx.ALIGN_CENTER)
        text.SetFont(wx.GetApp().settings.title_text_font)
        text.SetBackgroundColour(settings.title_bg_color)
        text.SetForegroundColour(settings.title_fg_color)
        sizer_text.Add(text, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        panel_text.SetSizer(sizer_text)

        sizer.Add(panel_text, proportion=1, flag=wx.EXPAND | wx.LEFT, border=10)
        header.SetSizer(sizer)
        header.SetAutoLayout(True)

    # ---------------------------------------------------------------------------

    def CreateToolbar(self):
        """Create a customized toolbar panel.

        """
        pass

    # ---------------------------------------------------------------------------

    def CreateButtons(self, left_flags, right_flags):
        """Create a customized buttons panel.

        flags is a bit list of the following flags:
            - wx.OK,
            - wx.CANCEL,
            - wx.YES,
            - wx.NO,
            - wx.APPLY,
            - wx.CLOSE,
            - wx.ID_SAVE.

        """
        actions = wx.Panel(self, name="actions")

        settings = wx.GetApp().settings
        self.SetMinSize((-1, settings.action_height))
        self.SetBackgroundColour(settings.bg_color)

        action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # action_sizer.AddStretchSpacer(1)

        if len(left_flags) > 0:
            for flag in left_flags:
                button = self.__create_button(actions, flag)
                action_sizer.Add(button, proportion=2, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.EXPAND, border=2)
                action_sizer.Add(wx.StaticLine(actions, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)

        if len(right_flags) > 0:
            for flag in right_flags:
                button = self.__create_button(actions, flag)
                action_sizer.Add(wx.StaticLine(actions, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)
                action_sizer.Add(button, proportion=2, flag=wx.TOP | wx.BOTTOM | wx.RIGHT | wx.EXPAND, border=2)

        # action_sizer.AddStretchSpacer(1)
        actions.SetSizer(action_sizer)
        self.SetAutoLayout(True)

    def __create_button(self, parent, flag):
        btns = {
            wx.OK: ("Okay", "ok", wx.ID_OK),
            wx.CANCEL: ("Cancel", "cancel", wx.ID_CANCEL),
            wx.YES: ("Yes", "yes", wx.ID_YES),
            wx.NO: ("No", "no", wx.ID_NO),
            wx.APPLY: ("Apply", "apply", wx.ID_APPLY),
            wx.CLOSE: ("Close", "close", wx.ID_CLOSE),
            wx.ID_SAVE: ("Save", "save", wx.ID_SAVE),
        }
        btn = sppasBitmapTextButton(parent, btns[flag][0], btns[flag][1])
        btn.SetId(btns[flag][2])
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

    def _process_event(self, event):
        """Process any kind of events.

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
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Add header
        header = self.FindWindow("header")
        if header is not None:
            vbox.Add(header, 1, flag=wx.ALL | wx.EXPAND, border=0)
            vbox.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), 0, wx.ALL | wx.EXPAND, 0)

        # Add toolbar
        toolbar = self.FindWindow("toolbar")
        if toolbar is not None:
            vbox.Add(toolbar, 1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=0)

        # Add content
        content = self.FindWindow("content")
        if content is not None:
            vbox.Add(content, 2, flag=wx.ALL | wx.EXPAND, border=10)
        else:
            vbox.AddSpacer(2)

        # Add button box
        buttons = self.FindWindow("actions")
        if buttons is not None:
            vbox.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL), 0, wx.ALL | wx.EXPAND, 0)
            vbox.Add(buttons, 1, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=0)

        self.SetSizer(vbox)
        self.Layout()

# ----------------------------------------------------------------------------


class sppasBaseMessageDialog(sppasDialog):

    def __init__(self, parent, message, style=wx.ICON_INFORMATION):
        """Create a dialog with a message.


        :param parent: (wx.Window)
        :param message: (str) the file to display in this frame.
        :param style: ONE of wx.ICON_INFORMATION, wx.ICON_ERROR, wx.ICON_EXCLAMATION, wx.YES_NO

        """
        super(sppasBaseMessageDialog, self).__init__(
            parent=parent,
            title="Message",
            style=wx.DEFAULT_FRAME_STYLE | wx.DIALOG_NO_PARENT)

        if style == wx.ICON_ERROR:
            self.CreateHeader("Error")
        elif style == wx.ICON_WARNING:
            self.CreateHeader("Warning")
        elif style == wx.YES_NO:
            self.CreateHeader("Question")
        else:
            self.CreateHeader("Information")

        self._create_content(message)
        self._create_buttons()
        self.LayoutComponents()

    def _create_content(self, message):
        txt = wx.TextCtrl(
            self,
            wx.ID_ANY,
            value=message,
            style=wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_NO_VSCROLL | wx.TE_WORDWRAP,
            name="content"
        )
        font = wx.GetApp().settings.text_font
        txt.SetFont(font)
        txt.SetForegroundColour(self.GetForegroundColour())
        txt.SetBackgroundColour(self.GetBackgroundColour())
        # txt.SetMinSize((300, -1))

    def _create_buttons(self):
        raise NotImplementedError

# ---------------------------------------------------------------------------


class YesNoQuestion(sppasBaseMessageDialog):

    def __init__(self, message):
        super(YesNoQuestion, self).__init__(
            parent=None,
            message=message,
            style=wx.YES_NO)

    def _create_buttons(self):
        self.CreateButtons([wx.NO], [wx.YES])
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.Bind(wx.EVT_CLOSE, self._process_event)
        self.SetAffirmativeId(wx.ID_YES)

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()
        if event_id == wx.ID_NO:
            self.SetReturnCode(wx.ID_NO)
            self.Close()
        else:
            event.Skip()
