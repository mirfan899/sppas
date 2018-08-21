import wx
"""

Create my own App.

"""
# ---------------------------------------------------------------------------


class myApp(wx.App):
    """Create my own Application. Inherited from the wx.App.

    """
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
        # ensure the parent's __init__ is called with the args we want
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        # create the frame
        frm = wx.Frame(None, title='Title of the frame')
        self.SetTopWindow(frm)

        # create a panel in the frame
        pnl = wx.Panel(frm)

        # and put some text on it
        wx.StaticText(pnl, label="Hello World!", pos=(25, 25))

        # show result
        frm.Show()

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    app = myApp()
    app.MainLoop()
