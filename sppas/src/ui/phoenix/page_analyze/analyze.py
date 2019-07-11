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

    ui.phoenix.page_analyze.analyze.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import random
import logging
import wx

from sppas import sppasTypeError
from sppas.src.files import FileData, States

from ..main_events import DataChangedEvent, EVT_DATA_CHANGED
from ..main_events import EVT_TAB_CHANGE

from ..windows import sppasPanel
from ..windows import sppasStaticLine
from ..windows.book import sppasSimplebook

from .tabs import TabsManager

# ---------------------------------------------------------------------------


class sppasAnalyzePanel(sppasPanel):
    """Create a panel to analyze the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasAnalyzePanel, self).__init__(
            parent=parent,
            name="page_analyze",
            style=wx.BORDER_NONE
        )

        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (FileData) data of the files-viewer model.

        """
        return self.FindWindow("tabsview").get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (FileData)

        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        logging.debug('New data to set in the analyze page. '
                      'Id={:s}'.format(data.id))
        self.__send_data(self.GetParent(), data)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        # Create all the panels
        tm = TabsManager(self, name="tabsview")
        book = sppasSimplebook(self, name="content")

        # Organize all the panels vertically, separated by 2px grey lines.
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(tm, 0, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(book, 2, wx.EXPAND, 0)

        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_vline(self):
        """Create a vertical line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(2, -1))
        line.SetSize(wx.Size(2, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(2)
        line.SetForegroundColour(wx.Colour(128, 128, 128, 128))
        return line

    # -----------------------------------------------------------------------

    def __create_book(self):
        """Create the simple book to manage the opened files in tabs."""
        book = sppasSimplebook(
            parent=self,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS,
            name="content"
        )
        book.SetEffectsTimeouts(100, 150)
        return book

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

        # The data have changed.
        # This event is sent by the tabs manager or by the parent
        self.Bind(EVT_DATA_CHANGED, self._process_data_changed)

        # Tabs have changed. The book must do the same.
        self.Bind(EVT_TAB_CHANGE, self._process_tab_change)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()
        logging.debug('Analyze page received a key event. key_code={:d}'.format(key_code))

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_data_changed(self, event):
        """Process a change of data.

        Set the data of the event to the other panels.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        try:
            data = event.data
        except AttributeError:
            logging.error('Data were not sent in the event emitted by {:s}'
                          '.'.format(emitted.GetName()))
            return

        self.__send_data(emitted, data)

    # -----------------------------------------------------------------------

    def _process_tab_change(self, event):
        """Process a change of page.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        try:
            action = event.action
            cur_page_name = event.cur_tab
            dest_page_name = event.dest_tab
        except:
            logging.error('Malformed event emitted by {:s}'
                          '.'.format(emitted.GetName()))
            return

        book = self.FindWindow("content")

        # Append a page to the book
        if action == "append":
            new_page = sppasPanel(book, name=cur_page_name)
            new_page.SetBackgroundColour(
                wx.Colour(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

            )
            book.AddPage(new_page, text="")

        # Delete the page, without deleting the associated window
        if action == "remove":
            w = book.FindWindow(cur_page_name)
            if w is None:
                return
            book.RemovePage(w)

        if action == "open":
            w = book.FindWindow(cur_page_name)
            if w is None:
                return
            # TODO: implement the opening of files in pages...
            # set checked files as locked
            # send data to the parent

        # Show a page of the book
        if dest_page_name is not None:
            w = book.FindWindow(dest_page_name)
            self.show_page(w)

    # -----------------------------------------------------------------------
    # Management of the book
    # -----------------------------------------------------------------------

    def show_page(self, page):
        """Show a page of the content panel.

        :param page:

        """
        book = self.FindWindow("content")

        # the page number to switch on
        p = book.FindPage(page)
        if p == wx.NOT_FOUND:
            return

        # the current page number
        c = book.FindPage(book.GetCurrentPage())

        # assign the effect
        if c < p:
            book.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_LEFT,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_LEFT)
        elif c > p:
            book.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_RIGHT,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_RIGHT)
        else:
            book.SetEffects(showEffect=wx.SHOW_EFFECT_NONE,
                            hideEffect=wx.SHOW_EFFECT_NONE)

        # then change the current tab
        book.ChangeSelection(p)
        self.Refresh()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __send_data(self, emitted, data):
        """Set a change of data to the children, send to the parent.

        :param emitted: (wx.Window) The panel the data are coming from
        :param data: (FileData)

        """
        # Set the data to appropriate children panels
        panel = self.FindWindow("tabsview")
        if emitted != panel:
            panel.set_data(data)

        # Send the data to the parent
        pm = self.GetParent()
        if pm is not None and emitted != pm:
            data.set_state(States().CHECKED)
            evt = DataChangedEvent(data=data)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)
