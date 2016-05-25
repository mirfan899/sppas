#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
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
# ---------------------------------------------------------------------------
# File: sndroamerclient.py
# ----------------------------------------------------------------------------
import os
import datetime
import codecs
import wx
import wx.lib.scrolledpanel as scrolled

from wxgui.ui.CustomEvents  import NotebookClosePageEvent
from wxgui.ui.CustomEvents  import FileWanderEvent, spEVT_FILE_WANDER
from wxgui.ui.CustomEvents  import spEVT_SETTINGS

from baseclient              import BaseClient
from wxgui.panels.sndplayer  import SndPlayer
from wxgui.panels.audioinfo  import AudioInfo
from wxgui.structs.prefs     import Preferences
from wxgui.structs.themes    import BaseTheme

from wxgui.cutils.imageutils import spBitmap
from wxgui.cutils.ctrlutils  import CreateGenButton
from wxgui.cutils.textutils   import TextAsNumericValidator

from wxgui.sp_icons  import SNDROAMER_APP_ICON
from wxgui.sp_icons  import SAVE_FILE
from wxgui.sp_icons  import SAVE_AS_FILE

from wxgui.sp_consts import INFO_COLOUR
from wxgui.sp_consts import MIN_PANEL_W
from wxgui.sp_consts import MIN_PANEL_H
from wxgui.sp_consts import BUTTON_ICONSIZE

from wxgui.dialogs.filedialogs import SaveAsAudioFile, SaveAsAnyFile
from wxgui.dialogs.msgdialogs import ShowInformation
from wxgui.dialogs.basedialog import spBaseDialog

import audiodata.io
from audiodata.channelsilence   import ChannelSilence
from audiodata.channelformatter import ChannelFormatter
from audiodata.audioframes      import AudioFrames
from audiodata.audio            import AudioPCM

from sp_glob import program, version, copyright, url, author, contact
from sp_glob import encoding

# ----------------------------------------------------------------------------

ID_DIALOG_AUDIOROAMER  = wx.NewId()

# ----------------------------------------------------------------------------
# Main class that manage the notebook
# ----------------------------------------------------------------------------

