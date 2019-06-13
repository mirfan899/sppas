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

    ui.phoenix.page_annotate.annotaction.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx
import os

from sppas import annots

from ..windows import sppasPanel
from ..windows import sppasStaticText
from ..windows import BitmapTextButton

from .annotevent import PageChangeEvent
from .annotselect import LANG_NONE

# ---------------------------------------------------------------------------


class sppasActionAnnotate(sppasPanel):
    """Create a panel to configure then run automatic annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, param):
        super(sppasActionAnnotate, self).__init__(
            parent=parent,
            name="page_annot_actions",
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
        choice = self.__create_lang_btn()

        sizer_lang = wx.BoxSizer(wx.VERTICAL)
        sizer_lang.Add(stl, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 15)
        sizer_lang.Add(choice, 0, wx.ALIGN_TOP | wx.ALIGN_CENTRE_HORIZONTAL)

        # The buttons to select annotations (switch to other pages)
        sta = sppasStaticText(self, label="STEP 2: select the annotations to perform")
        s1 = wx.BoxSizer(wx.HORIZONTAL)
        for ann_type in annots.types:
            btn = self.__create_select_annot_btn("{:s} annotations".format(ann_type))
            self.__btns_annot[ann_type] = btn
            s1.Add(btn, 1, wx.EXPAND | wx.ALL, 4)

        sizer_select = wx.BoxSizer(wx.VERTICAL)
        sizer_select.Add(sta, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 15)
        sizer_select.Add(s1, 0, wx.ALIGN_TOP | wx.ALIGN_CENTRE_HORIZONTAL)

        # The button to perform annotations
        str = sppasStaticText(self, label="STEP 3: perform the annotations")
        self.btn_run = self.__create_select_annot_btn("Let's go!")
        self.btn_run.SetName("wizard")
        self.btn_run.Enable(False)
        self.btn_run.BorderColour = wx.Colour(228, 24, 24, 128)
        sizer_run = wx.BoxSizer(wx.VERTICAL)
        sizer_run.Add(str, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 15)
        sizer_run.Add(self.btn_run, 0, wx.ALIGN_TOP | wx.ALIGN_CENTRE_HORIZONTAL)

        # The button to save the POR
        stp = sppasStaticText(self, label="STEP 4: save the procedure outcome report")
        self.btn_por = self.__create_select_annot_btn("Save report as...")
        self.btn_por.SetName("save_as")
        self.btn_por.Enable(False)
        self.btn_por.BorderColour = wx.Colour(228, 24, 24, 128)
        sizer_log = wx.BoxSizer(wx.VERTICAL)
        sizer_log.Add(stp, 1, wx.ALIGN_BOTTOM | wx.ALIGN_CENTRE_HORIZONTAL | wx.TOP | wx.BOTTOM, 15)
        sizer_log.Add(self.btn_por, 0, wx.ALIGN_TOP | wx.ALIGN_CENTRE_HORIZONTAL | wx.BOTTOM, 10)

        # Organize all the objects
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sizer_lang, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        sizer.Add(sizer_select, 2, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        sizer.Add(sizer_run, 2, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        sizer.Add(sizer_log, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

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
        # Bind all events from our buttons
        self.Bind(wx.EVT_BUTTON, self._process_event)

        # Language choice changed
        self.FindWindow("lang_choice").Bind(wx.EVT_COMBOBOX, self._on_lang_changed)

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
                self.notify("page_annot_{:s}".format(ann_type))

        if event_name == "wizard":
            self._annotate()

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _on_lang_changed(self, event):
        choice = event.GetEventObject()
        lang = choice.GetValue()
        if lang == LANG_NONE:
            lang = None

        for i in range(self.__param.get_step_numbers()):
            a = self.__param.get_step(i)
            if len(a.get_langlist()) > 0:
                if lang in a.get_langlist():
                    a.set_lang(lang)
                else:
                    a.set_lang(None)

        self.UpdateUI(update_lang=False)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def _annotate(self):
        """Perform the selected automatic annotations."""
        pass

    # -----------------------------------------------------------------------

    def UpdateUI(self,
                 update_lang=True,
                 update_annot=True,
                 update_run=True,
                 update_log=True):
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
                if a.get_lang() is None or \
                        (len(a.get_langlist()) > 0 and len(a.get_lang()) > 0):
                    lang.append(a.get_lang())

        # update the button to set the language
        if update_lang is True:
            langs = list(set(lang))
            if None in langs:
                langs.remove(None)
            choice = self.FindWindow("lang_choice")
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
        if update_annot is True:
            for i, ann_type in enumerate(annots.types):
                if ann_enabled[i] is True:
                    self.__btns_annot[ann_type].SetName("on-off-on")
                else:
                    self.__btns_annot[ann_type].SetName("on-off-off")

        # update the button to perform annotations
        # at least one annotation is enabled and lang is fixed.
        if update_run is True:
            if len(lang) == 0:
                self.btn_run.Enable(False)
                self.btn_run.BorderColour = wx.Colour(228, 24, 24, 128)
            else:
                self.btn_run.Enable(True)
                self.btn_run.BorderColour = wx.Colour(24, 228, 24, 128)

        report = self.__param.get_report_filename()
        if update_log is True:
            if report is None or os.path.exists(report) is False:
                self.btn_por.Enable(False)
                self.btn_por.BorderColour = wx.Colour(228, 24, 24, 128)
            else:
                self.btn_por.Enable(True)
                self.btn_por.BorderColour = wx.Colour(24, 228, 24, 128)
