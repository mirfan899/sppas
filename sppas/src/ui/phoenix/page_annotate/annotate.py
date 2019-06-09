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
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    One of the main pages of the wx4-based GUI of SPPAS: the one to annotate.

"""

import logging
import wx

from sppas import sppasTypeError
from sppas import annots
from sppas import msg
from sppas import u

from sppas.src.annotations import sppasParam, sppasAnnotationsManager
from sppas.src.files import FileData, States

from ..windows import sppasPanel
from ..windows import sppasStaticText
from ..windows.book import sppasSimplebook
from ..windows.button import BitmapTextButton
from ..main_events import DataChangedEvent

from .annotevent import PageChangeEvent, EVT_PAGE_CHANGE
from .annpanel import sppasAnnotations, LANG_NONE

# -----------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))

# ---------------------------------------------------------------------------


class sppasAnnotatePanel(sppasSimplebook):
    """Create a book to annotate automatically the selected files.

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
        self.SetEffectsTimeouts(150, 150)

        # The data this page is working on
        self.__data = FileData()

        # The annotations the system can perform
        self.__param = sppasParam()
        self.__pages_annot = dict()

        # 1st page: the buttons to perform actions
        self.ShowNewPage(sppasActionAnnotate(self, self.__param))

        # 2nd: list of standalone annotations
        # 3rd: list of speaker annotations
        # 4th: list of interaction annotations
        for ann_type in annots.types:
            page = sppasAnnotations(self, self.__param, ann_type)
            self.AddPage(page, text="")
            self.__pages_annot[ann_type] = page

        # Change the displayed page
        self.Bind(EVT_PAGE_CHANGE, self._process_page_change)

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

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
    # Public methods to navigate
    # -----------------------------------------------------------------------

    def show_page(self, page_name):
        """Show a page of the book.

        :param page_name: (str) one of 'page_to_annotate', 'page_...', ...

        """
        # Find the page number to switch on
        dest_w = self.FindWindow(page_name)
        if dest_w is None:
            dest_w = self.FindWindow("page_to_annotate")
        p = self.FindPage(dest_w)
        if p == -1:
            p = 0

        # current page number
        c = self.FindPage(self.GetCurrentPage())  # current page position
        cur_w = self.GetPage(c)  # Returns the window at the given page position

        # Showing the current page is already done!
        if c == p:
            return

        # assign the effect
        if c < p:
            self.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_TOP,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_TOP)
        elif c > p:
            self.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_BOTTOM,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_BOTTOM)

        # then change to the destination page
        dest_w.set_param(cur_w.get_param())
        self.ChangeSelection(p)
        dest_w.Refresh()

# ---------------------------------------------------------------------------


