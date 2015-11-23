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
# File: sndplayer.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import logging
import wx.media

from wxgui.sp_images         import PLAYER_BACKGROUND

from wxgui.sp_icons          import PLAYER_INFO
from wxgui.sp_icons          import PLAYER_INFO_DISABLED
from wxgui.sp_icons          import PLAYER_EJECT
from wxgui.sp_icons          import PLAYER_EJECT_DISABLED
from wxgui.sp_icons          import PLAYER_NEXT
from wxgui.sp_icons          import PLAYER_NEXT_DISABLED
from wxgui.sp_icons          import PLAYER_REWIND
from wxgui.sp_icons          import PLAYER_REWIND_DISABLED
from wxgui.sp_icons          import PLAYER_PLAY
from wxgui.sp_icons          import PLAYER_PLAY_DISABLED
from wxgui.sp_icons          import PLAYER_REPLAY
from wxgui.sp_icons          import PLAYER_REPLAY_DISABLED
from wxgui.sp_icons          import PLAYER_PAUSE
from wxgui.sp_icons          import PLAYER_PAUSE_DISABLED
from wxgui.sp_icons          import PLAYER_STOP
from wxgui.sp_icons          import PLAYER_STOP_DISABLED

from wxgui.sp_consts         import TB_ICONSIZE

from wxgui.ui.CustomEvents import FileWanderEvent
import wxgui.ui.KnobCtrl as KC
from wxgui.structs.prefs   import Preferences
from wxgui.structs.themes  import BaseTheme

from wxgui.cutils.ctrlutils  import CreateButton
from wxgui.cutils.imageutils import spBitmap

from wxgui.dialogs.sndinfodialog import SndInfoDialog


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TIMER_STEP     = 10    # timer step event (in milliseconds)
FORWARD_STEP   = 1000  # forward step (in milliseconds)
BACKWARD_STEP  = 1000  # backward step (in milliseconds)

# ---------------------------------------------------------------------------

