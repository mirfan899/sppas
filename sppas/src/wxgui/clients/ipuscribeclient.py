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
# File: ipuscribeclient.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import wx.stc
import wx.media
import wx.lib.scrolledpanel as scrolled
import wx.lib.platebtn      as platebtn
import logging
import os.path

from wxgui.sp_icons               import APPLY_ICON
from wxgui.sp_icons               import PAGE_FIRST_ICON
from wxgui.sp_icons               import PAGE_PREV_ICON
from wxgui.sp_icons               import PAGE_NEXT_ICON
from wxgui.sp_icons               import PAGE_LAST_ICON
from wxgui.cutils.imageutils      import spBitmap

from baseclient                 import BaseClient
import wxgui.cutils.colorutils as co
from wxgui.panels.sndplayer     import SndPlayer
from wxgui.ui.CustomEvents      import FileWanderEvent, spEVT_FILE_WANDER
from wxgui.structs.themes       import BaseTheme
from wxgui.structs.prefs        import Preferences

from wxgui.dialogs.msgdialogs import ShowInformation
from wxgui.dialogs.msgdialogs import ShowYesNoQuestion

import annotationdata.io


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

IPU_BY_PAGE = 50


# ----------------------------------------------------------------------------
# Main class that manage the notebook
# ----------------------------------------------------------------------------