class SndRoamerClient( BaseClient ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Manage the opened files in a notebook.

    This class manages the pages of a notebook with all opened files.
    Each page (except if empty...) contains an instance of a SndRoamer.

    """
    def __init__( self, parent, prefsIO ):
        BaseClient.__init__( self, parent, prefsIO )

    def CreateComponent(self, parent, prefsIO ):
        return SndRoamer(parent, prefsIO)


# ----------------------------------------------------------------------------
# The Component is the content of one page of the notebook.
# ----------------------------------------------------------------------------

class SndRoamer( scrolled.ScrolledPanel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Manage audio files.

    Panel to manage audio files:
        - show information,
        - manage the content of the audio,
        - play.

    """
    def __init__(self, parent, prefsIO):
        """
        SndRoamer Component ScrolledPanel.

        """
        scrolled.ScrolledPanel.__init__(self, parent, -1)

        # members
        self._prefsIO  = self._check_prefs(prefsIO)
        self._filename = None

        # GUI
        sizer = self._create_content()

        # Bind events
        self.Bind(spEVT_FILE_WANDER, self.OnFileWander)
        self.Bind(spEVT_SETTINGS,    self.OnSettings)

        self.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR'))
        self.SetSizer(sizer)
        self.SetAutoLayout( True )
        self.Layout()
        self.SetupScrolling()

    # ----------------------------------------------------------------------

    def _create_content(self):
        """
        GUI design.

        """
        sizer = wx.BoxSizer( wx.VERTICAL )
        # create the panels
        self._propertyPanel = AudioInfo(self, self._prefsIO)
        self._managerPanel  = AudioRoamer(self, self._prefsIO)
        self._playerPanel   = SndPlayer(self, prefsIO=self._prefsIO)

        sizer.Add(self._managerPanel,  proportion=0, flag=wx.CENTRE|wx.ALL, border=2 )
        sizer.Add(self._propertyPanel, proportion=0, flag=wx.LEFT|wx.EXPAND|wx.ALL, border=2 )
        sizer.Add(self._playerPanel,   proportion=1, flag=wx.CENTRE|wx.ALL, border=2 )
        return sizer

    # ----------------------------------------------------------------------

    def _check_prefs(self, prefs):
        """
        Check if preferences are set properly. Set new ones if required.
        Return the new version.

        """
        if prefs is None:
            prefs = Preferences( BaseTheme() )
        else:
            try:
                prefs.GetValue( 'M_BG_COLOUR' )
                prefs.GetValue( 'M_FG_COLOUR' )
                prefs.GetValue( 'M_FONT' )
                prefs.GetValue( 'M_ICON_THEME' )
            except Exception:
                self._prefsIO.SetTheme( BaseTheme() )
                prefs = self._prefsIO

        prefs.SetValue('SND_INFO',       'bool', False)
        prefs.SetValue('SND_PLAY',       'bool', True)
        prefs.SetValue('SND_AUTOREPLAY', 'bool', False)
        prefs.SetValue('SND_PAUSE',      'bool', True)
        prefs.SetValue('SND_STOP',       'bool', True)
        prefs.SetValue('SND_NEXT',       'bool', True)
        prefs.SetValue('SND_REWIND',     'bool', True)
        prefs.SetValue('SND_EJECT',      'bool', True)

        return prefs

    # ----------------------------------------------------------------------
    # GUI
    # ----------------------------------------------------------------------

    def OnSettings(self, event):
        """
        Set new preferences, then apply them.

        """
        self._prefsIO = self._check_prefs( event.prefsIO )

        # Apply the changes on self
        self.SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ) )
        self.SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ) )
        self.SetFont( self._prefsIO.GetValue( 'M_FONT' ) )

        self.Layout()
        self.Refresh()

    # ----------------------------------------------------------------------

    def SetFont(self, font):
        """
        Change font of all wx texts.

        """
        wx.Window.SetFont( self, font )
        self._propertyPanel.SetFont( font )
        self._playerPanel.SetFont( font )

    # ----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """
        Change background of all texts.

        """
        wx.Window.SetBackgroundColour( self, color )
        self._propertyPanel.SetBackgroundColour( color )
        self._playerPanel.SetBackgroundColour( color )

    # ----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """
        Change foreground of all texts.

        """
        wx.Window.SetForegroundColour( self, color )
        self._propertyPanel.SetForegroundColour( color )
        self._playerPanel.SetForegroundColour( color )


    # ----------------------------------------------------------------------
    # Callbacks
    # ----------------------------------------------------------------------

    def OnFileWander(self, event):
        """
        A file was checked/unchecked/ejected somewhere else.

        """
        o = event.GetEventObject()
        if o == self._playerPanel:
            evt = NotebookClosePageEvent()
            evt.SetEventObject(self)
            wx.PostEvent( self.GetParent().GetParent().GetParent(),evt )
            self._propertyPanel.FileDeSelected()
            return

        f = event.filename
        s = event.status

        if s is True:
            self._propertyPanel.FileSelected( f )
            self._playerPanel.FileSelected( f )
            self._managerPanel.FileSelected( f )
            self._filename = f
        else:
            self._propertyPanel.FileDeSelected()
            self._playerPanel.FileDeSelected()
            self._managerPanel.FileDeSelected( f )
            evt = FileWanderEvent(filename=self._filename, status=False)
            evt.SetEventObject(self)
            wx.PostEvent( self.GetParent().GetParent().GetParent(), evt )
            self._filename = None

# ----------------------------------------------------------------------------

class AudioRoamer( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Propose to manage the content of an audio file.

    """
    def __init__(self, parent, preferences):
        """
        Create a new AudioRoamer instance.

        @parent (wxWindow)

        """
        wx.Panel.__init__(self, parent)
        self._prefs = preferences
        self._filename = None

        sizer = wx.BoxSizer( wx.HORIZONTAL )
        FONT = self._prefs.GetValue('M_FONT')
        bmproamer = spBitmap(SNDROAMER_APP_ICON, theme=self._prefs.GetValue('M_ICON_THEME'))
        self.roamerButton = CreateGenButton(self, ID_DIALOG_AUDIOROAMER, bmproamer, text="Want more?", tooltip="Show more information, manage channels, framerate, etc.", colour=wx.Colour(220,120,180), SIZE=BUTTON_ICONSIZE, font=FONT)
        self.Bind(wx.EVT_BUTTON, self.OnAudioRoamer,  self.roamerButton, ID_DIALOG_AUDIOROAMER)

        sizer.Add( self.roamerButton )

        self.SetSizer(sizer)
        self.SetAutoLayout( True )
        self.Layout()


    def FileSelected(self, filename ):
        self._filename = filename
        self.roamerButton.Enable(True)

    def FileDeSelected(self, filename ):
        self._filename = None
        self.roamerButton.Enable(False)

    def OnAudioRoamer(self, event):
        if self._filename is not None:
            ShowAudioRoamerDialog(self, self._prefs, self._filename)

