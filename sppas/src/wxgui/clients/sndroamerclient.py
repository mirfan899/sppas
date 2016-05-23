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
from wxgui.sp_icons  import SNDROAMER_APP_ICON
from wxgui.sp_icons  import SAVE_FILE
from wxgui.sp_icons  import SAVE_AS_FILE

from wxgui.sp_consts import INFO_COLOUR
from wxgui.sp_consts import MIN_PANEL_W
from wxgui.sp_consts import MIN_PANEL_H
from wxgui.sp_consts import BUTTON_ICONSIZE

from wxgui.dialogs.filedialogs import SaveAsAudioFile
from wxgui.dialogs.msgdialogs import ShowInformation

from wxgui.dialogs.basedialog import spBaseDialog
import audiodata.io
from audiodata.channelvolume import ChannelVolume
from audiodata.audioframes   import AudioFrames

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
        self.Bind(wx.EVT_BUTTON, self._on_save_channel, btn_save_channel)
        btn_save_info = self.CreateButton(SAVE_AS_FILE, "Save these information as...", "Save the displayed information in a text file.", btnid=wx.ID_SAVE)
        self.Bind(wx.EVT_BUTTON, self._on_save_info, btn_save_info)
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

    NO_INFO_LABEL = " ... "

    def __init__(self, parent, preferences, channel):
        """
        Create a new AudioRoamerPanel instance.

        @parent (wxWindow)

        """
        wx.Panel.__init__(self, parent)
        self._prefs = preferences
        self.channel = channel
        self.cv = None
        self.ca = None
        self._values = []

        sizerinfos = wx.BoxSizer(wx.VERTICAL)
        gbs1 = self._create_content_infos()
        gbs2 = self._create_content_clipping()
        gbs3 = self._create_content_modif()

        sizerinfos.Add(gbs1, 1, wx.EXPAND|wx.ALL, 2)
        sizerinfos.AddSpacer(10)
        sizerinfos.Add(gbs2, 0, wx.ALL, 2)
        sizerinfos.AddSpacer(10)
        sizerinfos.Add(gbs3, 0, wx.ALL, 2)
        sizerinfos.AddSpacer(10)

        self.SetFont( self._prefs.GetValue('M_FONT') )
        self.SetBackgroundColour( self._prefs.GetValue('M_BG_COLOUR') )
        self.SetForegroundColour( self._prefs.GetValue('M_FG_COLOUR') )

        self.SetSizer(sizerinfos)
        self.SetAutoLayout( True )
        self.SetMinSize((MIN_PANEL_W,MIN_PANEL_H))
        self.Layout()

    # -----------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # -----------------------------------------------------------------------

    def _add_info(self, gbs, label, row, col):
        static_tx = wx.StaticText(self, -1, label)
        gbs.Add(static_tx, (row, col), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        tx = wx.TextCtrl(self, -1, AudioRoamerPanel.NO_INFO_LABEL, style=wx.TE_READONLY)
        self._values.append( tx )
        gbs.Add(tx, (row, col+1), flag=wx.EXPAND|wx.RIGHT, border=4)

    def _create_content_infos(self):
        """
        GUI design for volume/amplitude information.

        """
        gbs = wx.GridBagSizer(3, 4)
        self._add_info(gbs, "Number of frames: ", 0,0)
        self._add_info(gbs, "Min/Max values: ",   1,0)
        self._add_info(gbs, "Zero crossings: ",   2,0)
        self._add_info(gbs, "Volume min: ",       0,2)
        self._add_info(gbs, "Volume max: ",       1,2)
        self._add_info(gbs, "Volume mean: ",      2,2)
        gbs.AddGrowableCol(1)
        gbs.AddGrowableCol(3)
        return gbs

    def _create_content_clipping(self):
        """
        GUI design for clipping information.

        """
        gbs = wx.GridBagSizer(2, 11)
        static_tx = wx.StaticText(self, -1, "Factor:")
        gbs.Add(static_tx, (0, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        static_tx = wx.StaticText(self, -1, "Clipping rate (%):")
        gbs.Add(static_tx, (1, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        for i in range(1,10):
            static_tx = wx.StaticText(self, -1, str( float(i)/10.) )
            gbs.Add(static_tx, (0, i), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, border=2)
            tx = wx.TextCtrl(self, -1, AudioRoamerPanel.NO_INFO_LABEL, style=wx.TE_READONLY|wx.TE_RIGHT)
            gbs.Add(tx, (1, i), flag=wx.EXPAND|wx.RIGHT, border=2)
            self._values.append( tx )
        return gbs

    def _create_content_modif(self):
        """
        GUI design for modifiable information.

        """
        gbs = wx.GridBagSizer(2, 2)
        static_tx = wx.StaticText(self, -1, "Frame rate (Hz):")
        gbs.Add(static_tx, (0, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self.comboframerate = wx.ComboBox(self, -1, size=(150, -1), choices=AudioRoamerPanel.FRAMERATES, style=wx.CB_READONLY)
        gbs.Add(self.comboframerate, (1, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)

        static_tx = wx.StaticText(self, -1, "Samp. width (bits):")
        gbs.Add(static_tx, (0, 1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)
        self.combosampwidth = wx.ComboBox(self, -1, size=(150, -1), choices=AudioRoamerPanel.SAMPWIDTH, style=wx.CB_READONLY)
        gbs.Add(self.combosampwidth, (1, 1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=2)

        return gbs

    def ShowInfo(self):
        if self.cv is None:
            self.cv = ChannelVolume(self.channel)
            self.ca = AudioFrames(self.channel.get_frames(self.channel.get_nframes()), self.channel.get_sampwidth(), 1)
        # Volume/Amplitude
        self._values[0].ChangeValue( " "+str(self.channel.get_nframes())+" " )
        self._values[1].ChangeValue( " "+str(self.ca.minmax())+" " )
        self._values[2].ChangeValue( " "+str(self.ca.cross())+" " )
        self._values[3].ChangeValue( " "+str(self.cv.min())+" " )
        self._values[4].ChangeValue( " "+str(self.cv.max())+" " )
        self._values[5].ChangeValue( " "+str(int(self.cv.mean()) )+" ")
        # Clipping
        for i in range(1,10):
            cr = self.ca.clipping_rate( float(i)/10. ) * 100.
            self._values[5+i].ChangeValue( " "+str( round(cr,2))+" ")
        for v in self._values:
            v.SetForegroundColour( INFO_COLOUR )
        # Modifiable
        fm = str(self.channel.get_framerate())
        if not fm in AudioRoamerPanel.FRAMERATES:
            self.comboframerate.Append( fm )
        self.comboframerate.SetStringSelection(fm)
        sp = str(self.channel.get_sampwidth()*8)
        if not sp in AudioRoamerPanel.SAMPWIDTH:
            self.combosampwidth.Append( sp )
        self.combosampwidth.SetStringSelection( sp )


    def SaveChannel(self, parentfilename):
#         newfilename = SaveAsAudioFile( )
#         # If it is the OK response, process the data.
#         if newfilename:
#             try:
#                 channel = ChannelFormatter()
#                 audio = AudioPCM()
#                 audio.append_channel( channel )
#
#                 audiodata.io.write(newfilename, audio)
#             except Exception as e:
#                 ShowInformation( self, self._prefs, "Save has failed: %s" % e, style=wx.ICON_ERROR)

        fm = int(self.comboframerate.GetValue())
        sp = int(self.combosampwidth.GetValue())/8
        ShowInformation( self, self._prefs, "Not implemented yet.", style=wx.ICON_ERROR)

    def SaveInfos(self, parentfilename):
        ShowInformation( self, self._prefs, "Not implemented yet.", style=wx.ICON_ERROR)

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------

def ShowAudioRoamerDialog(parent, preferences, filename):
    dialog = AudioRoamerDialog(parent, preferences, filename)
    dialog.ShowModal()
    dialog.Destroy()
