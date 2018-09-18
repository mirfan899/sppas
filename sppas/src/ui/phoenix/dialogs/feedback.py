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

    src.ui.phoenix.dialogs.feedback.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx
import webbrowser
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

from sppas.src.config import sg

from ..controls.buttons import sppasBitmapTextButton
from ..controls.texts import sppasMessageText, sppasStaticText
from .basedialog import sppasDialog
from .messages import Information

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

DESCRIBE_TEXT = "Your message here..."

# -------------------------------------------------------------------------


class FeedbackForm(object):
    """Create a form to send an e-mail, and do it.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Data of the form are picked up from a feedback dialog.

    """
    def __init__(self, dialog, web_browser):
        self.dialog = dialog
        self.web_browser = web_browser

    # -----------------------------------------------------------------------

    def SendWithDefault(self):
        text = self.dialog.GetBodyText()
        text = text.strip()
        self.web_browser.open("mailto:%s?subject=%s&body=%s" % (
            quote(self.dialog.GetToText()),
            quote(self.dialog.GetSubjectText()),
            quote(text.encode('utf-8'))))

    # -----------------------------------------------------------------------

    def SendWithGmail(self):
        self.web_browser.open("https://mail.google.com/mail/?compose=1&view=cm&fs=1&to=%s&su=%s&body=%s" % (
            quote(self.dialog.GetToText()),
            quote(self.dialog.GetSubjectText()),
            quote(self.dialog.GetBodyText())))

    # -----------------------------------------------------------------------

    def SendWithOther(self):
        Information("Copy and paste this email into your favorite email "
                    "client and send it from there.")

# ----------------------------------------------------------------------------


class sppasFeedbackDialog(sppasDialog):
    """Dialog to send a message by e-mail to the author.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent):
        """Create a feedback dialog.

        :param parent: (wx.Window)

        """
        super(sppasDialog, self).__init__(
            parent=parent,
            title="Feedback",
            style=wx.DEFAULT_FRAME_STYLE)
        self.controller = FeedbackForm(self, webbrowser)

        # Create the header
        self.CreateHeader("Send feedback to the author", icon_name="mail-at")
        self._create_content()
        self._create_buttons()

        self.SetMinSize(wx.Size(480, 320))
        self.LayoutComponents()
        self.CenterOnParent()

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""

        panel = wx.Panel(self, name="content")
        panel.SetBackgroundColour(wx.GetApp().settings.bg_color)

        # Create the message content

        body_style = wx.TAB_TRAVERSAL | \
                     wx.TE_BESTWRAP | \
                     wx.TE_AUTO_URL | \
                     wx.TE_LEFT | \
                     wx.BORDER_SIMPLE
        feed_style = body_style | wx.TE_MULTILINE | wx.TE_READONLY

        # -----------------------------------------------------------------------

        self.to_text = wx.TextCtrl(panel, value=sg.__contact__, style=feed_style)
        self.to_text.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.to_text.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.to_text.SetFont(wx.GetApp().settings.text_font)

        self.subject_text = wx.TextCtrl(panel,
                                        value=sg.__name__ +
                                              " " +
                                              sg.__version__ +
                                              " - Feedback...",
                                        style=feed_style)
        self.subject_text.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.subject_text.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.subject_text.SetFont(wx.GetApp().settings.text_font)

        self.body_text = wx.TextCtrl(panel, value=DESCRIBE_TEXT, style=body_style)
        self.body_text.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.body_text.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.body_text.SetFont(wx.GetApp().settings.text_font)
        self.body_text.SetMinSize((300, 200))
        self.body_text.Bind(wx.EVT_CHAR, self._on_char, self.body_text)
        self.body_text.SetSelection(0, len(DESCRIBE_TEXT))

        grid = wx.FlexGridSizer(4, 2, 5, 5)
        grid.AddGrowableCol(1)
        grid.AddGrowableRow(2)
        grid.Add(sppasStaticText(panel, label="To: "), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.to_text, 0, flag=wx.EXPAND)
        grid.Add(sppasStaticText(panel, label="Subject: "), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.subject_text, 0, flag=wx.EXPAND)
        grid.Add(sppasStaticText(panel, label="Body: "), flag=wx.TOP)
        grid.Add(self.body_text, 1, flag=wx.EXPAND)

        panel.SetSizer(grid)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        """Override to create the buttons and bind events."""

        settings = wx.GetApp().settings
        panel = wx.Panel(self, name="actions")

        # Create the action panel and sizer
        self.SetMinSize(wx.Size(-1, settings.action_height))
        self.SetBackgroundColour(settings.button_bg_color)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        exit_btn = sppasBitmapTextButton(panel, "Close", name="close")
        exit_btn.Bind(wx.EVT_BUTTON, self._process_event, exit_btn)

        #log_btn = sppasBitmapTextButton(self, "View logs", name="view_log")
        vertical_line = wx.StaticLine(panel, style=wx.LI_VERTICAL)

        #sizer.Add(log_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(vertical_line, 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(exit_btn, 4, wx.ALL | wx.EXPAND, 0)

        panel.SetSizer(sizer)

    # ------------------------------------------------------------------------
    # Callback to events
    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()
        print("event:"+event_name)

        if event_name == "close":
            self.SetReturnCode(wx.ID_CLOSE)
            self.Close()
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _on_char(self, evt):
        if self.body_text.GetValue().strip() == DESCRIBE_TEXT:
            self.body_text.SetForegroundColour(wx.GetApp().settings.bg_color)
            self.body_text.SetValue('')
        if self._ctrl_a(evt):
            self.body_text.SelectAll()
        else:
            evt.Skip()

    def _ctrl_a(self, evt):
        KEY_CODE_A = 1
        return evt.ControlDown() and evt.KeyCode == KEY_CODE_A

    def _on_send(self, event):
        idb = event.GetId()
        if idb == self.btn_default.GetId():
            self.controller.SendWithDefault()
        elif idb == self.btn_gmail.GetId():
            self.controller.SendWithGmail()
        elif idb == self.btn_other.GetId():
            self.controller.SendWithOther()
        else:
            event.Skip()

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def GetToText(self):
        return self.to_text.GetValue()

    def GetSubjectText(self):
        return self.subject_text.GetValue()

    def GetBodyText(self):
        return self.body_text.GetValue()

# -------------------------------------------------------------------------


def Feedback(parent):
    """Display a dialog to send feedback.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    :param message: (str) The question to ask
    :returns: the response

    wx.ID_CANCEL is returned if the dialog is destroyed or no e-mail
    was sent.

    """
    dialog = sppasFeedbackDialog(parent)
    dialog.controller.Populate(None)
    response = dialog.ShowModal()
    dialog.Destroy()
    return response
