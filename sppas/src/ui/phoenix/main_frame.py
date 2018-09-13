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

from sppas.src.config import sg

from .main_log import sppasLogFrame
from .controls.buttons import sppasBitmapTextButton

# ---------------------------------------------------------------------------


class sppasFrame(wx.Frame):
    """Create my own frame. Inherited from the wx.Frame."""

    def __init__(self):
        super(sppasFrame, self).__init__(
            parent=None,
            title=wx.GetApp().GetAppDisplayName(),
            style=wx.DEFAULT_FRAME_STYLE | wx.CLOSE_BOX)
        self.SetMinSize((300, 200))
        self.SetSize(wx.Size(640, 480))  # wx.GetApp().settings.frame_size

        # Create the log frame of the application and show it.
        self.log_window = sppasLogFrame(self,
                                        wx.GetApp().cfg.log_level)

        # create a sizer to add and organize objects
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        # add a customized menu (instead of a traditional menu+toolbar)
        menus = sppasMenuPanel(self)
        top_sizer.Add(menus, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # separate menu and the rest with a line
        line_top = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        top_sizer.Add(line_top, 0, wx.ALL | wx.EXPAND, 0)

        # add a panel for the message
        msg_panel = sppasMessagePanel(self)
        top_sizer.Add(msg_panel, 3, wx.ALL | wx.EXPAND, 0)

        # separate top and the rest with a line
        line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        top_sizer.Add(line, 0, wx.ALL | wx.EXPAND, 0)

        # add some action buttons
        actions = sppasActionPanel(self)
        top_sizer.Add(actions, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        self.setup_events()

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
        self.CenterOnScreen()
        self.Show(True)

    # -----------------------------------------------------------------------
    # Events
    # -----------------------------------------------------------------------

    def setup_events(self):
        """Associate a handler function with the events.

        That means that when an event occurs then the process handler function
        will be called.

        """
        # Bind close event from the close dialog 'x' on the frame
        self.Bind(wx.EVT_CLOSE, self.on_exit)

        # Bind all events from our buttons (including 'exit')
        self.Bind(wx.EVT_BUTTON, self.process_event)

    # -----------------------------------------------------------------------

    def process_event(self, event):
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

    def exit(self):
        """Close the frame, terminating the application."""
        # Stop redirecting logging to this application
        self.log_window.redirect_logging(False)
        # Terminate all frames
        self.DestroyChildren()
        self.Destroy()

# ---------------------------------------------------------------------------


class sppasTitleText(wx.StaticText):
    """Create a title."""
    def __init__(self, parent, label):
        super(sppasTitleText, self).__init__(
            parent,
            label=label,
            style=wx.ALIGN_CENTER)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetFont(settings.title_text_font)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetForegroundColour(settings.title_fg_color)

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
        st = sppasTitleText(self, "Installation error...")
        menu_sizer.Add(st, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)

        self.SetSizer(menu_sizer)
        self.SetAutoLayout(True)
        self.Show(True)

# ---------------------------------------------------------------------------


class sppasMessagePanel(wx.Panel):
    """Create my own panel to work with files.

    """
    def __init__(self, parent):
        super(sppasMessagePanel, self).__init__(parent)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetBackgroundColour(settings.bg_color)

        message = \
            "Welcome to {:s}!\n\n"\
            "{:s} requires wxpython version 3 but version 4 is installed.\n"\
            "The Graphical User Interface can't work. See the installation "\
            "web page for details: {:s}." \
            "".format(sg.__longname__, sg.__name__, sg.__url__)
        text_style = wx.TAB_TRAVERSAL|\
                     wx.TE_MULTILINE|\
                     wx.TE_READONLY|\
                     wx.TE_BESTWRAP|\
                     wx.TE_AUTO_URL|\
                     wx.NO_BORDER
        txt = wx.TextCtrl(self, wx.ID_ANY,
                          value=message,
                          style=text_style)
        font = settings.text_font
        txt.SetFont(font)
        txt.SetForegroundColour(settings.fg_color)
        txt.SetBackgroundColour(settings.bg_color)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(txt, 1, wx.ALL|wx.EXPAND, border=10)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Show(True)

# ---------------------------------------------------------------------------


class sppasActionPanel(wx.Panel):
    """Create my own panel with some action buttons.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)

        settings = wx.GetApp().settings
        self.SetMinSize((-1, settings.action_height))
        self.SetBackgroundColour(settings.bg_color)

        exit_btn = sppasBitmapTextButton(self, "Exit", name="exit")
        log_btn = sppasBitmapTextButton(self, "View logs", name="view_log")

        action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_sizer.Add(exit_btn, 4, wx.ALL | wx.EXPAND, 1)
        action_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(log_btn, 1, wx.ALL | wx.EXPAND, 1)
        self.SetSizer(action_sizer)
