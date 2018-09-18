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

    ui.phoenix.main_frame.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx
import logging

from sppas.src.config import sg

from .main_log import sppasLogWindow
from .controls.buttons import sppasBitmapTextButton
from .controls.texts import sppasTitleText
from .panels import sppasWelcomePanel
from .tools import sppasSwissKnife
from .dialogs import sppasDialog

# ---------------------------------------------------------------------------


class sppasMainWindow(wx.Dialog):
    """Create the main frame of SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    This class:
        - does not inherit of wx.TopLevelWindow because we need EVT_CLOSE
        - does not inherit of wx.Frame because we don't need neither a
        status bar, nor a toolbar, nor a menu.

    """

    def __init__(self):
        super(sppasMainWindow, self).__init__(
            parent=None,
            title=wx.GetApp().GetAppDisplayName(),
            style=wx.DEFAULT_FRAME_STYLE | wx.DIALOG_NO_PARENT)

        # Members
        self._init_infos()

        # Create the log window of the application and show it.
        self.log_window = sppasLogWindow(self, wx.GetApp().cfg.log_level)

        # Fix this frame content
        self._create_content()
        self._setup_events()

        self.Enable()
        self.SetFocus()
        self.CenterOnScreen()
        self.Show(True)

    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # ------------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
        # Fix frame properties
        self.SetMinSize(wx.Size(640, 480))
        self.SetSize(wx.GetApp().settings.frame_size)
        self.SetName('{:s}'.format(sg.__name__))

        # icon
        _icon = wx.Icon()
        _icon.CopyFromBitmap(sppasSwissKnife.get_bmp_icon("sppas"))
        self.SetIcon(_icon)

        # colors & font
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the frame.

        Content is made of a menu, an area for panels and action buttons.

        """
        # create a sizer to add and organize objects
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        # add a customized menu (instead of a traditional menu+toolbar)
        menus = sppasMenuPanel(self)
        top_sizer.Add(menus, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # separate menu and the rest with a line
        line_top = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        top_sizer.Add(line_top, 0, wx.ALL | wx.EXPAND, 0)

        # add a panel with a welcome message
        msg_panel = sppasWelcomePanel(self)
        top_sizer.Add(msg_panel, 3, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        # separate with a line
        line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        top_sizer.Add(line, 0, wx.ALL | wx.EXPAND, 0)

        # add some action buttons
        actions = sppasActionsPanel(self)
        top_sizer.Add(actions, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # Since Layout doesn't happen until there is a size event, you will
        # sometimes have to force the issue by calling Layout yourself. For
        # example, if a frame is given its size when it is created, and then
        # you add child windows to it, and then a sizer, and finally Show it,
        # then it may not receive another size event (depending on platform)
        # in order to do the initial layout. Simply calling self.Layout from
        # the end of the frame's __init__ method will usually resolve this.
        self.SetAutoLayout(True)
        self.SetSizer(top_sizer)
        self.Layout()

    # -----------------------------------------------------------------------
    # Events
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind close event from the close dialog 'x' on the frame
        self.Bind(wx.EVT_CLOSE, self.on_exit)

        # Bind all events from our buttons (including 'exit')
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

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

        if event_name == "exit":
            self.exit()
        elif event_name == "view_log":
            self.log_window.focus()
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()

        if key_code == wx.WXK_F4 and event.AltDown():
            self.on_exit(event)
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def on_exit(self, event):
        """Makes sure the user was intending to exit the application."""
        dialog = wx.MessageDialog(
            self,
            message="Are you sure you want to exit {:s}?".format(sg.__name__),
            caption="Confirm exit...",
            style=wx.YES_NO,
            pos=wx.DefaultPosition)
        response = dialog.ShowModal()
        if response == wx.ID_YES:
            self.exit()

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def exit(self):
        """Close the frame, terminating the application."""
        # Stop redirecting logging to this application
        self.log_window.redirect_logging(False)
        # Terminate all frames
        self.DestroyChildren()
        self.Destroy()

    # ---------------------------------------------------------------------------
    # Override existing but un-useful methods
    # ---------------------------------------------------------------------------

    def CreateButtonSizer(self, flags):
        """Override to disable."""
        pass

    def CreateSeparatedButtonSizer(self, flags):
        """Override to disable."""
        pass

    def CreateSeparatedSizer(self, sizer):
        """Override to disable."""
        pass

    def CreateStdDialogButtonSizer(self, flags):
        """Override to disable."""
        pass

    def CreateTextSizer(self, message):
        """Override to disable."""
        pass

# ---------------------------------------------------------------------------


class sppasMenuPanel(wx.Panel):
    """Create my own menu panel with several action buttons.

    It aims to replace the old-style menus.

    """
    def __init__(self, parent):
        super(sppasMenuPanel, self).__init__(parent)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetBackgroundColour(settings.title_bg_color)
        self.SetMinSize((-1, settings.title_height))

        menu_sizer = wx.BoxSizer(wx.HORIZONTAL)
        st = sppasTitleText(self, "{:s}".format(sg.__longname__))
        menu_sizer.Add(st, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)

        self.SetSizer(menu_sizer)
        self.SetAutoLayout(True)

# ---------------------------------------------------------------------------


class sppasActionsPanel(wx.Panel):
    """Create my own panel with some action buttons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)

        settings = wx.GetApp().settings
        self.SetMinSize((-1, settings.action_height))
        self.SetBackgroundColour(settings.bg_color)

        exit_btn = sppasBitmapTextButton(self, "Exit", name="exit")
        log_btn = sppasBitmapTextButton(self, "View logs", name="view_log")

        action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_sizer.Add(log_btn, 1, wx.ALL | wx.EXPAND, 2)
        action_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(exit_btn, 4, wx.ALL | wx.EXPAND, 2)

        self.SetSizer(action_sizer)