class SndPlayer( wx.Panel ):
    """
    Sound Player.
    """

    def __init__(self, parent, orient=wx.VERTICAL, refreshtimer=TIMER_STEP, prefsIO=None):
        """ Create a new WavProperty instance. """

        wx.Panel.__init__(self, parent)

        # members
        self._prefs = self._check_prefs(prefsIO)
        self._filename       = None
        self._mediaplayer    = None
        self._buttons        = {}
        self._showpanel      = None  # panel to show information (clock, peakmeter, signal, ...)
        self._playbackSlider = None  # slider (to change the position with the mouse)
        self._knob           = None  # volume control
        self._offsets        = (0,0) # from/to offsets

        self._autoreplay = False

        logging.debug(' ... SndPlayer Autoreplay = %s'%str(self._autoreplay))

        self.BMP_PLAYER_INFO            = spBitmap( PLAYER_INFO, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_INFO_DISABLED   = spBitmap( PLAYER_INFO_DISABLED, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_EJECT           = spBitmap( PLAYER_EJECT, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_EJECT_DISABLED  = spBitmap( PLAYER_EJECT_DISABLED, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_NEXT            = spBitmap( PLAYER_NEXT, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_NEXT_DISABLED   = spBitmap( PLAYER_NEXT_DISABLED, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_REWIND          = spBitmap( PLAYER_REWIND, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_REWIND_DISABLED = spBitmap( PLAYER_REWIND_DISABLED, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_PLAY            = spBitmap( PLAYER_PLAY, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_PLAY_DISABLED   = spBitmap( PLAYER_PLAY_DISABLED, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_REPLAY          = spBitmap( PLAYER_REPLAY, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_REPLAY_DISABLED = spBitmap( PLAYER_REPLAY_DISABLED, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_PAUSE           = spBitmap( PLAYER_PAUSE, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_PAUSE_DISABLED  = spBitmap( PLAYER_PAUSE_DISABLED, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_STOP            = spBitmap( PLAYER_STOP, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )
        self.BMP_PLAYER_STOP_DISABLED   = spBitmap( PLAYER_STOP_DISABLED, TB_ICONSIZE, theme=self._prefs.GetValue('M_ICON_THEME') )

        # create the audio bar
        if orient == wx.VERTICAL:
            sizer = self._build_audioadvanced()
        else:
            sizer = self._build_audiosimple()

        # events
        self.Bind(wx.EVT_SLIDER, self.onSeek)

        # timer, used to update the playing state
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self._refreshTimer = refreshtimer

        self.SetBackgroundColour( self._prefs.GetValue("M_BG_COLOUR") )
        self.SetForegroundColour( self._prefs.GetValue("M_FG_COLOUR") )
        self.SetFont( self._prefs.GetValue("M_FONT") )

        self.SetSizer( sizer )
        self.SetAutoLayout( True )
        self.Layout()

    # End __init__
    # -----------------------------------------------------------------------


    def _build_showpanel(self, wave):
        """ Build or change the show panel. """

        # a showpanel is already existing
        if self._showpanel is not None:
            self._showpanel.Destroy()

        # no wav: show a nice picture
        if wave is None:
            self._showpanel = wx.Panel(self, size=(320,120))
            img  = wx.Image(PLAYER_BACKGROUND, wx.BITMAP_TYPE_ANY)
            img2 = wx.StaticBitmap(self._showpanel, wx.ID_ANY, wx.BitmapFromImage(img))
        else:
            # a wave is given:
            # show dynamic information while playing (clock, peakmeter, ...)
            # TO DO
            self._showpanel = wx.Panel(self, size=(320,120))
            img  = wx.Image(PLAYER_BACKGROUND, wx.BITMAP_TYPE_ANY)
            img2 = wx.StaticBitmap(self._showpanel, wx.ID_ANY, wx.BitmapFromImage(img))


    def _build_audioadvanced(self):
        """ Build the audio controls. """

        # create the main sizer.
        sizer = wx.GridBagSizer(4, 4)
        bgcolour = self._prefs.GetValue('M_BG_COLOUR')

        # 1st column
        self._buttons['eject']    = CreateButton(self, self.BMP_PLAYER_EJECT_DISABLED, self.onEject,  sizer, colour=bgcolour)
        self._buttons['next']     = CreateButton(self, self.BMP_PLAYER_NEXT_DISABLED,  self.onNext,   sizer, colour=bgcolour)
        self._buttons['previous'] = CreateButton(self, self.BMP_PLAYER_REWIND_DISABLED,self.onRewind, sizer, colour=bgcolour)

        # 2nd column
        self._build_showpanel( None )

        # 3rd column
        self._buttons['play']  = CreateButton(self, self.BMP_PLAYER_PLAY_DISABLED,  self.onNormalPlay,  sizer, colour=bgcolour)
        self._buttons['stop']  = CreateButton(self, self.BMP_PLAYER_STOP_DISABLED,  self.onStop,  sizer, colour=bgcolour)
        self._buttons['pause'] = CreateButton(self, self.BMP_PLAYER_PAUSE_DISABLED, self.onPause, sizer, colour=bgcolour)

        # 4th column
        minvalue = 0
        maxvalue = 101
        therange = 5
        self._knob = KC.KnobCtrl(self, -1, size=(80, 80))
        self._knob.SetTags(range(minvalue, maxvalue+1, therange))
        self._knob.SetAngularRange(-45, 225)
        self._knob.SetValue( int((minvalue+maxvalue+1)/2) )
        tickrange = range(minvalue, maxvalue+1, therange)
        self._knob.SetTags(tickrange)
        self.Bind(KC.KC_EVENT_ANGLE_CHANGED, self.onAngleChanged, self._knob)
        self._knobtracker = wx.StaticText(self, -1, "Volume = %d" % int((minvalue+maxvalue)/2))

        # sizer
        sizer.Add(self._buttons['eject'],   (0,0), flag=wx.ALL, border=4)
        sizer.Add(self._buttons['next'],    (1,0), flag=wx.ALL, border=4)
        sizer.Add(self._buttons['previous'],(2,0), flag=wx.ALL, border=4)
        sizer.Add(self._showpanel, (0,1),(3,1),    flag=wx.EXPAND|wx.ALL, border=4)
        sizer.Add(self._buttons['play'],  (0,2), flag=wx.ALL, border=4)
        sizer.Add(self._buttons['stop'],  (1,2), flag=wx.ALL, border=4)
        sizer.Add(self._buttons['pause'], (2,2), flag=wx.ALL, border=4)
        sizer.Add(self._knob, (0,3), (2,1),  flag=wx.EXPAND|wx.TOP, border=4)
        sizer.Add(self._knobtracker, (2,3), flag=wx.TOP, border=4)

        # create playback slider
        self._playbackSlider = wx.Slider(self, wx.ID_ANY, size=wx.DefaultSize, style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS)
        sizer.Add(self._playbackSlider, (3,0), (1,4), wx.ALL|wx.EXPAND, border=4)

        return sizer

    #----------------------------------------------------------------------

    def __create_audio_button(self, name, preftag, bmp, method, sizer):
        try:
            info = self._prefs.GetValue(preftag)
        except Exception:
            info = False
        else:
            if info is True:
                self._buttons[name] = CreateButton(self, bmp, method, sizer)
                sizer.Add(self._buttons[name], 1, flag=wx.ALL, border=2)


    def _build_audiosimple(self):
        """ Build the audio controls. """

        self._showpanel      = None
        self._playbackSlider = None
        self._knob           = None
        self._knobtracker    = None

        # create the main sizer.
        sizer = wx.BoxSizer( wx.HORIZONTAL )

        # create the audio bar
        self.__create_audio_button('info',   'SND_INFO',   self.BMP_PLAYER_INFO_DISABLED, self.onInfo, sizer)
        self.__create_audio_button('play',   'SND_PLAY',   self.BMP_PLAYER_PLAY_DISABLED, self.onNormalPlay, sizer)
        self.__create_audio_button('replay', 'SND_AUTOREPLAY', self.BMP_PLAYER_REPLAY_DISABLED, self.onAutoPlay, sizer)
        self.__create_audio_button('pause',  'SND_PAUSE',  self.BMP_PLAYER_PAUSE_DISABLED, self.onPause, sizer)
        self.__create_audio_button('stop',   'SND_STOP',   self.BMP_PLAYER_STOP_DISABLED, self.onStop, sizer)
        self.__create_audio_button('next',   'SND_NEXT',   self.BMP_PLAYER_NEXT_DISABLED, self.onNext, sizer)
        self.__create_audio_button('rewind', 'SND_REWIND', self.BMP_PLAYER_REWIND_DISABLED, self.onRewind, sizer)

        return sizer

    # End _build_audiosimple
    #-------------------------------------------------------------------------


    def _check_prefs(self, prefs):
        """
        Check if preferences are set properly. Set new ones if required.
        Return the new version.
        """
        if prefs is None:
            prefs = Preferences( BaseTheme() )

        else:
            try:
                bg = prefs.GetValue( 'M_BG_COLOUR' )
                fg = prefs.GetValue( 'M_FG_COLOUR' )
                font = prefs.GetValue( 'M_FONT' )
                icons = prefs.GetValue( 'M_ICON_THEME' )
            except Exception:
                self._prefsIO.SetTheme( BaseTheme() )
        return prefs

    #-------------------------------------------------------------------------



    #----------------------------------------------------------------------
    # Methods
    #----------------------------------------------------------------------


    def FileSelected(self, filename):
        """
        Set a sound file.
        """
        logging.debug(' ... sndplayer file selected ...')
        # do not assign the same file!!!
        if filename == self._filename and self._mediaplayer is not None:
            logging.debug(' same file name/ Return!!!')
            return

        try:
            m = wx.media.MediaCtrl(self, style=wx.NO_BORDER)
            m.Load( filename )
            self._length = m.Length()
            if self._length == 0: # **** BUG of the MediaPlayer! ****
                import wave
                w = wave.Wave_read(filename)
                self._length = int( 1000 * float(w.getnframes())/float(w.getframerate()) )
        except Exception as e:
            logging.info(" ... Error loading: %s" % filename)
            wx.MessageBox('Error loading: '+filename+' '+str(e), 'Info', wx.OK | wx.ICON_INFORMATION)
            return False

        # set mediaplayer with the new one
        self._filename = filename
        self._mediaplayer = m

        #self._mediaplayer.SetInitialSize()
        self.ActivateButtons(True)
        self._offsets = (0,self._length)
        if self._playbackSlider is not None:
            self._playbackSlider.SetRange(0, self._length)
            self._playbackSlider.SetTickFreq(int(self._length/10), 1)

        self._timer.Start( self._refreshTimer )

        self.Refresh()

    # End FileSelected
    #------------------------------------------------------------------------


    def FileDeSelected(self):
        """
        Reset information.
        """
        # take care... the current mediaplayer can be playing. Unset properly!!
        if self._mediaplayer is not None and self._mediaplayer.GetState() != wx.media.MEDIASTATE_STOPPED :
            self.onStop(None)

        if self._showpanel is not None:
            self._build_showpanel( None )
        if self._mediaplayer is not None:
            self._mediaplayer.Destroy()

        self._filename    = None
        self._mediaplayer = None
        self._offsets = (0,0)
        if self._playbackSlider is not None:
            self._playbackSlider.SetRange(0, 0)

        self.ActivateButtons(False)
        self.EnableButtons(False)

        self._timer.Stop()

        self.Layout()
        self.Refresh()

    # End FileDeSelected
    # -----------------------------------------------------------------------


    def SetOffsetPeriod(self, start, end):
        """
        Fix a start position and a end position to play the sound.
        """
        if self._mediaplayer is not None and self._mediaplayer.GetState() == wx.media.MEDIASTATE_PLAYING:
            self.onStop(None)

        if self._mediaplayer is not None and end > self._length:
            end = self._length

        self._offsets = (start,end)
        if self._playbackSlider is not None:
            self._playbackSlider.SetRange(start,end)

    # End SetOffsetPeriod
    #----------------------------------------------------------------------


    #----------------------------------------------------------------------
    # Callbacks
    #----------------------------------------------------------------------


    def onInfo(self, event):
        """ Display information about the selected Wave. """

        if self._mediaplayer is None:
            return
        pass
        try:
            dlg = SndInfoDialog( self, self._prefs, self._filename )
        except Exception as e:
            wx.MessageBox('No information available. %s'%str(e), 'Info', wx.OK | wx.ICON_INFORMATION)

    # End onInfo
    #-------------------------------------------------------------------------


    def onSeek(self,event):
        """ Seeks the media file according to the amount the slider has been adjusted. """

        if self._mediaplayer is None:
            return

        if self._playbackSlider is not None:
            offset = self._playbackSlider.GetValue()
        else:
            offset = self._offsets[0]

        self._mediaplayer.Seek( offset, mode=wx.FromStart )

    # End onSeek
    #----------------------------------------------------------------------


    def onEject(self, event):
        """ Eject the music. """

        if self._mediaplayer is None:
            return

        evt = FileWanderEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

        #self.FileDeSelected()

    # End onEject
    #----------------------------------------------------------------------


    def onNext(self, event):
        """ Go forward in the music. """

        if self._mediaplayer is None:
            return

        offset = self._mediaplayer.Tell()
        forward = offset + FORWARD_STEP
        (omin,omax) = self._offsets
        if forward > omax:
            forward = omin # come back at the beginning!

        if self._playbackSlider is not None:
            self._playbackSlider.SetValue( forward )

        self._mediaplayer.Seek( forward, mode=wx.FromStart )

    # End onNext
    #----------------------------------------------------------------------


    def onRewind(self, event):
        """ Go backward in the music. """

        if self._mediaplayer is None:
            return

        offset = self._mediaplayer.Tell()
        backward = offset - BACKWARD_STEP
        (omin,omax) = self._offsets
        if backward < omin:
            backward = omax # loop

        if self._playbackSlider is not None:
            self._playbackSlider.SetValue( backward )

        self._mediaplayer.Seek( backward, mode=wx.FromStart )

    # End onRewind
    #----------------------------------------------------------------------


    def onPause(self, event):
        """ Pauses the music. """

        if self._mediaplayer is None:
            return

        logging.debug(' PAUSE EVENT RECEIVED ')

        state = self._mediaplayer.GetState()

        if state == wx.media.MEDIASTATE_PLAYING:
            self._mediaplayer.Pause()
            self._buttons['pause'].SetBitmapLabel( self.BMP_PLAYER_PAUSE_DISABLED )

        elif state == wx.media.MEDIASTATE_PAUSED:
            self.onPlay(event)
            self._buttons['play'].SetBitmapLabel( self.BMP_PLAYER_PLAY )
            self._buttons['pause'].SetBitmapLabel( self.BMP_PLAYER_PAUSE )

    # End onPause
    #----------------------------------------------------------------------


    def onAutoPlay(self, event):
        """ Plays the music and re-play from the beginning. """

        self._autoreplay = True
        self.onPlay(event)

    # End onAutoPlay
    #----------------------------------------------------------------------

    def onNormalPlay(self, event):
        """ Plays the music once. """

        self._autoreplay = False
        self.onPlay(event)

    # End onNormalPlay
    #----------------------------------------------------------------------


    def onPlay(self, event):
        """ Plays the music. """

        if self._mediaplayer is None:
            logging.debug('onPlay. Unable to play: No media player.')
            return
        if self._mediaplayer.GetState() == wx.media.MEDIASTATE_PLAYING:
            logging.debug('onPlay. Unable to play: already playing!')
            return

        # save current position
        offset = self._mediaplayer.Tell()
        omin,omax = self._offsets
        if self._playbackSlider is not None:
            offset = self._playbackSlider.GetValue()
        elif (offset < omin or offset > omax):
            offset = omin

        if not self._mediaplayer.Play():
            logging.debug('onPlay. Unable to play. offset=%d'%offset)
            wx.MessageBox("Unable to Play. Offset=%d"%offset,
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
            return

        # force to play at the good position
        self._mediaplayer.Seek( offset, mode=wx.FromStart ) # required!

        if self._knob is not None:
            self._mediaplayer.SetVolume( float(self._knob.GetValue())/100.0 )

        self._buttons['play'].SetBitmapLabel( self.BMP_PLAYER_PLAY )
        self._buttons['pause'].SetBitmapLabel( self.BMP_PLAYER_PAUSE )

        self.Refresh()

    # End onPlay
    #----------------------------------------------------------------------


    def onStop(self, event):
        """ Stops the music and resets the play button. """

        if self._mediaplayer is None:
            return

        try:
            self._mediaplayer.Stop()
            s,e = self._offsets
            self._mediaplayer.Seek( s )
            if self._playbackSlider is not None:
                self._playbackSlider.SetValue( s )
        except Exception:
            # provide errors like:"ressource temporairement indisponible"
            pass

        self._buttons['play'].SetBitmapLabel( self.BMP_PLAYER_PLAY )
        self._buttons['pause'].SetBitmapLabel( self.BMP_PLAYER_PAUSE )
        self._autoreplay = False

    # End onStop
    #----------------------------------------------------------------------


    def onAngleChanged(self, event):
        """ Change the volume value. """

        value = event.GetValue()
        self._knobtracker.SetLabel("Volume = " + str(value))
        if self._mediaplayer:
            self._mediaplayer.SetVolume( float(value)/100.0 )

    # End onAngleChanged
    #----------------------------------------------------------------------


    def onTimer(self, event):
        """ Keeps the player slider updated. """

        if self._mediaplayer is None:
            return

        offset = self._mediaplayer.Tell()
        # On MacOS, it seems that offset is not so precise we could expect...
        # It can be + or - 3 compared to the expected value!

        if self._mediaplayer.GetState() == wx.media.MEDIASTATE_PLAYING and self._playbackSlider is not None:
            self._playbackSlider.SetValue( offset )

        omin,omax = self._offsets
        if self._mediaplayer.GetState() == wx.media.MEDIASTATE_PLAYING and (offset < omin-3 or offset > omax+3):
            if self._autoreplay is True:
                self.onStop(event)
                self.onAutoPlay(event)
            else:
                self.onStop(event)

    # End onTimer
    #----------------------------------------------------------------------


    def onClose(self, event):
        """
        Close (destructor).
        """
        self._timer.Stop()
        self.Destroy()

    # End Close
    # ------------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # GUI
    # -----------------------------------------------------------------------


    def SetPreferences(self, prefs):
        """ Set new preferences. """

        self._prefs = prefs
        self.SetBackgroundColour( self._prefs.GetValue("M_BG_COLOUR") )
        self.SetForegroundColour( self._prefs.GetValue("M_FG_COLOUR") )
        self.SetFont( self._prefs.GetValue("M_FONT") )
        # apply bg on all buttons...
        for b in self._buttons.keys():
            self._buttons[b].SetBackgroundColour( self._prefs.GetValue("M_BG_COLOUR") )

    #-------------------------------------------------------------------------


    def SetFont(self, font):
        """ Change font of all texts. """

        wx.Window.SetFont( self,font )
        if self._knobtracker is not None:
            self._knobtracker.SetFont( font )

    # End SetFont
    # -----------------------------------------------------------------------


    def SetBackgroundColour(self, colour):
        """ Change the background color of all objects. """

        wx.Window.SetBackgroundColour( self,colour )

        for b in self._buttons:
            self._buttons[b].SetBackgroundColour( colour )

        if self._showpanel is not None:
            self._showpanel.SetBackgroundColour( colour )
        if self._knobtracker is not None:
            self._knobtracker.SetBackgroundColour( colour )
        if self._playbackSlider is not None:
            self._playbackSlider.SetBackgroundColour( colour )

        self.Refresh()

    # End SetForegroundColour
    # -----------------------------------------------------------------------


    def SetForegroundColour(self, colour):
        """ Change the foreground color of all objects. """

        wx.Window.SetForegroundColour( self,colour )

        for b in self._buttons:
            self._buttons[b].SetForegroundColour( colour )

        if self._showpanel is not None:
            self._showpanel.SetForegroundColour( colour )
        if self._knobtracker is not None:
            self._knobtracker.SetForegroundColour( colour )
        if self._playbackSlider is not None:
            self._playbackSlider.SetForegroundColour( colour )

        self.Refresh()

    # End SetForegroundColour
    # -----------------------------------------------------------------------


    # ------------------------------------------------------------------------

    def ActivateButtons(self, value=True):
        self.EnableButtons(False)
        if value is True:
            self._buttons['play'].SetBitmapLabel(  self.BMP_PLAYER_PLAY )
            self._buttons['pause'].SetBitmapLabel( self.BMP_PLAYER_PAUSE )
            try:
                self._buttons['eject'].SetBitmapLabel( self.BMP_PLAYER_EJECT )
            except Exception:
                pass
            try:
                self._buttons['info'].SetBitmapLabel( self.BMP_PLAYER_INFO )
            except Exception:
                pass
            try:
                self._buttons['next'].SetBitmapLabel( self.BMP_PLAYER_NEXT )
                self._buttons['previous'].SetBitmapLabel( self.BMP_PLAYER_REWIND )
            except Exception:
                pass
            try:
                self._buttons['stop'].SetBitmapLabel(  self.BMP_PLAYER_STOP )
            except Exception:
                pass
            try:
                self._buttons['replay'].SetBitmapLabel(  self.BMP_PLAYER_REPLAY )
            except Exception:
                pass

        else:
            self._buttons['play'].SetBitmapLabel(  self.BMP_PLAYER_PLAY_DISABLED )
            self._buttons['pause'].SetBitmapLabel( self.BMP_PLAYER_PAUSE_DISABLED )
            try:
                self._buttons['eject'].SetBitmapLabel( self.BMP_PLAYER_EJECT_DISABLED )
            except Exception:
                pass
            try:
                self._buttons['info'].SetBitmapLabel( self.BMP_PLAYER_INFO_DISABLED )
            except Exception:
                pass
            try:
                self._buttons['stop'].SetBitmapLabel(  self.BMP_PLAYER_STOP_DISABLED )
            except Exception:
                pass
            try:
                self._buttons['previous'].SetBitmapLabel( self.BMP_PLAYER_REWIND_DISABLED )
                self._buttons['next'].SetBitmapLabel(  self.BMP_PLAYER_NEXT_DISABLED )
            except Exception:
                pass
            try:
                self._buttons['replay'].SetBitmapLabel( self.BMP_PLAYER_REPLAY_DISABLED )
            except Exception:
                pass


    def EnableButtons(self, value=True):
        for b in self._buttons:
            self._buttons[b].Enable( not value )

# ----------------------------------------------------------------------------