class IPUscribeClient( BaseClient ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: This class is used to manage the opened files.

    This class manages the pages of a notebook with all opened files.

    Each page (except if empty...) contains an instance of a SndRoamer.

    """

    def __init__( self, parent, prefsIO ):
        BaseClient.__init__( self, parent, prefsIO )
        self._update_members()

    # End __init__
    # ------------------------------------------------------------------------


    def _update_members(self):
        """
        Update members.
        """
        self._multiplefiles = False

    # End _update_members
    # ------------------------------------------------------------------------


    def CreateComponent(self, parent, prefsIO ):
        return IPUscribe(parent, prefsIO)

    # ------------------------------------------------------------------------


    def Save(self):
        """
        Save the current file(s).
        """
        page = self._notebook.GetCurrentPage()
        for i in range(self._xfiles.GetSize()):
            if self._xfiles.GetOther(i) == page:
                o = self._xfiles.GetObject(i)
                o.Save()

    # Save
    # ------------------------------------------------------------------------


    def SaveAll(self):
        """
        Save all files (one per page).
        """
        for i in range(self._xfiles.GetSize()):
            o = self._xfiles.GetObject(i)
            o.Save()

    # SaveAll
    # ------------------------------------------------------------------------


# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# The Component is the content of one page of the notebook.
# ----------------------------------------------------------------------------


class IPUscribe( wx.Panel ):
    """
    Create the whole IPUscribe panel.
    """

    def __init__(self, parent, prefsIO):
        """
        Create a new instance.
        """
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        sizer = wx.BoxSizer( wx.VERTICAL )

        # members
        self._prefsIO = self._check_prefs(prefsIO)
        self._current_page = 0
        self._sndname = None

        # a set of panels:
        self._txtinfo = wx.StaticText(self,  -1, "", style=wx.ALIGN_LEFT)
        self._trsPanel = IPUscribeData(self, prefsIO)
        self._create_media()
        self._create_nav()

        sizer.Add(self._txtinfo,    proportion=0, flag=wx.ALL|wx.EXPAND, border=8 )
        sizer.Add(self._trsPanel,   proportion=1, flag=wx.ALL|wx.EXPAND, border=2 )
        sizer.Add(self._mediaPanel, proportion=0, flag=wx.ALL|wx.EXPAND, border=2 )
        sizer.Add(self._navPanel,   proportion=0, flag=wx.ALL|wx.EXPAND, border=2)

        # Bind events
        self.Bind(spEVT_FILE_WANDER, self.OnFileWander)
        self.Bind(wx.EVT_SET_FOCUS,  self.OnFocus)
        self.GetTopLevelParent().Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)

        self.SetSizer(sizer)
        self.SetAutoLayout( True )
        self.Layout()

        self.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )
        self.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )
        self.SetFont( self._prefsIO.GetValue('M_FONT') )

    # ----------------------------------------------------------------------

    def __create_button(self, bmp):
        """
        Create a button and add it to the sizer.
            - bmp is a picture file name
        """
        btn = platebtn.PlateButton(self._navPanel, -1, bmp=spBitmap(bmp, 24, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        btn.SetInitialSize()
        btn.SetPressColor(wx.LIGHT_GREY)
        btn.Enable( True )
        return btn

    #----------------------------------------------------------------------

    def _create_media(self):
        """
        Create the media panel.
        """
        #self._mediaPanel = SndPlayer(self, orient=wx.HORIZONTAL, refreshtimer=10, prefsIO=self._prefsIO)
        self._mediaPanel = SndPlayer(self, orient=wx.HORIZONTAL, refreshtimer=10, prefsIO=self._prefsIO)

        self._mediaPanel.SetPreferences(self._prefsIO)
        self._mediaPanel.ActivateButtons(False)

    #----------------------------------------------------------------------

    def _create_nav(self):
        """
        Create the page-navigation panel.
        """
        self._navPanel = wx.Panel(self)
        s = wx.BoxSizer( wx.HORIZONTAL )

        # Number of IPUs by page
        self._infoipus = wx.StaticText(self._navPanel, -1, label="IPUs by page: ")
        self._textpage = wx.TextCtrl(self._navPanel, -1, value=str(IPU_BY_PAGE))
        self._spinpage = wx.SpinButton(self._navPanel, style=wx.SP_VERTICAL)
        self._spinpage.SetRange(20, 300)
        self._spinpage.SetValue(IPU_BY_PAGE)

        # Buttons to change the page
        self._buttons = {}
        self._buttons['apply'] = self.__create_button(APPLY_ICON)
        self._buttons['first'] = self.__create_button(PAGE_FIRST_ICON)
        self._buttons['prev']  = self.__create_button(PAGE_PREV_ICON)
        self._buttons['next']  = self.__create_button(PAGE_NEXT_ICON)
        self._buttons['last']  = self.__create_button(PAGE_LAST_ICON)

        # Text to indicate the current page
        self._footer = wx.StaticText(self._navPanel, -1, "")
        self.__set_footer()

        s.Add(self._infoipus, 0, wx.ALL|wx.CENTER)
        s.Add(self._textpage, 0, wx.ALL|wx.CENTER)
        s.Add(self._spinpage, 0, wx.ALL|wx.CENTER)
        s.Add(self._buttons['apply'], proportion=0, flag=wx.ALL, border=2)
        s.AddStretchSpacer()
        s.Add(self._buttons['first'], proportion=0, flag=wx.ALL, border=2)
        s.Add(self._buttons['prev'], proportion=0, flag=wx.ALL, border=2)
        s.Add(self._buttons['next'], proportion=0, flag=wx.ALL, border=2)
        s.Add(self._buttons['last'], proportion=0, flag=wx.ALL, border=2)
        s.AddStretchSpacer()
        s.Add(self._footer, 0, wx.ALL, 6)

        self.Bind(wx.EVT_SPIN, self.OnSpinPage, self._spinpage)
        self._buttons['apply'].Bind(wx.EVT_BUTTON, self.OnChangeIPUbyPage)
        self._buttons['first'].Bind(wx.EVT_BUTTON, self.OnFirstPage)
        self._buttons['prev'].Bind(wx.EVT_BUTTON, self.OnPrevPage)
        self._buttons['next'].Bind(wx.EVT_BUTTON, self.OnNextPage)
        self._buttons['last'].Bind(wx.EVT_BUTTON, self.OnLastPage)

        self._navPanel.SetSizer(s)

    # ----------------------------------------------------------------------

    def __set_footer(self):
        """ Set the label of the footer. """
        pagenb = "---"
        if self._current_page:
            pagenb = str(self._current_page)
        pagetotal = "---"
        if self._trsPanel.GetPageCount():
            pagetotal = str(self._trsPanel.GetPageCount())

        self._footer.SetLabel(" Page %s / %s " % (pagenb, pagetotal))

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
                a = prefs.GetValue( 'M_BG_COLOUR' )
                a = prefs.GetValue( 'M_FG_COLOUR' )
                a = prefs.GetValue( 'M_FONT' )
                a = prefs.GetValue( 'M_ICON_THEME' )
            except Exception:
                self._prefsIO.SetTheme( BaseTheme() )
                prefs = self._prefsIO

        prefs.SetValue('SND_AUTOREPLAY', 'bool', True)
        prefs.SetValue('SND_INFO', 'bool', True)
        prefs.SetValue('SND_PLAY', 'bool', True)
        prefs.SetValue('SND_PAUSE', 'bool', True)
        prefs.SetValue('SND_STOP', 'bool', True)
        prefs.SetValue('SND_NEXT', 'bool', False)
        prefs.SetValue('SND_REWIND', 'bool', False)

        return prefs

    #-------------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Callbacks... Page navigation
    # ----------------------------------------------------------------------


    def OnFirstPage(self, evt=None):
        """
        Load the first page, except if the current page is already the first one!
        """
        if self._current_page > 1:
            self._current_page = self._trsPanel.LoadPage(1)
            self.__set_footer()
            self._trsPanel.KillFocus()
            self._mediaPanel.SetOffsetPeriod(0,0)


    def OnLastPage(self, evt=None):
        """
        Load the last page, except if the current page is already the last one!
        """
        if self._current_page < self._trsPanel.GetPageCount():
            self._current_page = self._trsPanel.LoadPage(self._trsPanel.GetPageCount())
            self.__set_footer()
            self._trsPanel.KillFocus()
            self._mediaPanel.SetOffsetPeriod(0,0)


    def OnPrevPage(self, evt=None):
        """
        Load the previous page, except if the current page is the first one!.
        """
        if self._current_page > 1:
            self._current_page = self._trsPanel.LoadPage(self._current_page-1)
            self.__set_footer()
            self._trsPanel.KillFocus()
            self._mediaPanel.SetOffsetPeriod(0,0)


    def OnNextPage(self, evt=None):
        """
        Load the next page, except if the current page is the last one.
        """
        if self._current_page < self._trsPanel.GetPageCount():
            self._current_page = self._trsPanel.LoadPage(self._current_page+1)
            self.__set_footer()
            self._trsPanel.KillFocus()
            self._mediaPanel.SetOffsetPeriod(0,0)


    def OnSpinPage(self, evt):
        """
        Update the text about the number of IPUs by page.
        """
        self._textpage.SetValue(str(evt.GetPosition()))


    def OnChangeIPUbyPage(self, evt):
        """
        Change the IPU_BY_PAGE value.
        """

        try:
            v = int(self._textpage.GetValue())
        except Exception:
            v = -1
        if v <= 0:
            self._textpage.SetValue(str(IPU_BY_PAGE))
            self._spinpage.SetValue(IPU_BY_PAGE)
            v = IPU_BY_PAGE
        self._current_page = self._trsPanel.SetState(ipu_by_page=v)
        self.__set_footer()

    # ------------------------------------------------------------------------


    def OnFocus(self, event):
        """
        An IPU received the focus.
        """
        obj = event.GetEventObject()
        if obj != self._trsPanel:
            return
        self._mediaPanel.FileSelected( self._sndname )
        (s,e) = self._trsPanel.GetSelectionStartEnd()
        self._mediaPanel.SetOffsetPeriod( int(s),int(e) )

    # ------------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Functions...
    # ----------------------------------------------------------------------


    def Save(self):
        """ Save the transcription. """

        self._trsPanel.Save()

    # End Save
    # ----------------------------------------------------------------------


    def SetFont(self, font):
        """ Change font of all texts. """

        wx.Window.SetFont( self,font )
        # Apply on all panels
        self._trsPanel.SetFont( font )
        self._mediaPanel.SetFont( font )
        self._navPanel.SetFont( font )

        self._infoipus.SetFont( font )
        self._textpage.SetFont( font )
        self._footer.SetFont( font )
        self._txtinfo.SetFont( font )

    # End SetFont
    # ----------------------------------------------------------------------


    def SetBackgroundColour(self, color):
        """ Change background of all panels. """

        wx.Window.SetBackgroundColour( self,color )
        # Apply as background on all panels
        self._trsPanel.SetBackgroundColour( color )
        self._mediaPanel.SetBackgroundColour( color )
        self._navPanel.SetBackgroundColour( color )

        self._infoipus.SetBackgroundColour( color )
        self._textpage.SetBackgroundColour( color )
        self._spinpage.SetBackgroundColour( color )
        self._footer.SetBackgroundColour( color )
        self._txtinfo.SetBackgroundColour( color )

    # End SetBackgroundColour
    # ----------------------------------------------------------------------


    def SetForegroundColour(self, color):
        """ Change foreground of all panels. """

        wx.Window.SetForegroundColour( self,color )
        # Apply as foreground on all panels
        self._trsPanel.SetForegroundColour( color )
        self._mediaPanel.SetForegroundColour( color )
        self._navPanel.SetForegroundColour( color )

        self._infoipus.SetForegroundColour( color )
        self._textpage.SetForegroundColour( color )
        self._spinpage.SetForegroundColour( color )
        self._footer.SetForegroundColour( color )
        self._txtinfo.SetForegroundColour( color )

    # End SetForegroundColour
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Callbacks
    # ----------------------------------------------------------------------


    def OnFileWander(self, event):
        """
        A file was selected/unselected.
        """
        f = event.filename
        s = event.status

        if s is True:
            self.FileSelected( f )
        else:
            self.FileDeSelected()

    # End OnFileWander
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Data Management
    # ----------------------------------------------------------------------

    def exists(self, filename):
        for x in os.listdir( os.path.dirname(filename)):
            try:
                if os.path.basename(filename.lower()) == x.lower():
                    return os.path.join(os.path.dirname(filename),x)
            except Exception:
                pass
        return None


    def FileSelected(self, filename):
        """
        Add files.
        """
        got = False
        name = os.path.splitext(filename)[0]
        for ext in annotationdata.io.extensions:
            if ext == '.txt':
                continue
            f = self.exists( name+ext )
            if got is False and f is not None:
                # create the object
                r = self._trsPanel.SetData(filename, f)
                if r is True:
                    self._txtinfo.SetLabel("Transcription file: "+f)
                    self._current_page = self._trsPanel.LoadPage(1)
                    # show the current page and the total amount of pages at the bottom of the window
                    self.__set_footer()
                    self.Layout()
                    got = True
                else:
                    self._trsPanel.UnsetData()

        if got is False:
            ShowInformation(self, self._prefsIO, "Missing IPUs: A file with an IPUs segmentation is required.", wx.ICON_ERROR)
            self.FileDeSelected()
            return

        self._sndname = filename

    # End OnFileSelected
    # ------------------------------------------------------------------------


    def FileDeSelected(self):
        """
        Remove the file.
        """
        if self._trsPanel._dirty is True:
            # dlg to ask to save or not
            userChoice = ShowYesNoQuestion( None, self._prefsIO, "Do you want to save changes on the transcription of audio file %s?"%self._sndname)
            if userChoice == wx.ID_YES:
                self._trsPanel.Save()

        self._trsPanel.UnsetData()
        self._mediaPanel.FileDeSelected()
        self._current_page = 0
        self._txtinfo.SetLabel("")
        self._mediaPanel.onClose(None)

        evt = FileWanderEvent(filename=self._sndname, status=False)
        evt.SetEventObject(self)
        wx.PostEvent( self.GetParent().GetParent().GetParent(), evt )
        self._sndname = None

    # End FileDeSelected
    # ------------------------------------------------------------------------

    def OnKeyPress(self, event):
        """
        Respond to a keypress event.
        """
        keycode = event.GetKeyCode()

        # Media player
        #     TAB -> PLay
        #     F1 -> Pause
        #     ESC -> Stop
        if keycode == wx.WXK_TAB:
            self._mediaPanel.onPlay( event )
        elif keycode == wx.WXK_F1:
            self._mediaPanel.onPause( event )
        elif keycode == wx.WXK_ESCAPE:
            self._mediaPanel.onStop( event )
        else:
            event.Skip()

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------


class IPUscribeData( scrolled.ScrolledPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This component allows to manually transcribe speech files.
    """

    def __init__(self, parent, prefsIO):
        """
        IPUscribe Component.
        """
        scrolled.ScrolledPanel.__init__(self, parent, -1)

        # members
        self._prefsIO = prefsIO

        # members
        self._ipupanels  = []    # list of IPU panels
        self._ipudata    = []    # list of all IPU data
        self._dirty      = False # status about the transcription file
        self._trsname    = None  # the transcription file name
        self._trsinput   = None  # the transcription object
        self._ipumin     = 0     # min index of IPUs displayed
        self._ipumax     = 0     # max index of IPUs displayed
        self._ipu_by_page = IPU_BY_PAGE
        self._ipu_selected = -1  # index of the selected ipu

        # main sizer
        self._ipusizer = wx.BoxSizer( wx.VERTICAL )
        self.SetSizer( self._ipusizer )

        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus) # An ipu was focused
        #self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

        self.SetAutoLayout( True )
        self.Layout()
        self.SetupScrolling()


    # ----------------------------------------------------------------------
    # Callbacks
    # ----------------------------------------------------------------------

    def OnFocus(self, event):
        """
        An IPU received the focus.
        """
        obj = event.GetEventObject()

        if obj not in self._ipupanels:
            logging.info('Error: %s not in ipupanels.'%obj)
        else:
            if self._ipu_selected == self._ipupanels.index( obj ):
                return # it is the same than the previous one!
            event.SetEventObject(self)
            wx.PostEvent(self.GetParent().GetEventHandler(), event)
            for ipu in self._ipupanels:
                if ipu != obj:
                    ipu.KillFocus()
            self._ipu_selected = self._ipupanels.index( obj )


    def KillFocus(self):
        if self._ipu_selected != -1:
            self._ipupanels[self._ipu_selected].KillFocus()
        self._ipu_selected = -1


    # ----------------------------------------------------------------------
    # GUI
    # ----------------------------------------------------------------------


    def SetFont(self, font):
        """ Change font of all texts. """

        wx.Window.SetFont( self,font )
        # Apply on all panels
        for p in self._ipupanels:
            p.SetFont(font)

    # End ChangeFont
    # ----------------------------------------------------------------------


    def SetForegroundColour(self, color):
        """ Change foreground of all panels. """

        wx.Window.SetForegroundColour( self,color )
        # Apply as foreground on all panels
        for p in self._ipupanels:
            p.SetForegroundColour(color)

    # End SetForegroundColour
    # ----------------------------------------------------------------------


    def SetState(self, dirty=None, ipumin=None, ipumax=None, ipu_by_page=None):
        """
        Change the current state:
        @param dirty (Boolean)
        @param ipumin (int)
        @param ipumax (int)
        @param ipu_by_page (int)
        """

        if dirty is not None:
            self._dirty = dirty

        if ipumin is not None:
            self._ipumin = ipumin

        if ipumax is not None:
            self._ipumax = ipumax

        if ipu_by_page is not None:
            if ipu_by_page != self._ipu_by_page:
                self._ipu_by_page = ipu_by_page
                # Then, try to keep the current displayed IPUs...
                if len(self._ipupanels) > 0:
                    m = int((self._ipumin + self._ipumax) / 2)
                    c = m/self._ipu_by_page + 1
                    self.LoadPage(c)
                    return c
            else:
                return ipu_by_page

        return 0

    # End SetState
    # -----------------------------------------------------------------------


    def SetData(self, wavname, trsname):
        """
        Open a transcription file with a wav file.

        @param wav: Wav file name
        @param trsname: Transcription file name

        """
        # What to do with the current opened transcription
        if len(self._ipupanels) > 0:
            if self._dirty is True:
                pass
                # TODO: a dialog box asking to save, or not!
                #userChoice = ShowYesNoQuestion( None, self._prefsIO, "Do you want to save changes on the transcription of\n%s?"%f)
                #if userChoice == wx.ID_YES:
                #    fix o object!!!
                #    o.Save()

            self.UnsetData()

        # Transcription retrieval
        (tieridx,trs) = self.__TierSelection(trsname)
        if trs is None or trs[tieridx].IsEmpty():
            ShowInformation( self, self._prefsIO, 'Error loading: '+trsname, style=wx.ICON_ERROR)
            return False

        # Gauge... to be patient!
        #progressMax = trs[tieridx].GetSize()
        #gauge = wx.ProgressDialog("IPUScribe", "Loading data...", progressMax, style=wx.STAY_ON_TOP|wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME|wx.PD_APP_MODAL)
        wx.BeginBusyCursor()
        b = wx.BusyInfo("Please wait while loading data...")

        # Store IPU data
        color = co.PickRandomColour(155,255)
        i   = 0 # interval index
        k   = 1 # ipu number
        for a in trs[tieridx]:
            # if it is not a silence
            if a.GetLabel().IsSilence() is False:
                ipu = IPUData(trs, tieridx, i, color, k)
                self._ipudata.insert(k, ipu)
                k = k+1
            i = i+1
            #gauge.Update(i)

        self._trsname  = trsname
        self._trsinput = trs
        #gauge.Destroy()
        b.Destroy()
        b = None
        wx.EndBusyCursor()

        return True

    # End SetData
    # -----------------------------------------------------------------------


    def LoadPage(self, nb_page):
        """
        Load the requested page.

        @param nb_page (int) is the page number to be loaded

        @return the page number if OK, -1 else
        """

        if nb_page > self.GetPageCount():
            return -1

        # Remove existing IPU panels
        for i in reversed(range(len(self._ipupanels))):
            self._ipupanels[i].Destroy()
            self._ipusizer.Remove(i)
        self._ipupanels = []

        # Add the IPUs corresponding to the new page to the listctrl
        i = 0
        self._ipumin = (nb_page-1) * self._ipu_by_page
        self._ipumax = min((nb_page * self._ipu_by_page), len(self._ipudata))
        logging.info(' ... Load page from IPU %d to %d.' % (self._ipumin,self._ipumax))
        while (self._ipumin+i) < self._ipumax:
            wnd = IPUPanel(self, self._ipudata[self._ipumin+i])
            # put the object in a sizer (required to enable Remove())
            s = wx.BoxSizer( wx.HORIZONTAL )
            s.Add( wnd, 1, wx.EXPAND)
            self._ipusizer.Add(s, proportion=0, flag=wx.EXPAND|wx.ALL, border=5 )
            # add in the list of ipus
            self._ipupanels.append(wnd)
            i = i+1

        self.Layout()
        return nb_page

    # End LoadPage
    # -----------------------------------------------------------------------


    def GetPageCount(self):
        """
        Return the number of pages (integer).
        """
        return len(self._ipudata) / self._ipu_by_page+1

    # End GetPageCount
    # -----------------------------------------------------------------------


    def GetSelectionStartEnd(self):
        """
        Return a tuple of start,end values of the selected ipu or (0,0).
        Time is in ms.
        """
        if self._ipu_selected == -1:
            return (0.,0.)
        s = self._ipudata[ self._ipu_selected + self._ipumin ].posstart
        e = self._ipudata[ self._ipu_selected + self._ipumin ].posend
        return (s,e)

    # End GetSelecttionStartEnd
    # -----------------------------------------------------------------------


    def UnsetData(self):
        """
        """
        self._ipudata   = []
        self._ipupanels = []
        self.SetState(dirty = False, ipumin = 0, ipumax = 0)

        for i in reversed(range(len(self._ipupanels))):
            self._ipupanels[i].Destroy()
            self._ipusizer.Remove(i)

        self.Layout()
        self.Refresh()


    # ----------------------------------------------------------------------
    # Functions...
    # ----------------------------------------------------------------------


    def Save(self):
        """ Save the transcription. """

        if self._dirty is True:
            try:
                annotationdata.io.write(self._trsname, self._trsinput)
                self._dirty = False
            except Exception as e:
                ShowInformation( self, self._prefsIO, "Transcription %s not saved: %s" % (self._trsname, str(e)), style=wx.ICON_ERROR)
                return None

    # ----------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------

    def __TierSelection(self, trsname):
        """
        Return the tier containing the orthographic transcription.
        It is then supposed that only one tier concerns orthographic
        transcription... which is a serious limitation of this tool.

        """
        transtier = -1
        try:
            trsinput = annotationdata.io.read(trsname)
        except:
            ShowInformation( self, self._prefsIO, "Transcription %s not loaded"%self._trsname, style=wx.ICON_ERROR)
            return None
        if trsinput.IsEmpty():
            return None

        # already a transcription
        for i, tier in enumerate(trsinput):
            tiername = tier.GetName().lower()
            if "trs" in tiername:
                transtier = i
                break
            elif "trans" in tiername:
                transtier = i
                break
            elif "ortho" in tiername:
                transtier = i
                break
            elif "toe" in tiername:
                transtier = i
                break

        # no transcription... try if IPUs...
        if transtier == -1:
            for i, tier in enumerate(trsinput):
                tiername = tier.GetName().lower()
                if "ipu" in tiername:
                    transtier = i
                    break

        # poor IPUScribe.... no tier is available to transcribe!
        if transtier == -1:
            lst = []
            for tier in trsinput:
                lst.append( tier.GetName() )
            #show a dialog
            dlg = wx.MultiChoiceDialog(self, "Select transcription tiers of file %s"%os.path.basename(trsname), "Select the tiers to view/edit", lst)

            if (dlg.ShowModal() == wx.ID_OK):
                transtiername = dlg.GetSelections()
                for i,tier in enumerate(trsinput):
                    if tier.GetName() == transtiername:
                        transtier = i
            else:
                return
            dlg.Destroy()

        return (transtier, trsinput)

    # ----------------------------------------------------------------------

