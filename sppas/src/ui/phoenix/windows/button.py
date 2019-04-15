# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.ui.phoenix.windows.button.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Description
    ===========

    This module implements various forms of generic buttons, meaning that
    they are not built on native controls but are self-drawn.

    They act like normal buttons.


    Sample usage:
    ============

        import wx
        import buttons

        class appFrame(wx.Frame):
            def __init__(self, parent, title):

                wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(400, 300))
                panel = wx.Panel(self)
                btn = buttons.BaseButton(panel, -1, pos=(50, 50), size=(128, 32))

        app = wx.App()
        frame = appFrame(None, 'Button Test')
        frame.Show()
        app.MainLoop()

"""
import wx
import logging
import wx.lib.newevent

from wx.lib.buttons import GenBitmapTextButton, GenButton, GenBitmapButton

from ..tools import sppasSwissKnife
from .image import ColorizeImage

# ---------------------------------------------------------------------------

DEFAULT_STYLE = wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS

# ---------------------------------------------------------------------------


class sppasTextButton(GenButton):
    """Create a simple text button. Inherited from the wx.Button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent, label, name):
        super(sppasTextButton, self).__init__(
           parent,
           wx.ID_ANY,
           label,
           style=DEFAULT_STYLE,
           name=name)

        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

# ---------------------------------------------------------------------------


class sppasBitmapTextButton(GenBitmapTextButton):
    """Create a simple text button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Create a button with bitmap and text. A tooltip can optionally be added.

    >>> button = sppasBitmapTextButton(None, "Exit", "exit")
    >>> button.SetToolTipString("Quit the application")

    """

    def __init__(self, parent, label, name, style=DEFAULT_STYLE):
        btn_height = int(parent.GetSize()[1])
        super(sppasBitmapTextButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bmp_icon(name, height=btn_height),
            label=" "+label+" ",
            style=style,
            name=name
        )

        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to both the image and the text.

        :param colour: (wx.Colour)

        """
        current = self.GetForegroundColour()
        try:
            bmp = self.GetBitmapLabel()
            img = bmp.ConvertToImage()
            ColorizeImage(img, current, colour)
            self.SetBitmapLabel(wx.Bitmap(img))
        except:
            logging.debug('SetForegroundColour not applied to image'
                          'for button {:s}'.format(self.GetName()))

        GenBitmapTextButton.SetForegroundColour(self, colour)

# ---------------------------------------------------------------------------


class sppasBitmapButton(GenBitmapButton):
    """Create a simple bitmap button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Create a button with bitmap. A tooltip can optionally be added.

    >>> button = sppasBitmapButton(None, "exit")
    >>> button.SetToolTipString("Quit the application")

    """

    def __init__(self, parent, name, style=DEFAULT_STYLE, height=None):

        if height is None:
            height = int(parent.GetSize()[1])
        super(sppasBitmapButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bmp_icon(name, height=height),
            style=style,
            name=name
        )

        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to the image.

        :param colour: (wx.Colour)

        """
        try:
            bmp = self.GetBitmapLabel()
            img = bmp.ConvertToImage()
            current = self.GetForegroundColour()
            ColorizeImage(img, current, colour)
            self.SetBitmapLabel(wx.Bitmap(img))
        except:
            logging.debug('SetForegroundColour not applied to image'
                          'for button {:s}'.format(self.GetName()))

        GenBitmapButton.SetForegroundColour(self, colour)

# ---------------------------------------------------------------------------


class ButtonEvent(wx.PyCommandEvent):
    """Base class for an event sent when the button is activated."""

    def __init__(self, eventType, eventId):
        """Default class constructor.

        :param `eventType`: the event type;
        :param `eventId`: the event identifier.

        """
        super(ButtonEvent, self).__init__(eventType, eventId)
        self.__button = None

    # ------------------------------------------------------------------------

    def SetButtonObject(self, btn):
        """Set the event object for the event.

        :param `btn`: the button object, an instance of L{FileButton}.

        """
        self.__button = btn

    # ------------------------------------------------------------------------

    def GetButtonObject(self):
        """Return the object associated with this event."""
        return self.__button

    # ------------------------------------------------------------------------

    Button = property(GetButtonObject, SetButtonObject)


# ----------------------------------------------------------------------------


