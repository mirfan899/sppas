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
#       Copyright (C) 2011-2016  Brigitte Bigi
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

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import logging

import wx
import wx.lib.newevent

from wxgui.cutils.colorutils import PickRandomColour, ContrastiveColour
from wxgui.cutils.textutils  import TextAsNumericValidator

from annotationctrl import AnnotationCtrl
from annotationctrl import MIN_W as annctrlMinWidth

from annotationdata.ptime.point import TimePoint

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
        self._panectrl = None
        self._dictanns = {}
        self._tier = tier

        wx.Window.__init__(self, parent, id, pos, size, STYLE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetDoubleBuffered(True)

        self.Reset( size )
        self._buildpanectrl()

        # Bind the events related to our control:
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_ERASE_BACKGROUND(self, lambda event: None)

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
        self.__initializeColours()
        if size:
            self.__initialSize(size)

        # Displayed period of time (can be taken from the Parent)
        self._mintime = 0.
        self._maxtime = 2.

        self._panepos = wx.ALIGN_LEFT
        if self._tier is not None and self._tier.IsPoint():
            self._labelalign = wx.ALIGN_LEFT
        else:
            self._labelalign = wx.ALIGN_CENTRE

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

        if torepaint is True:
            logging.debug('***** NEW TIME INTERVAL %s: %f - %f'%(self._tier.GetName(),self._mintime,self._maxtime))
            self.Refresh()

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
            for ann in self._dictanns.values():
                ann.SetLabelAlign( value )
                ann.Refresh()

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
        for ann in self._dictanns.values():
            ann.SetLabelFont( self.GetFont() )
            ann.Refresh()

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

            for ann in self._dictanns.keys():
                if ann.GetLabel().GetSize() == 1:
                    self._dictanns[ann].SetLabelColours(bgcolour,fontnormalcolour)
                else:
                    self._dictanns[ann].SetLabelColours(bgcolour,fontuncertaincolour)

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

        for annctrl in self._dictanns.values():
            annctrl.SetPointColours(self._midpointcolor, colourradius=None)

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

    def GetAnnotationWidth(self):
        """
        Return the width available to draw annotations of the tier.

        """
        return  self.GetSize().width - self.GetPaneWidth()

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
        for annctrl in self._dictanns.values():
            annctrl.SetHeight( h )

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
            for annctrl in self._dictanns.values():
                annctrl.SetLabelFont(self.GetFont())

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

        logging.debug(' Draw. %s'%self._tier.GetName())

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

        # Draw Pane and adjust position/size for the content
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

    def DrawBackground(self, dc, x,y, w,h):
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
        logging.debug(' DrawContent for tier: %s'%self._tier.GetName())
        tierbegin = self._tier.GetBeginValue()
        tierend   = self._tier.GetEndValue()

        # the period is overlapping this tier: draw partly
        if self._tier.IsPoint() is False:
            # Adjust width, if tier ends before the max
            if self._mintime < tierend and self._maxtime > tierend:
                ## reduce w (to cover until the end of the tier)
                missingtime = self._maxtime - tierend
                w = w - self._calcW(missingtime, w)

            # Adjust x if tier starts after the min
            if self._maxtime > tierbegin and self._mintime < tierbegin:
                missingtime = tierbegin - self._mintime
                x = x + self._calcW(missingtime, w)

        self.DrawBackground(dc, x,y, w,h)

        # get the list of annotations to display
        annotations = self._tier.Find(self._mintime, self._maxtime, overlaps=True)

        # from the current list of all created controls, hide the unused ones.
        for a in self._dictanns.keys():
            #if not a in annotations:
            self._dictanns[a].Hide()
            #logging.debug(' ** Hide: %s'%a.GetAnn())

        # display annotations (create if required)
        for ann in annotations:
            if not ann in self._dictanns.keys():
                annctrl = self._createAnnotationCtrl(ann, x,y, w,h)
                self._dictanns[ann] = annctrl
                logging.debug(' ** Create: %s'%ann)
            else:
                logging.debug(' ** Show: %s'%ann)
                annctrl = self._dictanns[ann]
            self._drawAnnotationCtrl(annctrl, x, y, w, h)

    #------------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _drawAnnotationCtrl(self, annctrl, xT,yT, wT,hT):
        """
        Draw an AnnotationCtrl.
        """
        ann = annctrl.GetAnn()
        # Then... draw at the right position with the right size!
        pxsec = self._calcPxSec(wT)
        time0 = self._mintime

        if self._tier.IsPoint() is False:
            time1 = ann.GetLocation().GetBegin().GetMidpoint() - ann.GetLocation().GetBegin().GetRadius()
            time2 = ann.GetLocation().GetEnd().GetMidpoint()   + ann.GetLocation().GetEnd().GetRadius()
            duration = time2 - time1
            w = round( duration * float(pxsec))
        else:
            time1 = ann.GetLocation().GetPoint().GetMidpoint() - ann.GetLocation().GetPoint().GetRadius()
            w = 50

        x = round( (time1-time0) * float(pxsec))
        if x < 0: # annotation starts before the displayed min time
            w = w+x
            x = 0
        if (x+w) > wT:
            w = w + (wT-x-w)
        annctrl.MoveWindow(pos=(x+xT,yT), size=wx.Size(w,hT))
        annctrl.SetPxSec( pxsec )
        annctrl.Show()

    #------------------------------------------------------------------------

    def _createAnnotationCtrl(self, ann, xT,yT, wT,hT):
        """ Create new controls for an annotation, or link to existing controls. """

        annctrl = AnnotationCtrl(self, id=-1, ann=ann)

        # Fix properties
        annctrl.SetLabelAlign( self._labelalign )
        annctrl.SetLabelFont( self.GetFont() )
        if ann.GetLabel().GetSize() == 1:
            annctrl.SetLabelColours(self._labelbgcolor, self._textcolor)
        else:
            annctrl.SetLabelColours(self._labelbgcolor, self._labelfgucolor)
        annctrl.SetPointColours(colourmidpoint=self._midpointcolor,colourradius=self._labelbgcolor)

        return annctrl

    #------------------------------------------------------------------------

    def _calcPxSec(self, width):
        duration = self._maxtime - self._mintime
        return int(float(width)/duration)

    def _calcW(self, time, width):
        tierduration = self._maxtime - self._mintime
        return int(time * float(width) / tierduration)

    #------------------------------------------------------------------------

    def _calcT(self, x, width):
        tierduration = self._maxtime - self._mintime
        return self._mintime + (float(x) * tierduration / float(width))

    #------------------------------------------------------------------------

    def __getTextHeight(self):
        dc = wx.ClientDC( self )
        dc.SetFont(self.GetFont())
        return dc.GetTextExtent('azertyuiopqsdfghjklmwxcvbn')[1]

    def __getTextWidth(self, text):
        dc = wx.ClientDC( self )
        dc.SetFont(self.GetFont())
        return dc.GetTextExtent(text)[0]

    #------------------------------------------------------------------------

    def __initializeColours(self):
        """ Create the pens and brush with default colors. """

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

        self._textcolor = self.GetParent().GetForegroundColour()
        self._labelbgcolor  = self._fgcolor #
        self._labelfgucolor = None          # uncertain label

    #------------------------------------------------------------------------

    def __initialSize(self, size):
        """ Initialize the size. """

        self.SetMinSize(wx.Size(MIN_W,MIN_H))
        if size:
            (w,h) = size
            if w < MIN_W: w = MIN_W
            if h < MIN_H: h = MIN_H
            self.SetSize(wx.Size(w,h))

    #------------------------------------------------------------------------

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
