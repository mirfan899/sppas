import wx
"""

Add a content to the frame, so requires to organize it.

"""

# ---------------------------------------------------------------------------


class myFrame(wx.Frame):
    """Create my own frame. Inherited from the wx.Frame.

    """
    def __init__(self):

        wx.Frame.__init__(self,
                          parent=None,
                          title='Title...')
        self.SetMinSize((300, 200))
        self.SetSize((640, 480))

# ---------------------------------------------------------------------------


class myApp(wx.App):
    """Create my own Application. Inherited from the wx.App.

    """
    def __init__(self):

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
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        topSizer.Add(st, 3, wx.ALL | wx.EXPAND, 5)

        # separate text and button with a line
        line = wx.StaticLine(frm, style=wx.LI_HORIZONTAL)
        topSizer.Add(line, 0, wx.ALL | wx.EXPAND, 0)

        # add some button in it and customize colors
        btn = wx.Button(frm, wx.ID_EXIT, "Exit", style=wx.NO_BORDER, name="exit")
        btn.SetForegroundColour(wx.Colour(250, 250, 250))
        btn.SetBackgroundColour(wx.Colour(50, 50, 50))
        topSizer.Add(btn, 1, wx.ALL | wx.EXPAND, 5)

        # Associate a handler function with the EVT_BUTTON event.
        # That means that when that button is clicked then the associated
        # handler function will be called.
        self.Bind(wx.EVT_BUTTON, self.on_exit, btn)

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

    def on_exit(self, event):
        """Close the frame, terminating the application."""

        # do whatever you want here (save session, ask for really quit, ...)
        print("Button exit clicked.")

        # then close all windows.
        self.GetTopWindow().Close(True)
        # After all windows are closed, the main loop iteration will stop.

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
