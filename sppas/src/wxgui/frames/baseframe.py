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
# File: baseframe.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import logging
import webbrowser

from sp_glob import SETTINGS_FILE

from wxgui.sp_icons import SETTINGS_ICON
from wxgui.sp_icons import COMPONENTS_ICON
from wxgui.sp_icons import ADD_FILE_ICON
from wxgui.sp_icons import REMOVE_ICON
from wxgui.sp_icons import TAB_NEW_ICON
from wxgui.sp_icons import TAB_CLOSE_ICON
from wxgui.sp_icons import ABOUT_ICON
from wxgui.sp_icons import LOGOUT_ICON
from wxgui.sp_icons import EXIT_ICON
from wxgui.sp_icons import HELP_ICON
from wxgui.sp_icons import APP_ICON
from wxgui.sp_icons import BUG_ICON
from wxgui.sp_icons import FEEDBACK_ICON
from wxgui.sp_icons import WEB_ICON

from wxgui.sp_consts  import DEFAULT_APP_NAME
from wxgui.sp_consts  import TB_ICONSIZE
from wxgui.sp_consts  import MENU_ICONSIZE
from wxgui.sp_consts  import MIN_PANEL_W
from wxgui.sp_consts  import MIN_FRAME_W
from wxgui.sp_consts  import MIN_FRAME_H
from wxgui.sp_consts  import FRAME_STYLE
from wxgui.sp_consts  import FRAME_TITLE

from wxgui.ui.CustomEvents     import FileWanderEvent, spEVT_FILE_WANDER
from wxgui.ui.CustomEvents     import FileCheckEvent
from wxgui.ui.CustomEvents     import NotebookNewPageEvent
from wxgui.ui.CustomEvents     import NotebookClosePageEvent
from wxgui.ui.CustomEvents     import SettingsEvent
from wxgui.ui.CustomStatus     import CustomStatusBar

from wxgui.dialogs.msgdialogs  import ShowYesNoQuestion, ShowInformation
from wxgui.views.about         import AboutBox
from wxgui.views.settings      import SettingsDialog
from wxgui.views.feedback      import ShowFeedbackDialog
from wxgui.frames.helpbrowser  import HelpBrowser

from wxgui.structs.prefs       import Preferences_IO
from wxgui.structs.themes      import Themes, BaseTheme

from wxgui.panels.filemanager   import FileManager
from wxgui.clients.baseclient   import BaseClient
import wxgui.dialogs.filedialogs as filedialogs

from wxgui.cutils.imageutils import spBitmap


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

VIEW_TOOLBAR_ID     = wx.NewId()
VIEW_STATUSBAR_ID   = wx.NewId()

TAB_NEW_ID          = wx.NewId()
TAB_CLOSE_ID        = wx.NewId()

ID_HOME            = wx.NewId()
ID_DOC             = wx.NewId()
ID_TRACK           = wx.NewId()
ID_FEEDBACK        = wx.NewId()

# ----------------------------------------------------------------------------

