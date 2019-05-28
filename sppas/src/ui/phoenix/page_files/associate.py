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

    ui.phoenix.page_files.associate.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Actions to associate files and references of the catalogue.

"""

import wx
import logging

from sppas import sppasTypeError
from sppas import sg
from sppas.src.config import ui_translation
from sppas.src.files import FileData
from sppas.src.files import States
from ..windows import sppasPanel
from ..windows import sppasDialog
from ..windows.button import BitmapTextButton

from .filesevent import DataChangedEvent
from .btntxttoolbar import BitmapTextToolbar

# ---------------------------------------------------------------------------

MSG_HEADER_FILTER = ui_translation.gettext("Checking files")

# ---------------------------------------------------------------------------


class AssociatePanel(sppasPanel):
    """Panel with tools to associate files and references of the catalogue.

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

        # State of the button to check all or none of the filenames
        self._checkall = False

        # The data this page is working on
        self.__data = FileData()

        # Construct the panel
        self._create_content()
        self._setup_events()
        self.Layout()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this panel.

        :param data: (FileData)

        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        logging.debug('New data to set in the associate panel.')
        self.__data = data

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

    # ------------------------------------------------------------------------

    def __create_button(self, icon, label=None):
        btn = BitmapTextButton(self, name=icon, label=label)
        btn.FocusStyle = wx.PENSTYLE_SOLID
        btn.FocusWidth = 3
        btn.FocusColour = wx.Colour(128, 128, 196, 128)  # violet
        btn.LabelPosition = wx.BOTTOM
        btn.Spacing = 4
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(24, 24))
        return btn

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # The user pressed a key of its keyboard
        self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked (LeftDown - LeftUp) an action button
        self.Bind(wx.EVT_BUTTON, self._process_action)

    # ------------------------------------------------------------------------

    def notify(self):
        """Send the EVT_DATA_CHANGED to the parent."""
        if self.GetParent() is not None:
            evt = DataChangedEvent(data=self.__data)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _process_key_event(self, event):
        """Respond to a keypress event."""
        key_code = event.GetKeyCode()
        logging.debug('Associate panel received a key event. key_code={:d}'.format(key_code))
        logging.debug('Key event skipped by the associate panel.')
        event.Skip()

    # ------------------------------------------------------------------------

    def _process_action(self, event):
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
        """Check all or any of the filenames and references."""
        # reverse the current state
        self._checkall = not self._checkall

        # ask the data to change their state
        if self._checkall is True:
            state = States().CHECKED
        else:
            state = States().UNUSED
        self.__data.set_object_state(state)

        # update the view of checked references & checked files
        self.notify()

    # ------------------------------------------------------------------------

    def check_filter(self):
        """Check filenames matching the user-defined filters."""
        dlg = sppasFilesFilterDialog(self)
        if dlg.ShowModal() == wx.ID_OK:

            data_filters = dlg.get_selected()
            if len(data_filters) > 0:
                # process = SingleFilterProcess(dlg, self.__data)
                # process.run()
                pass

        dlg.Destroy()

    # ------------------------------------------------------------------------

    def add_links(self):
        """Associate checked filenames with checked references."""
        associed = self.__data.associate()
        if associed > 0:
            self.notify()

    # ------------------------------------------------------------------------

    def delete_links(self):
        """Dissociate checked filenames with checked references."""
        dissocied = self.__data.dissociate()
        if dissocied > 0:
            self.notify()

# ---------------------------------------------------------------------------


class sppasFilesFilterDialog(sppasDialog):
    """Dialog to get filters to check files and references.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent):
        """Create a feedback dialog.

        :param parent: (wx.Window)

        """
        super(sppasFilesFilterDialog, self).__init__(
            parent=parent,
            title='{:s} Files selection'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self.CreateHeader(title="Check files with the following filters:",
                          icon_name="check_filter")
        self._create_content()
        self._create_buttons()
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.SetMinSize(wx.Size(480, 320))
        self.LayoutComponents()
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def get_selected(self):
        return None

    # -----------------------------------------------------------------------
    # Methods to construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")
        tb = self.__create_toolbar(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(wx.Panel(panel), proportion=1, flag=wx.EXPAND, border=0)
        panel.SetSizer(sizer)

        self.SetMinSize((320, 200))
        panel.SetAutoLayout(True)
        self.SetContent(panel)

    # -----------------------------------------------------------------------

    def __create_toolbar(self, parent):
        """Create the toolbar."""
        tb = BitmapTextToolbar(parent)
        tb.set_focus_color(wx.Colour(196, 196, 96, 128))
        tb.AddText("Create filters: ")
        tb.AddButton("filter_path", "+ Path")
        tb.AddButton("filter_file", "+ Name")
        tb.AddButton("filter_ext", "+ Type")
        tb.AddButton("filter", "+ Ref.")
        tb.AddButton("filter", "+ Id. Value")
        tb.AddSpacer()
        tb.AddButton("filter_remove", "- Remove")
        return tb

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        """Create the buttons and bind events."""
        panel = sppasPanel(self, name="actions")
        panel.SetMinSize(wx.Size(-1, wx.GetApp().settings.action_height))
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons
        cancel_btn = self.__create_action_button(panel, "Cancel", "cancel")
        apply_or_btn = self.__create_action_button(panel, "Apply - OR", "apply")
        apply_and_btn = self.__create_action_button(panel, "Apply - AND", "ok")

        sizer.Add(cancel_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(self.VertLine(parent=panel), 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(apply_or_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(self.VertLine(parent=panel), 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(apply_and_btn, 1, wx.ALL | wx.EXPAND, 0)

        panel.SetSizer(sizer)
        self.SetActions(panel)

    # -----------------------------------------------------------------------

    def __create_action_button(self, parent, text, icon):
        btn = BitmapTextButton(parent, label=text, name=icon)
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = 12
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize((32, 32))

        return btn

    # ------------------------------------------------------------------------
    # Callback to events
    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "cancel":
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()
        else:
            event.Skip()
