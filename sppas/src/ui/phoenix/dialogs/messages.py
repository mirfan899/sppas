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

"""
import wx
from .basedialog import sppasDialog

# ----------------------------------------------------------------------------


class sppasBaseMessageDialog(sppasDialog):
    """

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
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
        self.CreateButtons([wx.ID_NO], [wx.ID_YES])
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
