#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ----------------------------------------------------------------------------
# File: labelctrl.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import logging
import wx
import wx.lib.newevent


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

MIN_W=2
MIN_H=6

# transparent background by default, black font for the text
BG_COLOUR=None
FG_COLOUR=wx.BLACK

STYLE=wx.NO_BORDER|wx.NO_FULL_REPAINT_ON_RESIZE

# ----------------------------------------------------------------------------
# Events
# ----------------------------------------------------------------------------

LabelLeftEvent, spEVT_LABEL_LEFT = wx.lib.newevent.NewEvent()
LabelLeftCommandEvent, spEVT_LABEL_LEFT_COMMAND = wx.lib.newevent.NewCommandEvent()

LabelRightEvent, spEVT_LABEL_RIGHT = wx.lib.newevent.NewEvent()
LabelRightCommandEvent, spEVT_LABEL_RIGHT_COMMAND = wx.lib.newevent.NewCommandEvent()

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Class LabelCtrl
# ----------------------------------------------------------------------------


class LabelCtrl( wx.Window ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to display a Label (see annotationdata for details).

    LabelCtrl implements a static text label.

    """

    def __init__(self, parent, id=-1,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 label=None):
        """
        LabelCtrl constructor.
        Notice that each change of the object implies a refresh.

        Non-wxpython related parameter:
            - label (Label) the Label of an annotation.

        """
        wx.Window.__init__(self, parent, id, pos, size, STYLE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetDoubleBuffered(True)

        # Members, Initializations
        self.Reset( size )

        self._label = None
        self.SetValue(label)
        #self.SetToolTip(wx.ToolTip(self.__tooltip()))

        # Bind the events related to our control
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)

        wx.EVT_ENTER_WINDOW(self, self.OnMouseEntering)
        wx.EVT_LEAVE_WINDOW(self, self.OnMouseLeaving)
        wx.EVT_LEFT_UP(self, self.OnMouseLeftUp)
        wx.EVT_RIGHT_UP(self, self.OnMouseLeftUp)
        wx.EVT_MOTION(self, self.OnMouseMotion)

    # End __init__
    #-------------------------------------------------------------------------


    def Reset(self, size=None):
        """
        Reset all values to their default.

        @param size (wx.Size)

        """

        self.__initializeColours()
        self.__initializeStyle()
        if size:
            self.__initialSize(size)

    # End Reset
    #-------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Members: Getters and Setters
    #-------------------------------------------------------------------------


    def SetValue(self, label):
        """
        Sets the LabelCtrl label. Strip the new label.

        @param label (Label)

        """

        if not (label is self._label):
            self._label = label
            if self._label.GetSize()>1:
                self._underlined = True
            self.SetToolTip(wx.ToolTip(self.__tooltip()))


    def GetValue(self):
        """
        Retrieve the label associated to the LabelCtrl.

        """
        return self._label

    #-------------------------------------------------------------------------


    def SetUnderlined(self, underlined=False):
        """
        Sets if the label must be underlined.
        By default, an ambiguous label is systematically underlined.

        @param underlined (Boolean) sets whether a label has to be underlined or not.

        """
        if underlined != self._underlined:
            self._underlined = underlined
            self.Refresh()


    def GetUnderlined(self):
        """
        Returns whether a label has to be underlined or not.

        """
        return self._underlined

    #-------------------------------------------------------------------------


    def SetBold(self, bold=False):
        """
        Sets if the label must be bold.

        @param bold (Boolean) sets whether a label has to be bold or not.

        """
        if bold != self._bold:
            self._bold = bold
            self.Refresh()


    def GetBold(self):
        """
        Returns whether the label has to be bold or not.

        """
        return self._bold

    #-------------------------------------------------------------------------


    def SetAlign(self, value=wx.ALIGN_CENTRE):
        """
        Fix the position of the label.

        @param value is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        if value != self._align:
            self._align = value
            self.Refresh()


    def GetAlign(self):
        """
        Returns the label alignment value.

        @return one of: wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        return self._align

    #-------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Look & style
    #-------------------------------------------------------------------------


    def SetColours(self, bgcolour=None, fontcolour=None):
        """
        Change the main colors of the LabelCtrl.

        @param bgcolour (wx.Colour)
        @param fontcolour (wx.Colour)

        """

        if bgcolour is not None and bgcolour != self._bgcolour:
            self._bgcolour = bgcolour
            self._bgpen   = wx.Pen(bgcolour,1,wx.SOLID)
            self._bgbrush = wx.Brush(bgcolour, wx.SOLID)
            self.SetBackgroundColour(bgcolour)

        if fontcolour is not None and fontcolour != self.GetForegroundColour():
            self.SetForegroundColour(fontcolour)

    # End SetColour
    #-------------------------------------------------------------------------


    def SetFont(self, font):
        """
        Override. Set font.

        """
        if font != self.GetFont():
            wx.Window.SetFont(self,font)

    #-------------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnMouseMotion(self, event):
        wx.PostEvent(self.GetParent().GetEventHandler(), event)


    def OnMouseEntering(self, event):
        """ Mouse is Entering on the LabelCtrl, then starts to highlight. """
        if self._highlight is False:
            self._highlight = True
            self.Refresh()
        event.Skip()


    def OnMouseLeaving(self, event):
        """ Mouse is Entering on the LabelCtrl, then stops to highlight. """
        if self._highlight is True:
            self._highlight = False
            self.Refresh()
        event.Skip()


    def OnMouseLeftUp(self, event):
        """ Left Button was Pressed. """
        evt = LabelLeftEvent(label=self._label)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)
        event.Skip()


    def OnMouseRightUp(self, event):
        """ Right Button was Pressed. """
        evt = LabelRightEvent(label=self._label)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)
        event.Skip()

    # End OnMouseEvent
    #-------------------------------------------------------------------------


    def SetHeight(self, height):
        """
        Change the height of the LabelCtrl.

        @param height (int) is the new height.

        """
        if self.GetSize().height != height:
            self.SetSize( wx.Size(self.GetSize().width, int(height)) )
            self.Refresh()

    # End SetHeight
    #-------------------------------------------------------------------------


    def MoveWindow(self, pos, size):
        """
        Define a new position and/or size to display.
        Refresh only if something has changed.

        @param pos (wx.Point)
        @param size (wx.Size)

        """
        (w,h) = size
        (x,y) = pos
        (ow,oh) = self.GetSize()
        (ox,oy) = self.GetPosition()

        if ow != w or oh != h:
            self.SetSize(size)
            self.Refresh()

        if ox != x or oy != y:
            self.SetPosition(pos)
            #self.Refresh()

    # End MoveWindow
    #-------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Painting
    #-------------------------------------------------------------------------


    def OnPaint(self, event):
        """
        Handles the wx.EVT_PAINT event for LabelCtrl.

        """

        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    # OnPaint
    #-------------------------------------------------------------------------


    def Draw(self, dc):
        """
        Draw the label on the DC, starting at (x,y).

        @param dc (DC) Drawing Context of the LabelCtrl.

        """
        # Get the actual client size of ourselves
        w, h = self.GetClientSize()

        # Nothing to do, we still don't have dimensions!
        if not w or not h:
            return

        # Initialize
        if not self._bgcolour:
            dc.SetBackgroundMode( wx.TRANSPARENT )
        else:
            dc.SetBackgroundMode( wx.SOLID )
            dc.SetBackground( self._bgbrush )
            dc.SetTextBackground( self._bgcolour )
        dc.Clear()

        # Set the font with the expected style
        font_face = self.GetFont()
        font_face.SetUnderlined(self._underlined)
        if self._bold is True:
            font_face.SetWeight( wx.FONTWEIGHT_BOLD )
        else:
            font_face.SetWeight( wx.FONTWEIGHT_NORMAL )
        dc.SetFont(font_face)
        dc.SetTextForeground( self.GetForegroundColour() )

        # Adjust position
        if self._label is not None:
            textwidth, textheight = dc.GetTextExtent( self._label.GetValue() )
            if self._align == wx.ALIGN_LEFT:
                x=0
            elif self._align == wx.ALIGN_RIGHT:
                x=max(1,w-textwidth-1)
            else:
                x=(w-textwidth)/2
            y = (h-textheight)/2
            dc.DrawText(self._label.GetValue(), x, y)

        # If highlighted
        if self._highlight is True:
            dc.SetPen( wx.BLACK_DASHED_PEN )
            dc.DrawLine(0,0,w,0)
            dc.DrawLine(0,h-1,w,h-1)

    # End Draw
    #-------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Private
    #-------------------------------------------------------------------------


    def __initializeStyle(self):
        """ Initializes the label style. """

        self._align      = wx.ALIGN_LEFT
        self._underlined = False
        self._bold       = False
        self._highlight  = False

    # End InitializeStyle
    #-------------------------------------------------------------------------


    def __initializeColours(self):
        """ Initializes the pens. """

        self._bgpen      = wx.Pen(BG_COLOUR,1,wx.SOLID)
        self._bgbrush    = wx.Brush(BG_COLOUR,wx.SOLID)
        self._bgcolour   = BG_COLOUR

        self.SetBackgroundColour( BG_COLOUR )
        self.SetForegroundColour( FG_COLOUR )

    # End InitializeColours
    #-------------------------------------------------------------------------


    def __initialSize(self, size):
        """ Initialize the size. """

        self.SetMinSize(wx.Size(MIN_W,MIN_H))
        self.SetSize(size)

    # End InitialSize
    #-------------------------------------------------------------------------


    def __tooltip(self):
        """ Set a tooltip string with the label. """

        if self._label is not None:
            if self._label.GetSize()>1:
                alltexts = self._label.GetLabels()
                s = ""
                for t in alltexts:
                    s += str(t.Score) + " " + t.Value + "\n"
                return s
            return self._label.GetValue()
        return ""

    #-------------------------------------------------------------------------


# ----------------------------------------------------------------------------
