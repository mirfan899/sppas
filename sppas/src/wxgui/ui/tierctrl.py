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
#       Copyright (C) 2011-2014  Brigitte Bigi
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
# File: tierctrl.py
# ----------------------------------------------------------------------------

__docformat__ = "epytext"
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = "Copyright (C) 2011-2015  Brigitte Bigi"

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import logging

import wx
import wx.lib.newevent

from wxgui.cutils.colorutils import PickRandomColour, ContrastiveColour
from wxgui.cutils.textutils  import TextAsNumericValidator

from pointctrl import PointCtrl
from pointctrl import spEVT_MOVING,spEVT_MOVED,spEVT_RESIZING,spEVT_RESIZED, spEVT_POINT_LEFT
from pointctrl import MIN_W as pointctrlMinWidth

from labelctrl import LabelCtrl
from labelctrl import spEVT_LABEL_LEFT

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

MIN_W=2
MIN_H=8

NORMAL_COLOUR    = wx.Colour(0,0,0)
UNCERTAIN_COLOUR = wx.Colour(70,70,180)

STYLE=wx.NO_BORDER|wx.NO_FULL_REPAINT_ON_RESIZE

FONT_SIZE_MIN = 8
FONT_SIZE_MAX = 32

PANE_WIDTH_MIN = 10
PANE_WIDTH_MAX = 200
PANE_WIDTH     = 100

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Class PaneTierCtrl
# ----------------------------------------------------------------------------

