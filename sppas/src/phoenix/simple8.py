import wx
"""

Add several content panels and allow to switch.

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


class myButton(wx.Button):
    """ Create my own button. Inherited from the wx.Button.

    """
    def __init__(self, parent, label, name):

        wx.Button.__init__(self, parent, wx.ID_ANY, label, style=wx.NO_BORDER, name=name)
        self.SetForegroundColour(foreground_color)
        self.SetBackgroundColour(btn_background_color)

# ---------------------------------------------------------------------------


class myFrame(wx.Frame):
    """ Create my own frame. Inherited from the wx.Frame.

    """
    def __init__(self):

        wx.Frame.__init__(self,
                          parent=None,
                          title='Title...',
                          style=FRAME_STYLE)
        #self.SetBackgroundColour(background_color)
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
        self.SetSize((-1, 64))

        menuSizer = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(self, wx.ID_ANY, label="My App!", pos=(25, 25))
        st.SetForegroundColour(foreground_color)
        font = st.GetFont()
        font = font.Bold()
        st.SetFont(font)
        menuSizer.Add(st, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        menuSizer.AddStretchSpacer(prop=1)

        # Will switch to the "Files" main panel
        fileBtn = myButton(self, "Files", name="files")
        menuSizer.Add(fileBtn, 1, wx.EXPAND, 0)

        # Will switch to the "Annotate" main panel
        annotBtn = myButton(self, "Annotate", name="annotate")
        menuSizer.Add(annotBtn, 1, wx.EXPAND, 0)

        # Will switch to the "Analyze" main panel
        analyseBtn = myButton(self, "Analyze", name="analyze")
        menuSizer.Add(analyseBtn, 1, wx.EXPAND, 0)

        menuSizer.AddStretchSpacer(prop=5)

        # Will open an about message dialog
        aboutBtn = myButton(self, "About", name="about")
        menuSizer.Add(aboutBtn, 0, wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # Bind all buttons of this menu
        self.Bind(wx.EVT_BUTTON, self.OnAction, fileBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, annotBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, analyseBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, aboutBtn)

        self.SetSizer(menuSizer)

    # -----------------------------------------------------------------------

    def OnAction(self, event):
        """ A button was clicked.
        Here we just send the event to the parent.

        """
        print("A button was clicked on.")
        wx.PostEvent(self.GetTopLevelParent(), event)

    # -----------------------------------------------------------------------

    def OnAbout(self, event):
        """ Display an About Dialog. """

        # Default dialog which will have the default style... so, it won't
        # have our own colors...
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

        exitBtn = myButton(self, "Exit", name="exit")
        openBtn = myButton(self, "Open", name="open")
        saveBtn = myButton(self, "Save", name="save")

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


class myFilePanel(wx.Panel):
    """ Create my own panel to work with files.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(background_color)

        st = wx.StaticText(self, wx.ID_ANY, label="Files panel", pos=(25, 25))
        st.SetForegroundColour(foreground_color)
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        self.Show(True)

# ---------------------------------------------------------------------------


class myAnnotatePanel(wx.Panel):
    """ Create my own panel to annotate files.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(10, 10, 5))

        st = wx.StaticText(self, wx.ID_ANY, label="Annotate panel", pos=(25, 25))
        st.SetForegroundColour(foreground_color)
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        self.Show(False)

# ---------------------------------------------------------------------------


class myAnalyzePanel(wx.Panel):
    """ Create my own panel to analyze files.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(80, 80, 75))

        st = wx.StaticText(self, wx.ID_ANY, label="Analyze panel", pos=(25, 25))
        st.SetForegroundColour(foreground_color)
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        self.Show(False)

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

        # Store all panels in a dictionary with key=name, value=object
        self.panels = dict()

        # create a sizer to add and organize objects
        topSizer = wx.BoxSizer(wx.VERTICAL)

        # add a customized menu (instead of a traditional menu+toolbar)
        menus = myMenuPanel(frm)
        topSizer.Add(menus, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # separate menu and text with a line
        line_top = wx.StaticLine(frm, style=wx.LI_HORIZONTAL)
        topSizer.Add(line_top, 0, wx.ALL | wx.EXPAND, 0)

        # add a 1st panel for files
        self.panels["files"] = myFilePanel(frm)
        topSizer.Add(self.panels["files"], 3, wx.ALL | wx.EXPAND, 0)

        # add a 2nd panel for annotations
        self.panels["annotate"] = myAnnotatePanel(frm)
        topSizer.Add(self.panels["annotate"], 3, wx.ALL | wx.EXPAND, 0)

        # add a 3rd panel for analysis
        self.panels["analyze"] = myAnalyzePanel(frm)
        topSizer.Add(self.panels["analyze"], 3, wx.ALL | wx.EXPAND, 0)

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
        elif event_name in ["files", "annotate", "analyze"]:
            self.switch_to_panel(event_name)
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

    # -----------------------------------------------------------------------

    def switch_to_panel(self, panel_name):
        """ Switch to the expected panel. Hide the current. """

        print("Requested to switch on panel: {:s}".format(panel_name))

        if panel_name not in self.panels:
            print("  [ ERROR] Wrong panel name... ")
            return

        if self.panels[panel_name].IsShown() is False:
            # hide the current
            for p in self.panels:
                if self.panels[p].IsShown() is True:
                    self.panels[p].HideWithEffect(wx.SHOW_EFFECT_SLIDE_TO_BOTTOM, timeout=400)
            # show the expected
            self.panels[panel_name].ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_BOTTOM, timeout=400)

        self.GetTopWindow().Layout()
        self.GetTopWindow().Refresh()

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    app = myApp()
    app.MainLoop()
