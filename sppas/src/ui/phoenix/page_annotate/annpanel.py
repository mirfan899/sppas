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

    ui.phoenix.page_annotate.annpanel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx

from sppas import msg
from sppas import u
from sppas import annots

from ..windows import sppasTextCtrl
from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..windows import sppasStaticLine
from ..windows.button import BitmapTextButton, sppasTextButton

from .annotevent import PageChangeEvent

# ---------------------------------------------------------------------------

LANG_NONE = "---"


def _(message):
    return u(msg(message, "ui"))

# ---------------------------------------------------------------------------


class sppasAnnotations(sppasScrolledPanel):
    """Create a panel to fix properties of all the annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent, param, anntype=annots.types[0]):
        super(sppasAnnotations, self).__init__(
            parent=parent,
            name="page_"+anntype,
            style=wx.BORDER_NONE
        )
        # The type of annotations this page is supporting
        self.__anntype = anntype

        # The parameters to set the properties
        self.__param = param

        # Construct the panel

        self._create_content()
        self._setup_events()

        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to manage the data
    # -----------------------------------------------------------------------

    def get_param(self):
        for i in range(self.__param.get_step_numbers()):
            annparam = self.__param.get_step(i)
            if annparam.get_activate() is True:
                logging.info("Annotation {:s} is activated. "
                             "Language is set to '{!s:s}'"
                             "".format(annparam.get_name(), annparam.get_lang()))
        return self.__param

    # -----------------------------------------------------------------------

    def set_param(self, param):
        logging.debug('ANNOTATIONS PAGE: set param')
        for i in range(param.get_step_numbers()):
            annparam = param.get_step(i)
            w = self.FindWindow("page_" + annparam.get_key())
            if w is not None:
                w.set_annparam(annparam)
            else:
                logging.error("Panel not found for step: {:s}"
                              "".format(annparam.get_key()))
        self.__param = param

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

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

        title = wx.StaticText(self, label="Annotations of type {:s}".format(self.__anntype), name="title_text")
        sizer_top.Add(title, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(sizer_top, 0, wx.EXPAND)

        for i in range(self.__param.get_step_numbers()):
            a = self.__param.get_step(i)
            if self.__anntype in a.get_types():
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

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        wx.Window.SetFont(self, font)
        for child in self.GetChildren():
            if child.GetName() != "title_text":
                child.SetFont(font)
            else:
                try:
                    settings = wx.GetApp().settings
                    child.SetFont(settings.header_text_font)
                except:
                    pass

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Window.SetForegroundColour(self, colour)
        for child in self.GetChildren():
            if child.GetName() != "title_text":
                child.SetForegroundColour(colour)
            else:
                try:
                    settings = wx.GetApp().settings
                    child.SetForegroundColour(settings.header_fg_color)
                except:
                    child.SetForegroundColour(colour)

# ---------------------------------------------------------------------------
# Annotation panel to enable and select language.
# ---------------------------------------------------------------------------


class sppasEnableAnnotation(sppasPanel):
    """Create a panel to enable and select language of an annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

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

    def set_annparam(self, p):
        """Set a new AnnotationParam()."""
        self.__annparam = p
        self.Refresh()

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
        choicelist = self.__annparam.get_langlist()
        w = int(80. * wx.GetApp().settings.size_coeff)

        # choice of the language
        choice = sppasPanel(self, name="lang_panel")

        # if there are different languages available, add a choice to the panel
        if len(choicelist) > 0:
            choicelist.append(LANG_NONE)
            lang = self.__annparam.get_lang()
            if lang is None or len(lang) == 0:
                lang = LANG_NONE
            choice = wx.ComboBox(self, -1, choices=sorted(choicelist), name="lang_choice")
            choice.SetSelection(choice.GetItems().index(lang))
            choice.Bind(wx.EVT_COMBOBOX, self._on_lang_changed)

        choice.SetMinSize(wx.Size(w, -1))

        return choice

    # ------------------------------------------------------------------------

    def __create_description_sizer(self):
        text_style = wx.TAB_TRAVERSAL | \
                     wx.TE_MULTILINE | \
                     wx.TE_READONLY | \
                     wx.TE_BESTWRAP | \
                     wx.TE_AUTO_URL | \
                     wx.NO_BORDER | \
                     wx.TE_RICH
        #sizer = wx.BoxSizer(wx.VERTICAL)
        td = sppasTextCtrl(self, value=self.__annparam.get_descr(), style=text_style)
        td.SetMinSize(wx.Size(256, 64))
        td.SetMinSize(wx.Size(512, 64))
        #sizer.Add(td, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 12)
        #return sizer
        return td

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
        choice = event.GetEventObject()
        lang = choice.GetValue()
        if lang == LANG_NONE:
            lang = None
        self.__annparam.set_lang(lang)

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

    # -----------------------------------------------------------------------

    def Refresh(self, eraseBackground=True, rect=None):
        """Overridden."""
        if len(self.__annparam.get_langlist()) > 0:
            lang = self.__annparam.get_lang()
            if lang is None or len(lang) == 0:
                lang = LANG_NONE
            choice = self.FindWindow("lang_choice")
            choice.SetSelection(choice.GetItems().index(lang))

        wx.Window.Refresh(self, eraseBackground=True, rect=None)