class ToggleButtonEvent(ButtonEvent):
    """Base class for an event sent when the toggle button is activated."""

    def __init__(self, eventType, eventId):
        """Default class constructor.

        :param `eventType`: the event type;
        :param `eventId`: the event identifier.

        """
        super(ToggleButtonEvent, self).__init__(eventType, eventId)
        self.__isdown = False

    # ------------------------------------------------------------------------

    def SetIsDown(self, isDown):
        """Set the button toggle status as 'down' or 'up'.

        :param `isDown`: (bool) ``True`` if the button is clicked, ``False`` otherwise.

        """
        self.__isdown = bool(isDown)

    # ------------------------------------------------------------------------

    def GetIsDown(self):
        """Return the button toggle status as ``True`` if the button is down.

        :return: (bool)

        """
        return self.__isdown


# ---------------------------------------------------------------------------


class BaseButton(wx.Window):
    """BaseButton is a custom type of window to represent a button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """
    # Button States
    NORMAL = 0
    PRESSED = 1
    HIGHLIGHT = 2

    # Button Min Size
    MIN_WIDTH = 64
    MIN_HEIGHT = 32

    # ------------------------------------------------------------------------

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param `parent`: (wx.Window) parent window. Must not be ``None``;
        :param `id`: (int) window identifier. A value of -1 indicates a default value;
        :param `pos`: the control position. A value of (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython, depending on
         platform;
        :param `size`: the control size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `name` (str): the button name.

        """
        super(BaseButton, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.CLIP_CHILDREN,
            name=name)

        # Preceding state and current one
        self._state = [BaseButton.NORMAL, BaseButton.NORMAL]

        # Border width to draw (0=no border)
        self._border = 2

        self._hasfocus = False
        
        # Setup Initial Size
        self.InheritAttributes()
        self.SetInitialSize(size)

        # Bind the events related to our control
        self.Bind(wx.EVT_PAINT, lambda evt: self.DrawButton())
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

        self.Bind(wx.EVT_SET_FOCUS, self.OnGainFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)
        self.InitOtherEvents()

    # -----------------------------------------------------------------------

    def InitOtherEvents(self):
        """Initialize other events than paint, mouse or focus.

        Override this method in a subclass to initialize any other events that
        need to be bound.  Added so :meth:`__init__` doesn't need to be
        overridden, which is complicated with multiple inheritance.

        """
        pass

    # -----------------------------------------------------------------------

    def GetDefaultAttributes(self):
        """Overridden base class virtual.

        By default we should use the same font/colour attributes as the native
        :class:`wx.Button` but we use the parent ones.

        :return: an instance of :class:`wx.VisualAttributes`.
        .. note:: Overridden from :class:`wx.Control`.

        """
        return self.GetParent().GetClassDefaultAttributes()

    # -----------------------------------------------------------------------

    def AcceptsFocusFromKeyboard(self):
        """Can this window be given focus by tab key?"""
        return True

    # -----------------------------------------------------------------------

    def AcceptsFocus(self):
        """Can this window be given focus by mouse click?"""
        return self.IsShown() and self.IsEnabled()

    # ------------------------------------------------------------------------

    def HasFocus(self):
        """Return whether or not we have the focus."""
        # We just returns the _hasfocus property that has been set in the
        # wx.EVT_SET_FOCUS and wx.EVT_KILL_FOCUS event handlers.
        return self._hasfocus

    # ------------------------------------------------------------------------

    def ShouldInheritColours(self):
        """Overridden base class virtual.

        Buttons usually don't inherit the parent's colours but we do it!

        """
        return True

    # -----------------------------------------------------------------------

    def Enable(self, enable=True):
        """Enable or disable the button.

        :param enable: ``True`` to enable the button.

        """
        if enable != self.IsEnabled():
            wx.Window.Enable(self, enable)
            self.Refresh()

    # -----------------------------------------------------------------------

    def SetBorderWidth(self, value):
        """Set the width of the border all around the button.

        :param value: (int) Border size. Not applied if not appropriate.

        """
        value = int(value)
        w, h = self.GetClientSize()
        if value < 0:
            return
        if value >= (w // 2):
            return
        if value >= (h // 2):
            return
        self._border = value

    # -----------------------------------------------------------------------

    def GetBorderWidth(self):
        """Get the width of the border all around the button.

        :return: (int)

        """
        return self._border

    # ------------------------------------------------------------------------

    def GetPenForegroundColour(self):
        """Get the foreground color for the pen.

        Pen foreground is normal if the button is enabled and state is normal,
        but this color is lightness if button is disabled and darkness if
        state is highlighted, or the contrary depending on the color.

        """
        color = self.GetForegroundColour()
        if self.IsEnabled() is True and self._state != BaseButton.HIGHLIGHT:
            return color

        r, g, b = color.Red(), color.Green(), color.Blue()
        delta = 40
        if ((r + g + b) > 384 and self.IsEnabled() is False) or \
                ((r + g + b) < 384 and self._state == BaseButton.HIGHLIGHT):
            return wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)

        return wx.Colour(r, g, b, 50).ChangeLightness(100 + delta)

    # ------------------------------------------------------------------------

    def GetHighlightedBackgroundColour(self):
        color = self.GetParent().GetBackgroundColour()
        r, g, b = color.Red(), color.Green(), color.Blue()
        delta = 20
        if (r + g + b) > 384:
            return wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a wx.SizeEvent event to be processed.

        """
        (w, h) = event.GetSize()
        if w < BaseButton.MIN_WIDTH:
            w = BaseButton.MIN_WIDTH
        if h < BaseButton.MIN_HEIGHT:
            h = BaseButton.MIN_HEIGHT
        wx.Window.SetMinSize(self, wx.Size(w, h))

        event.Skip()
        self.Refresh()

    # -----------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """Handle the wx.EVT_MOUSE_EVENTS event.

        Do not accept the event if the button is disabled.

        """
        if self.IsEnabled() is True:

            if event.Entering():
                logging.debug('  Entering event')
                self.OnMouseEnter(event)

            elif event.Leaving():
                logging.debug('  Leaving event')
                self.OnMouseLeave(event)

            elif event.LeftDown():
                logging.debug('  LeftDown event')
                self.OnMouseLeftDown(event)

            elif event.LeftUp():
                logging.debug('  LeftUp event')
                self.OnMouseLeftUp(event)

            elif event.Moving():
                # a motion event and no mouse buttons were pressed.
                self.OnMotion(event)

            elif event.Dragging():
                # motion while a button was pressed
                self.OnDragging(event)

            elif event.ButtonDClick():
                logging.debug('  DClick event')
                self.OnMouseDoubleClick(event)

            elif event.RightDown():
                logging.debug('  Right down event')
                self.OnMouseRightDown(event)

            elif event.RightUp():
                logging.debug('  Right up event')
                self.OnMouseRightUp(event)

        wx.PostEvent(self.GetParent().GetEventHandler(), event)
        event.Skip()

    # ------------------------------------------------------------------------

    def OnMouseRightDown(self, event):
        """Handle the wx.EVT_RIGHT_DOWN event.

        :param event: a wx.MouseEvent event to be processed.

        """
        event.Skip()

    # ------------------------------------------------------------------------

    def OnMouseRightUp(self, event):
        """Handle the wx.EVT_RIGHT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        event.Skip()

    # ------------------------------------------------------------------------

    def OnMouseLeftDown(self, event):
        """Handle the wx.EVT_LEFT_DOWN event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if not self.IsEnabled():
            return

        logging.debug('  ... OnMouseLeftDown: {:s} current'.format(str(self._state)))
        self._set_state(BaseButton.PRESSED)
        logging.debug('  ... OnMouseLeftDown: {:s} new set'.format(str(self._state)))
        self.CaptureMouse()
        self.SetFocus()
        self.Refresh()
        event.Skip()

    # ------------------------------------------------------------------------

    def SetFocus(self):
        """Set this button to have the focus."""
        if self._state[1] != BaseButton.PRESSED:
            self._set_state(BaseButton.HIGHLIGHT)
        super(BaseButton, self).SetFocus()

    # ------------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Handle the wx.EVT_LEFT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if not self.IsEnabled():
            return

        if not self.HasCapture():
            return

        self.ReleaseMouse()

        # If the button was down when the mouse was released...
        logging.debug('  ... OnMouseLeftUp: {:s} current'.format(str(self._state)))
        if self._state[1] == BaseButton.PRESSED:
            self.Notify()
            self._set_state(self._state[0])
            logging.debug('  ... OnMouseLeftUp: {:s} new set'.format(str(self._state)))

    # ------------------------------------------------------------------------

    def OnMotion(self, event):
        """Handle the wx.EVT_MOTION event.

        To be overriden.

        :param event: a :class:wx.MouseEvent event to be processed.

        """
        event.Skip()

    # ------------------------------------------------------------------------

    def OnDragging(self, event):
        """Handle the wx.EVT_MOTION event.

        To be overriden.

        :param event: a :class:wx.MouseEvent event to be processed.

        """
        event.Skip()

    # ------------------------------------------------------------------------

    def OnMouseEnter(self, event):
        """Handle the wx.EVT_ENTER_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        logging.debug('  ... OnMouseEnter: {:s} current'.format(str(self._state)))
        if self._state[1] == BaseButton.NORMAL:
            self._set_state(BaseButton.HIGHLIGHT)
            logging.debug('  ... OnMouseEnter: {:s} set new'.format(str(self._state)))
            self.Refresh()
            event.Skip()

    # ------------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        logging.debug('  ... OnMouseLeave: {:s} current'.format(str(self._state)))
        if self._state[1] == BaseButton.HIGHLIGHT:
            self._set_state(BaseButton.NORMAL)
            event.Skip()

        elif self._state[1] == BaseButton.PRESSED:
            self._state[0] = BaseButton.NORMAL
            logging.debug('  ... OnMouseLeave: {:s} set new'.format(str(self._state)))
            event.Skip()

    # ------------------------------------------------------------------------

    def OnGainFocus(self, event):
        """Handle the wx.EVT_SET_FOCUS event.

        :param event: a wx.FocusEvent event to be processed.

        """
        logging.debug('  ... OnGainFocus: {:s} current'.format(str(self._state)))
        if self._state[1] == BaseButton.NORMAL:
            self._set_state(BaseButton.HIGHLIGHT)
            logging.debug('  ... OnGainFocus: {:s} set new'.format(str(self._state)))
            self.Refresh()
            self.Update()

    # ------------------------------------------------------------------------

    def OnLoseFocus(self, event):
        """Handle the wx.EVT_KILL_FOCUS event.

        :param event: a wx.FocusEvent event to be processed.

        """
        logging.debug('  ... OnLoseFocus: {:s} current'.format(str(self._state)))
        if self._state[1] == BaseButton.HIGHLIGHT:
            self._set_state(self._state[0])
            logging.debug('  ... OnGainFocus: {:s} set new'.format(str(self._state)))
            self.Refresh()
            event.Skip()

    # ------------------------------------------------------------------------

    def OnKeyDown(self, event):
        """Handle the wx.EVT_KEY_DOWN event.

        :param event: a wx.KeyEvent event to be processed.

        """
        event.Skip()

    # ------------------------------------------------------------------------

    def OnKeyUp(self, event):
        """Handle the wx.EVT_KEY_UP event.

        :param event: a wx.KeyEvent event to be processed.

        """
        if event.GetKeyCode() == wx.WXK_SPACE:
            self.Notify()
            self._set_state(BaseButton.HIGHLIGHT)

        elif event.GetKeyCode() == wx.WXK_ENTER:
            self.Notify()
            self._set_state(BaseButton.PRESSED)
            wx.CallLater(100, self._set_state, BaseButton.HIGHLIGHT)

        else:
            event.Skip()

    # ------------------------------------------------------------------------

    def OnMouseDoubleClick(self, event):
        """Handle the wx.EVT_LEFT_DCLICK or wx.EVT_RIGHT_DCLICK event.

        :param event: a wx.MouseEvent event to be processed.

        """
        event.Skip()

    # ------------------------------------------------------------------------

    def OnErase(self, evt):
        """Trap the erase event to keep the background transparent on windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        pass

    # ------------------------------------------------------------------------
    # Design
    # ------------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        :param size: an instance of wx.Size.

        """
        self.SetMinSize(wx.Size(BaseButton.MIN_WIDTH, BaseButton.MIN_HEIGHT))
        if size is None:
            size = wx.DefaultSize

        (w, h) = size
        if w < BaseButton.MIN_WIDTH:
            w = BaseButton.MIN_WIDTH
        if h < BaseButton.MIN_HEIGHT:
            h = BaseButton.MIN_HEIGHT

        wx.Window.SetInitialSize(self, wx.Size(w, h))

    SetBestSize = SetInitialSize

    # ------------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_BUTTON event to the listener (if any)."""
        evt = ButtonEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetButtonObject(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    # ------------------------------------------------------------------------

    def GetBackgroundBrush(self, dc):
        """Get the brush for drawing the background of the button.

        :return: :class:`Brush`

        ..note::
            used internally when on gtk

        """
        color = self.GetParent().GetBackgroundColour()
        state = self._state[1]

        if state != BaseButton.PRESSED:
            if wx.Platform == '__WXMAC__':
                return wx.TRANSPARENT_BRUSH

            brush = wx.Brush(color, wx.SOLID)
            my_attr = self.GetDefaultAttributes()
            p_attr = self.GetParent().GetDefaultAttributes()
            my_def = color == my_attr.colBg
            p_def = self.GetParent().GetBackgroundColour() == p_attr.colBg
            if my_def and not p_def:
                color = self.GetParent().GetBackgroundColour()
                brush = wx.Brush(color, wx.SOLID)

        else:
            # this line assumes that a pressed button should be hilighted with
            # a solid colour even if the background is supposed to be transparent
            c = self.GetHighlightedBackgroundColour()
            brush = wx.Brush(c, wx.SOLID)

        return brush

    # ------------------------------------------------------------------------
    # Draw methods (private)
    # ------------------------------------------------------------------------

    def PrepareDraw(self):
        """Prepare the DC to draw the button.

        :return: (tuple) dc, gc

        """
        # Create the Graphic Context
        dc = wx.AutoBufferedPaintDCFactory(self)
        gc = wx.GCDC(dc)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()

        # In any case, the brush is transparent
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBackgroundMode(wx.TRANSPARENT)
        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            # The background needs some help to look transparent on
            # Gtk and Windows
            gc.SetBackground(self.GetBackgroundBrush(gc))
            gc.Clear()

        # Font
        gc.SetFont(self.Font)
        dc.SetFont(self.Font)

        return dc, gc

    # ------------------------------------------------------------------------

    def DrawButton(self):
        """Draw the button after the WX_EVT_PAINT event.

        """
        # Get the actual client size of ourselves
        width, height = self.GetClientSize()
        if not width or not height:
            # Nothing to do, we still don't have dimensions!
            return

        logging.debug('Draw button:')
        logging.debug('  - state: {:s}'.format(str(self._state)))
        self.Draw()

    # ------------------------------------------------------------------------

    def Draw(self):
        """Draw some parts of the button.

            1. Prepare the Drawing Context
            2. Draw the background
            3. Draw the border (if border > 0)
            4. Draw focus indicator (if state is 'HIGHLIGHT')

        :returns: dc, gc

        """
        dc, gc = self.PrepareDraw()

        self.DrawBackground(dc, gc)

        if self._border > 0:
            self.DrawBorder(dc, gc)

        if self._state[1] == BaseButton.HIGHLIGHT:
            self.DrawFocusIndicator(dc, gc)

        return dc, gc

    # ------------------------------------------------------------------------

    def DrawBorder(self, dc, gc):
        w, h = self.GetClientSize()

        pen = wx.Pen(self.GetPenForegroundColour(), self._border, wx.SOLID)
        dc.SetPen(pen)

        # draw the upper left sides
        for i in range(self._border):
            dc.DrawLine(i, 0, i, w - i)
            dc.DrawLine(0, i, w - i, i)

        # draw the lower right sides
        for i in range(self._border):
            dc.DrawLine(i, h - i - 1, w + 1, h - i - 1)
            dc.DrawLine(w - i - 1, i, w - i - 1, h)

    # ------------------------------------------------------------------------

    def DrawBackground(self, dc, gc):
        w, h = self.GetClientSize()

        brush = self.GetBackgroundBrush(dc)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(brush)
        dc.DrawRectangle(self._border,
                         self._border,
                         w - (2 * self._border),
                         h - (2 * self._border))

    # ------------------------------------------------------------------------

    def DrawFocusIndicator(self, dc, gc):
        w, h = self.GetClientSize()

        textClr = self.GetForegroundColour()
        focus_w = max(1, self._border)
        focus_pen = wx.Pen(textClr, focus_w, wx.PENSTYLE_USER_DASH)
        focus_pen.SetDashes([1, 1])
        focus_pen.SetCap(wx.CAP_BUTT)

        if wx.Platform == "__WXMAC__":
            dc.SetLogicalFunction(wx.XOR)
        else:
            focus_pen.SetColour(self.GetForegroundColour())
            dc.SetLogicalFunction(wx.INVERT)
        dc.SetPen(focus_pen)
        dc.DrawLine(self._border + 2,
                    h - self._border - focus_w - 2,
                    w - (2 * self._border) - 2,
                    h - self._border - focus_w - 2)
        # dc.SetLogicalFunction(wx.COPY)

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _set_state(self, state):
        """Manually set the state of the button.

        :param `state`: (int) one of the state values

        """
        self._state[0] = self._state[1]
        self._state[1] = state
        if wx.Platform == '__WXMSW__':
            self.GetParent().RefreshRect(self.Rect, False)
        else:
            self.Refresh()


# ----------------------------------------------------------------------------


class BaseToggleButton(BaseButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.PanelNameStr):
        """Default class constructor.

        :param parent: (wx.Window) parent window. Must not be ``None``;
        :param id: (int) window identifier. A value of -1 indicates a default value;
        :param pos: the button position. A value of (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython, depending on
         platform;
        :param size: the button size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param name: (str) the button name.

        """
        super(BaseToggleButton, self).__init__(
            parent, id, pos, size, name)

        self._pressed = False

    # ------------------------------------------------------------------------

    def IsPressed(self):
        """Return if button is pressed.

        :return: (bool)

        """
        return self._pressed

    # ------------------------------------------------------------------------

    def Check(self, value):
        if self._pressed != value:
            self._pressed = value
            if value:
                self._set_state(BaseButton.PRESSED)
            else:
                self._set_state(BaseButton.NORMAL)
            self.Refresh()

    # ------------------------------------------------------------------------
    # Override BaseButton
    # ------------------------------------------------------------------------

    def OnMouseLeftDown(self, event):
        """Handle the ``wx.EVT_LEFT_DOWN`` event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self.IsEnabled() is True:
            self._pressed = not self._pressed
            BaseButton.OnMouseLeftDown(self, event)

    # ------------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Handle the ``wx.EVT_LEFT_UP`` event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if not self.IsEnabled():
            return

        # Mouse was down outside of the button (but is up inside)
        if not self.HasCapture():
            return

        # Directs all mouse input to this window
        self.ReleaseMouse()

        # If the button was down when the mouse was released...
        logging.debug('  ... OnMouseLeftUp: {:s} current'.format(str(self._state)))
        if self._state[1] == BaseButton.PRESSED:
            self.Notify()

            if self._pressed:
                self._set_state(BaseButton.PRESSED)
            else:
                self._set_state(BaseButton.HIGHLIGHT)
            logging.debug('  ... OnMouseLeftUp: {:s} new set'.format(str(self._state)))

            # test self, in case the button was destroyed in the eventhandler
            if self:
                self.Refresh()
                event.Skip()

    # ------------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        logging.debug('  ... OnMouseLeave: {:s} current'.format(str(self._state)))
        if self._pressed is True:
            self._set_state(BaseButton.PRESSED)
            logging.debug('  ... OnMouseLeave: {:s} set new'.format(str(self._state)))
            return

        if self._state[1] == BaseButton.HIGHLIGHT:
            self._set_state(BaseButton.NORMAL)
            logging.debug('  ... OnMouseLeave: {:s} set new'.format(str(self._state)))
            self.Refresh()
            event.Skip()

        elif self._state[1] == BaseButton.PRESSED:
            self._state[0] = BaseButton.NORMAL
            logging.debug('  ... OnMouseLeave: {:s} set new'.format(str(self._state)))
            self.Refresh()
            event.Skip()

        self._pressed = False

# ----------------------------------------------------------------------------


class BitmapTextButton(BaseButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        """
        super(BitmapTextButton, self).__init__(
            parent, id, pos, size, name)

        self._label = label

    # ------------------------------------------------------------------------

    def DoGetBestSize(self):
        """Overridden base class virtual.

        Determines the best size of the button based on the label.

        """
        label = self.GetLabel()
        if not label:
            return wx.Size(32, 32)

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        retWidth, retHeight = dc.GetTextExtent(label)

        width = int(max(retWidth, retHeight) * 1.5)
        return wx.Size(width, width)

    # ------------------------------------------------------------------------

    def Draw(self):
        """Draw some parts of the button.

            1. Prepare the Drawing Context
            2. Draw the background
            3. Draw the border (if border > 0)
            4. Draw focus indicator (if state is 'HIGHLIGHT')

        :returns: dc, gc

        """
        dc, gc = self.PrepareDraw()

        self.DrawBackground(dc, gc)

        if self._border > 0:
            self.DrawBorder(dc, gc)

        if self._state[1] == BaseButton.HIGHLIGHT:
            self.DrawFocusIndicator(dc, gc)

        x, y, w, h = self.GetClientRect()
        tw, th = self.getTextExtend(dc, gc, self._label)

        # Draw horizontally
        if h < w:
            btn_height = int(0.7 * h)
            img = sppasSwissKnife.get_image(self.GetName())
            sppasSwissKnife.rescale_image(img, btn_height)
            bitmap = wx.Bitmap(img)
            if wx.Platform == '__WXGTK__':
                dc.DrawBitmap(bitmap, x + 4, (h - btn_height) // 2)
            else:
                gc.DrawBitmap(bitmap, x + 4, (h - btn_height) // 2)
            label_h = int(0.35 * h)
            self.__drawLabel(dc, gc, x + btn_height + 8, ((h * 0.9) - label_h) // 2)

        # Draw vertically (not tested)
        else:
            btn_height = int(0.6 * w)
            bitmap = sppasSwissKnife.get_bmp_icon(self.GetName(), height=btn_height)
            if wx.Platform == '__WXGTK__':
                dc.DrawBitmap(bitmap, (w - btn_height) // 2, y+2)
            else:
                gc.DrawBitmap(bitmap, (w - btn_height) // 2, y+2)

            label_h = int(0.35 * h)
            self.__drawLabel(dc, gc, (w - tw) // 2, (h - label_h) // 2)

    # ------------------------------------------------------------------------

    def DrawFocusIndicator(self, dc, gc):
        w, h = self.GetClientSize()

        textClr = self.GetForegroundColour()
        focus_w = max(1, self._border)
        focus_pen = wx.Pen(textClr, focus_w, wx.PENSTYLE_SOLID)

        if wx.Platform == "__WXMAC__":
            dc.SetLogicalFunction(wx.XOR)
        else:
            focus_pen.SetColour(self.GetForegroundColour())
            dc.SetLogicalFunction(wx.INVERT)
        dc.SetPen(focus_pen)
        dc.DrawLine(self._border + 2,
                    h - self._border - focus_w - 2,
                    w - (2 * self._border) - 2,
                    h - self._border - focus_w - 2)
        # dc.SetLogicalFunction(wx.COPY)

    # ------------------------------------------------------------------------

    @staticmethod
    def getTextExtend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # ------------------------------------------------------------------------

    def __drawLabel(self, dc, gc, x, y):
        font = self.GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        if wx.Platform == '__WXGTK__':
            dc.SetTextForeground(self.GetParent().GetForegroundColour())
            dc.DrawText(self._label, x, y)
        else:
            gc.SetTextForeground(self.GetParent().GetForegroundColour())
            gc.DrawText(self._label, x, y)

# ----------------------------------------------------------------------------


class CheckButton(BaseToggleButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name.

        """
        super(CheckButton, self).__init__(
            parent, id, pos, size, name)

        self._border = 1
        self._label = label

        # Set the spacing between the check bitmap and the label to 4 by default.
        # This can be changed using SetSpacing later.
        self._spacing = 4

    # ------------------------------------------------------------------------

    def IsChecked(self):
        """Return if button is checked.

        :return: (bool)

        """
        return self._pressed

    # ------------------------------------------------------------------------

    def SetSpacing(self, spacing):
        """Set a new spacing between the check bitmap and the text.

        :param spacing: (int) Value between 0 and 20.

        """
        spacing = int(spacing)
        if spacing < 0:
            spacing = 0
        if spacing > 20:
            spacing = 20
        # we should check if spacing < self height
        self._spacing = spacing

    # ------------------------------------------------------------------------

    def GetSpacing(self):
        """Return the spacing between the check bitmap and the text."""
        return self._spacing

    # ------------------------------------------------------------------------

    def GetDefaultAttributes(self):
        """Overridden base class virtual.

        By default we should use
        the same font/colour attributes as the native wx.CheckBox.

        """
        return wx.CheckBox.GetClassDefaultAttributes()

    # ------------------------------------------------------------------------

    def GetValue(self):
        return self._pressed

    # ------------------------------------------------------------------------

    def GetLabel(self):
        """Return the label text as it was passed to SetLabel."""
        return self._label

    # ------------------------------------------------------------------------

    def SetLabel(self, label):
        """Set the label text.

        :param label: (str) Label text.

        """
        self._label = label

    # ------------------------------------------------------------------------

    def DrawCheckImage(self, dc, gc):
        """Draw the check image.

        """
        w, h = self.GetClientSize()

        prop_size = int(min(h * 0.7, 32))
        img_size = max(16, prop_size)
        logging.debug('Image size={:d}'.format(img_size))

        box_x = self._border + 2
        box_y = (h - img_size) // 2

        # Draw square box
        c = self.GetPenForegroundColour()
        pen = wx.Pen(c, self._border, wx.SOLID)
        dc.SetPen(pen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBackgroundMode(wx.TRANSPARENT)
        dc.DrawRectangle(box_x, box_y, img_size - 1, img_size - 1)

        # Adjust image size then draw
        if self._pressed:

            img = sppasSwissKnife.get_image('check')
            sppasSwissKnife.rescale_image(img, img_size - 4)
            # ColorizeImage(img, wx.BLACK, c)

            # Draw image as bitmap
            bmp = wx.Bitmap(img)
            bmp_x = box_x + 2
            bmp_y = box_y + 2
            if wx.Platform == '__WXGTK__':
                dc.DrawBitmap(bmp, bmp_x, bmp_y)
            else:
                gc.DrawBitmap(bmp, bmp_x, bmp_y)

        return img_size

    # ------------------------------------------------------------------------

    @staticmethod
    def __getTextExtend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # ------------------------------------------------------------------------

    def __DrawLabel(self, dc, gc, x):
        w, h = self.GetClientSize()
        tw, th = self.__getTextExtend(dc, gc, self._label)
        y = ((h - th) // 2)
        if wx.Platform == '__WXGTK__':
            dc.SetTextForeground(self.GetPenForegroundColour())
            dc.DrawText(self._label, x, y)
        else:
            gc.SetTextForeground(self.GetPenForegroundColour())
            gc.DrawText(self._label, x, y)

    # ------------------------------------------------------------------------

    def DrawButton(self):
        """Draw the button.

        Override the base method.

        """
        # Get the actual client size of ourselves
        width, height = self.GetClientSize()
        if not width or not height:
            # Nothing to do, we still don't have dimensions!
            return

        dc, gc = self.Draw()
        img_size = self.DrawCheckImage(dc, gc)
        if self._label:
            self.__DrawLabel(dc, gc, img_size + self._spacing)

    # ------------------------------------------------------------------------

    def OnEraseBackground(self, event):
        """Handle the wx.EVT_ERASE_BACKGROUND event for CustomCheckBox."""

        # This is intentionally empty, because we are using the combination
        # of wx.BufferedPaintDC + an empty OnEraseBackground event to
        # reduce flicker
        pass

    # ------------------------------------------------------------------------

    def GetBackgroundBrush(self, dc):
        """Get the brush for drawing the background of the button.

        :return: :class:`Brush`

        ..note::
            used internally when on gtk

        """
        color = self.GetParent().GetBackgroundColour()
        if wx.Platform == '__WXMAC__':
            return wx.TRANSPARENT_BRUSH

        brush = wx.Brush(color, wx.SOLID)
        my_attr = self.GetDefaultAttributes()
        p_attr = self.GetParent().GetDefaultAttributes()
        my_def = color == my_attr.colBg
        p_def = self.GetParent().GetBackgroundColour() == p_attr.colBg
        if my_def and not p_def:
            color = self.GetParent().GetBackgroundColour()
            return wx.Brush(color, wx.SOLID)

        return brush

    # ------------------------------------------------------------------------

    def Notify(self):
        """Actually sends the wx.wxEVT_COMMAND_CHECKBOX_CLICKED event."""
        evt = ButtonEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED, self.GetId())
        evt.SetButtonObject(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)


# ----------------------------------------------------------------------------
# Panel to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):
    MIN_WIDTH = 240
    MIN_HEIGHT = 64

    # ------------------------------------------------------------------------

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0,
                 name=wx.PanelNameStr):
        super(TestPanel, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name="Test BaseButton")

        self.SetForegroundColour(wx.Colour(150, 160, 170))

        btn = BaseButton(self, pos=(20, 10), size=(256, 96), name="nomal")
        btn.SetBorderWidth(2)
        btn.Bind(wx.EVT_BUTTON, self.on_btn_event)

        btn_disabled = BaseButton(self, pos=(325, 10), size=(128, 96), name="disabled")
        btn_disabled.Enable(False)
        btn_disabled.Bind(wx.EVT_BUTTON, self.on_btn_event)

        btn_toggle = BaseToggleButton(self, pos=(25, 130), size=(256, 96), name="toggle")
        btn_toggle.Bind(wx.EVT_BUTTON, self.on_btn_event)

        btn_check_xs = CheckButton(self, pos=(25, 270), size=(32, 32), name="xscheck")
        btn_check_xs.Check(True)
        btn_check_xs.Bind(wx.EVT_BUTTON, self.on_btn_event)

        btn_check_s = CheckButton(self, label="disabled", pos=(100, 270), size=(128, 64), name="scheck")
        btn_check_s.Enable(False)

        btn_check_m = CheckButton(self, label='The text label', pos=(200, 300), size=(384, 128), name="mcheck")
        font = self.GetFont().MakeBold().Scale(1.4)
        btn_check_m.SetFont(font)
        btn_check_m.Bind(wx.EVT_BUTTON, self.on_btn_event)

    def on_btn_event(self, event):
        obj = event.GetEventObject()
        logging.debug('* * * PANEL: Button Event received by {:s} * * *'.format(obj.GetName()))


# ----------------------------------------------------------------------------
# App to test
# ----------------------------------------------------------------------------


class TestApp(wx.App):

    def __init__(self):
        """Create a customized application."""
        # ensure the parent's __init__ is called with the args we want
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        # create the frame
        frm = wx.Frame(None, title='Test frame', size=(640, 480))
        self.SetTopWindow(frm)

        # Fix language and translation
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)

        # create a panel in the frame
        sizer = wx.BoxSizer()
        sizer.Add(TestPanel(frm), 1, wx.EXPAND, 0)
        frm.SetSizer(sizer)

        # show result
        frm.Show()


# ---------------------------------------------------------------------------


if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()
