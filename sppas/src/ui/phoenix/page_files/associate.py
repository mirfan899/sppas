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
from sppas.src.files import sppasFileDataFilters

from ..dialogs import Information
from ..windows import sppasStaticText, sppasTextCtrl
from ..windows import sppasPanel
from ..windows import sppasDialog
from ..windows.button import BitmapTextButton, CheckButton

from .filesevent import DataChangedEvent
from .filesutils import IdentifierTextValidator
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

    def check_filter(self):
        """Check filenames matching the user-defined filters."""
        dlg = sppasFilesFilterDialog(self)
        response = dlg.ShowModal()
        if response != wx.ID_CANCEL:
            data_filters = dlg.get_filters()
            if len(data_filters) > 0:
                wx.BeginBusyCursor()
                data_set = self.__process_filter(data_filters, dlg.match_all)
                if len(data_set) == 0:
                    Information('None of the files is matching the given filters.')
                else:
                    # Uncheck all files (except the locked ones!) and all references
                    self.__data.set_object_state(States().UNUSED)

                    roots = list()
                    # Check files of the filtered data_set
                    for fn in data_set:
                        self.__data.set_object_state(States().CHECKED, fn)
                        root = self.__data.get_parent(fn)
                        if root not in roots:
                            roots.append(root)
                    Information('{:d} files were matching the given filters '
                                'and checked.'
                                ''.format(len(data_set)))

                    # Check references matching the checked files
                    for fr in roots:
                        for ref in fr.get_references():
                            ref.set_state(States().CHECKED)

                    self.notify()
                wx.EndBusyCursor()
        dlg.Destroy()

    # ------------------------------------------------------------------------

    def __process_filter(self, data_filters, match_all=True):
        """Perform the filter process.
    
        :param data_filters: list of tuples with (filter name, function name, values)
        
        """
        logging.info("Check files matching the following filter=sppasFileDataFilters():")
        f = sppasFileDataFilters(self.__data)
        data_sets = list()

        for d in data_filters:
            if len(d) != 3:
                logging.error("Bad data format: {:s}".format(str(d)))
                continue

            # the method to be uses by Compare
            method = d[0]
            # the function to be applied
            fct = d[1]
            # all the possible values are separated by commas
            values = d[2].split(",")
            if fct == "att":
                v = values[0]
                values = v.split(":")
                data_set = getattr(f, method)(**{fct: values[0]})
                logging.info(" >>> filter.{:s}({:s}={!s:s})".format(method, fct, values))

            # a little bit of doc:
            #   - getattr() returns the value of the named attributed of object:
            #     it returns f.tag if called like getattr(f, "tag")
            #   - func(**{'x': '3'}) is equivalent to func(x='3')
            if fct != "att":

                data_set = getattr(f, method)(**{fct: values[0]})
                logging.info(" >>> filter.{:s}({:s}={!s:s})".format(method, fct, values[0]))

                # Apply "or" between each data_set matching a value
                for i in range(1, len(values)):
                    v = values[i].strip()
                    data_set = data_set | getattr(f, method)(**{fct: v})
                    logging.info(" >>>    | filter.{:s}({:s}={!s:s})".format(method, fct, v))

            data_sets.append(data_set)
        
        # no filename is matching
        if len(data_sets) == 0:
            return list()
        
        # Merge results (apply '&' or '|' on the resulting data sets)
        data_set = data_sets[0]
        if match_all is True:
            for i in range(1, len(data_sets)):
                data_set = data_set & data_sets[i]
                if len(data_set) == 0:
                    # no need to go further...
                    return list()
        else:
            for i in range(1, len(data_sets)):
                data_set = data_set | data_sets[i]

        return data_set

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
        """Create a files filter dialog.

        :param parent: (wx.Window)

        """
        super(sppasFilesFilterDialog, self).__init__(
            parent=parent,
            title='{:s} Files selection'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self.match_all = True
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

    def get_filters(self):
        """Return a list of (filter, function, values)."""
        filters = list()
        for i in range(self.listctrl.GetItemCount()):
            filter_name = self.listctrl.GetValue(i, 0)
            fct_name = self.listctrl.GetValue(i, 1)
            values = self.listctrl.GetValue(i, 2)
            filters.append((filter_name, fct_name, values))
        return filters

    # -----------------------------------------------------------------------
    # Methods to construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")
        tb = self.__create_toolbar(panel)
        self.listctrl = wx.dataview.DataViewListCtrl(panel, wx.ID_ANY)
        self.listctrl.AppendTextColumn("filter", width=80)
        self.listctrl.AppendTextColumn("function", width=90)
        self.listctrl.AppendTextColumn("value", width=120)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(self.listctrl, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        panel.SetSizer(sizer)

        self.SetMinSize((320, 200))
        panel.SetAutoLayout(True)
        self.SetContent(panel)

    # -----------------------------------------------------------------------

    def __create_toolbar(self, parent):
        """Create the toolbar."""
        tb = BitmapTextToolbar(parent)
        tb.set_focus_color(wx.Colour(196, 196, 96, 128))
        tb.AddButton("filter_path", "Path")
        tb.AddButton("filter_file", "Name")
        tb.AddButton("filter_ext", "Type")
        tb.AddButton("filter_ref", "Ref.")
        tb.AddButton("filter_att", "Value")
        tb.AddSpacer()
        tb.AddButton("remove", "Remove")
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
        apply_and_btn.SetFocus()

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

        if event_name == "filter_path":
            dlg = sppasStringFilterDialog(self)
            response = dlg.ShowModal()
            if response == wx.ID_OK:
                # Name of the method in sppasFileDataFilters,
                # Name of the function and its value
                f = dlg.get_data()
                self.listctrl.AppendItem(["path", f[0], f[1]])
            dlg.Destroy()

        elif event_name == "filter_file":
            dlg = sppasStringFilterDialog(self)
            response = dlg.ShowModal()
            if response == wx.ID_OK:
                f = dlg.get_data()
                self.listctrl.AppendItem(["name", f[0], f[1]])
            dlg.Destroy()

        elif event_name == "filter_ext":
            dlg = sppasStringFilterDialog(self)
            response = dlg.ShowModal()
            if response == wx.ID_OK:
                f = dlg.get_data()
                self.listctrl.AppendItem(["extension", f[0], f[1]])
            dlg.Destroy()

        elif event_name == "filter_ref":
            dlg = sppasStringFilterDialog(self)
            response = dlg.ShowModal()
            if response == wx.ID_OK:
                f = dlg.get_data()
                self.listctrl.AppendItem(["ref", f[0], f[1]])
            dlg.Destroy()

        elif event_name == "filter_att":
            dlg = sppasAttributeFilterDialog(self)
            response = dlg.ShowModal()
            if response == wx.ID_OK:
                f = dlg.get_data()
                self.listctrl.AppendItem(["att", f[0], f[1]])
            dlg.Destroy()

        elif event_name == "cancel":
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()

        elif event_name == "apply":
            self.match_all = False
            self.EndModal(wx.ID_APPLY)

        elif event_name == "ok":
            self.match_all = True
            self.EndModal(wx.ID_OK)

        else:
            event.Skip()

# ---------------------------------------------------------------------------


class sppasStringFilterDialog(sppasDialog):
    """Dialog to get a filter on a string.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    choices = (
               ("exact", "exact"),
               ("not exact", "exact"),
               ("contains", "contains"),
               ("not contains", "contains"),
               ("starts with", "startswith"),
               ("not starts with", "startswith"),
               ("ends with", "endswith"),
               ("not ends with", "endswith"),
               ("match (regexp)", "regexp"),
               ("not match", "regexp")
              )

    DEFAULT_PATTERN = "x1, x2..."

    def __init__(self, parent):
        """Create a string filter dialog.

        :param parent: (wx.Window)

        """
        super(sppasStringFilterDialog, self).__init__(
            parent=parent,
            title='{:s} filter'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        self.SetMinSize(wx.Size(320, 220))
        self.LayoutComponents()
        self.CenterOnParent()

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        Returns: (tuple) with:

               - function (str): one of the methods in Compare
               - values (list): patterns to find separated by commas

        """
        idx = self.radiobox.GetSelection()
        given_fct = self.choices[idx][1]

        # Fill the resulting dict
        prepend_fct = ""

        if given_fct != "regexp":
            # prepend "not_" if reverse
            if (idx % 2) != 0:
                prepend_fct += "not_"
            # prepend "i" if case-insensitive
            if self.checkbox.GetValue() is False:
                prepend_fct += "i"

        return prepend_fct+given_fct, self.text.GetValue()

    # -----------------------------------------------------------------------
    # Methods to construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")

        label = sppasStaticText(panel, label="Search for pattern(s): ")
        self.text = sppasTextCtrl(panel, value=self.DEFAULT_PATTERN)
        self.text.Bind(wx.EVT_TEXT, self.OnTextChanged)
        self.text.Bind(wx.EVT_SET_FOCUS, self.OnTextClick)

        choices = [row[0] for row in self.choices]
        self.radiobox = wx.RadioBox(panel,
                                    label="Functions: ",
                                    choices=choices,
                                    majorDimension=2)
        self.radiobox.SetSelection(2)
        self.checkbox = CheckButton(panel, label="Case sensitive")
        self.checkbox.SetValue(False)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.text, 0, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.radiobox, 1, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.checkbox, 0, flag=wx.EXPAND | wx.ALL, border=4)

        panel.SetSizer(sizer)
        panel.SetMinSize((240, 160))
        panel.SetAutoLayout(True)
        self.SetContent(panel)

    # ------------------------------------------------------------------------

    def OnTextClick(self, event):
        self.text.SetForegroundColour(wx.BLACK)
        if self.text.GetValue() == self.DEFAULT_PATTERN:
            self.OnTextErase(event)
        event.Skip()

    def OnTextChanged(self, event):
        self.text.Refresh()

    def OnTextErase(self, event):
        self.text.SetValue('')
        self.text.SetFocus()
        self.text.Refresh()

# ---------------------------------------------------------------------------


class sppasAttributeFilterDialog(sppasDialog):
    """Dialog to get a filter on an attribute.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    choices = (
               ("exact", "exact"),
               ("not exact", "exact"),
               ("contains", "contains"),
               ("not contains", "contains"),
               ("starts with", "startswith"),
               ("not starts with", "startswith"),
               ("ends with", "endswith"),
               ("not ends with", "endswith"),
               ("match (regexp)", "regexp"),
               ("not match", "regexp"),
               ("equal", "equal"),
               ("greater than", "gt"),
               ("greater or equal", "ge"),
               ("lower than", "lt"),
               ("lower or equal", "le")
              )

    def __init__(self, parent):
        """Create an attribute filter dialog.

        :param parent: (wx.Window)

        """
        super(sppasAttributeFilterDialog, self).__init__(
            parent=parent,
            title='{:s} filter'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE)

        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        self.SetMinSize(wx.Size(320, 220))
        self.LayoutComponents()
        self.CenterOnParent()

    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data defined by the user.

        Returns: (tuple) with:

               - function (str): one of the methods in Compare
               - values (list): attribute to find as identifier, value

        """
        idx = self.radiobox.GetSelection()
        given_fct = self.choices[idx][1]

        # Fill the resulting dict
        prepend_fct = ""

        if given_fct in sppasAttributeFilterDialog.choices[:8]:
            # prepend "not_" if reverse
            if (idx % 2) != 0:
                prepend_fct += "not_"
            # prepend "i" if case-insensitive
            if self.checkbox.GetValue() is False:
                prepend_fct += "i"

        return prepend_fct + given_fct, \
               self.text_ident.GetValue() + ":" + self.text_value.GetValue()

    # -----------------------------------------------------------------------
    # Methods to construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")

        label = sppasStaticText(panel, label="Identifier: ")
        self.text_ident = sppasTextCtrl(panel, value="",
                                  validator=IdentifierTextValidator())
        # self.text_ident.Bind(wx.EVT_TEXT, self.OnTextChanged)
        # self.text_ident.Bind(wx.EVT_SET_FOCUS, self.OnTextClick)

        choices = [row[0] for row in sppasAttributeFilterDialog.choices]
        self.radiobox = wx.RadioBox(panel,
                                    label="Functions: ",
                                    choices=choices,
                                    majorDimension=2)
        self.radiobox.SetSelection(2)
        self.radiobox.Bind(wx.EVT_RADIOBOX, self._on_radiobox_checked)
        self.checkbox = CheckButton(panel, label="Case sensitive")
        self.checkbox.SetValue(False)

        self.text_value = sppasTextCtrl(panel, value="")

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 0, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.text_ident, 0, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.radiobox, 1, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.text_value, 0, flag=wx.EXPAND | wx.ALL, border=4)
        sizer.Add(self.checkbox, 0, flag=wx.EXPAND | wx.ALL, border=4)

        panel.SetSizer(sizer)
        panel.SetMinSize((240, 160))
        panel.SetAutoLayout(True)
        self.SetContent(panel)

    def _on_radiobox_checked(self, event):
        value = self.radiobox.GetStringSelection()
        if value in sppasAttributeFilterDialog.choices[10:]:
            self.checkbox.SetValue(False)
            self.checkbox.Enable(False)
        else:
            self.checkbox.Enable(True)