class PaneTierCtrl( wx.Window ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to display a pane for a TierCtrl.

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 text=""):
        """
        Constructor.

        Non-wxpython related parameters:

        @param text (str) the text to write in the pane.

        """
        wx.Window.__init__( self, parent, id, pos, size, STYLE )
        self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
        self.SetDoubleBuffered( True )

        # Members, Initializations
        self._text = text
        self.SetToolTip( wx.ToolTip(self.__tooltip()) )
        self.Reset( size )

        # Bind the events related to our control
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)
        wx.EVT_MOUSE_EVENTS(self, self.OnMouseEvents)

    #------------------------------------------------------------------------

    def Reset(self, size=None):
        """
        Reset all members to their default.

        @param size (wx.Size)

        """
        self._align = wx.ALIGN_LEFT
        self.__initializeColours()
        if size:
            self.__initialSize(size)

    #------------------------------------------------------------------------

    #------------------------------------------------------------------------
    # Look & style
    #------------------------------------------------------------------------

    def SetFont(self, font):
        """
        Override. Set a new font.

        """
        if font != self.GetFont():
            wx.Window.SetFont(self,font)

    #------------------------------------------------------------------------

    def SetTextAlign(self, value=wx.ALIGN_CENTRE):
        """
        Fix the position of the text.

        @param value is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        if value != self._align:
            self._align = value

    #------------------------------------------------------------------------

    def GetTextAlign(self):
        """
        Returns the text position.

        @return one of: wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        return self._align

    #------------------------------------------------------------------------

    def SetBorderColour(self, colour):
        """
        Fix the color of the top/bottom lines.

        """
        self._penbordercolor = wx.Pen(colour,1,wx.SOLID)

    #------------------------------------------------------------------------

    def SetWidth(self, width):
        """
        Change the width of the PaneTierCtrl, only if necessary.

        @param width (int) is the new width.

        """
        if width < PANE_WIDTH_MIN:
            width = PANE_WIDTH_MIN
        if self.GetSize().width != width:
            self.SetSize(wx.Size(int(width),self.GetSize().height))
            self._width = width

    #------------------------------------------------------------------------

    def GetWidth(self):
        """
        Return the defined width.
        It can un-match with the current width.

        @return (int) the current width in pixels.

        """
        return self._width

    #------------------------------------------------------------------------

    def SetHeight(self, height):
        """
        Change the height of the PointCtrl.

        @param height (int) is the new height.

        """
        if height < MIN_H:
            height = MIN_H
        if self.GetSize().height != height:
            self.SetSize( wx.Size(self.GetSize().width, int(height)) )
            self.Refresh()

    #------------------------------------------------------------------------

    def SetText(self, text):
        """
        Change the text to write.

        """
        self._text = text

    #------------------------------------------------------------------------

    def MoveWindow(self, pos, size):
        """
        Define a new position and/or size to display.

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

    #------------------------------------------------------------------------

    #------------------------------------------------------------------------
    # Callbacks
    #------------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """
        Handles the wx.EVT_MOUSE_EVENTS event for PaneTierCtrl.

        """
        wx.PostEvent(self.GetParent(), event)
        event.Skip()

    # -----------------------------------------------------------------------

    #------------------------------------------------------------------------
    # Painting
    #------------------------------------------------------------------------

    def OnPaint(self, event):
        """
        Handles the wx.EVT_PAINT event for PointCtrl.

        """
        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    #------------------------------------------------------------------------

    def Draw(self, dc):
        """
        Draw the PointCtrl on the DC.

        @param dc (wx.DC) The device context to draw on.

        """
        # Get the actual client size of ourselves
        w,h = self.GetClientSize()

        # Nothing to do, we still don't have dimensions!
        if w*h==0: return

        # Write the tier name
        textwidth, textheight = dc.GetTextExtent( self._text )

        # Vertical position of the text
        y = int( (h - textheight)/2 ) - 1

        # Write text
        dc.Clear()
        dc.SetBackground( wx.Brush( self.GetBackgroundColour(), wx.SOLID ) )
        dc.SetTextBackground( wx.NullColour )
        dc.SetFont( self.GetFont() )
        dc.SetTextForeground( self.GetForegroundColour() )

        textwidth, textheight = dc.GetTextExtent( self._text )
        if self._align == wx.ALIGN_LEFT:
            x=2
        elif self._align == wx.ALIGN_RIGHT:
            x=max(1,w-textwidth-1)
        else:
            x=(w-textwidth)/2
        y = (h-textheight)/2
        dc.DrawText(self._text, x, y)

        # Top and Bottom lines
        x,y=self.GetPosition()
        dc.SetPen( self._penbordercolor )
        dc.DrawLine(0,y,w,y)
        dc.DrawLine(0,h-1,w,h-1)

    #------------------------------------------------------------------------
    # Private
    #------------------------------------------------------------------------

    def __initializeColours(self):
        """ Create the pens and brush with default colors. """
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self._penbordercolor = wx.Pen(wx.BLACK,1,wx.SOLID)

    #------------------------------------------------------------------------

    def __initialSize(self, size):
        """ Initialize the size. """

        self.SetMinSize(wx.Size(MIN_W,MIN_H))
        if size:
            self.SetSize(size)

    #------------------------------------------------------------------------

    def __tooltip(self):
        """ Set a tooltip string indicating the text content. """

        return self._text

    #------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Class TierCtrl
# ---------------------------------------------------------------------------

class TierCtrl( wx.Window ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to display a Tier (see annotationdata for details).

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 tier=None):
        """
        Constructor.

        Non-wxpython related parameter:
            - tier (Tier) the Tier to draw (see annotationdata library for details).

        """
        self._pointsctrl = []
        self._labelsctrl = []
        self._panectrl = None
        self._anns = {} # To link the annotations to the displayed controls
        self._tier = tier

        wx.Window.__init__(self, parent, id, pos, size, STYLE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetDoubleBuffered(True)

        self.Reset( size )
        self._buildpanectrl()

        # Bind the events related to our control:
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)

        wx.EVT_MOUSE_EVENTS(self, self.OnMouseEvents)

        #spEVT_LABEL_LEFT(self, self.OnLabelEdit)
        #spEVT_POINT_LEFT(self, self.OnPointEdit)
        #spEVT_RESIZING(self,   self.OnPointResizing)
        #spEVT_RESIZED(self,    self.OnPointResized)
        spEVT_MOVING(self,     self.OnPointMoving)
        #spEVT_MOVED(self,      self.OnPointMoved)

    #------------------------------------------------------------------------

    def _buildpanectrl(self):
        """
        Construct the left pane.

        """
        if not self._tier:
            text="" # not declared
        elif self._tier is None:
            text="" # not initialized
        else:
            text=self._tier.GetName()
        self._panectrl = PaneTierCtrl(self, text=text)
        self._panectrl.SetBackgroundColour( self.GetBackgroundColour() )
        self._panectrl.SetForegroundColour( self.GetForegroundColour() )
        self._panectrl.SetWidth( PANE_WIDTH )
        self._panectrl.SetBorderColour( self._bgdarkencolor )

    #------------------------------------------------------------------------
    # Getters and Setters
    #------------------------------------------------------------------------

    def Reset(self, size):
        """
        Reset all members to their default.

        @param size (wx.Size)

        """
        self.SetMinSize(wx.Size(MIN_W,MIN_H))
        if size:
            (w,h) = size
            if w < MIN_W: w = MIN_W
            if h < MIN_H: h = MIN_H
            self.SetSize(wx.Size(w,h))

        # Displayed period of time (can be taken from the Parent)
        self._mintime = 0.
        self._maxtime = 2.

        self._panepos = wx.ALIGN_LEFT

        # Colors
        self._bgcolor = self.GetParent().GetBackgroundColour()
        self._bgpen   = wx.Pen( self._bgcolor, 1, wx.SOLID )
        self._bgbrush = wx.Brush( self._bgcolor, wx.SOLID )

        self._bgdarkencolor = ContrastiveColour(self._bgcolor)
        self._bgdarkenpen   = wx.Pen( self._bgdarkencolor, 1, wx.SOLID )

        self._fgcolor = PickRandomColour(180,250)
        self._fgpen   = wx.Pen( self._fgcolor, 1, wx.SOLID )
        self._fgbrush = wx.Brush( self._fgcolor, wx.SOLID )

        self._midpointcolor = wx.BLACK

        # Label in each annotation
        self._textcolor = self.GetParent().GetForegroundColour()
        if self._tier is not None and self._tier.IsPoint():
            self._labelalign = wx.ALIGN_LEFT
        else:
            self._labelalign = wx.ALIGN_CENTRE
        self._labelbgcolor  = self._fgcolor #
        self._labelfgucolor = None          # uncertain label

        # &²Adjust font size when self is resized or when a new font is fixed:
        self._fontsizeauto = True
        self.AutoAdjustFont()

    #------------------------------------------------------------------------

    def SetTime(self, start, end):
        """
        Define a new period to display.
        Redraw only if the period has changed.

        @param start (float) begin time value, in seconds.
        @param end (float) end time value, in seconds.

        """
        torepaint = False

        if start > end:
            b = start
            end = start
            start = b

        if self._mintime != start:
            self._mintime = start
            torepaint = True

        if self._maxtime != end:
            self._maxtime = end
            torepaint = True

        if torepaint is True: self.Refresh()

    #------------------------------------------------------------------------

    def SetLabelAlign(self, value):
        """
        Fix the position of the text of an annotation.

        @param value is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        if self._tier.IsPoint(): return

        if self._labelalign != value:
            # Apply this new value to self.
            self._labelalign = value
            # propagate to all label controls
            for label in self._labelsctrl:
                label.SetAlign( value )

    #------------------------------------------------------------------------

    def SetFont(self, font):
        """
        Fix a font.
        Redraw only if the font has changed.
        Automatically adjust the size (compared to the previous one).

        @param font (wx.Font)

        """
        if font == self.GetFont(): return

        # check font size (more than min, less than max!)
        fontsize = font.GetPointSize()
        if fontsize < FONT_SIZE_MIN:
            font.SetPointSize(FONT_SIZE_MIN)
        if fontsize > FONT_SIZE_MAX:
            font.SetPointSize(FONT_SIZE_MAX)

        # Apply this new font to self.
        wx.Window.SetFont( self,font )
        if self._fontsizeauto:
            self.AutoAdjustFont()

        # propagate to all controls
        self._panectrl.SetFont( self.GetFont() )
        for label in self._labelsctrl:
            label.SetFont( self.GetFont() )

        self.Refresh()

    #------------------------------------------------------------------------

    def SetTextColour(self, colour):
        """
        Sets the tier text color.

        @param colour (wx.Colour)

        """
        if colour != self._textcolor:
            self._panectrl.SetForegroundColour( colour )
            self._textcolor = colour
            self._textpen   = wx.Pen(colour,1,wx.SOLID)
            self.Refresh()

    #------------------------------------------------------------------------

    def SetLabelColours(self, bgcolour=None, fontnormalcolour=None, fontuncertaincolour=None):
        """
        Change the main colors of the Labels.
        Notice that uncertain labels can be of a different color,
        like links in web browsers.

        @param bgcolour (wx.Colour)
        @param fontcolour (wx.Colour)
        @param fontuncertaincolour (wx.Colour)

        """
        redraw = False

        if fontnormalcolour is not None:
            self.SetTextColour(fontnormalcolour)

        if fontuncertaincolour is not None:
            self._labelfgucolor = fontuncertaincolour
            redraw = True

        if bgcolour is not None and bgcolour != self._labelbgcolor:
            self._labelbgcolor = bgcolour

            for label in self._labelsctrl:
                if label.GetValue().GetSize() == 1:
                    label.SetColours(bgcolour,fontnormalcolour)
                else:
                    label.SetColours(bgcolour,fontuncertaincolour)

            for point in self._pointsctrl:
                point.SetColours(self._midpointcolor, colourradius=bgcolour)

            redraw = True

        if redraw: self.Refresh()

    #------------------------------------------------------------------------

    def SetPointColour(self, colourmidpoint=None):
        """
        Change the color of the PointCtrl. Only the midpoint can be fixed.
        The color of the radius depends on the tier background color.

        @param colourmidpoint (wx.Colour)

        """

        if colourmidpoint is not None:
            self._midpointcolor = colourmidpoint

        for point in self._pointsctrl:
            point.SetColours(self._midpointcolor, colourradius=None)

    #------------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """
        Sets the tier background color.

        @param colour (wx.Colour)

        """

        if colour != self._bgcolor:
            self._bgcolor = colour
            self._bgpen   = wx.Pen(colour,1,wx.SOLID)
            self._bgbrush = wx.Brush(colour, wx.SOLID)
            self._panectrl.SetBackgroundColour( colour )
            self.Refresh()

    #------------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """
        Sets the tier foreground color.

        @param colour (wx.Colour)

        """

        if colour != self._fgcolor:
            self._fgcolor = colour
            self._fgpen   = wx.Pen(colour,1,wx.SOLID)
            self._fgbrush = wx.Brush(colour, wx.SOLID)
            self.Refresh()

    #------------------------------------------------------------------------

    def SetPanePosition(self, value):
        """
        Fix the position of the information pane.
        It also fixes the position of the text inside the pane...

        @param value is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT.
        @raise TypeError

        """
        if value not in [ wx.ALIGN_LEFT, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE ]:
            raise TypeError

        if self._panepos != value:
            self._panepos = value
            self._panectrl.SetTextAlign( value )
            self.Refresh()

    #------------------------------------------------------------------------

    def SetPaneWidth(self, value):
        """
        Fix the width of the information pane.

        @param value (int) is between 10 and 200.

        """
        self._panectrl.SetWidth(value)
        self.Refresh()

    # -----------------------------------------------------------------------

    def GetPanePosition(self):
        """
        Return the position of the information pane.
        The position is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT.

        """
        return self._panepos

    #------------------------------------------------------------------------

    def GetLabelAlign(self):
        """
        Get the position of the text of an annotation.
        The position is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT.

        """
        return self._labelalign

    # -----------------------------------------------------------------------

    def GetPaneWidth(self):
        """
        Return the width of the information pane.

        """
        return self._panectrl.GetWidth()

    # -----------------------------------------------------------------------

    def GetHeight(self):
        """
        Return the current height.

        """
        return self.GetSize().height

    # -----------------------------------------------------------------------

    def GetTier(self):
        """
        Return the tier to draw.

        """
        return self._tier

    #------------------------------------------------------------------------

    #------------------------------------------------------------------------
    # Methods to move/zoom/resize objects
    #------------------------------------------------------------------------

    def SetHeight(self, height):
        """
        Set the height (int).
        Ask to redraw only if height is different of the actual one.

        @param height (int) in pixels

        """
        w,h = self.GetSize()

        if h != height:
            # apply new height
            new_height = max(MIN_H, height)
            self.SetSize(wx.Size(w,int(new_height)))
            # adjust font size
            if self._fontsizeauto:
                self.AutoAdjustFont()

        # Apply to all objects of the tier
        h = self.GetHeight()

        self._panectrl.SetHeight( h )
        for point in self._pointsctrl:
            point.SetHeight( h )
        for label in self._labelsctrl:
            label.SetHeight( h )
            label.SetFont( self.GetFont() )

    # -----------------------------------------------------------------------

    def MoveWindow(self, pos, size):
        """
        Define a new position and/or size to display.
        Ask to redraw only if something has changed.

        @param pos (wx.Point)
        @param size (wx.Size)

        """
        torepaint = False
        (w,h) = size
        (x,y) = pos
        (ow,oh) = self.GetSize()
        (ox,oy) = self.GetPosition()

        # New width
        if ow != w:
            self.SetSize( wx.Size(w,oh) )
            torepaint = True

        # New height
        if oh != h:
            self.SetHeight(h)
            torepaint = True

        # New position (x and/or y)
        if ox != x or oy != y:
            self.Move(pos)
            torepaint = True

        if torepaint is True: self.Refresh()

        # If MoveWindow has changed the font size:
        if self._fontsizeauto and size != self.GetFont().GetPointSize():
            for label in self._labelsctrl:
                label.SetFont(self.GetFont())

    #------------------------------------------------------------------------

    def VertZoom(self, z):
        """
        Apply a vertical zoom to the TierCtrl.

        @param z (float) is the zoom coefficient.

        """
        h = int(z * self.GetHeight())
        self.SetHeight(h)

    # -----------------------------------------------------------------------

    def AutoAdjustFont(self):
        """
        Fix and apply the most appropriate font size,
        depending on the available height.

        """
        h = self.GetHeight()
        if not h: return

        fontsize = FONT_SIZE_MIN
        font = self.GetFont()
        font.SetPointSize(fontsize)
        wx.Window.SetFont(self,font)

        pxh = self.__getTextHeight()
        pxmax = int(0.6*h)
        while fontsize < FONT_SIZE_MAX and pxh<pxmax:
            fontsize = fontsize + 1
            font = self.GetFont()
            font.SetPointSize(fontsize)
            wx.Window.SetFont(self,font)
            pxh = self.__getTextHeight()

        return fontsize

        # wx bug: self.GetFont().SetPointSize(fontsize) does not do anything!!

    #------------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """
        Handles the wx.EVT_MOUSE_EVENTS event for PointCtrl.

        """
        wx.PostEvent(self.GetParent(), event)
        event.Skip()

    # -----------------------------------------------------------------------

    def OnPointEdit(self, event):
        """ Point Edit. Open a dialog to edit the point values. """

        logging.debug('TIER. OnPointEdit. Not implemented.')
        return
        # get point from the event
        point = event.GetEventObject()
        # show point editor
        dlg = PointEditor( self, point.GetValue(), point.GetRadius() )
        if dlg.ShowModal() == wx.ID_OK:
            (m,r) = dlg.GetValues()
            # do something with the new value (accept or reject)

        dlg.Destroy()

    # -----------------------------------------------------------------------

    def OnPointResizing(self, event):
        """ Point Resizing means a new radius value for the TimePoint. """
        # TODO
        logging.debug('TIER. OnPointResizing. Not implemented.')
        return

        # which point is resized and what are new coordinates?
        ptr = event.GetEventObject()
        (x,y) = event.pos
        (w,h) = event.size

        # self coordinates
        sx,sy = self.GetPosition()
        sw,sh = self.GetSize()

    # -----------------------------------------------------------------------

    def OnPointMoving(self, event):
        logging.debug('TIER. OnPointMoving. Not implemented.')

        # which point is moving and what is new size?
        ptr = event.GetEventObject()
        (x,y) = event.pos
        (w,h) = ptr.GetSize()

        # self coordinates
        sx,sy = self.GetPosition()
        sw,sh = self.GetSize()

        return

        # get new time value
        # b =
        # e =

        # get annotations related to this pointctrl
        # _newanns = {}
        # _newok = True
        # for ann in self._anns.keys()
        #    label, p1, p2 = self._anns[ann]
        #    if p1 == ptr:
        #        # try to fix the new value to this timepoint
        #        try:
        #            p = TimePoint( b, ptr.GetValue().GetRadius() )
        #            ann.GetLocation().SetBegin( p )
        #        except Exception:
        #            _newok = False
        #    if p2 == ptr:
        #        # try to fix the new value to this timepoint
        #        try:
        #            p = TimePoint( e, ptr.GetValue().GetRadius() )
        #            ann.GetLocation().SetEnd( p )
        #        except Exception:
        #            _newok = False
        #    _newanns[ann] = [ label, p1, p2 ]
        #
        # if _newok is True:
        #    self._anns = _newanns
        #    # accept new pos...
        #    ptr.Move(event.pos)

        logging.debug(' ... new point pos: %d,%d'%(x,y))
        self.GetTopLevelParent().GetStatusBar().SetStatusText('Point is moving: %d'%x)

        self.Refresh()

    # -----------------------------------------------------------------------

    #------------------------------------------------------------------------
    # Painting
    #------------------------------------------------------------------------

    def OnPaint(self, event):
        """
        Handles the wx.EVT_PAINT event for TierCtrl.

        """
        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    #------------------------------------------------------------------------

    def Draw(self, dc):
        """
        Draw the TierCtrl on the DC.

        1. fill the background,
        2. draw the pane,
        3. draw the content,

        @param dc (wx.DC) The device context to draw on.

        """
        if not self._tier:     return # not declared
        if self._tier is None: return # not initialized

        # Get the actual client size and position of ourselves
        w,h = self.GetClientSize()

        # Nothing to do, we still don't have dimensions!
        if w*h==0: return

        # Initialize the DC
        if self._bgcolor is None:
            dc.SetBackgroundMode( wx.TRANSPARENT )
        else:
            dc.SetBackground( self._bgbrush )
        dc.Clear()

        # Pane
        x=0
        if self._panepos == wx.ALIGN_LEFT:
            self._panectrl.MoveWindow(pos=(0,0),size=(self._panectrl.GetWidth(),h))
            x=self._panectrl.GetWidth()
            w=w-self._panectrl.GetWidth()
        elif self._panepos == wx.ALIGN_RIGHT:
            self._panectrl.MoveWindow(pos=(w-self._panectrl.GetWidth(),0),size=(self._panectrl.GetWidth(),h))
            w=w-self._panectrl.GetWidth()
        else:
            self._panectrl.MoveWindow(pos=(0,0),size=(0,0))

        # Content
        self.DrawContent(dc, x,0, w,h)

    #------------------------------------------------------------------------

    def DrawBackground(self, dc, x,y, w, h):
        """
        Draw the background of the tier.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param w,h (int,int) are width and height available for drawing.

        """
        # Gradient background
        mid = h / 3
        box_rect = wx.Rect(x, y, w, mid)
        dc.GradientFillLinear(box_rect, self._bgcolor, self._fgcolor, wx.NORTH)
        box_rect = wx.Rect(x, 2*mid, w, mid+1)
        dc.GradientFillLinear(box_rect, self._bgcolor, self._fgcolor, wx.SOUTH)

        dc.SetPen( self._bgpen )
        dc.SetBrush( self._bgbrush )
        dc.DrawRectangle(x, mid, w, mid)

        # Top and Bottom lines
        dc.SetPen( self._bgdarkenpen )
        dc.DrawLine(x,y,x+w,y)
        dc.DrawLine(x,h-1,x+w,h-1)

    #------------------------------------------------------------------------

    def DrawContent(self, dc, x,y, w,h):
        """
        Draw the tier on the DC.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param x,y (int,int) are coord. of top left corner from which drawing
        @param w,h (int,int) are width and height available for drawing.

        """
        tierbegin = self._tier.GetBeginValue()
        tierend   = self._tier.GetEndValue()

        # the period is overlapping this tier: draw partly
        if self._tier.IsPoint() is False:
            # Adjust width, if tier ends before the max
            if self._mintime < tierend and self._maxtime > tierend:
                ## reduce w (to cover until the end of the tier)
                missingtime = self._maxtime - tierend
                w = w - self._calcW(w, missingtime)

            # Adjust x if tier starts after the min
            if self._maxtime > tierbegin and self._mintime < tierbegin:
                missingtime = tierbegin - self._mintime
                x = x + self._calcW(w, missingtime)

        self.DrawBackground(dc, x,y, w,h)

        # keep in memory the current list of all created controls, just hide them
        for point in self._pointsctrl:
            point.Hide()
        for label in self._labelsctrl:
            label.Hide()

        # get the list of annotations to display
        annotations = self._tier.Find(self._mintime, self._maxtime, overlaps=True)

        # displayed annotations
        for ann in annotations:
            # Must create new controls
            if not ann in self._anns.keys():
                if self._tier.IsPoint():
                    self._addAnnotationPoint(ann)
                elif self._tier.IsInterval():
                    self._addAnnotationInterval(ann)
                else:
                    logging.info(' TierCtrl [WARNING] Can NOT draw annotation: bad type. %s'%ann)
            # Show controls
            self._drawAnnotation( ann, x,y, w,h )

    #------------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _drawPoint(self, point, x,y, w,h):
        """ Display a point. """

        xpt, wpt = self._calcPointXW( point.GetValue(), w,h )
        # Do not draw if point is outsite the available area!
        if xpt>w:
            point.Hide()
            return

        if self._tier.IsPoint():
            point.MoveWindow(wx.Point(x+xpt,y), wx.Size(wpt,int(h/2)))
        else:
            point.MoveWindow(wx.Point(x+xpt,y), wx.Size(wpt,h))
        point.Show()

    # -----------------------------------------------------------------------

    def _drawAnnotation(self, ann, x,y, w,h):
        """ Display an existing annotation. """

        label  = self._anns[ann][0]
        point  = self._anns[ann][1]
        point2 = self._anns[ann][2]

        th=h-2 # 2 is top/bottom lines of 1 pixel each
        ty=y+1

        # Draw the label
        xpt1, wpt1 = self._calcPointXW(point.GetValue(), w,h)
        if xpt1>w: return

        if self._tier.IsPoint():
            tw = min(50, self.__getTextWidth(label.GetValue().GetValue())+2 )
            if (xpt1+wpt1+tw) > w: # ensure to stay in our allocated area
                tw = w - (xpt1+wpt1) # reduce width to the available area
            tw = max(0,tw)
            label.MoveWindow(wx.Point(x+xpt1+wpt1,ty), wx.Size(tw,th))
        else:
            xpt2, wpt2 = self._calcPointXW(point2.GetValue(), w,h)
            tx = x+xpt1+wpt1
            tw = xpt2-xpt1-wpt1
            if (tx+tw) > (x+w):  # ensure to stay in our allocated area
                tw = tw - ((tx+tw)-(w+x)) # reduce width to the available area
            tw = max(0,tw)
            label.MoveWindow(wx.Point(tx,ty), wx.Size(tw,th))

        label.Show()

        # Draw the points
        self._drawPoint(point, x,ty, w,th)
        if self._tier.IsInterval():
            self._drawPoint(point2, x,ty, w,th)

    # -----------------------------------------------------------------------

    def _addAnnotationInterval(self, ann):
        """ Create new controls for an annotation, or link to existing controls. """

        tp1 = ann.GetLocation().GetBegin()
        tp2 = ann.GetLocation().GetEnd()

        p1 = None
        p2 = None

        # Is there a pointctrl at the same place? .
        for point in self._pointsctrl:
            if tp1.GetValue() == point.GetValue().GetMidpoint():
                p1 = point
                break
            if tp2.GetValue() == point.GetValue().GetMidpoint():
                p2 = point

        if p1 is None:
            p1 = PointCtrl(self, id=-1, point=tp1)
            self._pointsctrl.append( p1 )

        if p2 is None:
            p2 = PointCtrl(self, id=-1, point=tp2)
            self._pointsctrl.append( p2 )

        label = LabelCtrl(self, id=-1, label=ann.GetLabel())
        self._labelsctrl.append( label )

        self._anns[ann] = [ label, p1, p2 ]

        # Fix properties
        label.SetAlign( self._labelalign )
        label.SetFont( self.GetFont() )
        if label.GetValue().GetSize() == 1:
            label.SetColours(self._labelbgcolor, self._textcolor)
        else:
            label.SetColours(self._labelbgcolor, self._labelfgucolor)
        p1.SetColours(colourmidpoint=self._midpointcolor,colourradius=self._labelbgcolor)
        if self._tier.IsPoint():
            p2.SetColours(colourmidpoint=self._midpointcolor,colourradius=self._labelbgcolor)

    # -----------------------------------------------------------------------

    def _addAnnotationPoint(self, ann):
        """ Create new controls for an annotation, or link to existing controls. """

        tp = ann.GetLocation().GetPoint()

        p = None

        # Is there a pointctrl at the same place?
        for point in self._pointsctrl:
            if tp.GetValue() == point.GetValue().GetMidpoint():
                p = point
                break

        if p is None:
            p = PointCtrl(self, id=-1, point=tp)
            self._pointsctrl.append( p )

        label = LabelCtrl(self, id=-1, label=ann.GetLabel())
        self._labelsctrl.append( label )

        self._anns[ann] = [ label, p, None ]

        # Fix properties
        label.SetAlign(self._labelalign)
        label.SetFont( self.GetFont() )
        if label.GetValue().GetSize() == 1:
            label.SetColours(self._labelbgcolor, self._textcolor)
        else:
            label.SetColours(self._labelbgcolor, self._labelfgucolor)

        p.SetColours(colourmidpoint=self._midpointcolor,colourradius=self._labelbgcolor)

    # -----------------------------------------------------------------------

    def _calcPointXW(self, point, tierwidth, tierheight):
        """
        tierwidth is always corresponding to the real width of the tier
        (the width of its duration, even if the sreen displays a larger width).
        """
        tiermintime,tiermaxtime = self._mintime,self._maxtime

        # adjust if required
        tierbegin = self._tier.GetBeginValue()
        tierend   = self._tier.GetEndValue()
        if self._mintime < tierend and self._maxtime > tierend:
            tiermaxtime = tierend
        if self._maxtime > tierbegin and self._mintime < tierbegin:
            tiermintime = tierbegin

        # Get information
        tierduration = tiermaxtime - tiermintime

        # Fix position and width of the point
        b = point.GetMidpoint() - point.GetRadius()
        e = point.GetMidpoint() + point.GetRadius()
        # hum.... take care:
        # b can be "before" tiermintime
        # e can be "after" tiermaxtime

        delta = max(0., b - tiermintime)
        ptbx =  delta * float(tierwidth) / tierduration
        delta = max(0., e - tiermintime)
        ptex =  delta * float(tierwidth) / tierduration

        x = int(ptbx) #round(ptbx,0)
        w = max(int(ptex-ptbx), pointctrlMinWidth)

        return x,w

    #------------------------------------------------------------------------

    def _calcW(self, tierwidth, time):
        tierduration = self._maxtime - self._mintime
        return int(time * float(tierwidth) / tierduration)

    #------------------------------------------------------------------------

    def __getTextHeight(self):
        dc = wx.ClientDC( self )
        dc.SetFont(self.GetFont())
        return dc.GetTextExtent('azertyuiopqsdfghjklmwxcvbn')[1]

    def __getTextWidth(self, text):
        dc = wx.ClientDC( self )
        dc.SetFont(self.GetFont())
        return dc.GetTextExtent(text)[0]


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------

class PointEditor( wx.Dialog ):
    """
    Show a dialog to display/change midpoint and radius.
    """

    def __init__(self, parent, middle, radius):
        wx.Dialog.__init__(self, parent, title="Point", size=(320,150), style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)

        self.middle = middle
        self.radius = radius

        fontsize = 10
        if wx.Platform == "__WXMSW__":
            fontsize = 8
        font = wx.Font(fontsize, wx.SWISS, wx.NORMAL, wx.NORMAL)

        # create the main sizer.
        gbs = wx.GridBagSizer(hgap=5, vgap=5)

        txtfrom = wx.StaticText(self, label="  MidPoint: ", size=(80, 24))
        txtfrom.SetFont( font )
        txtto   = wx.StaticText(self, label="  Radius:   ", size=(80, 24))
        txtto.SetFont( font )

        self.fieldfrom = wx.TextCtrl(self, -1, str(self.start), size=(150, 24), validator=TextAsNumericValidator())
        self.fieldfrom.SetFont(font)
        self.fieldfrom.SetInsertionPoint(0)
        self.fieldto   = wx.TextCtrl(self, -1, str(self.end),  size=(150, 24), validator=TextAsNumericValidator())
        self.fieldto.SetFont(font)
        self.fieldto.SetInsertionPoint(0)

        gbs.Add(txtfrom,       (0,0), flag=wx.ALL, border=2)
        gbs.Add(self.fieldfrom,(0,1), flag=wx.EXPAND, border=2)
        gbs.Add(txtto,         (1,0), flag=wx.ALL, border=2)
        gbs.Add(self.fieldto,  (1,1), flag=wx.EXPAND, border=2)

        # the buttons for close, and cancellation
        Buttons = wx.StdDialogButtonSizer()
        ButtonClose = wx.Button(self, wx.ID_OK)
        Buttons.AddButton(ButtonClose)
        ButtonCancel = wx.Button(self, wx.ID_CANCEL)
        Buttons.AddButton(ButtonCancel)
        Buttons.Realize()
        gbs.Add(Buttons, (2,0), (1,2), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, border=5)

        self.SetMinSize((300, 120))
        self.SetSizer( gbs )
        self.Layout()
        self.Refresh()

    #------------------------------------------------------------------------

    def GetValues(self):
        """
        Return the new midpoint/radius values.

        """
        return self.fieldfrom.GetValue(), self.fieldto.GetValue()

    #------------------------------------------------------------------------