# ----------------------------------------------------------------------------


class IPUPanel( wx.Panel ):
    """
    A panel for one IPU.
    """

    def __init__(self, parent, ipu):

        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour( ipu.color )

        self._ipu = ipu
        self._selected = False

        # create the information panel
        self._infopanel = wx.Panel(self)
        self._infopanel.SetBackgroundColour(self._ipu.color)

        self._title    = wx.StaticText(self._infopanel)
        self._title.SetForegroundColour( self.GetForegroundColour() )
        self._startend = wx.StaticText(self._infopanel)
        self._startend.SetForegroundColour( self.GetForegroundColour() )
        self._length   = wx.StaticText(self._infopanel)
        self._length.SetForegroundColour( co.LightenColor( self.GetForegroundColour(), 80 ))

        info_sizer = wx.BoxSizer(wx.VERTICAL)
        info_sizer.Add(self._title, 1, wx.ALL|wx.CENTER, 2)
        info_sizer.Add(self._startend, 0, wx.ALL | wx.CENTER, 2)
        info_sizer.Add(self._length,   0, wx.ALL | wx.CENTER, 2)
        self._infopanel.SetSizer(info_sizer)
        self.refresh_title()

        # create the text control
        self._text = wx.TextCtrl(self, size=wx.Size(0, 50), style=wx.TE_MULTILINE|wx.TE_RICH2)
        self._text.SetBackgroundColour( wx.WHITE )
        self._text.AppendText(self._ipu.get_label())

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._infopanel, 0, wx.EXPAND | wx.ALL , 2)
        sizer.Add(self._text, 1, wx.EXPAND | wx.ALL, 2)
        self.SetSizer(sizer)

        # Handling events.
        wx.EVT_MOUSE_EVENTS(self,            self.OnMouseEvents)
        wx.EVT_MOUSE_EVENTS(self._infopanel, self.OnMouseEvents)
        wx.EVT_MOUSE_EVENTS(self._text,      self.OnMouseEvents)
        wx.EVT_MOUSE_EVENTS(self._title,     self.OnMouseEvents)
        wx.EVT_MOUSE_EVENTS(self._startend,  self.OnMouseEvents)
        wx.EVT_MOUSE_EVENTS(self._length,    self.OnMouseEvents)

        self._text.Bind(wx.EVT_TEXT, self.OnTextChanged)
        self._text.Bind(wx.EVT_SET_FOCUS, self.OnFocus)

    # ----------------------------------------------------------------------


    def refresh_title(self):
        """ Update infos of the infopanel. """

        self._title.SetLabel("%s (%s)" % (self._ipu.get_tier_name(), self._ipu.nb_ipu))
        s = "{:6.2f}".format(self._ipu.get_start())
        e = "{:6.2f}".format(self._ipu.get_end())
        self._startend.SetLabel("%s - %s" % (s,e))
        self._length.SetLabel("  (%.2f)  " % self._ipu.get_length())
        self.Refresh()

    #-------------------------------------------------------------------------


    def SetFont(self, font):
        """ Change font of all texts. """

        wx.Window.SetFont( self,font )
        self._title.SetFont( font )
        self._startend.SetFont( font )
        self._length.SetFont( font )
        self.Refresh()

    # End SetFont
    # ----------------------------------------------------------------------


    def SetForegroundColour(self, color):
        """ Change foreground of all texts. """

        wx.Window.SetForegroundColour( self,color )
        self._title.SetForegroundColour( color )
        self._startend.SetForegroundColour( color )
        self._length.SetForegroundColour( co.LightenColor( color, 80 ))
        self.Refresh()

    # End SetForegroundColour
    # ----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------


    def OnTextChanged(self, evt):
        """
        The text was changed: must change the IPU label.
        """
        self._ipu.set_label(self._text.GetValue())
        self.GetParent().SetState(dirty = True)
        evt.Skip()

    # End OnTextChanged
    #-------------------------------------------------------------------------


    def OnFocus(self,event):
        """
        The text was clicked on.
        """
        self.SetBackgroundColour( wx.Colour(20,140,20) )
        self._text.SetBackgroundColour( wx.Colour(175,245,165) )
        self._text.Enable(True)
        self._text.SetInsertionPointEnd()
        self._text.Refresh()
        self._selected = True
        self.Refresh()

        event.SetEventObject(self)
        wx.PostEvent(self.GetParent().GetEventHandler(), event)

        event.Skip() # REQUIRED on Win32

    # End OnFocus
    #-------------------------------------------------------------------------


    def KillFocus(self):
        """
        The text was leaved.
        """
        self.SetBackgroundColour( self._ipu.color )
        self._text.SetBackgroundColour( wx.WHITE )
        self.Refresh()
        self._selected = False

    # End KillFocus
    #-------------------------------------------------------------------------


    def OnMouseEvents(self, event):
        """ Handles the wx.EVT_MOUSE_EVENTS event for self and self._infopanel. """

        if event.Entering() and self._selected is False:
            self.SetBackgroundColour( wx.Colour(175,245,165) )
            self.Refresh()

        elif event.Leaving() and self._selected is False:
            self.SetBackgroundColour( self._ipu.color )
            self.Refresh()

        event.Skip()

    # End OnMouseEvents
    #-------------------------------------------------------------------------