# ----------------------------------------------------------------------------

class AudioRoamerDialog( spBaseDialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Frame allowing to show details of a tier.

    """
    def __init__(self, parent, preferences, filename):
        """
        Constructor.

        @param parent is a wx.Window or wx.Frame or wx.Dialog
        @param preferences (Preferences or Preferences_IO)
        @param filename

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - AudioRoamer")
        wx.GetApp().SetAppName( "audio" )
        self._filename = filename

        titlebox   = self.CreateTitle(SNDROAMER_APP_ICON,"Audio Data Manager")
        contentbox = self._create_content()
        buttonbox  = self._create_buttons()

        self.LayoutComponents( titlebox,
                               contentbox,
                               buttonbox )

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_close = self.CreateCloseButton()
        btn_save_channel  = self.CreateButton(SAVE_FILE, "Save this channel as...", "Save the channel in an audio file.", btnid=wx.ID_SAVE)
        btn_save_channel.Bind(wx.EVT_BUTTON, self._on_save_channel)
        btn_save_info = self.CreateButton(SAVE_AS_FILE, "Save these information as...", "Save the displayed information in a text file.", btnid=wx.ID_SAVE)
        btn_save_info.Bind(wx.EVT_BUTTON, self._on_save_info)
        return self.CreateButtonBox( [btn_save_channel,btn_save_info],[btn_close] )

    def _create_content(self):
        audio = audiodata.io.open(self._filename)
        nchannels = audio.get_nchannels()
        audio.extract_channels()

        self.notebook = wx.Notebook(self)
        self.pages = []
        for i in range(nchannels):
            page = AudioRoamerPanel(self.notebook, self.preferences, audio.get_channel(i))
            # add the pages to the notebook with the label to show on the tab
            self.notebook.AddPage(page, "Channel %d"%i )

        self.ShowPage(0)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_notebook_page_changed)
        audio.close()
        return self.notebook

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _on_notebook_page_changed(self, event):
        oldselection = event.GetOldSelection()
        newselection = event.GetSelection()
        if oldselection != newselection:
            self.ShowPage(newselection)

    def _on_save_channel(self, event):
        page = self.notebook.GetPage( self.notebook.GetSelection() )
        page.SaveChannel( self._filename )

    def _on_save_info(self, event):
        page = self.notebook.GetPage( self.notebook.GetSelection() )
        page.SaveInfos( self._filename )

    # ------------------------------------------------------------------------

    def ShowPage(self, idx):
        wx.BeginBusyCursor()
        b = wx.BusyInfo("Please wait while loading data...")
        page = self.notebook.GetPage( idx )
        page.ShowInfo()
        b.Destroy()
        b = None
        wx.EndBusyCursor()

# ----------------------------------------------------------------------------

# ---------------------------------------------------------------------------

