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
# File: mainframe.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import webbrowser
import logging

import annotationdata.io
import audiodata.io

from sp_glob import program,version,copyright,license
from sp_glob import PLUGIN_PATH

# panels
from wxgui.panels.filetree     import FiletreePanel
from wxgui.panels.aannotations import AnnotationsPanel
from wxgui.panels.components   import ComponentsPanel
from wxgui.panels.plugins      import PluginPanel

# views and frames
from wxgui.dialogs.msgdialogs  import ShowInformation
from wxgui.views.about         import AboutBox
from wxgui.views.feedback      import ShowFeedbackDialog
from wxgui.views.settings      import SettingsDialog
from wxgui.frames.helpbrowser  import HelpBrowser

from wxgui.ui.CustomStatus     import CustomStatusBar

from wxgui.cutils.imageutils  import spBitmap

from wxgui.sp_consts import MIN_FRAME_W
from wxgui.sp_consts import MIN_FRAME_H
from wxgui.sp_consts import FRAME_H
from wxgui.sp_consts import PANEL_W
from wxgui.sp_consts import PREFS_FILE
from wxgui.sp_consts import TB_ICONSIZE
from wxgui.sp_consts import MENU_ICONSIZE

from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE

# action icons
from wxgui.sp_icons import APP_ICON
from wxgui.sp_icons import ABOUT_ICON
from wxgui.sp_icons import BUG_ICON
from wxgui.sp_icons import EXIT_ICON
from wxgui.sp_icons import FEEDBACK_ICON
from wxgui.sp_icons import HELP_ICON
from wxgui.sp_icons import PLUGIN_ICON
from wxgui.sp_icons import SETTINGS_ICON
from wxgui.sp_icons import WEB_ICON

# file icons
from wxgui.sp_icons import ADD_FILE_ICON
from wxgui.sp_icons import ADD_DIR_ICON
from wxgui.sp_icons import REMOVE_ICON
from wxgui.sp_icons import DELETE_ICON
from wxgui.sp_icons import EXPORT_AS_ICON
from wxgui.sp_icons import EXPORT_ICON

# -----------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------

VIEW_TOOLBAR_ID    = wx.NewId()
VIEW_STATUSBAR_ID  = wx.NewId()

ID_FRAME_PLUGIN    = wx.NewId()
ID_ADDDIR          = wx.NewId()
ID_EXPORT          = wx.NewId()
ID_HOME            = wx.NewId()
ID_DOC             = wx.NewId()
ID_TRACK           = wx.NewId()
ID_FEEDBACK        = wx.NewId()

# -----------------------------------------------------------------------
# S P P A S  Graphical User Interface... is here!
# -----------------------------------------------------------------------