class ComponentFrame( wx.Frame ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Component main frame (base class).

    The Component base main frame. This frames is made of:
    - a menu
    - a toolbar
    - a statusbar
    - a panel at left, which is a file manager (with check buttons)
    - a panel at right, which contains the client.

    """
    def __init__(self, parent, idf, args={}):
        """
        Creates a new ComponentFrame instance.

        """

        wx.Frame.__init__(self, parent, idf, title=FRAME_TITLE+" - Component", style=FRAME_STYLE)

        # To enable translations of wx stock items.
        #self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)

        # Members
        self._init_members( args )

        # Set title and icon of the frame
        self._init_infos( args )

        # Creates the default menubar, toolbar, and status bar
        # and the client panel
        self._init_frame( )

        # Frame properties
        self._frame_properties()

        # Events of this frame
        wx.EVT_CLOSE(self, self.OnExitApp)

        # events sent by the file manager
        spEVT_FILE_WANDER(self, self.OnFileWander)

        self._LayoutFrame()
        self.Show(True)

    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # ------------------------------------------------------------------------

    def _init_members( self, args ):
        """
        Sets the members settings.

        """
        if "prefs" in args.keys():
            self._prefsIO = args["prefs"]
        else:
            # Try to get prefs from a file, or fix default values.
            self._prefsIO = Preferences_IO( SETTINGS_FILE )
            if self._prefsIO.Read() is False:
                self._prefsIO.SetTheme( BaseTheme() )

        self._fmtype = "DATAFILES"
        if "type" in args.keys():
            self._fmtype = args['type']
            # expected: "DATAFILES", "SOUNDFILES", "ANYFILES"

    # ------------------------------------------------------------------------

    def _init_infos( self, args ):
        """
        Sets the title and the icon.

        If args contains title, get it... or use the default.

        """
        # Set title
        _app = DEFAULT_APP_NAME
        if "title" in args.keys():
            _app = args["title"]
        self.SetTitle( _app )
        wx.GetApp().SetAppName( _app )

        # Set icon
        _iconname = COMPONENTS_ICON
        if "icon" in args.keys():
            _iconname = args["icon"]

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(_iconname) )
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

        # Create the toolbar
        self._create_toolbar()

        # Create the accelerators
        self._create_accelerators()

        # Create the panels and set the menu
        if wx.Platform == '__WXMAC__':
            self.SetMenuBar(menubar)  # wxBug: Have to set the menubar at the very end or the automatic MDI "window" menu doesn't get put in the right place when the services add new menus to the menubar

        self._mainpanel = self._create_panels( self )

        if wx.Platform != '__WXMAC__':
            self.SetMenuBar(menubar)  # wxBug: Have to set the menubar at the very end or the automatic MDI "window" menu doesn't get put in the right place when the services add new menus to the menubar

        # Create the status bar
        self._create_statusbar()

    # ------------------------------------------------------------------------

    def _frame_properties(self):
        """
        Fix frame size (adjust size depending on screen capabilities).

        """
        self.SetSizeHints(MIN_FRAME_W, MIN_FRAME_H)
        (w,h) = wx.GetDisplaySize()
        self.SetSize( wx.Size(w*0.75,h*0.75) )
        self.Centre()
        self.Enable()
        self.SetFocus()

    # ------------------------------------------------------------------------

    def _create_menu(self):
        """
        Creates a menu with bitmaps and accelerators and return it.

        It creates the following menu:
        - File
            - Add
            - Remove
            - New tab
            - Close tab
            - Quit
        - Preferences
            - Settings
            - Show/Hide Status Bar
            - Show/Hide Toolbar
        - Help
            - Help
            - About

        """
        menubar = wx.MenuBar()

        # All Menus
        fileMenu = wx.Menu()
        prefMenu = wx.Menu()
        helpMenu = wx.Menu()

        # Items of the menu "File"

        addItem      = wx.MenuItem(fileMenu, wx.ID_ADD,    'Add file\tCtrl+A',    'Add files into the list')
        removeItem   = wx.MenuItem(fileMenu, wx.ID_REMOVE, 'Remove file\tCtrl+R', 'Remove files of the list')
        tabnewItem   = wx.MenuItem(fileMenu, TAB_NEW_ID,   'New tab\tCtrl+T',     'Open a new page in the notebook')
        tabcloseItem = wx.MenuItem(fileMenu, TAB_CLOSE_ID, 'Close tab\tCtrl+W', 'Close the selected page of the notebook')
        if wx.Platform == '__WXMAC__':
            exitItem = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q', 'Closes this program')
        else:
            exitItem = wx.MenuItem(fileMenu, wx.ID_EXIT, 'E&xit\tCtrl+Q', 'Closes this program')

        addItem.SetBitmap( spBitmap(ADD_FILE_ICON,   MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        removeItem.SetBitmap( spBitmap(REMOVE_ICON,  MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        tabnewItem.SetBitmap( spBitmap(TAB_NEW_ICON, MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        tabcloseItem.SetBitmap( spBitmap(TAB_CLOSE_ICON, MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        exitItem.SetBitmap( spBitmap(EXIT_ICON, MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )

        fileMenu.AppendItem( addItem )
        fileMenu.AppendItem( removeItem )
        fileMenu.AppendSeparator()
        fileMenu.AppendItem( tabnewItem )
        fileMenu.AppendItem( tabcloseItem )
        fileMenu.AppendSeparator()
        fileMenu.AppendItem( exitItem )

        # Items of the menu "Preferences"

        settingItem = wx.MenuItem(prefMenu, wx.ID_PREFERENCES, 'Settings',  'Fix settings (colors, fonts...)')
        settingItem.SetBitmap( spBitmap(SETTINGS_ICON, MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )

        prefMenu.AppendItem( settingItem )
        prefMenu.AppendSeparator()
        prefMenu.AppendCheckItem(VIEW_STATUSBAR_ID, '&Status Bar', 'Shows or hides the status bar')
        prefMenu.AppendCheckItem(VIEW_TOOLBAR_ID,   '&Toolbar',    'Shows or hides the toolbar')

        # Items of the menu "Help"
        # Items of the menu Help
        helpItem  = wx.MenuItem(helpMenu, wx.ID_HELP,  '&Help browser...\tF1')
        aboutItem = wx.MenuItem(helpMenu, wx.ID_ABOUT, '&About' + ' ' + wx.GetApp().GetAppName()+"...\tF2")
        homeItem  = wx.MenuItem(helpMenu, ID_HOME,     'Homepage...' , 'Visit the project homepage.')
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
        menubar.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR')) # do anything!
        menubar.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR')) # do anything!
        menubar.SetFont(self._prefsIO.GetValue('M_FONT')) #  # does not work with windows, bug in wx?

        # Events
        eventslist = [ wx.ID_ADD, wx.ID_REMOVE, TAB_NEW_ID, TAB_CLOSE_ID, wx.ID_EXIT, wx.ID_PREFERENCES, wx.ID_ABOUT, wx.ID_HELP, ID_HOME, ID_DOC, ID_TRACK, ID_FEEDBACK, VIEW_TOOLBAR_ID, VIEW_STATUSBAR_ID ]
        for event in eventslist:
            wx.EVT_MENU(self, event, self.ProcessEvent)

        wx.EVT_UPDATE_UI(self, VIEW_TOOLBAR_ID,   self.OnUpdateViewToolBar)
        wx.EVT_UPDATE_UI(self, VIEW_STATUSBAR_ID, self.OnUpdateViewStatusBar)

        return menubar

    # ------------------------------------------------------------------------

    def _create_toolbar(self):
        """
        Creates the default toolbar.

        """

        toolbar = self.CreateToolBar(style=wx.TB_TEXT)

        # Define the size of the icons and buttons
        iconSize = (TB_ICONSIZE, TB_ICONSIZE)
        # Set the size of the buttons
        toolbar.SetToolBitmapSize(iconSize)

        if self.GetParent() is not None:
            toolbar.AddLabelTool(wx.ID_EXIT, 'Close', spBitmap(LOGOUT_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        else:
            toolbar.AddLabelTool(wx.ID_EXIT, 'Exit', spBitmap(EXIT_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        toolbar.AddSeparator()
        toolbar.AddLabelTool(wx.ID_ADD, 'Add', spBitmap(ADD_FILE_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        toolbar.AddLabelTool(wx.ID_REMOVE, 'Remove', spBitmap(REMOVE_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        toolbar.AddSeparator()
        toolbar.AddLabelTool(TAB_NEW_ID, 'New tab', spBitmap(TAB_NEW_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        toolbar.AddLabelTool(TAB_CLOSE_ID, 'Close tab', spBitmap(TAB_CLOSE_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        toolbar.AddSeparator()
        toolbar.AddLabelTool(wx.ID_PREFERENCES, 'Settings', spBitmap(SETTINGS_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        toolbar.AddSeparator()
        toolbar.AddLabelTool(wx.ID_HELP,  'Help',  spBitmap(HELP_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        toolbar.AddLabelTool(wx.ID_ABOUT, 'About', spBitmap(ABOUT_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )

        toolbar.SetToolSeparation(10)
        toolbar.Realize()
        self.SetToolBar(toolbar)

        # colors and font
        toolbar.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        toolbar.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        toolbar.SetFont(self._prefsIO.GetValue('M_FONT'))

        # events
        eventslist = [ wx.ID_NEW, wx.ID_EXIT, wx.ID_ADD, wx.ID_REMOVE, TAB_NEW_ID, TAB_CLOSE_ID, wx.ID_PREFERENCES, wx.ID_HELP, wx.ID_ABOUT ]
        for event in eventslist:
            wx.EVT_TOOL(self, event, self.ProcessEvent)

    # ------------------------------------------------------------------------

    def _create_accelerators(self):
        """
        Creates the list of accelerators.

        Most power users prefer to use keyboard shortcuts rather than digging
        through convoluted menus or icons.

        """
        return
        # Quit with ATL+F4
        accelQ = wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F4, wx.ID_EXIT)

        accel_tbl = wx.AcceleratorTable([ accelQ ])
        self.SetAcceleratorTable(accel_tbl)

    # ------------------------------------------------------------------------

    def _create_statusbar(self):
        """
        Creates the customized StatusBar.

        """

        sb = CustomStatusBar(self)
        sb.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        sb.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        sb.SetFont(self._prefsIO.GetValue('M_FONT'))
        sb.SetStatusText("...", 0)

        self.SetStatusBar(sb)
        self.GetStatusBar().Show(wx.ConfigBase_Get().ReadInt("ViewStatusBar", True))

    # ------------------------------------------------------------------------

    def _create_panels(self, parent):
        """
        Creates the children panels:
            - filepanel (left)
            - clientpanel (right).

        """
        _panel = wx.SplitterWindow(parent, -1)
        _panel.SetMinimumPaneSize( MIN_PANEL_W )

        # Left: a list of files
        self._filepanel = self.CreateFileManager( _panel, self._prefsIO )

        # Right: a client
        self._clientpanel = self.CreateClient( _panel, self._prefsIO )

        # Split
        w,h = self._filepanel.GetSize()
        if w < MIN_PANEL_W:
            w = MIN_PANEL_W
        _panel.SplitVertically(self._filepanel, self._clientpanel, w)

        #self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSize, _panel)

        return _panel

    # ------------------------------------------------------------------------

    def _LayoutFrame(self):
        """
        Lays out the frame.

        """

        wx.LayoutAlgorithm().LayoutFrame(self, self._mainpanel)
        self._clientpanel.SendSizeEvent()
        self.Refresh()

    # ------------------------------------------------------------------------
    # Public method to create the GUI
    # ------------------------------------------------------------------------

    def CreateClient(self, parent, prefsIO):
        """
        Create the client panel and return it.
        Must be overridden.

        @param parent (wx.Frame)
        @param prefsIO (Preferences_IO)

        @return wx.Panel

        """

        raise NotImplementedError

    # ------------------------------------------------------------------------

    def CreateFileManager(self, parent, prefsIO):
        """
        Create the file manager panel and return it.
        Can be overridden.

        @param parent (wx.Frame)
        @param prefsIO (Preferences_IO)

        @return wx.Panel

        """

        return FileManager( parent, prefsIO=self._prefsIO)

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

        if ide == wx.ID_ADD:
            # add a file in the file manager
            self.OnAdd(event)
            return True
        elif ide == wx.ID_REMOVE:
            # remove all checked files of the file manager, delete the instances
            self.OnRemove(event)
            return True
        elif ide == wx.ID_EXIT:
            # quit the application
            self.OnClose(event)
            return True

        elif ide == wx.ID_PREFERENCES:
            # customize
            self.OnSettings(event)

        elif ide == TAB_NEW_ID:
            # new tab in the client
            self.OnNewTab(event)

        elif ide == TAB_CLOSE_ID:
            # close tab in the client
            self.OnCloseTab(event)

        elif ide == VIEW_TOOLBAR_ID:
            # enable/disable toolbar
            self.OnViewToolBar(event)
            return True

        elif ide == VIEW_STATUSBAR_ID:
            # enable/disable statusbar
            self.OnViewStatusBar(event)
            return True

        elif ide == wx.ID_HELP or ide == ID_DOC or ide == ID_HOME or ide == ID_TRACK:
            self.OnExternalLink(event)
            return True

        elif ide == wx.ID_ABOUT:
            # open the about frame
            self.OnAbout(event)
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
    # File management... Callbacks to menu/toolbar/accelerator
    # ------------------------------------------------------------------------

    def OnAdd(self, event):
        """
        Received an event to add new files.

        """
        if self._fmtype == "DATAFILES":
            self.AddFiles( filedialogs.OpenAnnotationFiles() )

        elif self._fmtype == "SOUNDFILES":
            self.AddFiles( filedialogs.OpenSoundFiles() )

        else:
            self.AddFiles( filedialogs.OpenAnyFiles() )

    # ------------------------------------------------------------------------

    def OnRemove(self, event):
        """
        Received an event to close files:
        ask the file manager to remove them.

        """

        evt = FileWanderEvent(filename=None,status=False)
        evt.SetEventObject(self)
        wx.PostEvent(self._filepanel, evt)

    # ------------------------------------------------------------------------

    def OnExitApp(self, event):
        """
        Destroys the main frame which quits the wxPython application.
        Destroy without worrying about anything!

        """
        response = ShowYesNoQuestion( self, self._prefsIO, "Are you sure you want to quit?")
        if response == wx.ID_YES:
            logging.info('Bye bye... Hope to see you again!')
            self.Destroy()
        else:
            event.StopPropagation()

    # ------------------------------------------------------------------------

    def OnClose(self, event):
        """
        Close properly the client then exit.

        """
        closeEvent = wx.CloseEvent(wx.wxEVT_CLOSE_WINDOW, self.GetId())
        closeEvent.SetEventObject(self)
        wx.PostEvent(self._clientpanel, closeEvent)
        #self.Destroy() # this causes troubles to the client (access to dead objects)!
        self.Close()

    #-------------------------------------------------------------------------
    # Preferences... Callbacks
    #-------------------------------------------------------------------------

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
        except Exception:
            # the toolbar was not created with the frame
            return False

        r = t.IsShown()
        event.Check(t.IsShown())

        # send size event to force the whole frame layout
        self.SendSizeEvent()

    # ------------------------------------------------------------------------

    def OnViewStatusBar(self, event):
        """
        Toggles whether the StatusBar is visible.

        """

        self.GetStatusBar().Show(not self.GetStatusBar().IsShown())
        self._LayoutFrame()

    # ------------------------------------------------------------------------

    def OnUpdateViewStatusBar(self, event):
        """
        Updates the View StatusBar menu item.

        """

        event.Check(self.GetStatusBar().IsShown())

    #-------------------------------------------------------------------------
    # Client Callbacks
    #-------------------------------------------------------------------------

    def OnNewTab(self, event):
        """
        Add a page in the client.

        """
        evt = NotebookNewPageEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self._clientpanel, evt)

    #-------------------------------------------------------------------------

    def OnCloseTab(self, event):
        """
        Close a page in the client.

        """

        evt = NotebookClosePageEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self._clientpanel, evt)

    #-------------------------------------------------------------------------

    def OnFileAdded(self, event):
        """
        Add a file of the file manager.

        """
        self.AddFiles( [event.filename] )

    #-------------------------------------------------------------------------

    def OnFileClosed(self, event):
        """
        Remove of the file manager.

        """
        # Get the list of closed files and remove them of the file manager
        files = event.filenames

        for f in files:
            # Remove of the file manager
            evt = FileWanderEvent( filename=f, status=False )
            evt.SetEventObject(self)
            wx.PostEvent(self._filepanel, evt)

    #-------------------------------------------------------------------------
    # Help... Callbacks
    #-------------------------------------------------------------------------

    def OnAbout(self, event):
        """
        Open the About box.

        """
        wx.AboutBox( self._about )

    # ------------------------------------------------------------------------

    def OnSettings(self, event):
        """
        Open the Settings box.

        """
        import copy
        p = copy.deepcopy( self._prefsIO )
        #p = self._prefsIO.Copy() # does not work.

        prefdlg = SettingsDialog( self, p )
        res = prefdlg.ShowModal()
        if res == wx.ID_OK:
            self.SetPrefs( prefdlg.GetPreferences() )
            if self.GetParent() is not None:
                try:
                    self.GetParent().SetPrefs( prefdlg.GetPreferences() )
                except Exception:
                    pass
        prefdlg.Destroy()
        self._LayoutFrame()

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

    #-------------------------------------------------------------------------
    # Data management
    #-------------------------------------------------------------------------

    def AddFiles(self, files):
        """
        Add files into the file manager.

        @param files (list of String)

        """
        if len(files) > 0:
            # Get the list of files to open/view
            for f in files:
                # Add in the file manager
                evt = FileWanderEvent( filename=f, status=True )
                evt.SetEventObject(self)
                wx.PostEvent(self._filepanel, evt)

            self.Refresh()

    # ------------------------------------------------------------------------

    def OnFileWander(self, event):
        """
        We received an event: a file was added/removed.

        """
        owner = event.GetEventObject()
        f = event.filename
        s = event.status

        if owner == self._filepanel:
            event.SetEventObject(self)
            wx.PostEvent(self._clientpanel, event)
        else:
            evt = FileCheckEvent( filename=f, status=s )
            evt.SetEventObject(self)
            wx.PostEvent(self._filepanel, evt)

    #-------------------------------------------------------------------------
    # Other
    #-------------------------------------------------------------------------

    def DisplayTextInStatusbar(self, text):
        """
        Display a text in the default field of the status bar.

        """
        try:
            text = text.decode('utf8')
        except Exception:
            pass

        try:
            self.SetStatusText(text, 0)
        except Exception:
            logging.info('Got StatusText message: %s'%text)

    #-------------------------------------------------------------------------

    def StartTimeInStatusBar(self):
        """
        Start the date of the StatusBar.

        """
        self.GetStatusBar().StartTime()

    #-------------------------------------------------------------------------

    def StopTimeInStatusBar(self):
        """
        Stop the date of the StatusBar.

        """
        self.GetStatusBar().StopTime()

    #-------------------------------------------------------------------------

    def SetPrefs(self, prefs):
        """
        Fix new preferences.

        """
        self._prefsIO = prefs
        self.GetToolBar().SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ))
        self.GetStatusBar().SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ))
        self.GetMenuBar().SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ))

        self.GetToolBar().SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ))
        self.GetStatusBar().SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ))
        self.GetMenuBar().SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ))

        self.GetToolBar().SetFont(   self._prefsIO.GetValue( 'M_FONT' ))
        self.GetStatusBar().SetFont( self._prefsIO.GetValue( 'M_FONT' ))
        self.GetMenuBar().SetFont(   self._prefsIO.GetValue( 'M_FONT' ))

        # change to the children panels
        evt = SettingsEvent( prefsIO=self._prefsIO )
        evt.SetEventObject(self)
        wx.PostEvent(self._filepanel, evt)
        wx.PostEvent(self._clientpanel, evt)

    #-------------------------------------------------------------------------

#-----------------------------------------------------------------------------
