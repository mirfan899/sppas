import wx

# -------------------------------------------------------------------- #
# Name:        src/generic/busyinfo.cpp
# Purpose:     Information window when app is busy
# Author:      Vaclav Slavik
# Copyright:   (c) 1999 Vaclav Slavik
# RCS-ID:      $Id: busyinfo.cpp,v 1.22 2006/03/31 18:07:08 ABX Exp $
# Licence:     wxWindows licence
# -------------------------------------------------------------------- #

# -------------------------------------------------------------------- #
# Adapted and converted from original C++ wxWidgets code by:
#
# Andrea Gavana @ 29 Jan 2008
# -------------------------------------------------------------------- #

__author__  = "Andrea Gavana <andrea.gavana@gmail.com>, <gavana@kpo.kz>"
__date__    = "29 Jan 2008, 10:15 GMT"
__version__ = "0.1"
__docformat__ = "epytext"


class PyInfoFrame(wx.Frame):
    """ Base class for PyBusyInfo. """

    def __init__(self, parent, message, useCustom):
        
        wx.Frame.__init__(self, parent, wx.ID_ANY, "Busy", wx.DefaultPosition,
                             wx.DefaultSize, wx.SIMPLE_BORDER | wx.FRAME_TOOL_WINDOW)

        panel = wx.Panel(self)
        panel.SetCursor(wx.HOURGLASS_CURSOR)

        if not useCustom:

            text = wx.StaticText(panel, wx.ID_ANY, message)
            text.SetCursor(wx.HOURGLASS_CURSOR)

            # make the frame of at least the standard size (400*80) but big enough
            # for the text we show
            sizeText = text.GetBestSize()

        else:

            # We will take care of drawing the text and not using wx.StaticText
            self._message = message
            dc = wx.ClientDC(self)
            textWidth, textHeight, dummy = dc.GetMultiLineTextExtent(self._message)
            sizeText = wx.Size(textWidth, textHeight)

        self.SetClientSize((max(sizeText.x, 340) + 60, max(sizeText.y, 40) + 40))
        # need to size the panel correctly first so that text.Centre() works
        panel.SetSize(self.GetClientSize())

        if useCustom:
            panel.Bind(wx.EVT_PAINT, self.OnPaint)
            panel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
            
        else:
            text.Centre(wx.BOTH)
            
        self.Centre(wx.BOTH)


    def OnPaint(self, event):
        """ Custom OnPaint event handler to draw nice backgrounds. """

        panel = event.GetEventObject()
        
        dc = wx.BufferedPaintDC(panel)
        dc.Clear()

        # Fill the background with a gradient shading
        startColour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION)
        endColour = wx.WHITE

        rect = panel.GetRect()
        dc.GradientFillLinear(rect, startColour, endColour, wx.SOUTH)

        # Draw the label
        font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dc.SetFont(font)
        
        dc.DrawLabel(self._message, rect, alignment=wx.ALIGN_CENTER|wx.ALIGN_CENTER)


    def OnErase(self, event):
        """
        Erase background event is intentionally empty to avoid flicker during
        custom drawing.
        """

        pass

                
# -------------------------------------------------------------------- #
# The actual PyBusyInfo implementation
# -------------------------------------------------------------------- #

class PyBusyInfo(object):
    """
    Constructs a busy info window as child of parent and displays msg in it.
    NB: If parent is not None you must ensure that it is not closed while the busy info is shown.
    """

    def __init__(self, message, parent=None, useCustom=False):
        """
        Default class constructor.

        @param message: the message to display;
        @param parent: the PyBusyInfo parent (can be None);
        @parent useCustom: if True, custom drawing/shading can be implemented.
        """

        self._infoFrame = PyInfoFrame(parent, message, useCustom)
        self._infoFrame.Show(True)
        self._infoFrame.Refresh()
        self._infoFrame.Update()
        

    def __del__(self):
        """ Overloaded method, for compatibility with wxWidgets. """

        self._infoFrame.Show(False)
        self._infoFrame.Destroy()


        
# -------------------------------------------------------------------- #
# A small demo :-D
# -------------------------------------------------------------------- #

def main():

    # --------------------------------------------------------- #
    # SIMPLY CHANGE THE useCustom VARIABLE TO GET A DIFFERENT - #
    # PyBusyInfo BEHAVIOUR                                    - #

    useCustom = True

    # --------------------------------------------------------- #
    
    app = wx.PySimpleApp()

    frame = wx.Frame(None, -1, "Sample PyBusyInfo ;-)", size=(500, 300))
    app.SetTopWindow(frame)

    frame.CenterOnScreen()
    frame.Show()
    
    busy = PyBusyInfo("Connecting To Message Server...", useCustom=useCustom)

    print "PyBusyInfo Created :-D\n"
    for i in xrange(10):
        print "Sleeping To Demonstrate PyBusyInfo..."
        wx.MilliSleep(300)

    print "\nDeleting PyBusyInfo...\n\n"
    del busy

    print "Demo Terminated."
    app.MainLoop()


if __name__ == "__main__":

    main()


    