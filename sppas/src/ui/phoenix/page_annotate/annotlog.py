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

    ui.phoenix.page_annotate.annotlog.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx
import codecs

from sppas import sg

from ..windows import sppasScrolledPanel
from ..windows import BitmapTextButton

from .annotevent import PageChangeEvent

# -----------------------------------------------------------------------


ERROR_COLOUR = wx.Colour(220, 30, 10)     # red
INFO_COLOUR = wx.Colour(55, 30, 200)      # blue
IGNORE_COLOUR = wx.Colour(140, 100, 160)  # gray-violet
WARNING_COLOUR = wx.Colour(240, 190, 45)  # orange
OK_COLOUR = wx.Colour(25, 160, 50)        # green

# ---------------------------------------------------------------------------


class sppasLogAnnotate(sppasScrolledPanel):
    """Create a panel to run automatic annotations and show log.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, param, data):
        super(sppasLogAnnotate, self).__init__(
            parent=parent,
            name="page_annot_log",
            style=wx.BORDER_NONE
        )
        self.__param = param
        self.__data = data

        self._create_content()
        self._setup_events()

        self.Layout()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        btn_size = int(64. * wx.GetApp().settings.size_coeff)

        sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        btn_back_top = BitmapTextButton(self, name="arrow_back")
        btn_back_top.FocusWidth = 0
        btn_back_top.BorderWidth = 0
        btn_back_top.BitmapColour = self.GetForegroundColour()
        btn_back_top.SetMinSize(wx.Size(btn_size, btn_size))
        sizer_top.Add(btn_back_top, 0, wx.RIGHT, btn_size // 4)

        title = wx.StaticText(self, label="Procedure Outcome Report", name="title_text")
        sizer_top.Add(title, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(sizer_top, 0, wx.EXPAND)

        self.log_txt = wx.TextCtrl(self, -1,  # size=(620, 480),
                                   style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)
        self.log_txt.SetDefaultStyle(wx.TextAttr(wx.BLACK, wx.WHITE))
        self.log_txt.SetFont(wx.Font(wx.GetApp().text_font,
                                     wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                                     False, u'Courier New'))
        try:
            with codecs.open(self.__param.get_report_filename(), 'r', sg.__encoding__) as fp:
                logcontent = fp.read()
        except Exception as e:
            logcontent = "No report is available...\n" \
                         "Error is: %s" % str(e)
        self.log_txt.SetValue(logcontent)
        i = 0
        oldi = 0
        while i >= 0:
            i = logcontent.find("[ ", oldi)
            if logcontent.find("OK", i, i+14) > -1:
                self.log_txt.SetStyle(i, i+12, wx.TextAttr(OK_COLOUR))

            elif logcontent.find("ERROR", i, i+14) > -1:
                self.log_txt.SetStyle(i, i+12, wx.TextAttr(ERROR_COLOUR))

            elif logcontent.find("WARNING", i, i+14) > -1:
                self.log_txt.SetStyle(i, i+12, wx.TextAttr(WARNING_COLOUR))

            elif logcontent.find("INFO", i, i+14) > -1:
                self.log_txt.SetStyle(i, i+12, wx.TextAttr(INFO_COLOUR))

            elif logcontent.find("IGNORED", i, i+14) >- 1:
                self.log_txt.SetStyle(i, i+12, wx.TextAttr(IGNORE_COLOUR))

            oldi = i + 13

        btn_back_bottom = BitmapTextButton(self, name="arrow_back")
        btn_back_bottom.FocusWidth = 0
        btn_back_bottom.BorderWidth = 0
        btn_back_bottom.BitmapColour = self.GetForegroundColour()
        btn_back_bottom.SetMinSize(wx.Size(btn_size, btn_size))
        sizer.Add(btn_back_bottom, 0)

        self.SetSizer(sizer)
        self.SetupScrolling(scroll_x=True, scroll_y=True)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """Send the EVT_PAGE_CHANGE to the parent."""
        if self.GetParent() is not None:
            evt = PageChangeEvent(from_page=self.GetName(),
                                  to_page="page_annot_actions")
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind all events from our buttons (including 'exit')
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()
        event_id = event_obj.GetId()

        if event_name == "arrow_back":
            self.notify()


