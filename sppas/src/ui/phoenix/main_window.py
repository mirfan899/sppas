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
from .panels import sppasWelcomePanel
from .panels import sppasPanel
from .dialogs import sppasDialog
from .dialogs import YesNoQuestion
from .dialogs import About
from .dialogs import Settings

# ---------------------------------------------------------------------------


class sppasMainWindow(sppasDialog):
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

        # Fix this frame properties
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
        sppasDialog._init_infos(self)

        # Fix other frame properties
        self.SetMinSize(wx.Size(640, 480))
        self.SetSize(wx.GetApp().settings.frame_size)
        self.SetName('{:s}'.format(sg.__name__))

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the frame.

        Content is made of a menu, an area for panels and action buttons.

        """
        # add a customized menu (instead of an header+toolbar)
        menus = sppasMenuPanel(self)
        self.SetHeader(menus)

        # add a panel with a welcome message
        msg_panel = sppasWelcomePanel(self)
        self.SetContent(msg_panel)

        # add some action buttons
        actions = sppasActionsPanel(self)
        self.SetActions(actions)

        # organize the content and lays out.
        self.LayoutComponents()

    # -----------------------------------------------------------------------
    # Events management
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

        # Capture keys
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

        elif event_name == "about":
            About(self)

        elif event_name == "settings":
            self.on_settings()

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
    # Callbaks to events
    # -----------------------------------------------------------------------

    def on_exit(self, event):
        """Makes sure the user was intending to exit the application.

        :param event: (wx.Event) Un-used.

        """
        response = YesNoQuestion("Confirm exit of {:s}..."
                                 "".format(sg.__name__))
        if response == wx.ID_YES:
            self.exit()

    # -----------------------------------------------------------------------

    def on_settings(self):
        """Open settings dialog and apply changes."""
        response = Settings(self)
        if response == wx.ID_CANCEL:
            return

        self.UpdateUI()
        self.log_window.UpdateUI()

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def exit(self):
        """Destroy the frame, terminating the application."""
        # Stop redirecting logging to this application
        self.log_window.redirect_logging(False)
        # Terminate all frames
        self.DestroyChildren()
        self.Destroy()

# ---------------------------------------------------------------------------


class sppasMenuPanel(sppasPanel):
    """Create my own menu panel with several action buttons.

    It aims to replace the old-style menus.

    """
    def __init__(self, parent):
        super(sppasMenuPanel, self).__init__(
            parent=parent,
            name="header")

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetMinSize(wx.Size(-1, settings.title_height))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(parent=self, label="{:s}".format(sg.__longname__))
        sizer.Add(st, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)

        self.SetSizer(sizer)

# ---------------------------------------------------------------------------


class sppasActionsPanel(sppasPanel):
    """Create my own panel with some action buttons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent):

        super(sppasActionsPanel, self).__init__(
            parent=parent,
            name="actions")

        settings = wx.GetApp().settings

        # Create the action panel and sizer
        self.SetMinSize(wx.Size(-1, settings.action_height))
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        exit_btn = sppasBitmapTextButton(self, "Exit", name="exit")
        about_btn = sppasBitmapTextButton(self, "About", name="about")
        settings_btn = sppasBitmapTextButton(self, "Settings", name="settings")
        log_btn = sppasBitmapTextButton(self, "View logs", name="view_log")

        vertical_line_1 = wx.StaticLine(self, style=wx.LI_VERTICAL)
        vertical_line_2 = wx.StaticLine(self, style=wx.LI_VERTICAL)
        vertical_line_3 = wx.StaticLine(self, style=wx.LI_VERTICAL)

        sizer.Add(log_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(vertical_line_1, 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(settings_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(vertical_line_2, 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(about_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(vertical_line_3, 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(exit_btn, 4, wx.ALL | wx.EXPAND, 0)

        self.SetSizer(sizer)
