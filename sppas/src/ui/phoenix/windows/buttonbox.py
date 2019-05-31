import wx
import logging
from .button import RadioButton, ButtonEvent
from .panel import sppasPanel

# ---------------------------------------------------------------------------


class RadioBox(sppasPanel):

    def __init__(self, parent,
                 id=wx.ID_ANY, label="",
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 choices=[], majorDimension=0,
                 name=wx.RadioBoxNameStr):

        content = sppasRadioBoxPanel(self, wx.ID_ANY,
                             pos, size, choices, majorDimension,
                             name="content")

# ---------------------------------------------------------------------------


class sppasRadioBoxPanel(sppasPanel):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 choices=[],
                 majorDimension=0,
                 style=wx.RA_SPECIFY_COLS,
                 name=wx.RadioBoxNameStr):
        super(sppasRadioBoxPanel, self).__init__(parent, id, pos, size, name=name)

        self.__buttons = list()
        self.__selection = 0
        self._create_content(style, choices, majorDimension)
        self._setup_events()
        self.Layout()

    # ------------------------------------------------------------------------

    def EnableItem(self, n, enable=True):
        """Enable or disable an individual button in the radiobox.

        :param n: (int) – The zero-based button to enable or disable.
        :param enable: (bool) – True to enable, False to disable.
        :return: (bool)

        """
        if n > len(self.__buttons):
            return False
        # do not disable the selected button
        if n == self.__selection and enable is False:
            return False

        self.__buttons[n].Enable(enable)
        return True

    # ------------------------------------------------------------------------

    def FindString(self, string, bCase=False):
        """Find a button matching the given string.

        :param string: (string) – The string to find.
        :param bCase: (bool) – Should the search be case-sensitive?

        :return: (int) the position if found, or -1 if not found.

        """
        found = -1
        for i, c in enumerate(self.__buttons):
            label = c.GetLabel()
            if bCase is False and label.lower() == string.lower():
                found = i
                break
            if bCase is True and label == string:
                found = i
                break
        return found

    # ------------------------------------------------------------------------

    def GetColumnCount(self):
        """Return the number of columns in the radiobox."""
        return self.GetSizer().GetEffectiveColsCount()

    # ------------------------------------------------------------------------

    def GetRowCount(self):
        """Return the number of rows in the radiobox."""
        return self.GetSizer().GetEffectiverowsCount()

    # ------------------------------------------------------------------------

    def GetCount(self):
        """Return the number of items in the control."""
        return len(self.__buttons)

    # ------------------------------------------------------------------------

    def GetItemLabel(self, n):
        """Return the text of the n'th item in the radio box."""
        self.GetString(n)

    # ------------------------------------------------------------------------

    def GetSelection(self):
        """Return the index of the selected item or -1 if no item is selected.
    
        :return: (int) The position of the current selection.
        
        """
        return self.__selection

    # ------------------------------------------------------------------------

    def GetString(self, n):
        """Return the label of the item with the given index.

        :param n: (int) – The zero-based index.
        :return: (str) The label of the item or an empty string if the position
        was invalid.

        """
        if n > len(self.__buttons):
            return ""
        return self.__buttons[n].GetLabel()

    # ------------------------------------------------------------------------

    def IsItemEnabled(self, n):
        """Return True if the item is enabled or False if it was disabled using Enable .

        :param n: (int) – The zero-based button position.
        :return: (bool)

        """
        if n > len(self.__buttons):
            return False
        return self.__buttons[n].IsEnabled(n)

    # ------------------------------------------------------------------------

    def IsItemShown(self, n):
        """Return True if the item is currently shown or False if it was hidden using Show .

        :param n: (int) – The zero-based button position.
        :return: (bool)

        """
        if n > len(self.__buttons):
            return False
        return self.__buttons[n].IsShown()

    # ------------------------------------------------------------------------

    def SetItemLabel(self, n, text):
        """Set the text of the n’th item in the radio box.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def SetSelection(self, n):
        """Set the selection to the given item.

        :param n: (int) –

        """
        if self.__selection == n:
            return
        if n > len(self.__buttons):
            return
        btn = self.__buttons[n]
        if btn.IsEnabled() is True:
            btn.SetValue(True)
            self.__buttons[self.__selection].SetValue(False)
            self.__selection = n

    # ------------------------------------------------------------------------

    def SetString(self, n, string):
        """Set the label for the given item.

        :param n: (int) – The zero-based item index.
        :param string: (string) – The label to set.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def ShowItem(self, item, show=True):
        """Show or hide individual buttons.

        :param item: (int) – The zero-based position of the button to show or hide.
        :param show: (bool) – True to show, False to hide.
        :return: (bool) True if the item has been shown or hidden or False
        if nothing was done because it already was in the requested state.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_RADIOBUTTON event to the listener (if any)."""
        evt = ButtonEvent(wx.EVT_RADIOBUTTON.typeId, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self, style, choices, majorDimension):
        """Create the main content."""
        rows = len(choices)
        cols = 1
        if len(choices) > 1:
            if majorDimension > 0:
                if style == wx.RA_SPECIFY_COLS:
                    cols = majorDimension
                    rows = len(choices) // majorDimension
                elif style == wx.RA_SPECIFY_ROWS:
                    rows = majorDimension
                    cols = len(choices) // majorDimension

        logging.debug('Number of rows: {:d}'.format(rows))
        logging.debug('Number of cols: {:d}'.format(cols))

        grid = wx.GridBagSizer(rows, cols)
        for c in range(cols):
            logging.debug(' - col nb: {:d}'.format(c))
            for r in range(rows):
                logging.debug(' - row nb: {:d}'.format(r))
                btn = RadioButton(self, label=choices[(c*r)+r])
                grid.Add(btn, pos=(r, c), flag=wx.EXPAND)
                self.__buttons.append(btn)
            grid.AddGrowableCol(c)
        self.__buttons[0].SetValue(True)
        self.SetSizer(grid)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # The user pressed a key of its keyboard
        # self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked (LeftDown - LeftUp) an action button
        self.Bind(wx.EVT_BUTTON, self._process_btn_event)

    # ------------------------------------------------------------------------

    def _process_btn_event(self, event):
        """Respond to a button event."""
        evt_btn = event.GetButtonObj()
        for i, btn in enumerate(self.__buttons):
            if btn is evt_btn:
                self.__selection = i
                btn.Enable(True)
            btn.Enable(False)


# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanelRadioBox(wx.Panel):

    def __init__(self, parent):
        super(TestPanelRadioBox, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test RadioBox")

        rb = sppasRadioBoxPanel(
            self,
            pos=(10, 10),
            size=wx.Size(300, 200),
            choices=["bananas", "pears", "tomatoes", "apples", "pineapples"],
            majorDimension=2)
        rb.Bind(wx.EVT_RADIOBOX, self.on_btn_event)

    # -----------------------------------------------------------------------

    def on_btn_event(self, event):
        obj = event.GetEventObject()
        logging.debug('* * * PANEL: RadioBox Event received by {:s} * * *'.format(obj.GetName()))

# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test ButtonBox")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(TestPanelRadioBox(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticLine(self))

        self.SetSizer(sizer)
