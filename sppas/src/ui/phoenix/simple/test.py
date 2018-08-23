# -*- coding: UTF-8 -*-
import wx
import os
from datetime import datetime

log_filename = "C:\\Users\\brigi\\Desktop\\sppas_gui.log"

# ---------------------------------------------------------------------------


class sppasMainFrame(wx.Frame):
    """
    Border styles :
        wx.BORDER_DEFAULT: The window class will decide the kind of border to show, if any.
        wx.BORDER_SIMPLE: Displays a thin border around the window. wx.SIMPLE_BORDER is the old name for this style.
        wx.BORDER_SUNKEN: Displays a sunken border. wx.SUNKEN_BORDER is the old name for this style.
        wx.BORDER_RAISED: Displays a raised border. wx.RAISED_BORDER is the old name for this style.
        wx.BORDER_STATIC: Displays a border suitable for a static control. wx.STATIC_BORDER is the old name for this style. Windows only.
        wx.BORDER_THEME: Displays a native border suitable for a control, on the current platform.
        wx.BORDER_NONE: Displays no border, overriding the default border style for the window. wx.NO_BORDER is the old name for this style.
        wx.BORDER_DOUBLE: This style is obsolete and should not be used.

    Other styles:
        wx.WANTS_CHARS: Use this to indicate that the window wants to get all char/key events for all keys - even for keys like TAB or ENTER
        wx.VSCROLL: Use this style to enable a vertical scrollbar.
        wx.HSCROLL: Use this style to enable a horizontal scrollbar.
        wx.CLIP_CHILDREN: Use this style to eliminate flicker caused by the background being repainted, then children being painted over them. Windows only.

    Event macros for events emitted by this class:

        EVT_ACTIVATE: Process a wxEVT_ACTIVATE event.
        EVT_CHILD_FOCUS: Process a wxEVT_CHILD_FOCUS event.
        EVT_CONTEXT_MENU: A right click (or other context menu command depending on platform) has been detected. See wx.ContextMenuEvent.
        EVT_HELP: Process a wxEVT_HELP event.
        EVT_HELP_RANGE: Process a wxEVT_HELP event for a range of ids.
        EVT_DROP_FILES: Process a wxEVT_DROP_FILES event.
        EVT_ERASE_BACKGROUND: Process a wxEVT_ERASE_BACKGROUND event.
        EVT_SET_FOCUS: Process a wxEVT_SET_FOCUS event.
        EVT_KILL_FOCUS: Process a wxEVT_KILL_FOCUS event.
        EVT_IDLE: Process a wxEVT_IDLE event.
        EVT_JOY_*: Processes joystick events.
        EVT_KEY_DOWN: Process a wxEVT_KEY_DOWN event (any key has been pressed).
        EVT_KEY_UP: Process a wxEVT_KEY_UP event (any key has been released).
        EVT_CHAR: Process a wxEVT_CHAR event.
        EVT_CHAR_HOOK: Process a wxEVT_CHAR_HOOK event.
        EVT_MOUSE_CAPTURE_LOST: Process a wxEVT_MOUSE_CAPTURE_LOST event.
        EVT_MOUSE_CAPTURE_CHANGED: Process a wxEVT_MOUSE_CAPTURE_CHANGED event.
        EVT_MOUSE_*: See wx.MouseEvent.
        EVT_PAINT: Process a wxEVT_PAINT event.
        EVT_POWER_*: The system power state changed.
        EVT_SCROLLWIN_*: Process scroll events.
        EVT_SET_CURSOR: Process a wxEVT_SET_CURSOR event.
        EVT_SIZE: Process a wxEVT_SIZE event.
        EVT_SYS_COLOUR_CHANGED: Process a wxEVT_SYS_COLOUR_CHANGED event.

    """
    def __init__(self):

        style = wx.BORDER_THEME | wx.WANTS_CHARS | wx.CLIP_CHILDREN

        wx.Frame.__init__(self,
                          parent=None,
                          title='SPPAS...')
        self.SetMinSize((300, 200))
        self.SetSize((640, 480))

        # parent, id = ID_ANY, title ='', pos = DefaultPosition, size = DefaultSize,
        # style = DEFAULT_FRAME_STYLE, name = FrameNameStr

