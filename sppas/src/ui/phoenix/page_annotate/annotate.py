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
    It's content is organized with a wxSimpleBook() with:
        - a page to fix parameters then run, then save the report,
        - 3 pages with the lists of annotations to select and configure,
        - a page with the progress bar and the procedure outcome report.

"""

import logging
import wx

from sppas import sppasTypeError
from sppas import annots
from sppas import msg
from sppas import u

from sppas.src.annotations import sppasParam
from sppas.src.files import FileData, States

from ..windows.book import sppasSimplebook
from ..main_events import DataChangedEvent

from .annotevent import EVT_PAGE_CHANGE
from .annotselect import sppasAnnotationsPanel
from .annotaction import sppasActionAnnotatePanel
from .annotlog import sppasLogAnnotatePanel

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
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasAnnotatePanel, self).__init__(
            parent=parent,
            name="page_annotate",
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS
        )
        self.SetEffectsTimeouts(150, 150)

        # The annotations the system can perform
        self.__param = sppasParam()
        self.__pages_annot = dict()

        # 1st page: the buttons to perform actions
        self.ShowNewPage(sppasActionAnnotatePanel(self, self.__param))

        # list of "ann_types" annotations
        for ann_type in annots.types:
            page = sppasAnnotationsPanel(self, self.__param, ann_type)
            self.AddPage(page, text="")
            self.__pages_annot[ann_type] = page

        # 5th page: procedure outcome report
        page = sppasLogAnnotatePanel(self, self.__param)
        self.AddPage(page, text="")

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

        :return: (FileData) The workspace with files to annotate/annotated

        """
        return self.__param.get_workspace()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (FileData) The workspace with files to annotate/annotated

        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        logging.debug('New data to set in the annotate page. '
                      'Id={:s}'.format(data.id))

        self.__param.set_workspace(data)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """Send the EVT_DATA_CHANGED to the parent."""
        if self.GetParent() is not None:
            data = self.__param.get_workspace()
            data.set_state(States().CHECKED)
            evt = DataChangedEvent(data=data)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def _process_page_change(self, event):
        """Process a PageChangeEvent.

        :param event: (wx.Event)

        """
        try:
            destination = event.to_page
            fct = event.fct
        except AttributeError:
            destination = "page_annot_actions"
            fct = ""

        self.show_page(destination, fct)

    # -----------------------------------------------------------------------
    # Public methods to navigate
    # -----------------------------------------------------------------------

    def show_page(self, page_name, fct=""):
        """Show a page of the book.

        :param page_name: (str) one of 'page_annot_actions', 'page_...', ...
        :param fct: (str) a method of the page

        """
        # Find the page number to switch on
        dest_w = self.FindWindow(page_name)
        if dest_w is None:
            dest_w = self.FindWindow("page_annot_actions")
        p = self.FindPage(dest_w)
        if p == -1:
            p = 0

        # Current page number
        c = self.FindPage(self.GetCurrentPage())  # current page position
        cur_w = self.GetPage(c)  # Returns the window at the given page position

        # Showing the current page is already done!
        if c == p:
            return

        # Assign the effect
        if c < p:
            self.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_TOP,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_TOP)
        elif c > p:
            self.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_BOTTOM,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_BOTTOM)

        # Change to the destination page
        dest_w.set_param(cur_w.get_param())
        self.ChangeSelection(p)
        dest_w.Refresh()

        # Call a method of the class
        if len(fct) > 0:
            try:
                getattr(dest_w, fct)()
            except AttributeError as e:
                logging.error("{:s}".format(str(e)))
