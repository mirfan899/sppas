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

    ui.phoenix.pages.filespck.associate.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Actions to associate files and references of the catalogues.

"""

import wx
import logging

from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows.button import BitmapTextButton

# ---------------------------------------------------------------------------


class AssociatePanel(sppasPanel):
    """Panel with tools to associate files and references of the catalogues.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name=wx.PanelNameStr):
        super(AssociatePanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN,
            name=name)

        self._create_content()

        # State of the button to check all or none of the filenames
        self._checkall = False

        self.Bind(wx.EVT_KEY_DOWN, self.on_key_press)
        self.Layout()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        filtr = self.__create_button("check_filter")
        check = self.__create_button("checklist")
        link = self.__create_button("link_add")
        unlink = self.__create_button("link_del")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(4)
        sizer.Add(filtr, 1, wx.TOP | wx.ALIGN_CENTRE, 0)
        sizer.Add(check, 1, wx.TOP | wx.ALIGN_CENTRE, 0)
        sizer.AddStretchSpacer(2)
        sizer.Add(link, 1, wx.BOTTOM | wx.ALIGN_CENTRE, 0)
        sizer.Add(unlink, 1, wx.BOTTOM | wx.ALIGN_CENTRE, 0)
        sizer.AddStretchSpacer(4)

        self.SetMinSize(wx.Size(32, -1))
        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_button(self, icon):
        btn = BitmapTextButton(self, name=icon)
        btn.FocusStyle = wx.PENSTYLE_SOLID
        btn.FocusWidth = 3
        btn.FocusColour = wx.Colour(128, 128, 196, 128)  # violet
        # btn.LabelPosition = wx.RIGHT
        # btn.Spacing = 12
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(24, 24))
        btn.Bind(wx.EVT_BUTTON, self.on_associate)
        return btn

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def on_key_press(self, event):
        """Respond to a keypress event."""
        key_code = event.GetKeyCode()
        event.Skip()

    # ------------------------------------------------------------------------

    def on_associate(self, event):
        """Respond to an association event."""
        name = event.GetButtonObj().GetName()
        logging.debug("Event received of associate button: {:s}".format(name))

        if name == "check_filter":
            self.check_filter()

        elif name == "checklist":
            self.check_all()

        elif name == "link_add":
            self.add_links()

        elif name == "link_del":
            self.delete_links()

        event.Skip()

    # ------------------------------------------------------------------------
    # GUI methods to perform actions on the data
    # ------------------------------------------------------------------------

    def check_all(self):
        """Check all or any of the filenames."""
        # reverse the current state
        self._checkall = not self._checkall

        # get the current data of the workspace
        fd = self.GetParent().get_data()

        # ask the data to change their state
        fd.check(value=self._checkall)

        # TODO: update the list of checked catalogues

    # ------------------------------------------------------------------------

    def check_filter(self):
        """Check filenames matching the user-defined filters."""
        pass

    # ------------------------------------------------------------------------

    def add_links(self):
        """Associate checked filenames with checked catalogues."""
        pass

    # ------------------------------------------------------------------------

    def delete_links(self):
        """Dissociate checked filenames with checked catalogues."""
        pass