# ---------------------------------------------------------------------------


class sppasFilePanel(wx.Panel):
    def __init__(self, *args, **kw):
        wx.Panel.__init__(self, *args, **kw)
        self.SetBackgroundColour(wx.Colour(245, 245, 245, alpha=wx.ALPHA_OPAQUE))
        self.SetMinSize((-1, 256))

# ---------------------------------------------------------------------------


class sppasMenuPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(10, 20, 30, alpha=wx.ALPHA_OPAQUE))
        self.SetMinSize((-1, 64))
        self.SetSize((-1, 64))
        #  parent, id=ID_ANY, pos=DefaultPosition, size=DefaultSize, style=TAB_TRAVERSAL, name=PanelNameStr

# ---------------------------------------------------------------------------


class sppasActionPanel(wx.Panel):
    """Create a panel with 3 action buttons: exit, open, save.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(10, 20, 30, alpha=wx.ALPHA_OPAQUE))
        self.SetMinSize((-1, 32))
        self.SetSize((-1, 32))

        exitBtn = wx.Button(self, wx.ID_ANY, "Exit", style=wx.NO_BORDER, name="exit")
        exitBtn.SetForegroundColour(wx.Colour(250, 250, 250))
        exitBtn.SetBackgroundColour(self.GetBackgroundColour())

        openBtn = wx.Button(self, wx.ID_ANY, "Open workspace", style=wx.NO_BORDER, name="open")
        openBtn.SetForegroundColour(wx.Colour(250, 250, 250))
        openBtn.SetBackgroundColour(self.GetBackgroundColour())

        saveBtn = wx.Button(self, wx.ID_ANY, "Save workspace", style=wx.NO_BORDER, name="save")
        saveBtn.SetForegroundColour(wx.Colour(250, 250, 250))
        saveBtn.SetBackgroundColour(self.GetBackgroundColour())

        actionSizer = wx.BoxSizer(wx.HORIZONTAL)
        actionSizer.Add(exitBtn, 1, wx.ALL | wx.EXPAND, 0)
        actionSizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)
        actionSizer.Add(openBtn, 1, wx.ALL | wx.EXPAND, 0)
        actionSizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)
        actionSizer.Add(saveBtn, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(actionSizer)

        self.Bind(wx.EVT_BUTTON, self.OnAction, exitBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, openBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, saveBtn)

    # -----------------------------------------------------------------------

    def OnAction(self, event):
        """A button was clicked.
        Here we just send the event to the parent.

        """
        print("A button was clicked on.")
        wx.PostEvent(self.GetTopLevelParent(), event)


# ---------------------------------------------------------------------------


class sppasApp(wx.App):

    def __init__(self):
        """Create a customized application.

        This app is using the following parameters:

            - redirect (False) Should sys.stdout and sys.stderr be redirected?
            - filename (None) The name of a file to redirect output to.
            - useBestVisual (True) Should the app try to use the best
              available visual provided by the system
            - clearSigInt (True) Should SIGINT be cleared? This allows the app
              to terminate upon a Ctrl-C in the console like other GUI apps will.

        """
        # Fix look and feels of all objects
        self.load_config()

        # ensure the parent's __init__ is called
        wx.App.__init__(self,
                        redirect=True,
                        filename=log_filename,
                        useBestVisual=True,
                        clearSigInt=True)
        print("Starts at {:s}".format(datetime.now().strftime("%y-%m-%d-%H-%M")))

        # create the frame
        frm = sppasMainFrame()
        self.SetTopWindow(frm)

        # create a sizer to add and organize objects
        topSizer = wx.BoxSizer(wx.VERTICAL)

        # In normal use the sizers will treat a window's initial size when it
        # is Add'ed to the sizer as its minimum size, and will use that size
        # to calculate layout. Several window types default to (0,0) initial
        # size so if you don't give them another size that is what the sizer
        # will use for the minimum. If the sizer has no other reason to
        # enlarge the window then you will see nothing of it.
        topSizer.Add(sppasMenuPanel(frm), 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)
        topSizer.Add(sppasFilePanel(frm), 1, wx.ALL | wx.EXPAND, 0)
        topSizer.Add(sppasActionPanel(frm), 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # Often sizer.Fit(frame) is NOT what you want. It will use the minimum
        # size of all the contained windows and sub-sizers and resize the
        # frame so it just barely fits those minimums. More often I've found
        # that I would rather use the default size of a frame (or the user-set
        # size that I've loaded from a config file) and allow the sizer to
        # layout to that size instead.
        # topSizer.Fit(frame)

        # Associate a handler function with the EVT_BUTTON event.
        # That means that when a button is clicked then the process
        # handler function will be called.
        self.Bind(wx.EVT_BUTTON, self.process_event)

        # Since Layout doesn't happen until there is a size event, you will
        # sometimes have to force the issue by calling Layout yourself. For
        # example, if a frame is given its size when it is created, and then
        # you add child windows to it, and then a sizer, and finally Show it,
        # then it may not receive another size event (depending on platform)
        # in order to do the initial layout. Simply calling self.Layout from
        # the end of the frame's __init__ method will usually resolve this.
        frm.SetAutoLayout(True)
        frm.SetSizer(topSizer)
        frm.Layout()
        frm.Show()

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def process_event(self, event):

        event_name = event.GetEventObject().GetName()
        event_id = event.GetEventObject().GetId()
        print("Received event id {:d} of {:s}".format(event_id, event_name))

        if event_name == "exit":
            self.exit()
        elif event_name == "save":
            pass
        elif event_name == "open":
            pass
        else:
            event.skip()

    # -----------------------------------------------------------------------

    def exit(self):
        """Close the frame, terminating the application."""

        print("Bye bye.")
        self.GetTopWindow().Close(True)

    # -----------------------------------------------------------------------

    def OnSize(self, evt):
        """
        Why this callback?

        https://wiki.wxpython.org/UsingSizers

        The actual layout of windows controlled by a sizer (or layout
        constraints for that matter) happens in the default EVT_SIZE handler
        for a window. In other words, when EVT_SIZE happens, if you haven't
        connected your own size handler, and if the window has had a sizer
        assigned, and if auto-layout has been turned on, then the window's
        Layout method is called where it uses the assigned sizer
        or layout constraints to layout sub-windows.

        Not all windows have this default behaviour for the EVT_SIZE handler.
        Off the top of my head, those that do have it are wxFrame (and other
        frame types), wxDialog, wxPanel and wxScrolledWindow. wxSplitterWindow,
        and wxNotebook; and some others do specialized layout of their
        children, but if the children have sizers of their own then it should
        work as expected. Notice that wxWindow is not on the list (for various
        reasons), but if needed you can still allow it (or your own class
        derived directly form wxWindow) to have sizers and do auto layout by
        hooking EVT_SIZE and doing something like this:

        :param evt: (wx.Event)

        """
        if self.GetTopWindow().GetAutoLayout():
            self.GetTopWindow().Layout()

    # -----------------------------------------------------------------------

    def load_config(self):
        """Load the configuration file."""

        self.globals = dict()

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    if os.path.exists(log_filename) is False:
        with open(log_filename, "w") as fp:
            fp.write('Log file for SPPAS.')
            fp.write(' - SPPAS version:')
            fp.write(' - File creation date:')
        fp.close()

    app = sppasApp()
    app.MainLoop()
