# -*- coding: UTF-8 -*-
import wx
"""

This is the basic "Hello World! application."

"""
if __name__ == '__main__':

    # Create an application object.
    app = wx.App()

    # Create a frame. (None is the parent)
    frm = wx.Frame(None, title="Title of the frame")

    # Show it.
    frm.Show()

    # Start the event loop.
    app.MainLoop()