# ----------------------------------------------------------------------------


class IPUData:

    def __init__(self, trs, tier_idx, ann_idx, color=wx.ColourRGB(0xd1d1d1), nb_ipu=0):
        self.trs      = trs           # the transcription
        self.tier_idx = tier_idx      # the tier index
        self.ann_idx  = ann_idx       # the annotation index
        self.color    = color         # the bg color
        self.nb_ipu   = nb_ipu        # the ipu number
        posS = self.trs[self.tier_idx][self.ann_idx].GetLocation().GetBeginMidpoint() * 1000.0
        posE = self.trs[self.tier_idx][self.ann_idx].GetLocation().GetEndMidpoint()   * 1000.0
        self.posstart = int(posS)      # used by the MediaCtrl, to Seek.
        self.posend   = int(posE)      # used by the MediaCtrl, to Seek.

    def get_start(self):
        """
        Return the IPU start time in seconds (float).
        """
        return self.trs[self.tier_idx][self.ann_idx].GetLocation().GetBeginMidpoint()


    def get_end(self):
        """
        Return the IPU end time in seconds (float).
        """
        return self.trs[self.tier_idx][self.ann_idx].GetLocation().GetEndMidpoint()


    def set_label(self, value):
        """
        Change the IPU label.

        @param value (string)
        """
        self.trs[self.tier_idx][self.ann_idx].GetLabel().SetValue( value )


    def get_label(self):
        """
        Return the IPU label(string).
        """
        return self.trs[self.tier_idx][self.ann_idx].GetLabel().GetValue()


    def get_tier_name(self):
        """
        Return the name of the tier containing the IPU (string).
        """
        return self.trs[self.tier_idx].GetName()


    def get_length(self):
        """
        Return the IPU length in seconds (float).
        """
        return self.get_end() - self.get_start()


    def in_same_tier(self, ipu):
        """
        Return True if the two IPUs are in the same tier of the same transcription.

        @param ipu is the IPU to compare (IPUData).

        """
        return self.trs == ipu.trs and self.tier_idx == ipu.tier_idx

# ---------------------------------------------------------------------------
