import wx
"""

Add an action panel to... perform actions.

"""

# ---------------------------------------------------------------------------
# Some variables
# ---------------------------------------------------------------------------

btn_background_color = wx.Colour(65, 65, 60, alpha=wx.ALPHA_OPAQUE)
background_color = wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE)
foreground_color = wx.Colour(250, 250, 250, alpha=wx.ALPHA_OPAQUE)

# ---------------------------------------------------------------------------


class myFrame(wx.Frame):
    """Create my own frame. Inherited from the wx.Frame.

    """
    def __init__(self):

        wx.Frame.__init__(self,
                          parent=None,
                          title='Title...')
        self.SetBackgroundColour(background_color)
        self.SetMinSize((300, 200))
        self.SetSize((640, 480))

# ---------------------------------------------------------------------------


class myActionPanel(wx.Panel):
    """Create my own panel with 3 action buttons: exit, open, save.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(btn_background_color)
        self.SetMinSize((-1, 32))
        self.SetSize((-1, 32))

        exitBtn = wx.Button(self, wx.ID_EXIT, "Exit", style=wx.NO_BORDER, name="exit")
        exitBtn.SetForegroundColour(foreground_color)
        exitBtn.SetBackgroundColour(btn_background_color)

        openBtn = wx.Button(self, wx.ID_OPEN, "Open", style=wx.NO_BORDER, name="open")
        openBtn.SetForegroundColour(foreground_color)
        openBtn.SetBackgroundColour(btn_background_color)

        saveBtn = wx.Button(self, wx.ID_SAVE, "Save", style=wx.NO_BORDER, name="save")
        saveBtn.SetForegroundColour(foreground_color)
        saveBtn.SetBackgroundColour(btn_background_color)

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


class myApp(wx.App):
    """
    Create my own Application. Inherited from the wx.App.

    """
    def __init__(self, *args, **kw):

        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        # create the frame
        frm = myFrame()
        self.SetTopWindow(frm)

        # create a sizer to add and organize objects
        topSizer = wx.BoxSizer(wx.VERTICAL)

        # add some text in it and customize font
        st = wx.StaticText(frm, wx.ID_ANY, label="Hello World!", pos=(25, 25))
        st.SetForegroundColour(foreground_color)
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        topSizer.Add(st, 3, wx.ALL | wx.EXPAND, 5)

        # separate text and button with a line
        line = wx.StaticLine(frm, style=wx.LI_HORIZONTAL)
        topSizer.Add(line, 0, wx.ALL | wx.EXPAND, 0)

        # add some button in it and customize colors
        btns = myActionPanel(frm)
        topSizer.Add(btns, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

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
        """Process any kind of event."""

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
            event.Skip()

    # -----------------------------------------------------------------------

    def exit(self):
        """Close the frame, terminating the application."""

        print("Bye bye.")
        self.GetTopWindow().Close(True)

    # -----------------------------------------------------------------------

    def OnExit(self):
        """Optional. Override the already existing method."""

        # do whatever you want here (save session, ...)
        print("OnExit method invoked")

        # then it will exit. Nothing special to do. Return the exit status.
        return 0

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    app = myApp()
    app.MainLoop()