class FrameSPPAS( wx.Frame ):
    """
    @authors: Brigitte Bigi, Cazembe Henry, Tatsuya Watanabe
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: SPPAS Main frame.

    SPPAS Graphical User Interface... is here!

    """

    def __init__( self, preferencesIO ):
        """
        Constructor, with default parameters and preferences.

        @param preferences (Preferences_IO)

        """
        wx.Frame.__init__(self, None, -1, title=FRAME_TITLE, style=FRAME_STYLE)

        # To enable translations of wx stock items.
        #self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)

        # Members
        self._prefsIO = preferencesIO

        # Set title and icon of the frame
        self._init_infos()

        # Creates the menubar, toolbar, status bar and the client panel
        self._init_frame()

        # Frame properties
        self._frame_properties()

        # Events of this frame
        wx.EVT_CLOSE(self, self.OnExit)

        self.Show( True )

    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # ------------------------------------------------------------------------

    def _init_infos( self ):
        """
        Set the title and the icon.

        """
        wx.GetApp().SetAppName( "sppas" )

        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(APP_ICON) )
        self.SetIcon(_icon)

        # colors
        self.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR'))

    # ------------------------------------------------------------------------

    def _init_frame(self):
        """
        Initializes the frame.
        Creates the default about, menubar, toolbar and status bar.

        """
        # Create the about box
        self._about = AboutBox()

        # Create the menu
        menubar = self._create_menu()

        # Create the status bar
        self._create_statusbar()

        # Create the toolbar
        self._create_toolbar()

        # wxBug: Have to set the menubar at the very end or the automatic
        # MDI "window" menu doesn't get put in the right place when the
        # services add new menus to the menubar
        if wx.Platform == '__WXMAC__':
            self.SetMenuBar(menubar)

        self._mainpanel = self._create_content( self )

        if wx.Platform != '__WXMAC__':
            self.SetMenuBar(menubar)

    # ------------------------------------------------------------------------

    def _frame_properties(self):
        """
        Fix frame size (adjust size depending on screen capabilities).

        """
        self.SetSizeHints(MIN_FRAME_W, MIN_FRAME_H)
        (w,h) = wx.GetDisplaySize()
        height = min(FRAME_H, h)
        width  = min(FRAME_H*w/h, w)

        self.SetSize( wx.Size(width,height) )
        self.Centre()
        self.Enable()
        self.SetFocus()

    # ------------------------------------------------------------------------

    def _create_menu(self):
        """
        Create the menu bar and return it.

        """
        menubar = wx.MenuBar()

        # All Menus
        fileMenu = wx.Menu()
        prefMenu = wx.Menu()
        helpMenu = wx.Menu()

        # Items of the menu "File"
        addfileItem = wx.MenuItem(fileMenu, wx.ID_ADD,    'Add file\tCtrl+A', 'Add files into the list')
        adddirItem  = wx.MenuItem(fileMenu, ID_ADDDIR,    'Add directory\tCtrl+Shift+A')
        removeItem  = wx.MenuItem(fileMenu, wx.ID_REMOVE, "Remove files\tDel")
        deleteItem  = wx.MenuItem(fileMenu, wx.ID_DELETE, "Delete files\tShift+Del")
        copyItem    = wx.MenuItem(fileMenu, wx.ID_COPY,   "Copy files\tCtrl+C")
        exportItem  = wx.MenuItem(fileMenu, ID_EXPORT,    "Export files\tCtrl+E")
        if wx.Platform == '__WXMAC__':
            exitItem = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q', 'Exits this program')
        else:
            exitItem = wx.MenuItem(fileMenu, wx.ID_EXIT, 'E&xit\tCtrl+Q', 'Exits this program')

        addfileItem.SetBitmap( spBitmap(ADD_FILE_ICON,  MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        adddirItem.SetBitmap(  spBitmap(ADD_DIR_ICON,   MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        removeItem.SetBitmap(  spBitmap(REMOVE_ICON,    MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        deleteItem.SetBitmap(  spBitmap(DELETE_ICON,    MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        copyItem.SetBitmap(    spBitmap(EXPORT_AS_ICON, MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        exportItem.SetBitmap(  spBitmap(EXPORT_ICON,    MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        exitItem.SetBitmap(    spBitmap(EXIT_ICON,      MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )

        fileMenu.AppendItem(addfileItem)
        fileMenu.AppendItem(adddirItem)
        fileMenu.AppendItem(removeItem)
        fileMenu.AppendItem(deleteItem)
        fileMenu.AppendItem(copyItem)
        fileMenu.AppendItem(exportItem)
        fileMenu.AppendSeparator()
        fileMenu.AppendItem(exitItem)

        # Items of the menu "Preferences"
        settingItem = wx.MenuItem(prefMenu, wx.ID_PREFERENCES, 'Settings',  'Fix settings (colors, fonts...)')
        settingItem.SetBitmap( spBitmap(SETTINGS_ICON, MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )

        prefMenu.AppendItem( settingItem )
        prefMenu.AppendSeparator()
        prefMenu.AppendCheckItem(VIEW_STATUSBAR_ID, '&Status Bar', 'Shows or hides the status bar')
        prefMenu.AppendCheckItem(VIEW_TOOLBAR_ID,   '&Toolbar',    'Shows or hides the toolbar')

        # Items of the menu Help
        helpItem  = wx.MenuItem(helpMenu, wx.ID_HELP,  '&Help browser...\tF1')
        aboutItem = wx.MenuItem(helpMenu, wx.ID_ABOUT, '&About' + ' ' + wx.GetApp().GetAppName()+"...\tF2")
        homeItem  = wx.MenuItem(helpMenu, ID_HOME,     'Project Homepage...' , 'Visit the project homepage.')
        docItem   = wx.MenuItem(helpMenu, ID_DOC,      'Online Documentation...' , 'Open the documentation in a web browser.')
        trackItem = wx.MenuItem(helpMenu, ID_TRACK,    'Bug tracker...' , 'Declare a bug.')
        feedbackItem = wx.MenuItem(helpMenu, ID_FEEDBACK, 'Give Feedback...' , 'Send information, or any suggestions by email.')

        aboutItem.SetBitmap( spBitmap(ABOUT_ICON, MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        helpItem.SetBitmap(  spBitmap(HELP_ICON,  MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        homeItem.SetBitmap(  spBitmap(APP_ICON,   MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        docItem.SetBitmap(   spBitmap(WEB_ICON,   MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        trackItem.SetBitmap( spBitmap(BUG_ICON,   MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        feedbackItem.SetBitmap( spBitmap(FEEDBACK_ICON, MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))

        helpMenu.AppendItem( helpItem )
        helpMenu.AppendItem( aboutItem )
        helpMenu.AppendItem( homeItem )
        helpMenu.AppendItem( docItem )
        helpMenu.AppendItem( trackItem )
        helpMenu.AppendItem( feedbackItem )

        # Append all menus in the menubar
        menubar.Append(fileMenu, '&File')         # Alt+F
        menubar.Append(prefMenu, '&Preferences')  # Alt+P
        menubar.Append(helpMenu, "&Help")         # Alt+H to get the menu

        # Set the menu to the frame
        self.SetMenuBar(menubar)

        # Must be AFTER SetMenuBar because wx can not apply a SetForeground / SetBackground to an un-attached menu!
        menubar.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        menubar.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        menubar.SetFont(self._prefsIO.GetValue('M_FONT'))
        # Must be also applied to all items! TODO

        # Events
        eventslist = [ wx.ID_ADD, ID_ADDDIR, wx.ID_REMOVE, wx.ID_DELETE, wx.ID_COPY, ID_EXPORT, wx.ID_EXIT, wx.ID_ABOUT, wx.ID_HELP, ID_HOME, ID_DOC, ID_TRACK, ID_FEEDBACK, wx.ID_PREFERENCES, VIEW_TOOLBAR_ID, VIEW_STATUSBAR_ID ]
        for event in eventslist:
            wx.EVT_MENU(self, event, self.ProcessEvent)

        wx.EVT_UPDATE_UI(self, VIEW_TOOLBAR_ID,   self.OnUpdateViewToolBar)
        wx.EVT_UPDATE_UI(self, VIEW_STATUSBAR_ID, self.OnUpdateViewStatusBar)

        return menubar

    # -----------------------------------------------------------------------

    def _create_statusbar(self):
        """
        Creates a customized a StatusBar.

        """
        sb = CustomStatusBar(self)
        sb.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        sb.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        sb.SetFont(self._prefsIO.GetValue('M_FONT'))
        sb.SetStatusText("Welcome to "+program+" - version "+version, 0)
        sb.SetStatusText(copyright, 1)
        sb.SetStatusText(license, 2)
        self.SetStatusBar(sb)
        self.GetStatusBar().Show(wx.ConfigBase_Get().ReadInt("ViewStatusBar", True))

    # ------------------------------------------------------------------------

    def _create_toolbar(self):
        """
        Creates the default toolbar.

        """
        toolbar = self.CreateToolBar(style=wx.TB_TEXT|wx.TB_FLAT|wx.TB_DOCKABLE|wx.TB_NODIVIDER)

        toolbar.AddLabelTool(wx.ID_EXIT, 'Exit', spBitmap(EXIT_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        toolbar.AddSeparator()
        toolbar.AddLabelTool(wx.ID_PREFERENCES, 'Settings', spBitmap(SETTINGS_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        toolbar.AddLabelTool(ID_FRAME_PLUGIN, 'Plug-in', spBitmap(PLUGIN_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')), shortHelp="Import a plugin")
        toolbar.AddLabelTool(wx.ID_ABOUT, 'About', spBitmap(ABOUT_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        toolbar.AddLabelTool(wx.ID_HELP,  'Help', spBitmap(HELP_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))

        toolbar.SetToolSeparation(5)
        self.SetToolBar(toolbar)

        # Must be AFTER SetToolBar because wx can not apply a SetForeground / SetBackground to an un-attached toolbar!
        toolbar.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        toolbar.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        #toolbar.SetFont(self._prefsIO.GetValue('M_FONT'))
        toolbar.Realize()

        # events
        eventslist = [ wx.ID_NEW, wx.ID_EXIT, wx.ID_PREFERENCES, wx.ID_ABOUT, wx.ID_HELP, ID_FRAME_PLUGIN ]
        for event in eventslist:
            wx.EVT_TOOL(self, event, self.ProcessEvent)

    # ------------------------------------------------------------------------

    def _create_accelerators(self):
        """
        Creates the list of accelerators.

        Most power users prefer to use keyboard shortcuts rather than digging
        through convoluted menus or icons.

        """
        # Quit with ATL+F4
        accelQ = wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F4, wx.ID_EXIT)

        accel_tbl = wx.AcceleratorTable([ accelQ ])
        self.SetAcceleratorTable(accel_tbl)

    # ------------------------------------------------------------------------

    def _create_content(self, parent):
        """
        Create the frame content.

        """
        panel = wx.SplitterWindow(parent, -1, style=wx.SP_3DSASH)
        #panel.SetMinimumPaneSize( 200 )
        panel.SetSashGravity(0.3)

        #### Left splitter creation ####

        self.flp = FiletreePanel(panel, self._prefsIO)

        #### Right splitter creation ####

        self._right_panel = wx.Panel(panel, id=wx.ID_ANY, style=wx.NO_BORDER)

        self.aap = AnnotationsPanel(self._right_panel, self._prefsIO)
        self.ccp = ComponentsPanel(self._right_panel, self._prefsIO)
        self.ppp = PluginPanel(self._prefsIO, PLUGIN_PATH, style=wx.SIMPLE_BORDER, parent=self._right_panel)

        right_panel_sizer = wx.GridBagSizer()
        right_panel_sizer.Add(self.aap, pos=(0, 0), flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        right_panel_sizer.Add(self.ccp, pos=(1, 0), flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        right_panel_sizer.Add(self.ppp, pos=(0, 1), span=(2, 2), flag=wx.EXPAND|wx.ALL)
        right_panel_sizer.AddGrowableCol(0)
        right_panel_sizer.AddGrowableRow(0, proportion=1)

        self._right_panel.SetSizer(right_panel_sizer)

        panel.SplitVertically( self.flp , self._right_panel , PANEL_W )

        return panel

    # ------------------------------------------------------------------------

    def _LayoutFrame(self):
        """
        Lays out the frame.

        """
        wx.LayoutAlgorithm().LayoutFrame(self, self._mainpanel)
        self._right_panel.SendSizeEvent()
        self.Refresh()

    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Callbacks to any kind of event
    # ------------------------------------------------------------------------

    def ProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.

        """

        ide = event.GetId()

        if ide == wx.ID_EXIT:
            self.OnExit(event)
            return True
        elif ide == wx.ID_PREFERENCES:
            self.OnSettings(event)
            return True
        elif ide == wx.ID_ABOUT:
            wx.AboutBox( self._about )
            return True
        elif ide == VIEW_TOOLBAR_ID:
            self.OnViewToolBar(event)
            return True
        elif ide == VIEW_STATUSBAR_ID:
            self.OnViewStatusBar(event)
            return True
        elif ide == wx.ID_ADD:
            self.flp.OnAddFile(event)
            return True
        elif ide == ID_ADDDIR:
            self.flp.OnAddDir(event)
            return True
        elif ide == wx.ID_REMOVE:
            self.flp.OnRemove(event)
            return True
        elif ide == wx.ID_DELETE:
            self.flp.OnDelete(event)
            return True
        elif ide == wx.ID_COPY:
            self.flp.OnSaveAs(event)
            return True
        elif ide == ID_EXPORT:
            self.flp.OnExport(event)
            return True
        elif ide == ID_FRAME_PLUGIN:
            self.ppp.Import()
            return True
        elif ide == wx.ID_HELP:
            HelpBrowser( self, self._prefsIO )
            return True
        elif ide == wx.ID_HELP or ide == ID_DOC or ide == ID_HOME or ide == ID_TRACK:
            self.OnExternalLink(event)
            return True
        elif ide == ID_FEEDBACK:
            ShowFeedbackDialog(self, preferences=self._prefsIO)
            return True

        return wx.GetApp().ProcessEvent(event)

    # ------------------------------------------------------------------------

    def ProcessUpdateUIEvent(self, event):
        """
        Processes a UI event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.

        """
        ide = event.GetId()

        if ide == VIEW_TOOLBAR_ID:
            self.OnUpdateViewToolBar(event)
            return True
        elif ide == VIEW_STATUSBAR_ID:
            self.OnUpdateViewStatusBar(event)
            return True

        return wx.GetApp().ProcessUpdateUIEvent(event)

    # ------------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnViewToolBar(self, event):
        """
        Toggles whether the ToolBar is visible.

        """
        try:
            t = self.GetToolBar()
        except Exception:
            # the toolbar was not created with the frame
            return False

        t.Show(not t.IsShown())
        # send size event to force the whole frame layout
        self.SendSizeEvent()

    # ------------------------------------------------------------------------

    def OnUpdateViewToolBar(self, event):
        """
        Updates the View ToolBar menu item.

        """
        try:
            t = self.GetToolBar()
            if t is None: return False
        except Exception:
            # the toolbar was not created with the frame
            return False

        t.IsShown()
        event.Check(t.IsShown())
        # send size event to force the whole frame layout
        self.SendSizeEvent()

    # ------------------------------------------------------------------------

    def OnViewStatusBar(self, event):
        """
        Toggles whether the StatusBar is visible.

        """
        try:
            s = self.GetStatusBar()
            if s is None: return False
        except Exception:
            # the statusbar was not created with the frame
            return False

        s.Show(not self.GetStatusBar().IsShown())
        self._LayoutFrame()

    # ------------------------------------------------------------------------

    def OnUpdateViewStatusBar(self, event):
        """
        Updates the View StatusBar menu item.

        """
        try:
            s = self.GetStatusBar()
            if s is None: return False
        except Exception:
            # the statusbar was not created with the frame
            return False

        event.Check(s.IsShown())
        self._LayoutFrame()

    # ------------------------------------------------------------------------

    def OnSettings(self, event):
        """
        Open the Settings dialog.

        """
        import copy
        p = copy.deepcopy( self._prefsIO )
        #p = self._prefsIO.Copy() # does not work!

        prefdlg = SettingsDialog( self, p )
        res = prefdlg.ShowModal()
        if res == wx.ID_OK:
            self.SetPrefs( prefdlg.GetPreferences() )

        prefdlg.Destroy()

    # ------------------------------------------------------------------------

    def OnExternalLink(self, evt):
        """
        Open the web browser, go to a specific location.

        """
        eid = evt.GetId()

        if eid == ID_HOME:
            url="http://www.sppas.org/"

        elif eid == ID_DOC:
            url="http://www.sppas.org/documentation.html"

        elif eid == ID_TRACK:
            url="https://github.com/brigittebigi/sppas/issues/"
            message= 'Your web browser will be opened.\nFirst, check if the issue is not already declared in the list.\nThen, declare an issue by clicking on the button "New Issue"'
            ShowInformation( self, self._prefsIO, message)

        else:
            evt.Skip()
            return

        # It seems under some cases when running under windows the call to
        # subprocess in webbrowser will fail and raise an exception here. So
        # simply trap and ignore it.
        wx.BeginBusyCursor()
        try:
            webbrowser.open(url,1)
        except:
            pass#self.SetStatusText("Error: Unable to open %s" % url)
        wx.EndBusyCursor()

    # -----------------------------------------------------------------------

    def OnExit(self, evt):
        """
        Close the frame.

        """
        logging.info("Good bye... Hope to see you soon!")
        self.Destroy()

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Functions
    # -----------------------------------------------------------------------

    def SetPrefs(self, prefs):
        """
        Set new preferences.

        """
        self._prefsIO = prefs
        self.GetToolBar().SetBackgroundColour(   self._prefsIO.GetValue( 'M_BG_COLOUR' ))
        self.GetStatusBar().SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ))
        self.GetMenuBar().SetBackgroundColour(   self._prefsIO.GetValue( 'M_BG_COLOUR' ))

        self.GetToolBar().SetForegroundColour(   self._prefsIO.GetValue( 'M_FG_COLOUR' ))
        self.GetStatusBar().SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ))
        self.GetMenuBar().SetForegroundColour(   self._prefsIO.GetValue( 'M_FG_COLOUR' ))

        self.GetToolBar().SetFont(   self._prefsIO.GetValue( 'M_FONT' ))
        self.GetStatusBar().SetFont( self._prefsIO.GetValue( 'M_FONT' ))
        self.GetMenuBar().SetFont(   self._prefsIO.GetValue( 'M_FONT' ))

        # change to the children panels
        self.flp.SetPrefs( self._prefsIO )
        self.aap.SetPrefs( self._prefsIO )
        self.ccp.SetPrefs( self._prefsIO )
        self.ppp.SetPrefs( self._prefsIO )
        self._LayoutFrame()

    # -----------------------------------------------------------------------

    def GetSelected(self, extension):
        """
        Return the list of selected files in FLP.

        """
        return self.flp.GetSelected(extension)

    # -----------------------------------------------------------------------

    def GetTrsSelection(self):
        """
        Return the list of annotated files selected in the FLP.

        """
        selection = []
        for ext in annotationdata.io.extensions:
            selection.extend(self.flp.GetSelected(ext))
        return selection

    # -----------------------------------------------------------------------

    def GetAudioSelection(self):
        """
        Return the list of audio files selected in the FLP.

        """
        selection = []
        for ext in audiodata.io.extensions:
            selection.extend( self.flp.GetSelected(ext) )
        return selection

    # -----------------------------------------------------------------------

    def RefreshTree(self, filelist=None):
        """
        Refresh the tree of the FLP.

        """
        self.flp.RefreshTree(filelist)

    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------