class sppasActionAnnotate(sppasPanel):
    """Create a panel to configure then run automatic annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent, param):
        super(sppasActionAnnotate, self).__init__(
            parent=parent,
            name="page_to_annotate",
            style=wx.BORDER_NONE
        )
        self.__param = param
        self.__btns_annot = dict()

        self._create_content()
        self._setup_events()

        self.Layout()

    # ------------------------------------------------------------------------

    def get_param(self):
        return self.__param

    def set_param(self, param):
        self.__param = param
        self.UpdateUI()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""

        # The language (if any)
        stl = sppasStaticText(self, label="STEP 1: fix the language(s)")
        self.choice = self.__create_lang_btn()

        # The buttons to select annotations (switch to other pages)
        sta = sppasStaticText(self, label="STEP 2: select the annotations to perform")
        s1 = wx.BoxSizer(wx.HORIZONTAL)
        for ann_type in annots.types:
            btn = self.__create_select_annot_btn("{:s} annotations".format(ann_type))
            self.__btns_annot[ann_type] = btn
            s1.Add(btn, 1, wx.EXPAND | wx.ALL, 4)

        # The button to perform annotations
        str = sppasStaticText(self, label="STEP 3: perform the annotations")
        self.btn_run = self.__create_select_annot_btn("Let's go!")
        self.btn_run.SetName("wizard")
        self.btn_run.Enable(False)
        self.btn_run.BorderColour = wx.Colour(228, 24, 24, 128)

        # The button to save the POR
        stp = sppasStaticText(self, label="STEP 4: save the procedure outcome report")
        self.btn_por = self.__create_select_annot_btn("Save report as...")
        self.btn_por.SetName("save_as")
        self.btn_por.Enable(False)
        self.btn_por.BorderColour = wx.Colour(228, 24, 24, 128)

        # Organize all the objects
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(stl, 1, wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 15)
        sizer.Add(self.choice, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL)

        sizer.Add(sta, 1, wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 15)
        sizer.Add(s1, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL)

        sizer.Add(str, 1, wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 15)
        sizer.Add(self.btn_run, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL)

        sizer.Add(stp, 1, wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 15)
        sizer.Add(self.btn_por, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL | wx.BOTTOM, 15)

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

    # ------------------------------------------------------------------------

    def __create_lang_btn(self):
        w = int(80. * wx.GetApp().settings.size_coeff)

        all_langs = list()
        for i in range(self.__param.get_step_numbers()):
            a = self.__param.get_step(i)
            all_langs.extend(a.get_langlist())

        langlist = list(set(all_langs))
        langlist.append(LANG_NONE)
        choice = wx.ComboBox(self, -1, choices=sorted(langlist), name="lang_choice")
        choice.SetSelection(choice.GetItems().index(LANG_NONE))
        choice.SetMinSize(wx.Size(w, -1))
        choice.Bind(wx.EVT_COMBOBOX, self._on_lang_changed)
        return choice

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

        for ann_type in annots.types:
            if event_obj == self.__btns_annot[ann_type]:
                self.notify("page_{:s}".format(ann_type))

        if event_name == "wizard":
            self._annotate()
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _on_lang_changed(self, event):
        logging.debug('Lang changed:')
        lang = self.choice.GetValue()
        for i in range(self.__param.get_step_numbers()):
            a = self.__param.get_step(i)
            if len(a.get_langlist()) > 0:
                a.set_lang(lang)
                logging.debug('  - {:s}'.format(a.get_key()))

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def _annotate(self):
        """Perform the selected automatic annotations."""
        pass

    # -----------------------------------------------------------------------

    def UpdateUI(self):
        """Update the UI depending on the parameters."""

        # search for enabled annotations and fixed languages
        ann_enabled = [False] * len(annots.types)
        lang = list()

        for i in range(self.__param.get_step_numbers()):
            a = self.__param.get_step(i)
            if a.get_activate() is True:
                for x, ann_type in enumerate(annots.types):
                    if ann_type in a.get_types():
                        ann_enabled[x] = True
                # at least one annotation can be performed
                # (no need of the lang or lang is defined)
                if a.get_lang() is None or (len(a.get_langlist()) > 0 and len(a.get_lang()) > 0):
                    lang.append(a.get_lang())

        # update the button to set the language
        choice = self.FindWindow("lang_choice")
        langs = list(set(lang))
        if None in langs:
            langs.remove(None)
        if len(langs) <= 1:
            mix_item = choice.FindString("MIX")
            if mix_item != wx.NOT_FOUND:
                choice.Delete(mix_item)
            if len(langs) == 0:
                choice.SetSelection(choice.GetItems().index(LANG_NONE))
            else:
                choice.SetSelection(choice.GetItems().index(langs[0]))
        else:
            # several languages
            i = choice.Append("MIX")
            choice.SetSelection(i)

        # update buttons to fix properties of annotations
        for i, ann_type in enumerate(annots.types):
            if ann_enabled[i] is True:
                self.__btns_annot[ann_type].SetName("on-off-on")
            else:
                self.__btns_annot[ann_type].SetName("on-off-off")

        # update the button to perform annotations
        # at least one annotation is enabled and lang is fixed.
        if len(lang) == 0:
            self.btn_run.Enable(False)
            self.btn_run.BorderColour = wx.Colour(228, 24, 24, 128)
        else:
            self.btn_run.Enable(True)
            self.btn_run.BorderColour = wx.Colour(24, 228, 24, 128)
