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
from sppas import msg
from sppas import u

from sppas.src.annotations import sppasParam, sppasAnnotationsManager
from sppas.src.files import FileData, States

from sppas.src.ui.phoenix.windows import sppasTextCtrl
from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows import sppasScrolledPanel
from sppas.src.ui.phoenix.windows import sppasStaticText
from sppas.src.ui.phoenix.windows import sppasStaticLine

from ..windows.book import sppasSimplebook
from ..windows.button import BitmapTextButton, sppasTextButton
from ..main_events import DataChangedEvent

from .annotevent import PageChangeEvent, EVT_PAGE_CHANGE

# -----------------------------------------------------------------------

LANG_NONE = "---"


def _(message):
    return u(msg(message, "ui"))

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

        # The annotations the system can perform
        self.__param = sppasParam()

        # 1st page: the buttons to perform actions
        self.ShowNewPage(sppasActionAnnotate(self, self.__param))

        # 2nd: list of standalone annotations
        self.AddPage(sppasAnnotations(self, self.__param, "STANDALONE"), text="")

        # 3rd: list of speaker annotations
        self.AddPage(sppasAnnotations(self, self.__param, "SPEAKER"), text="")

        # 4th: list of interaction annotations
        self.AddPage(sppasAnnotations(self, self.__param, "INTERACTION"), text="")

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

    def __init__(self, parent, param):
        super(sppasActionAnnotate, self).__init__(
            parent=parent,
            name="page_to_annotate",
            style=wx.BORDER_NONE
        )
        self.__param = param
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
        self.btn_select1 = self.__create_select_annot_btn("STANDALONE annotations")
        self.btn_select2 = self.__create_select_annot_btn("SPEAKER annotations")
        self.btn_select3 = self.__create_select_annot_btn("INTERACTION annotations")

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
        sizer.Add(s1, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL)
        sizer.Add(stl, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 20)
        sizer.Add(s2, 2,  wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL)
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

        btn = BitmapTextButton(self, name="on-off-off", label=label)
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = 12
        btn.BorderWidth = 2
        btn.BorderColour = wx.Colour(128, 128, 128, 128)
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(w, h))
        return btn

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
            self.notify("page_STANDALONE")
            found = False
            for i in range(self.__param.get_step_numbers()):
                a = self.__param.get_step(i)
                if a.get_activate() is True:
                    self.btn_select1.SetName("on-off-on")
                    found = True
                    break
            if found is False:
                self.btn_select1.SetName("on-off-off")

        elif event_obj == self.btn_select2:
            self.notify("page_SPEAKER")

        elif event_obj == self.btn_select3:
            self.notify("page_INTERACTION")

    # -----------------------------------------------------------------------

    def _annotate(self):
        """Perform the selected automatic annotations."""
        pass

# ---------------------------------------------------------------------------


