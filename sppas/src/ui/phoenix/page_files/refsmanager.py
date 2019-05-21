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

    src.ui.phoenix.refsmanager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Main panel to manage the references.

"""

import logging
import wx

from sppas import sg
from sppas.src.files import FileReference, sppasAttribute

from sppas.src.ui.phoenix.dialogs.messages import sppasErrorDialog
from sppas.src.ui.phoenix.windows.dialog import sppasDialog
from sppas.src.ui.phoenix.windows.panel import sppasPanel
from .btntxttoolbar import BitmapTextToolbar
from .refstreectrl import ReferencesTreeViewCtrl
from .filesevent import DataChangedEvent

# ----------------------------------------------------------------------------


class ReferencesManager(sppasPanel):
    """Manage a catalogue of references and actions on perform on them.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name=wx.PanelNameStr):
        super(ReferencesManager, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        self._create_content()
        self._setup_events()
        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to manage data
    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to display to this panel.

        :param data: (FileData)

        """
        self.FindWindow('refsview').set_data(data)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        tb = self.__create_toolbar()
        cv = ReferencesTreeViewCtrl(self, name="refsview")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(cv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)

        self.SetMinSize((220, 200))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = BitmapTextToolbar(self)
        tb.set_focus_color(wx.Colour(64, 64, 196, 128))
        tb.AddText("References: ")
        tb.AddButton("refs-add", "Create")
        tb.AddButton("refs-edit", "Edit")
        tb.AddButton("refs-delete", "Delete")
        return tb

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

        # The user clicked (LeftDown - LeftUp) an action button of the toolbar
        self.Bind(wx.EVT_BUTTON, self._process_action)

    # ------------------------------------------------------------------------

    def notify(self):
        """Send the EVT_DATA_CHANGED to the parent."""
        if self.GetParent() is not None:
            evt = DataChangedEvent(data=self.FindWindow("fileview").get_data())
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()
        logging.debug('Files manager received the key event {:d}'
                      ''.format(key_code))

        #if key_code == wx.WXK_F5 and cmd_down is False and shift_down is False:
        #    logging.debug('Refresh all the files [F5 keys pressed]')
        #    self.FindWindow("refsview").update_data()
        #    self.notify()

        event.Skip()

    # ------------------------------------------------------------------------

    def _process_action(self, event):
        """Process an action of a button.

        :param event: (wx.Event)

        """
        name = event.GetButtonObj().GetName()
        logging.debug("Event received of button: {:s}".format(name))

        if name == "refs-add":
            self._add()

        elif name == "refs-delete":
            self._delete()

        elif name == "refs-edit":
            self._edit()

        event.Skip()

    # ------------------------------------------------------------------------

    def _add(self):
        """Open a dialog to create and append a new reference."""
        dlg = sppasCreateReference(self)
        response = dlg.ShowModal()
        if response == wx.ID_OK:
            rname = dlg.get_name()
            rtype = dlg.get_rtype()
            try:
                self.FindWindow('refsview').CreateRef(rname, rtype)
            except Exception as e:
                logging.error(str(e))
                message = "The reference {:s} has not been created due to " \
                          "the following error: {:s}".format(rname, str(e))
                sppasErrorDialog(message)
        dlg.Destroy()

    # ------------------------------------------------------------------------

    def _delete(self, event):
        """Delete the selected references.

        :param event:

        """
        dlg = wx.MessageDialog(self, 'Delete checked references')
        dlg.ShowModal()
        dlg.Destroy()

    # ------------------------------------------------------------------------

    def _edit(self, event):
        # add/remove/modify attributes of the selected references
        dlg = wx.MessageDialog(self, 'Edit checked references')
        dlg.ShowModal()
        dlg.Destroy()

# ----------------------------------------------------------------------------
# Panel to create a reference
# ----------------------------------------------------------------------------


class sppasCreateReference(sppasDialog):
    """A dialog to create a reference.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent):
        """Create a dialog to collect required information to create a reference.

        :param parent: (wx.Window)

        """
        super(sppasCreateReference, self).__init__(
            parent=parent,
            title='{:s} Create Reference'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self._create_content()
        self._create_buttons()

        self.SetMinSize(wx.Size(480, 320))
        self.LayoutComponents()
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def get_name(self):
        return self.to_name.GetValue()

    def get_rtype(self):
        return self.choice.GetSelection()

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")

        rname = wx.StaticText(panel, label="Name:")
        self.to_name = wx.TextCtrl(parent=panel, value="")

        rtype = wx.StaticText(panel, label="Type:")
        self.choice = wx.Choice(panel, choices=FileReference.REF_TYPES)

        grid = wx.FlexGridSizer(2, 2, 5, 5)
        grid.AddGrowableCol(0)
        grid.AddGrowableCol(1)

        grid.Add(rname, 0)
        grid.Add(self.to_name, 1, flag=wx.EXPAND)

        grid.Add(rtype, 0)
        grid.Add(self.choice, 1, flag=wx.EXPAND)

        panel.SetSizer(grid)
        panel.SetAutoLayout(True)
        self.SetContent(panel)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()
        if event_id == wx.ID_CANCEL:
            logging.debug('EVENT BUTTON CANCEL')
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()
        else:
            logging.debug('EVENT BUTTON OK')
            event.Skip()

# ----------------------------------------------------------------------------
# Panel to create a reference
# ----------------------------------------------------------------------------


class sppasEditReferences(sppasDialog):
    """A dialog to edit a set of references.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent):
        """Create a dialog to manage attributes of references.

        :param parent: (wx.Window)

        """
        super(sppasEditReferences, self).__init__(
            parent=parent,
            title='{:s} Edit References'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self._create_content()
        self._create_buttons()

        self.SetMinSize(wx.Size(480, 320))
        self.LayoutComponents()
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")
        #panel.SetSizer(grid)
        panel.SetAutoLayout(True)
        self.SetContent(panel)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()
        if event_id == wx.ID_CANCEL:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()
        else:
            event.Skip()

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(ReferencesManager):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        self.add_test_data()

    # ------------------------------------------------------------------------

    def add_test_data(self):
        fr1 = FileReference("AB")
        fr1.set_type(1)
        fr1.append(sppasAttribute("position", "left", descr="Position related to the other participant"))
        fr2 = FileReference("CM")
        fr2.set_type("SPEAKER")
        fr2.append(sppasAttribute("position", "right", descr="Position related to the other participant"))
        fr3 = FileReference("Dialog1")
        fr3.set_type(2)
        fr3.add("year", "2003")
        fr3.append(sppasAttribute("place", "Aix-en-Provence", descr="Place of recording"))
        self.FindWindow('refsview').AddRefs([fr1, fr2, fr3])
