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

    src.ui.phoenix.page_files.refsmanager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Main panel to manage the references.

"""

import logging
import wx

from sppas import sg
from sppas.src.files.fileref import FileReference, sppasAttribute
from sppas.src.files.filebase import States

from ..windows import sppasDialog
from ..windows import sppasPanel
from ..windows import sppasStaticLine
from ..windows import sppasStaticText
from ..windows import sppasTextCtrl
from ..windows import RadioButton
from ..dialogs import Information
from ..dialogs import Error

from .btntxttoolbar import BitmapTextToolbar
from .refstreectrl import ReferencesTreeViewCtrl
from .filesevent import DataChangedEvent
from .filesutils import IdentifierTextValidator


# ---------------------------------------------------------------------------
# List of displayed messages:

REF_TITLE = "References: "
REF_ACT_CREATE = "Create"
REF_ACT_EDIT = "Edit"
REF_ACT_DEL = "Delete"

REF_MSG_CREATE_ERROR = "The reference {:s} has not been created due to " \
                       "the following error: {:s}"
REF_MSG_DEL_ERROR = "An error occurred while removing the references: {:s}"
REF_MSG_DEL_INFO = "{:d} references deleted."
REF_MSG_NB_CHECKED = "No reference checked."

# ----------------------------------------------------------------------------


class ReferencesManager(sppasPanel):
    """Manage a catalogue of references and actions on perform on them.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    HIGHLIGHT_COLOUR = wx.Colour(128, 128, 228, 196)  # blue

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
        tb.set_focus_color(ReferencesManager.HIGHLIGHT_COLOUR)
        tb.AddTitleText(REF_TITLE, color=ReferencesManager.HIGHLIGHT_COLOUR)
        tb.AddButton("refs-add", REF_ACT_CREATE)
        tb.AddButton("refs-edit", REF_ACT_EDIT)
        tb.AddButton("refs-delete", REF_ACT_DEL)
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
            data = self.FindWindow("refsview").get_data()
            data.set_state(States().CHECKED)
            evt = DataChangedEvent(data=data)
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
                self.notify()
            except Exception as e:
                logging.error(str(e))
                message = REF_MSG_CREATE_ERROR.format(rname, str(e))
                Error(message)
        dlg.Destroy()

    # ------------------------------------------------------------------------

    def _delete(self):
        """Delete the selected references.

        """
        view = self.FindWindow('refsview')
        if view.HasCheckedRefs() is False:
            Error(REF_MSG_NB_CHECKED)
        else:
            try:
                nb = view.RemoveCheckedRefs()
                if nb > 0:
                    Information(REF_MSG_DEL_INFO.format(nb))
                    self.notify()
            except Exception as e:
                Error(REF_MSG_DEL_ERROR.format(str(e)))

    # ------------------------------------------------------------------------

    def _edit(self):
        # add/remove/modify attributes of the selected references
        logging.debug('Edit attribute.')
        view = self.FindWindow('refsview')
        if view.HasCheckedRefs() is False:
            Error(REF_MSG_NB_CHECKED)
        else:
            dlg = sppasEditAttributes(self)
            response = dlg.ShowModal()
            if response == wx.ID_OK:
                self.notify()
                if dlg.get_action() == 0:
                    view.RemoveAttribute(dlg.get_id())
                else:
                    try:
                        view.AddAttribute(
                            dlg.get_id(),
                            dlg.get_value_type()[0],
                            dlg.get_value_type()[1],
                            dlg.get_description()
                        )
                    except Exception as e:
                        Error(str(e))

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

        # self.SetMinSize(wx.Size(480, 320))
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

        rname = sppasStaticText(panel, label="Name:")
        self.to_name = sppasTextCtrl(parent=panel, value="")

        rtype = wx.StaticText(panel, label="Type:")
        self.choice = wx.Choice(panel, choices=FileReference.REF_TYPES)
        self.choice.SetSelection(0)

        grid = wx.FlexGridSizer(2, 2, 5, 5)
        grid.AddGrowableCol(0)
        grid.AddGrowableCol(1)

        grid.Add(rname, 0)
        grid.Add(self.to_name, 1, flag=wx.EXPAND)

        grid.Add(rtype, 0)
        grid.Add(self.choice, 1, flag=wx.EXPAND)

        panel.SetSizer(grid)
        panel.SetMinSize(wx.Size(320, 200))
        panel.SetAutoLayout(True)
        grid.FitInside(panel)
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
# Panel to create a reference
# ----------------------------------------------------------------------------