class sppasAnnotations(sppasScrolledPanel):

    def __init__(self, parent, param, anntype="STANDALONE"):
        super(sppasAnnotations, self).__init__(
            parent=parent,
            name="page_"+anntype,
            style=wx.BORDER_NONE
        )
        self.__anntype = anntype
        self.__annparams = list()
        for i in range(param.get_step_numbers()):
            a = param.get_step(i)
            if self.__anntype in a.get_types():
                self.__annparams.append(a)

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
        sizer = wx.BoxSizer(wx.VERTICAL)

        btn_size = int(64. * wx.GetApp().settings.size_coeff)

        btn_back_top = BitmapTextButton(self, name="arrow_back")
        btn_back_top.FocusWidth = 0
        btn_back_top.BorderWidth = 0
        btn_back_top.BitmapColour = self.GetForegroundColour()
        btn_back_top.SetMinSize(wx.Size(btn_size, btn_size))
        sizer.Add(btn_back_top, 0)

        for i, a in enumerate(self.__annparams):
            pa = sppasEnableAnnotation(self, a)
            sizer.Add(self.HorizLine(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, btn_size // 4)
            sizer.Add(pa, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, btn_size // 4)
            sizer.Add(self.HorizLine(self), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, btn_size // 4)

        btn_back_bottom = BitmapTextButton(self, name="arrow_back")
        btn_back_bottom.FocusWidth = 0
        btn_back_bottom.BorderWidth = 0
        btn_back_bottom.BitmapColour = self.GetForegroundColour()
        btn_back_bottom.SetMinSize(wx.Size(btn_size, btn_size))
        sizer.Add(btn_back_bottom, 0)

        self.SetSizer(sizer)
        self.SetupScrolling(scroll_x=True, scroll_y=True)

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


class sppasEnableAnnotation(sppasPanel):

    def __init__(self, parent, annparam):
        super(sppasEnableAnnotation, self).__init__(
            parent=parent,
            name="page_" + annparam.get_key(),
            style=wx.BORDER_NONE
        )
        self.__annparam = annparam
        self._create_content()
        self._setup_events()

        self.Layout()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        es = self.__create_enable_sizer()
        ls = self.__create_lang_sizer()
        ds = self.__create_description_sizer()
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(es, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(ls, 0, wx.ALIGN_CENTRE)
        sizer.Add(ds, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        self.SetSizerAndFit(sizer)

    # ------------------------------------------------------------------------

    def __create_enable_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        w = int(128. * wx.GetApp().settings.size_coeff)
        h = int(32. * wx.GetApp().settings.size_coeff)

        btn_enable = BitmapTextButton(self, label=self.__annparam.get_name(), name="on-off-off")
        btn_enable.LabelPosition = wx.RIGHT
        btn_enable.Spacing = 12
        btn_enable.FocusWidth = 0
        btn_enable.BorderWidth = 0
        btn_enable.BitmapColour = self.GetForegroundColour()
        btn_enable.SetMinSize(wx.Size(w, h))

        btn_configure = sppasTextButton(self, label=_("Configure") + "...", name="configure")
        btn_configure.SetForegroundColour(wx.Colour(80, 100, 220))
        btn_configure.SetMinSize(wx.Size(w, h))

        sizer.Add(btn_enable, 1, wx.EXPAND)
        sizer.Add(btn_configure, 1, wx.ALIGN_CENTRE | wx.EXPAND)
        return sizer

    # ------------------------------------------------------------------------

    def __create_lang_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        choicelist = self.__annparam.get_langlist()
        w = int(80. * wx.GetApp().settings.size_coeff)

        # choice of the language
        self.choice = None
        # if there are different languages available, add a choice to the panel
        if len(choicelist) > 0:
            choicelist.append(LANG_NONE)
            self.choice = wx.ComboBox(self, -1, choices=sorted(choicelist))
            self.choice.SetSelection(self.choice.GetItems().index(LANG_NONE))
            self.choice.SetMinSize(wx.Size(w, -1))
            self.choice.Bind(wx.EVT_COMBOBOX, self._on_lang_changed)
            sizer.Add(self.choice, 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT, 12)
        else:
            p = sppasPanel(self)
            p.SetMinSize(wx.Size(w, -1))
            sizer.Add(p, 0, wx.ALIGN_CENTRE | wx.LEFT | wx.RIGHT, 12)

        return sizer

    # ------------------------------------------------------------------------

    def __create_description_sizer(self):
        text_style = wx.TAB_TRAVERSAL | \
                     wx.TE_MULTILINE | \
                     wx.TE_READONLY | \
                     wx.TE_BESTWRAP | \
                     wx.TE_AUTO_URL | \
                     wx.NO_BORDER | \
                     wx.TE_RICH
        sizer = wx.BoxSizer(wx.VERTICAL)
        td = sppasTextCtrl(self, value=self.__annparam.get_descr(), style=text_style)
        td.SetMinSize(wx.Size(256, 64))
        td.SetMinSize(wx.Size(512, 64))
        sizer.Add(td, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 12)
        return sizer

    # ------------------------------------------------------------------------
    # Events management
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

        if event_name == "on-off-off":
            event_obj.SetName("on-off-on")
            self.__annparam.set_activate(True)

        elif event_name == "on-off-on":
            event_obj.SetName("on-off-off")
            self.__annparam.set_activate(False)

        elif event_name == "configure":
            pass

    # -----------------------------------------------------------------------

    def _on_lang_changed(self, event):
        lang = self.choice.GetValue()
        if lang == LANG_NONE:
            lang = None
        # a.set_lang(lang, step_idx)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Window.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            if c.GetName() != "configure":
                c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        r, g, b = colour.Red(), colour.Green(), colour.Blue()
        delta = 10
        if (r + g + b) > 384:
            colour = wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)
        else:
            colour = wx.Colour(r, g, b, 50).ChangeLightness(100 + delta)

        wx.Window.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)
