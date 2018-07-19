import wx
"""

Add a menu panel.

"""
# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FRAME_STYLE = wx.DEFAULT_FRAME_STYLE | wx.CLOSE_BOX


# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

btn_background_color = wx.Colour(65, 65, 60, alpha=wx.ALPHA_OPAQUE)
background_color = wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE)
foreground_color = wx.Colour(250, 250, 250, alpha=wx.ALPHA_OPAQUE)


# ---------------------------------------------------------------------------


class myFrame(wx.Frame):
    """ Create my own frame. Inherited from the wx.Frame.

    """
    def __init__(self):

        wx.Frame.__init__(self,
                          parent=None,
                          title='Title...',
                          style=FRAME_STYLE)
        self.SetBackgroundColour(background_color)
        self.SetMinSize((300, 200))
        self.SetSize((640, 480))

# ---------------------------------------------------------------------------


class myMenuPanel(wx.Panel):
    """ Create my own menu panel with several action buttons.
    It aims to replace the old-style menus.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(btn_background_color)
        self.SetMinSize((-1, 64))

        menuSizer = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(self, wx.ID_ANY, label="My App!")
        st.SetForegroundColour(foreground_color)
        font = st.GetFont()
        font = font.Bold()
        st.SetFont(font)
        menuSizer.Add(st, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        menuSizer.AddStretchSpacer(prop=1)

        # Will switch to the "Files" main panel
        fileBtn = wx.Button(self, wx.ID_EXIT, "Files", style=wx.NO_BORDER, name="files")
        fileBtn.SetForegroundColour(foreground_color)
        fileBtn.SetBackgroundColour(btn_background_color)
        menuSizer.Add(fileBtn, 1, wx.ALL | wx.EXPAND, 1)

        # Will switch to the "Annotate" main panel
        annotBtn = wx.Button(self, wx.ID_ANY, "Annotate", style=wx.NO_BORDER, name="annot")
        annotBtn.SetForegroundColour(foreground_color)
        annotBtn.SetBackgroundColour(btn_background_color)
        menuSizer.Add(annotBtn, 1, wx.ALL | wx.EXPAND, 1)

        # Will switch to the "Analyze" main panel
        analyseBtn = wx.Button(self, wx.ID_ANY, "Analyze", style=wx.NO_BORDER, name="analyse")
        analyseBtn.SetForegroundColour(foreground_color)
        analyseBtn.SetBackgroundColour(btn_background_color)
        menuSizer.Add(analyseBtn, 1, wx.ALL | wx.EXPAND, 1)

        menuSizer.AddStretchSpacer(prop=5)

        # Will open an about message dialog
        aboutBtn = wx.Button(self, wx.ID_ABOUT, "About", style=wx.NO_BORDER, name="about")
        aboutBtn.SetForegroundColour(foreground_color)
        aboutBtn.SetBackgroundColour(btn_background_color)
        menuSizer.Add(aboutBtn, 1, wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # Bind all buttons of this menu
        self.Bind(wx.EVT_BUTTON, self.OnAction, fileBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, annotBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, analyseBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, aboutBtn)

        self.SetSizer(menuSizer)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def OnAction(self, event):
        """ A button was clicked.
        Here we just send the event to the parent.

        """
        print("A button was clicked on.")
        wx.PostEvent(self.GetTopLevelParent(), event)

    # -----------------------------------------------------------------------

    def OnAbout(self, event):
        """Display an About Dialog"""

        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World",
                      wx.OK | wx.ICON_INFORMATION)

# ---------------------------------------------------------------------------


class myActionPanel(wx.Panel):
    """ Create my own panel with 3 action buttons: exit, open, save.

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
        """ A button was clicked.
        Here we just send the event to the parent.

        """
        print("A button was clicked on.")
        wx.PostEvent(self.GetTopLevelParent(), event)


# ---------------------------------------------------------------------------


class myApp(wx.App):
    """ Create my own Application. Inherited from the wx.App.

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

        # add a customized menu (instead of a traditional menu+toolbar)
        menus = myMenuPanel(frm)
        topSizer.Add(menus, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT, 0)

        # separate menu and text with a line
        line_top = wx.StaticLine(frm, style=wx.LI_HORIZONTAL)
        topSizer.Add(line_top, 0, wx.ALL | wx.EXPAND, 0)

        # add some text in it and customize font
        st = wx.StaticText(frm, wx.ID_ANY, label="Hello World!", pos=(25, 25))
        st.SetForegroundColour(foreground_color)
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        topSizer.Add(st, 3, wx.ALL | wx.EXPAND, 5)

        # separate text and button with a line
        line_bottom = wx.StaticLine(frm, style=wx.LI_HORIZONTAL)
        topSizer.Add(line_bottom, 0, wx.ALL | wx.EXPAND, 0)

        # add some button in it and customize colors
        actions = myActionPanel(frm)
        topSizer.Add(actions, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

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
            event.Skip()

    # -----------------------------------------------------------------------

    def exit(self):
        """ Close the frame, terminating the application. """

        print("Bye bye.")
        self.GetTopWindow().Close(True)

    # -----------------------------------------------------------------------

    def OnExit(self):
        """ Optional. Override the already existing method. """

        # do whatever you want here (save session, ...)
        print("OnExit method invoked")

        # then it will exit. Nothing special to do. Return the exit status.
        return 0

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    app = myApp()
    app.MainLoop()
