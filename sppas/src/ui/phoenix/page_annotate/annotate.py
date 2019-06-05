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

    ui.phoenix.page_annotate.annotate.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    One of the main pages of the wx4-based GUI of SPPAS.

"""

import logging
import wx

from sppas import sppasTypeError
from sppas.src.annotations import sppasParam, sppasAnnotationsManager
from sppas.src.files import FileData, States

from sppas.src.ui.phoenix.windows import sppasMessageText
from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows import sppasStaticText
from sppas.src.ui.phoenix.windows import sppasStaticLine

from ..windows.book import sppasSimplebook
from ..windows.button import BitmapTextButton, sppasTextButton
from ..main_events import DataChangedEvent

from .annotevent import PageChangeEvent, EVT_PAGE_CHANGE

# ---------------------------------------------------------------------------


class sppasAnnotatePanel(sppasSimplebook):
    """Create a panel to annotate automatically the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasAnnotatePanel, self).__init__(
            parent=parent,
            name="page_annotate",
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS
        )
        self.SetEffectsTimeouts(200, 200)

        # The data this page is working on
        self.__data = FileData()

        # 1st page: the buttons to perform actions
        self.ShowNewPage(sppasActionAnnotate(self))

        # 2nd: list of standalone annotations
        self.AddPage(sppasStandaloneAnnotations(self), text="")

        # 3rd: list of speaker annotations
        self.AddPage(sppasSpeakerAnnotations(self), text="")

        # 4th: list of interaction annotations
        self.AddPage(sppasInteractionAnnotations(self), text="")

        # Change the displayed page
        self.Bind(EVT_PAGE_CHANGE, self._process_page_change)

        # self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        # self.SetForegroundColour(wx.GetApp().settings.fg_color)
        # self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed.

        :return: (FileData) .

        """
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (FileData)

        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        logging.debug('New data to set in the annotate page. '
                      'Id={:s}'.format(data.id))
        self.__data = data

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """Send the EVT_DATA_CHANGED to the parent."""
        if self.GetParent() is not None:
            self.__data.set_state(States().CHECKED)
            evt = DataChangedEvent(data=self.__data)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def _process_page_change(self, event):
        """Process a PageChangeEvent.

        :param event: (wx.Event)

        """
        try:
            destination = event.to_page
        except AttributeError:
            destination = "page_to_annotate"

        self.show_page(destination)

    # -----------------------------------------------------------------------

    def show_page(self, page_name):
        """Show a page of the book.

        If the page can't be found, the annotate page is shown.

        :param page_name: (str) one of 'page_to_annotate', 'page_...', ...

        """
        # Find the page number to switch on
        w = self.FindWindow(page_name)
        if w is None:
            w = self.FindWindow("page_to_annotate")
        p = self.FindPage(w)
        if p == -1:
            p = 0

        # current page number
        c = self.FindPage(self.GetCurrentPage())

        # assign the effect
        if c < p:
            self.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_LEFT,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_LEFT)
        elif c > p:
            self.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_RIGHT,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_RIGHT)
        else:
            self.SetEffects(showEffect=wx.SHOW_EFFECT_NONE,
                            hideEffect=wx.SHOW_EFFECT_NONE)

        # then change to the page
        self.ChangeSelection(p)
        w.Refresh()

# ---------------------------------------------------------------------------


class sppasActionAnnotate(sppasPanel):

    def __init__(self, parent):
        super(sppasActionAnnotate, self).__init__(
            parent=parent,
            name="page_to_annotate",
            style=wx.BORDER_NONE
        )
        self._create_content()
        self._setup_events()

        # self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        # self.SetForegroundColour(wx.GetApp().settings.fg_color)
        # self.SetFont(wx.GetApp().settings.text_font)

        self.Layout()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""

        sta = sppasStaticText(self, label="STEP 1: select the annotations to perform")

        # The buttons to select annotations (switch to other pages)
        self.btn_select1 = self.__create_select_annot_btn("Standalone annotations")
        self.btn_select2 = self.__create_select_annot_btn("'SPEAKER' annotations")
        self.btn_select3 = self.__create_select_annot_btn("'INTERACTION' annotations")

        stl = sppasStaticText(self, label="STEP 2: fix the language(s)")

        str = sppasStaticText(self, label="STEP 3: perform the annotations")

        # The button to perform annotations
        btn = self.__create_select_annot_btn("Let's go!")
        btn.SetName("wizard")
        btn.BorderColour = wx.Colour(228, 24, 24, 128)

        # Organize all the objects
        s1 = wx.BoxSizer(wx.HORIZONTAL)
        s1.Add(self.btn_select1, 1, wx.EXPAND | wx.ALL, 4)
        s1.Add(self.btn_select2, 1, wx.EXPAND | wx.ALL, 4)
        s1.Add(self.btn_select3, 1, wx.EXPAND | wx.ALL, 4)

        s2 = wx.BoxSizer(wx.HORIZONTAL)
        s2.Add(wx.Panel(self), 0, wx.LEFT, 20)

        s3 = wx.BoxSizer(wx.HORIZONTAL)
        s3.Add(btn)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sta, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 20)
        sizer.Add(s1, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL)
        # sizer.Add(self.HorizLine(self), 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        sizer.Add(stl, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 20)
        sizer.Add(s2, 2,  wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL)
        # sizer.Add(self.HorizLine(self), 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        sizer.Add(str, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 20)
        sizer.Add(s3, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL | wx.BOTTOM, 20)
        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_select_annot_btn(self, label):

        try:
            w = int(wx.GetApp().settings.size_coeff * 196.)
            h = int(wx.GetApp().settings.size_coeff * 42.)
        except Exception as e:
            logging.error(str(e))
            h = 42
            w = 196

        btn = BitmapTextButton(self, name="on-off", label=label)
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = 12
        btn.BorderWidth = 2
        btn.BorderColour = wx.Colour(128, 128, 128, 128)
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(w, h))
        return btn

    # ------------------------------------------------------------------------

    def HorizLine(self, parent, depth=1):
        """Return an horizontal static line."""
        line = sppasStaticLine(parent, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, depth))
        line.SetSize(wx.Size(-1, depth))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(depth)
        line.SetForegroundColour(self.GetForegroundColour())
        return line

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, destination):
        """Send the EVT_PAGE_CHANGE to the parent."""
        if self.GetParent() is not None:
            evt = PageChangeEvent(from_page=self.GetName(),
                                  to_page=destination)
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

        wx.LogMessage("Received event id {:d} of {:s}"
                      "".format(event_id, event_name))

        if event_name == "wizard":
            self._annotate()

        elif event_obj == self.btn_select1:
            self.notify("page_standalone_annot")

        elif event_obj == self.btn_select2:
            self.notify("page_speaker_annot")

        elif event_obj == self.btn_select3:
            self.notify("page_interaction_annot")

    # -----------------------------------------------------------------------

    def _annotate(self):
        """Perform the selected automatic annotations."""
        pass

# ---------------------------------------------------------------------------


class sppasStandaloneAnnotations(sppasPanel):

    def __init__(self, parent):
        super(sppasStandaloneAnnotations, self).__init__(
            parent=parent,
            name="page_standalone_annot",
            style=wx.BORDER_NONE
        )
        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.Layout()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""

        # Organize all the objects horizontally
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        btn = BitmapTextButton(self, name="arrow_back")
        btn.FocusWidth = 0
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(64, 64))

        sizer.Add(btn, 0)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """Send the EVT_PAGE_CHANGE to the parent."""
        if self.GetParent() is not None:
            evt = PageChangeEvent(from_page=self.GetName(),
                                  to_page="page_to_annotate")
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

        if event_name == "arrow_back":
            self.notify()

# ---------------------------------------------------------------------------


class sppasSpeakerAnnotations(sppasPanel):

    def __init__(self, parent):
        super(sppasSpeakerAnnotations, self).__init__(
            parent=parent,
            name="page_speaker_annot",
            style=wx.BORDER_NONE
        )
        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.Layout()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""

        # Organize all the objects horizontally
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        btn = BitmapTextButton(self, name="arrow_back")
        btn.FocusWidth = 0
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(64, 64))

        sizer.Add(btn, 0)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """Send the EVT_PAGE_CHANGE to the parent."""
        if self.GetParent() is not None:
            evt = PageChangeEvent(from_page=self.GetName(),
                                  to_page="page_to_annotate")
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

        if event_name == "arrow_back":
            self.notify()

# ---------------------------------------------------------------------------


class sppasInteractionAnnotations(sppasPanel):

    def __init__(self, parent):
        super(sppasInteractionAnnotations, self).__init__(
            parent=parent,
            name="page_interaction_annot",
            style=wx.BORDER_NONE
        )
        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.Layout()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""

        # Organize all the objects horizontally
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        btn = BitmapTextButton(self, name="arrow_back")
        btn.FocusWidth = 0
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(64, 64))

        sizer.Add(btn, 0)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """Send the EVT_PAGE_CHANGE to the parent."""
        if self.GetParent() is not None:
            evt = PageChangeEvent(from_page=self.GetName(),
                                  to_page="page_to_annotate")
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

        if event_name == "arrow_back":
            self.notify()


