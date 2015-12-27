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

FONT_SIZE_MIN = 6
FONT_SIZE_MAX = 32

PANE_WIDTH  = 100

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Class TierCtrl
# ----------------------------------------------------------------------------

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
        wx.Window.__init__(self, parent, id, pos, size, STYLE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetDoubleBuffered(True)

        # Tier Members
        self._tier = tier
        self._pointsctrl = list()
        self._labelsctrl = list()
        self._anns = {} # To link the annotations to the displayed controls

        self.Reset( size )

        # Bind the events related to our control:
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)

        #spEVT_LABEL_LEFT(self, self.OnLabelEdit)
        #spEVT_POINT_LEFT(self, self.OnPointEdit)
        #spEVT_RESIZING(self,   self.OnPointResizing)
        #spEVT_RESIZED(self,    self.OnPointResized)
        #spEVT_MOVING(self,     self.OnPointMoving)
        #spEVT_MOVED(self,      self.OnPointMoved)

        # Bind the events related to our control
        #wx.EVT_MOUSE_EVENTS(self, self.OnMouseEvent)

    #-------------------------------------------------------------------------

    #-------------------------------------------------------------------------
    # Members
    #-------------------------------------------------------------------------

    def Reset(self, size):
        """
        Reset all members to their default.

        @param size (wx.Size)

        """
        self.SetMinSize(wx.Size(MIN_W,MIN_H))
        if size:
            self.SetSize(size)

        # Displayed period of time (can be taken from the Parent)
        self._mintime = 0.
        self._maxtime = 2.

        # A pane that can be placed at left or right (or nowhere).
        self._infopanep = wx.ALIGN_LEFT   # position (CENTRE means nowhere)
        try:
            self._infopanew = self.GetParent().GetPaneWidth()
        except Exception:
            self._infopanew = PANE_WIDTH # width

        self._bgcolor = self.GetParent().GetBackgroundColour()
        self._bgpen   = wx.Pen( self._bgcolor, 1, wx.SOLID )
        self._bgbrush = wx.Brush( self._bgcolor, wx.SOLID )

        self._bgdarkencolor = ContrastiveColour(self._bgcolor)
        self._bgdarkenpen   = wx.Pen( self._bgdarkencolor, 1, wx.SOLID )

        self._fgcolor = PickRandomColour(180,250)
        self._fgpen   = wx.Pen( self._fgcolor, 1, wx.SOLID )
        self._fgbrush = wx.Brush( self._fgcolor, wx.SOLID )

        self._midpointcolor = wx.BLACK

        self._textcolor = self.GetParent().GetForegroundColour()
        if self._tier is not None and self._tier.IsPoint():
            self._labelalign = wx.ALIGN_LEFT # Label in each annotation
        else:
            self._labelalign = wx.ALIGN_CENTRE # Label in each annotation
        self._labelbgcolor  = self._fgcolor
        self._labelfgucolor = None # uncertain label

        # Adjust font size when self is resized or when a new font is fixed:
        self._fontsizeauto = True
        self.AutoAdjustFont()

    #-------------------------------------------------------------------------

    def GetTier(self):
        """
        Return the tier to draw.
        """
        return self._tier

    #-------------------------------------------------------------------------

    def SetTime(self, start, end):
        """
        Define a new period to display.
        Request to redraw only if the period has changed.

        @param start (float) begin time value
        @param end (float) end time value

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

    #-------------------------------------------------------------------------

    def SetLabelAlign(self, value):
        """
        Fix the position of the text of an annotation.

        @param value is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        if self._tier.IsPoint():
            return

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
        Automatically adjust the size (compared to the previous one).

        @param font (wx.Font)

        """
        if font == self.GetFont():
            return

        # Apply this new font to self.
        wx.Window.SetFont( self,font )

        if self._fontsizeauto:
            self.AutoAdjustFont()

        # propagate to all label controls
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
            self._textcolor = colour
            self._textpen   = wx.Pen(colour,1,wx.SOLID)
            self.Refresh()

    #-------------------------------------------------------------------------

    def SetLabelColours(self, bgcolour=None, fontnormalcolour=None, fontuncertaincolour=None):
        """
        Change the main colors of the Labels.

        @param bgcolour (wx.Colour)
        @param fontcolour (wx.Colour)
        @param fontuncertaincolour (wx.Colour)

        Notice that uncertain labels are of a different color (like links in web browsers).

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
            self.Refresh()

    #-------------------------------------------------------------------------

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

    #-------------------------------------------------------------------------

    def GetLabelAlign(self):
        """
        Get the position of the text of an annotation (left/center/right).

        """
        return self._labelalign

    # -----------------------------------------------------------------------

    def GetPanePosition(self):
        """
        Return the position of the information pane.

        The position is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        return self._infopanep

    #-------------------------------------------------------------------------

    def SetPanePosition(self, value):
        """
        Fix the position of the information pane.

        @param value is one of wx.ALIGN_LEFT, wx.ALIGN_CENTRE or wx.ALIGN_RIGHT

        """
        if value not in [ wx.ALIGN_LEFT, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE ]:
            raise TypeError

        if self._infopanep != value:
            self._infopanep = value
            self.Refresh()

    #-------------------------------------------------------------------------

    def GetPaneWidth(self):
        """
        Return the width of the information pane.

        """
        return self._infopanew

    # -----------------------------------------------------------------------

    def SetPaneWidth(self, value):
        """
        Fix the width of the information pane.

        @param value (int) is between 10 and 200.

        """

        value = min(200, max(10, int(value)))
        if self._infopanew != value:
            self._infopanew = value
            self.Refresh()

    #-------------------------------------------------------------------------

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

    #-------------------------------------------------------------------------

    def VertZoom(self, z):
        """
        Apply a vertical zoom to the TierCtrl.
        """
        self.SetHeight( int(z * self.GetHeight()) )

        h = self.GetSize().height

        for point in self._pointsctrl:
            point.SetHeight( h )

        for label in self._labelsctrl:
            label.SetHeight( h )
            label.SetFont( self.GetFont() )

    # -----------------------------------------------------------------------

    def GetHeight(self):
        """
        Return the current height.

        """
        return self.GetSize()[1]

    # -----------------------------------------------------------------------

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
            if self._fontsizeauto: # and new_height>0:
                self.AutoAdjustFont()

        h = self.GetSize().height

        for point in self._pointsctrl:
            point.SetHeight( h )

        for label in self._labelsctrl:
            label.SetHeight( h )
            label.SetFont( self.GetFont() )

        #self.Refresh()
    # -----------------------------------------------------------------------

    def AutoAdjustFont(self):
        """
        Fix the biggest font size (depending on the available height).

        """

        h = self.GetDrawingSize()[1]
        if not h: return

        fontsize = FONT_SIZE_MIN
        self.GetFont().SetPointSize(fontsize)

        pxh = self.__getTextHeight()
        pxmax = int(0.6*h)
        while fontsize < FONT_SIZE_MAX and pxh<pxmax:
            fontsize = fontsize + 1
            self.GetFont().SetPointSize(fontsize)
            pxh = self.__getTextHeight()

    #-------------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnPointEdit(self, event):
        """ Point Edit. Open a dialog to edit the point values. """

        logging.info('TIER. OnPointEdit. Not implemented.')
        return
        # get point from the event
        point = event.GetEventObject()
        # show point editor
        dlg = PointEditor( self, point.GetValue(), point.GetRadius() )
        if dlg.ShowModal() == wx.ID_OK:
            (m,r) = dlg.GetValues()
            # do something with the new value (accept or reject)

        dlg.Destroy()

    # ------------------------------------------------------------------------

    def OnPointResizing(self, event):
        """ Point Resizing means a new radius value for the TimePoint. """
        logging.info('TIER. OnPointResizing. Disabled.')
        return

        # which point is resized and what are new coordinates?
        ptr = event.GetEventObject()
        (x,y) = event.pos
        (w,h) = event.size

        # self coordinates
        sx,sy = self.GetPosition()
        sw,sh = self.GetSize()

    # ------------------------------------------------------------------------

    def OnPointMoving(self, event):
        logging.info('TIER. OnPointMoving. Disabled.')
        return

        ptr = event.GetEventObject()
        (x,y) = event.pos
        (w,h) = ptr.GetSize()
        sx,sy = self.GetPosition()
        sw,sh = self.GetSize()

        self.Refresh()

    # ------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Painting
    #-------------------------------------------------------------------------

    def OnPaint(self, event):
        """
        Handles the wx.EVT_PAINT event for PointCtrl.
        """

        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    #-------------------------------------------------------------------------

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

        # Get the actual client size of ourselves
        w,h = self.GetClientSize()
        logging.debug(' Tier %s. Draw  w=%d, h=%d'%(self._tier.GetName(),w,h))

        # Nothing to do, we still don't have dimensions!
        if w*h==0: return

        # Get the actual position of ourselves
        (x,y) = self.GetDrawingPosition()

        # Initialize the DC
        if self._bgcolor is None:
            dc.SetBackgroundMode( wx.TRANSPARENT )
        else:
            dc.SetBackground( self._bgbrush )
        dc.Clear()

        try:
            # Info Pane
            if self._infopanep == wx.ALIGN_LEFT:
                self.DrawPane(dc, 0, 0, self._infopanew, h)
            elif self._infopanep == wx.ALIGN_RIGHT:
                self.DrawPane(dc, w-self._infopanew, y, self._infopanew, h)
            # Content
            if w*h > 0:
                self.DrawContent(dc, x,y, w,h)
        except Exception as e:
            logging.info(' [ERROR]. Got exception %s'%e)
            pass

    #-------------------------------------------------------------------------

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

    #-------------------------------------------------------------------------

    def DrawPane(self, dc, x,y, w,h):
        """
        Draw a pane with the tier name.

        @param dc (PaintDC, MemoryDC, BufferedDC...)
        @param x,y (int,int) are coord. of top left corner from which drawing
        @param w,h (int,int) are width and height available for drawing.

        """
        self.DrawBackground(dc, x, y, w, h)

        # Write the tier name
        textwidth, textheight = dc.GetTextExtent( self._tier.GetName() )
        # Vertical position
        y = (h - textheight)/2
        # Write text
        dc.SetBackgroundMode( wx.TRANSPARENT )
        dc.SetTextBackground( wx.NullColour )
        dc.SetFont( self.GetFont() )
        dc.SetTextForeground( self._textcolor )
        dc.DrawText(self._tier.GetName(), x+1, y)

    #-------------------------------------------------------------------------

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

        # Adjust width, if tier ends before the max
        if self._mintime < tierend and self._maxtime > tierend:
            ## reduce w (to cover until the end of the tier)
            missing = self._maxtime - tierend
            w = w - int ((missing * float(w) ) / (self._maxtime-self._mintime))

        # Adjust x if tier starts after the min
        if self._maxtime > tierbegin and self._mintime < tierbegin:
            missing = tierbegin - self._mintime
            x = x + int ((missing * float(w) ) / (self._maxtime-self._mintime))

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
                    logging.info(' Can NOT draw annotation: bad type.')
            # Show controls
            self._drawAnnotation( ann )

    #-------------------------------------------------------------------------

    def GetDrawingSize(self):
        """
        Return the size available to draw (without the pane and without margins).
        """

        # Get the actual client size of ourselves
        (w,h) = self.GetClientSize()

        # Adjust width
        if self._infopanep == wx.ALIGN_LEFT:
            w = w - self._infopanew
        elif self._infopanep == wx.ALIGN_RIGHT:
            w = w - self._infopanew

        return (max(0,w), max(0,h))

    #-------------------------------------------------------------------------

    def GetDrawingPosition(self):
        """
        Return the position to draw (without the pane).
        """

        # Get the actual position of ourselves
        (x,y) = (0,0)

        # Adjust x
        if self._infopanep == wx.ALIGN_LEFT:
            x = x + self._infopanew

        return (x,y)

    #-------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------------

    def _drawPoint(self, point, x,y,h):
        """ Display a point. """

        xpt, wpt = self._calcPointXW( point.GetValue() )

        if self._tier.IsPoint():
            point.MoveWindow(wx.Point(x+xpt,y), wx.Size(wpt,int(h*0.65)))
        else:
            point.MoveWindow(wx.Point(x+xpt,y), wx.Size(wpt,h))
        point.Show()

    # -----------------------------------------------------------------------

    def _drawAnnotation(self, ann):
        """ Display an existing annotation. """

        label  = self._anns[ann][0]
        point  = self._anns[ann][1]
        point2 = self._anns[ann][2]

        (tw,th) = self.GetDrawingSize()
        th=th-2
        (tx,ty) = self.GetDrawingPosition()
        ty=ty+1

        # Draw the label
        xpt1, wpt1 = self._calcPointXW(point.GetValue())
        if self._tier.IsPoint():
            label.MoveWindow(wx.Point(tx+xpt1+wpt1,ty), wx.Size(50,th))

        else:
            xpt2, wpt2 = self._calcPointXW(point2.GetValue())
            label.MoveWindow(wx.Point(tx+xpt1+wpt1,ty), wx.Size(xpt2-xpt1-wpt1,th))
        label.Show()

        # Draw the points
        self._drawPoint(point, tx,ty,th)
        if self._tier.IsInterval():
            self._drawPoint(point2, tx,ty,th)

    # -----------------------------------------------------------------------

    def _addAnnotationInterval(self, ann):
        """ Create new controls for an annotation, or link to existing controls. """

        tp1 = ann.GetLocation().GetBegin()
        tp2 = ann.GetLocation().GetEnd()

        p1 = None
        p2 = None

        # Is there a pointctrl at the same place?
        for point in self._pointsctrl:
            if tp1.GetValue() == point.GetValue().GetValue():
                p1 = point
                break
            if tp2.GetValue() == point.GetValue().GetValue():
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
            if tp.GetValue() == point.GetValue().GetValue():
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

    def _calcPointXW(self, point):

        # Get information
        tierwidth,tierheight = self.GetDrawingSize()
        tiermintime,tiermaxtime = self._mintime,self._maxtime
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

    #-------------------------------------------------------------------------

    def __getTextHeight(self):
        dc = wx.ClientDC( self )
        dc.SetFont(self.GetFont())
        return dc.GetTextExtent('azertyuiopqsdfghjklmwxcvbn')[1]


# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------

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

    #-------------------------------------------------------------------------

    def GetValues(self):
        """
        Return the new midpoint/radius values.
        """
        return self.fieldfrom.GetValue(), self.fieldto.GetValue()

    #-------------------------------------------------------------------------