class sppasEditAttributes(sppasDialog):
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
        super(sppasEditAttributes, self).__init__(
            parent=parent,
            title='{:s} Manage Reference Values'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self._create_content()
        self._create_buttons()

        self.SetMinSize(wx.Size(480, 320))
        self.LayoutComponents()
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------

    def get_action(self):
        """Return 0/False to delete and 1/True to add."""
        return self.FindWindow('radio_add').GetValue()

    # -----------------------------------------------------------------------

    def get_id(self):
        """Return the identifier."""
        return self.FindWindow('text_id').GetValue()

    # -----------------------------------------------------------------------

    def get_value_type(self):
        """Return a tuple with the value and its type."""
        return (
            self.FindWindow('text_value').GetValue(),
            self.FindWindow('choice_type').GetStringSelection()
        )

    # -----------------------------------------------------------------------

    def get_description(self):
        """Return the description of the value."""
        return self.FindWindow('text_descr').GetValue()

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")
        sizer = wx.GridBagSizer(9, 3)

        st1 = sppasStaticText(panel, label="Required:")
        sizer.Add(st1, pos=(0, 0), span=(1, 2), flag=wx.EXPAND | wx.ALL,  border=2)

        add_btn = RadioButton(
            panel,
            label="Add a new value in the checked references",
            name="radio_add")
        add_btn.SetValue(True)
        sizer.Add(add_btn, pos=(1, 0), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=12)

        del_btn = RadioButton(
            panel,
            label="Delete an existing value in the checked references",
            name="radio_del")
        add_btn.SetValue(False)
        sizer.Add(del_btn, pos=(2, 0), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=12)

        id_st1 = sppasStaticText(panel, label="Identifier: ")
        sizer.Add(id_st1, pos=(3, 0), flag=wx.LEFT, border=12)
        ident = sppasTextCtrl(
            parent=panel,
            value="",
            validator=IdentifierTextValidator(),
            name="text_id"
        )
        self.Bind(wx.EVT_TEXT, self._process_event)
        self.Bind(wx.EVT_SET_FOCUS, self._process_event)
        sizer.Add(ident, pos=(3, 1), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=2)

        id_st2 = sppasStaticText(panel, label="between 2 and 12 ASCII-only characters")
        sizer.Add(id_st2, pos=(4, 1), flag=wx.EXPAND | wx.LEFT, border=2)

        line = sppasStaticLine(panel, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, 4))
        line.SetSize(wx.Size(-1, 4))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        sizer.Add(line, pos=(5, 0), span=(1, 3), flag=wx.EXPAND, border=2)

        st2 = sppasStaticText(panel, label="Optional: ")
        sizer.Add(st2, pos=(6, 0), span=(1, 2), flag=wx.ALL,  border=2)

        value_st = sppasStaticText(panel, label="Value: ")
        sizer.Add(value_st, pos=(7, 0), flag=wx.LEFT, border=12)
        value = sppasTextCtrl(parent=panel, value="", name="text_value")
        sizer.Add(value, pos=(7, 1), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=2)
        choice = wx.Choice(panel, choices=sppasAttribute.VALUE_TYPES, name='choice_type')
        choice.SetSelection(0)
        sizer.Add(choice, pos=(7, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=2)

        descr_st = sppasStaticText(panel, label="Description: ")
        sizer.Add(descr_st, pos=(8, 0), flag=wx.LEFT, border=12)
        descr = sppasTextCtrl(parent=panel, value="", name="text_descr")
        sizer.Add(descr, pos=(8, 1), span=(2, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=2)

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(8, proportion=0)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        self.SetContent(panel)
        self.Bind(wx.EVT_RADIOBUTTON, self._process_event)

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
        event_name = event_obj.GetName()
        if event_id == wx.ID_CANCEL:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()

        elif event_id == wx.ID_OK:
            text = self.FindWindow("text_id")
            valid = text.GetValidator().Validate()
            if valid is True:
                # Close the dialog and return wx.ID_OK
                event.Skip()

        elif event_name == "radio_add":
            #self.FindWindow("radio_add").SetValue(True)
            self.FindWindow("radio_del").SetValue(False)

        elif event_name == "radio_del":
            self.FindWindow("radio_add").SetValue(False)
            #self.FindWindow("radio_del").SetValue(True)

        elif event_name == "text_id":
            text = self.FindWindow("text_id")
            text.GetValidator().Validate()

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
        fr3.append(sppasAttribute("year", "2003", "int", "Year of recording"))
        fr3.add("place", "Aix-en-Provence")
        nb = self.FindWindow('refsview').AddRefs([fr1, fr2, fr3, fr3])
        if nb > 0:
            logging.debug('Test added {:d} references (3 expected)'.format(nb))