class AudioRoamerPanel( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      to do!

    """
    FRAMERATES = [ "16000", "32000", "48000" ]
    SAMPWIDTH  = [ "8", "16", "24", "32" ]
    INFO_LABEL_AMP = {"nframes":"Number of frames: " ,
                      "minmax":"Min/Max values: ",
                      "cross":"Zero crossings: "}
    INFO_LABEL_VOL = { "volmin":"Volume min: ",
                       "volmax":"Volume max: ",
                       "volmean":"Volume mean: "
                     }

    NO_INFO_LABEL = " ... "

    def __init__(self, parent, preferences, channel):
        """
        Create a new AudioRoamerPanel instance.

        @param parent (wxWindow)
        @param preferences (structs.Preferences)
        @param channel (audiodata.Channel)

        """
        wx.Panel.__init__(self, parent)
        self._prefs    = preferences
        self._channel  = channel  # Channel
        self._filename = None     # Fixed when "Save as" is clicked
        self._cv = None           # ChannelSilence, fixed by ShowInfos
        self._ca = None           # AudioFrames with only this channel, fixed by ShowInfos
        self._wxobj = {}          # List of wx objects for information values
        self._wxtxobj = []        # List of wx objects for information labels

        sizer = self._create_content()

        self.SetFont( preferences.GetValue('M_FONT') )
        self.SetBackgroundColour( preferences.GetValue('M_BG_COLOUR') )
        self.SetForegroundColour( preferences.GetValue('M_FG_COLOUR') )

        self.SetSizer(sizer)
        self.SetAutoLayout( True )
        self.SetMinSize((MIN_PANEL_W,MIN_PANEL_H))
        self.Layout()

    # -----------------------------------------------------------------------
    # Private methods to show information about the channel into the GUI.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """
        Create the main sizer, add content then return it.

        """
        sizerinfos = wx.BoxSizer(wx.VERTICAL)

        gbs1 = self._create_content_infos()
        gbs2 = self._create_content_clipping()
        gbs3 = self._create_content_modif()
        gbs4 = self._create_content_ipus()

        sizerinfos.AddSpacer(10)
        sizerinfos.Add(gbs1, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 2)
        sizerinfos.AddSpacer(10)
        sizerinfos.Add(gbs2, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 2)
        sizerinfos.AddSpacer(10)
        sizerinfos.Add(gbs3, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 2)
        sizerinfos.AddSpacer(10)
        sizerinfos.Add(gbs4, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 2)
        sizerinfos.AddSpacer(10)

        return sizerinfos

    def __add_info_amp(self, gbs, key, row, col):
        """ Private method to add an info in the GridBagSizer. """
        static_tx = wx.StaticText(self, -1, AudioRoamerPanel.INFO_LABEL_AMP[key])
        gbs.Add(static_tx, (row, col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxtxobj.append( static_tx )
        tx = wx.TextCtrl(self, -1, AudioRoamerPanel.NO_INFO_LABEL, style=wx.TE_READONLY)
        self._wxobj[key] = tx
        gbs.Add(tx, (row, col+1), flag=wx.EXPAND|wx.RIGHT, border=4)

    def __add_info_vol(self, gbs, key, row, col):
        """ Private method to add an info in the GridBagSizer. """
        static_tx = wx.StaticText(self, -1, AudioRoamerPanel.INFO_LABEL_VOL[key])
        gbs.Add(static_tx, (row, col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxtxobj.append( static_tx )
        tx = wx.TextCtrl(self, -1, AudioRoamerPanel.NO_INFO_LABEL, style=wx.TE_READONLY)
        self._wxobj[key] = tx
        gbs.Add(tx, (row, col+1), flag=wx.EXPAND|wx.RIGHT, border=4)

    def __add_clip(self, gbs, i):
        """ Private method to add a clipping value in a GridBagSizer. """
        static_tx = wx.StaticText(self, -1, str( float(i)/10.) )
        gbs.Add(static_tx, (0, i), flag=wx.ALIGN_RIGHT|wx.ALL, border=2)
        self._wxtxobj.append( static_tx )
        tx = wx.TextCtrl(self, -1, AudioRoamerPanel.NO_INFO_LABEL, style=wx.TE_READONLY|wx.TE_RIGHT)
        gbs.Add(tx, (1, i), flag=wx.RIGHT, border=2)
        self._wxobj["clip1"+str(i)] = tx

    def _create_content_infos(self):
        """
        GUI design for amplitude and volume information.

        """
        gbs = wx.GridBagSizer(3, 4)

        self.__add_info_amp(gbs, "nframes", 0,0)
        self.__add_info_amp(gbs, "minmax",  1,0)
        self.__add_info_amp(gbs, "cross",   2,0)
        self.__add_info_vol(gbs, "volmin",  0,2)
        self.__add_info_vol(gbs, "volmax",  1,2)
        self.__add_info_vol(gbs, "volmean", 2,2)
        gbs.AddGrowableCol(1)
        gbs.AddGrowableCol(3)

        return gbs

    def _create_content_clipping(self):
        """
        GUI design for clipping information.

        """
        gbs = wx.GridBagSizer(2, 11)

        static_tx = wx.StaticText(self, -1, "Factor: ")
        gbs.Add(static_tx, (0, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxtxobj.append( static_tx )
        static_tx = wx.StaticText(self, -1, "Clipping rate (%): ")
        gbs.Add(static_tx, (1, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxtxobj.append( static_tx )

        for i in range(1,10):
            self.__add_clip(gbs,i)

        return gbs

    def _create_content_modif(self):
        """
        GUI design for modifiable information.

        """
        gbs = wx.GridBagSizer(2, 5)
        static_tx = wx.StaticText(self, -1, "Frame rate (Hz): ")
        gbs.Add(static_tx, (0, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxtxobj.append( static_tx )
        comboframerate = wx.ComboBox(self, -1, size=(150, -1), choices=AudioRoamerPanel.FRAMERATES, style=wx.CB_READONLY)
        gbs.Add(comboframerate, (1, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxobj["framerate"] = comboframerate

        static_tx = wx.StaticText(self, -1, "Samp. width (bits): ")
        gbs.Add(static_tx, (0, 1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxtxobj.append( static_tx )
        combosampwidth = wx.ComboBox(self, -1, size=(150, -1), choices=AudioRoamerPanel.SAMPWIDTH, style=wx.CB_READONLY)
        gbs.Add(combosampwidth, (1, 1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxobj["sampwidth"] = combosampwidth

        static_tx = wx.StaticText(self, -1, "Multiply values by: ")
        gbs.Add(static_tx, (0, 2), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxtxobj.append( static_tx )
        tx = wx.TextCtrl(self, -1, "1.0", validator=TextAsNumericValidator())
        tx.SetInsertionPoint(0)
        gbs.Add(tx, (1, 2), flag=wx.EXPAND|wx.RIGHT, border=2)
        self._wxobj["mul"] = tx

        static_tx = wx.StaticText(self, -1, "Add bias value: ")
        gbs.Add(static_tx, (0, 3), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxtxobj.append( static_tx )
        tx = wx.TextCtrl(self, -1, "0", validator=TextAsNumericValidator())
        tx.SetInsertionPoint(0)
        gbs.Add(tx, (1, 3), flag=wx.EXPAND|wx.RIGHT, border=2)
        self._wxobj["bias"] = tx

        static_tx = wx.StaticText(self, -1, "Remove offset value: ")
        gbs.Add(static_tx, (0, 4), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self._wxtxobj.append( static_tx )
        cb = wx.CheckBox(self, -1, style=wx.NO_BORDER)
        cb.SetValue( False )
        gbs.Add(cb, (1, 4), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=2)
        self._wxobj["offset"] = cb

        # Extract fragment: from...to...
        return gbs

    def _create_content_ipus(self):
        """
        GUI design for information about an IPUs segmentation...

        """
        s = wx.BoxSizer(wx.HORIZONTAL)

        # Volume threshold we used...
        # Number of silences
        # Number of tracks
        # Total silence duration
        # Total tracks duration

        return s

    # -----------------------------------------------------------------------
    # Setters for GUI
    # ----------------------------------------------------------------------

    def SetFont(self, font):
        """
        Change font of all wx texts.

        """
        wx.Window.SetFont( self, font )
        for obj in self._wxobj.values():
            obj.SetFont(font)
        for obj in self._wxtxobj:
            obj.SetFont(font)

    # ----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """
        Change background of all texts.

        """
        wx.Window.SetBackgroundColour( self, color )
        for obj in self._wxobj.values():
            obj.SetBackgroundColour( color )
        for obj in self._wxtxobj:
            obj.SetBackgroundColour( color )

    # ----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """
        Change foreground of all texts.

        """
        wx.Window.SetForegroundColour( self, color )
        for obj in self._wxtxobj:
            obj.SetForegroundColour( color )

    # ----------------------------------------------------------------------
    # Methods of the workers
    # ----------------------------------------------------------------------

    def ShowInfo(self):
        """
        Estimate all values then display the information.

        """
        # we never estimated values. we have to do it!
        if self._cv is None:
            self.SetChannel(self._channel)

        # Volume/Amplitude
        self._wxobj["nframes"].ChangeValue( " "+str(self._channel.get_nframes())+" " )
        self._wxobj["minmax"].ChangeValue( " "+str(self._ca.minmax())+" " )
        self._wxobj["cross"].ChangeValue( " "+str(self._ca.cross())+" " )
        self._wxobj["volmin"].ChangeValue( " "+str(self._cv.get_volstats().min())+" " )
        self._wxobj["volmax"].ChangeValue( " "+str(self._cv.get_volstats().max())+" " )
        self._wxobj["volmean"].ChangeValue( " "+str(int(self._cv.get_volstats().mean()) )+" ")

        # Clipping
        for i in range(1,10):
            cr = self._ca.clipping_rate( float(i)/10. ) * 100.
            self._wxobj["clip1"+str(i)].ChangeValue( " "+str( round(cr,2))+" ")

        # Modifiable
        fm = str(self._channel.get_framerate())
        if not fm in AudioRoamerPanel.FRAMERATES:
            self._wxobj["framerate"].Append( fm )
        self._wxobj["framerate"].SetStringSelection(fm)
        sp = str(self._channel.get_sampwidth()*8)
        if not sp in AudioRoamerPanel.SAMPWIDTH:
            self._wxobj["sampwidth"].Append( sp )
        self._wxobj["sampwidth"].SetStringSelection( sp )

        # IPUs

        # Set a different foreground color to estimated values
        for v in self._wxobj.values():
            v.SetForegroundColour( INFO_COLOUR )

    # -----------------------------------------------------------------------

    def SetChannel(self, newchannel):
        """
        Set a new channel, estimates the values to be displayed.

        """
        # Set the channel
        self._channel = newchannel

        # To estimate values related to amplitude
        frames = self._channel.get_frames(self._channel.get_nframes())
        self._ca = AudioFrames(frames, self._channel.get_sampwidth(), 1)

        # Estimates the RMS (i.e. volume), then find where are silences
        self._cv = ChannelSilence(self._channel)
        volume = self._cv.search_threshold_vol()
        self._cv.search_silences(volume)
        self._cv.filter_silences(0.2)
        # Find where are IPUs
        #tracks = self._cv.extract_tracks(0.3)

    # -----------------------------------------------------------------------

    def ApplyChanges(self):
        """
        Apply changes on the channel then show new values.

        """
        # Get the list of modifiable values from wx objects
        fm     = int(self._wxobj["framerate"].GetValue())
        sp     = int(self._wxobj["sampwidth"].GetValue())/8
        mul    = float(self._wxobj["mul"].GetValue())
        bias   = int(self._wxobj["bias"].GetValue())
        offset = self._wxobj["offset"].GetValue()

        # If something changed, apply this/these change-s to the channel
        if fm != self._channel.get_framerate() or sp != self._channel.get_sampwidth() or mul != 1.0 or bias != 0 or offset is True:
            channelfmt = ChannelFormatter(self._channel)
            channelfmt.set_framerate(fm)
            channelfmt.set_sampwidth(sp)
            channelfmt.convert()
            channelfmt.mul(mul)
            channelfmt.bias()
            if offset is True:
                channelfmt.remove_offset()
            self.SetChannel( channelfmt.get_channel() )
            self.ShowInfo()

    # -----------------------------------------------------------------------

    def SaveChannel(self, parentfilename):
        """
        Save the channel in an audio file.

        """
        newfilename = SaveAsAudioFile()

        # If it is the OK response, process the data.
        if newfilename is not None:
            try:
                self.ApplyChanges()
                audio = AudioPCM()
                audio.append_channel(self._channel)
                audiodata.io.save(newfilename, audio)
            except Exception as e:
                ShowInformation( self, self._prefs, "Save has failed: %s" % e, style=wx.ICON_ERROR)
                return
            else:
                # Update members
                self._filename = newfilename
                # Tell the parent we changed his file
                if newfilename == parentfilename:
                    evt = FileWanderEvent(filename=self._filename, status=True)
                    evt.SetEventObject(self)
                    wx.PostEvent( self.GetParent().GetParent().GetParent(), evt )

    # -----------------------------------------------------------------------

    def SaveInfos(self, parentfilename):
        """
        Ask for a filename then save all displayed information.

        """
        newfilename = SaveAsAnyFile()
        # If it is the OK response, process the data.
        if newfilename is not None:
            content = self._infos_content(parentfilename)
            with codecs.open(newfilename, "w", encoding) as fp:
                fp.write(content)

    # -----------------------------------------------------------------------
    # Private methods to list information in a "formatted" text.
    # -----------------------------------------------------------------------

    def _infos_content(self, parentfilename):
        content  = ""
        content += self._sep()
        content += self._line(program + ' - Version ' + version)
        content += self._line(copyright)
        content += self._line("Web site: "+ url)
        content += self._line("Contact: "+ author + "("+ contact + ")")
        content += self._sep()
        content += self._newline()
        content += self._line("Date: " + str(datetime.datetime.now()))

        # General information
        content += self._section("General information")
        content += self._line("Filename: %s"%self._filename)
        content += self._line("Channel extracted from file: "+parentfilename)
        content += self._line("Duration: %s sec."%self._channel.get_duration())
        content += self._line("Framerate: %d Hz"%self._channel.get_framerate())
        content += self._line("Samp. width: %d bits"%(int(self._channel.get_sampwidth())*8))

        # Amplitude
        content += self._section("Amplitude")
        for k,label in AudioRoamerPanel.INFO_LABEL_AMP.items():
            content += self._line(label+self._wxobj[k].GetValue())

        # Clipping
        content += self._section("Amplitude clipping: ")
        for i in range(1,10):
            f = self._ca.clipping_rate( float(i)/10. ) * 100.
            content += self._item("factor "+str(float(i)/10.)+": "+str(round(f,2))+"%")

        # Volume
        content += self._section("Volume")
        for k,label in AudioRoamerPanel.INFO_LABEL_VOL.items():
            content += self._line(label+self._wxobj[k].GetValue())

        # IPUs
        content += self._section("Inter-Pausal Units automatic segmentation")

        return content

    def _section(self, title):
        text = self._newline()
        text += self._sep()
        text += self._line(title)
        text += self._sep()
        text += self._newline()
        return text

    def _line(self, msg):
        return msg.strip() + "\n"

    def _item(self, msg):
        return "  - "+msg.strip() + "\n"

    def _newline(self):
        return "\n"

    def _sep(self):
        return "-----------------------------------------------------------------\n"

# ----------------------------------------------------------------------------

def ShowAudioRoamerDialog(parent, preferences, filename):
    dialog = AudioRoamerDialog(parent, preferences, filename)
    dialog.ShowModal()
    dialog.Destroy()
