import wx
"""

Create my own frame.

"""
# ---------------------------------------------------------------------------


class myFrame(wx.Frame):
    """ Create my own frame. Inherited from the wx.Frame.

    """
    def __init__(self):

        wx.Frame.__init__(self,
                          parent=None,
                          title='Title...')
        self.SetMinSize((300, 200))
        self.SetSize((640, 480))

# ---------------------------------------------------------------------------


class myApp(wx.App):
    """ Create my own Application. Inherited from the wx.App.

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

        # create a panel in the frame
        pnl = wx.Panel(frm)

        # and put some text on it
        wx.StaticText(pnl, label="Hello World!", pos=(25, 25))

        frm.Show()

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    app = myApp()
    app.MainLoop()
