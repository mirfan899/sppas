import wx
"""

OOP... Create my own class.

"""

# ---------------------------------------------------------------------------


class HelloFrame(wx.Frame):
    """ A frame that says Hello World. Inherited from the wx.Frame.

    """
    def __init__(self, *args, **kw):

        # ensure the parent's __init__ is called
        super(HelloFrame, self).__init__(*args, **kw)

        # create a panel in the frame
        pnl = wx.Panel(self)

        # and put some text on it, at a given position
        wx.StaticText(pnl, label="Hello World!", pos=(25, 25))

# ---------------------------------------------------------------------------


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = HelloFrame(None, title='Title of the frame')
    frm.Show()
    app.MainLoop()
