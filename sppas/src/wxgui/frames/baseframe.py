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

from sp_glob import SETTINGS_FILE

from wxgui.sp_icons                     import SETTINGS_ICON
from wxgui.sp_icons                     import COMPONENT_ICON
from wxgui.sp_icons                     import ADD_FILE_ICON
from wxgui.sp_icons                     import REMOVE_ICON
from wxgui.sp_icons                     import TAB_NEW_ICON
from wxgui.sp_icons                     import TAB_CLOSE_ICON
from wxgui.sp_icons                     import ABOUT_ICON
from wxgui.sp_icons                     import LOGOUT_ICON
from wxgui.sp_icons                     import EXIT_ICON

from wxgui.sp_consts                    import DEFAULT_APP_NAME

from wxgui.sp_consts                    import TB_ICONSIZE
from wxgui.sp_consts                    import MENU_ICONSIZE
from wxgui.sp_consts                    import MIN_PANEL_W
from wxgui.sp_consts                    import MIN_FRAME_W
from wxgui.sp_consts                    import MIN_FRAME_H
from wxgui.sp_consts                    import FRAME_STYLE
from wxgui.sp_consts                    import FRAME_TITLE

from wxgui.ui.CustomEvents              import FileWanderEvent, spEVT_FILE_WANDER
from wxgui.ui.CustomEvents              import FileCheckEvent
from wxgui.ui.CustomEvents              import NotebookNewPageEvent
from wxgui.ui.CustomEvents              import NotebookClosePageEvent
from wxgui.ui.CustomEvents              import SettingsEvent

from wxgui.ui.CustomStatus              import CustomStatusBar

from wxgui.views.about                  import AboutBox
from wxgui.views.settings               import SettingsDialog

from wxgui.structs.prefs                import Preferences_IO
from wxgui.structs.themes               import Themes, BaseTheme

from wxgui.panels.filemanager           import FileManager
from wxgui.clients.baseclient        import BaseClient
import wxgui.dialogs.filedialogs as filedialogs

from wxgui.cutils.imageutils import spBitmap


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

VIEW_TOOLBAR_ID     = wx.NewId()
VIEW_STATUSBAR_ID   = wx.NewId()

TAB_NEW_ID          = wx.NewId()
TAB_CLOSE_ID        = wx.NewId()

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

    def __init__(self, parent, id, args={}):
        """
        Creates a new ComponentFrame instance.

        """

        wx.Frame.__init__(self, parent, id, title=FRAME_TITLE+" - Component", style=FRAME_STYLE)

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

    # End __init__
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialise members
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

    # End _init_members
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
        _iconname = COMPONENT_ICON
        if "icon" in args.keys():
            _iconname = args["icon"]

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(_iconname) )
        self.SetIcon(_icon)

        # colors
        self.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR'))

    # End _init_infos
    # ------------------------------------------------------------------------


    def _init_frame(self):
        """
        Initialises the frame.

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

    # End _init_frame
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

    # End _frame_properties
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
        aboutItem = wx.MenuItem(helpMenu, wx.ID_ABOUT, '&About' + ' ' + wx.GetApp().GetAppName()+"...\tF2")
        aboutItem.SetBitmap( spBitmap(ABOUT_ICON, MENU_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )
        helpMenu.AppendItem(aboutItem)

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
        eventslist = [ wx.ID_ADD, wx.ID_REMOVE, TAB_NEW_ID, TAB_CLOSE_ID, wx.ID_EXIT, wx.ID_PREFERENCES, wx.ID_ABOUT, VIEW_TOOLBAR_ID, VIEW_STATUSBAR_ID ]
        for event in eventslist:
            wx.EVT_MENU(self, event, self.ProcessEvent)

        wx.EVT_UPDATE_UI(self, VIEW_TOOLBAR_ID,   self.OnUpdateViewToolBar)
        wx.EVT_UPDATE_UI(self, VIEW_STATUSBAR_ID, self.OnUpdateViewStatusBar)

        return menubar

    # End _create_menubar
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
        toolbar.AddLabelTool(wx.ID_ABOUT, 'About', spBitmap(ABOUT_ICON, TB_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')) )

        toolbar.SetToolSeparation(10)
        toolbar.Realize()
        self.SetToolBar(toolbar)

        # colors and font
        toolbar.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        toolbar.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        toolbar.SetFont(self._prefsIO.GetValue('M_FONT'))

        # events
        eventslist = [ wx.ID_NEW, wx.ID_EXIT, wx.ID_ADD, wx.ID_REMOVE, TAB_NEW_ID, TAB_CLOSE_ID, wx.ID_PREFERENCES, wx.ID_ABOUT ]
        for event in eventslist:
            wx.EVT_TOOL(self, event, self.ProcessEvent)

    # End _create_toolbar
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

    # End _create_accelerators
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

    # End _create_statusbar
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

    # End _create_panels
    # ------------------------------------------------------------------------


    def _LayoutFrame(self):
        """
        Lays out the frame.

        """

        wx.LayoutAlgorithm().LayoutFrame(self, self._mainpanel)
        self._clientpanel.SendSizeEvent()
        self.Refresh()

    # End _LayoutFrame
    # ------------------------------------------------------------------------



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

    # End CreateClient
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

    # End CreateFileManager
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

        id = event.GetId()

        if id == wx.ID_ADD:
            # add a file in the file manager
            self.OnAdd(event)
            return True
        elif id == wx.ID_REMOVE:
            # remove all checked files of the file manager, delete the instances
            self.OnRemove(event)
            return True
        elif id == wx.ID_EXIT:
            # quit the application
            self.OnClose(event)
            return True

        elif id == wx.ID_PREFERENCES:
            # customize
            self.OnSettings(event)

        elif id == TAB_NEW_ID:
            # new tab in the client
            self.OnNewTab(event)
        elif id == TAB_CLOSE_ID:
            # close tab in the client
            self.OnCloseTab(event)

        elif id == VIEW_TOOLBAR_ID:
            # enable/disable toolbar
            self.OnViewToolBar(event)
            return True
        elif id == VIEW_STATUSBAR_ID:
            # enable/disable statusbar
            self.OnViewStatusBar(event)
            return True

        elif id == wx.ID_ABOUT:
            # open the about frame
            self.OnAbout(event)
            return True

        return wx.GetApp().ProcessEvent(event)

    # End ProcessEvent
    # ------------------------------------------------------------------------


    def ProcessUpdateUIEvent(self, event):
        """
        Processes a UI event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.

        """

        id = event.GetId()

        if id == VIEW_TOOLBAR_ID:
            self.OnUpdateViewToolBar(event)
            return True
        elif id == VIEW_STATUSBAR_ID:
            self.OnUpdateViewStatusBar(event)
            return True

        return wx.GetApp().ProcessUpdateUIEvent(event)

    # End ProcessUpdateUIEvent
    # ------------------------------------------------------------------------


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

    # End OnAdd
    # ------------------------------------------------------------------------


    def OnRemove(self, event):
        """
        Received an event to close files:
        ask the file manager to remove them.

        """

        evt = FileWanderEvent(filename=None,status=False)
        evt.SetEventObject(self)
        wx.PostEvent(self._filepanel, evt)

    # End OnRemove
    # ------------------------------------------------------------------------


    def OnExitApp(self, event):
        """
        Destroys the main frame which quits the wxPython application.
        Destroy without worrying about anything!

        """

        dialog = wx.MessageDialog(self, message = "Are you sure you want to quit?", caption = "Exit?", style = wx.YES_NO, pos = wx.DefaultPosition)
        response = dialog.ShowModal()

        if response == wx.ID_YES:
            logging.info('Bye bye... Hope to see you again!')
            self.Destroy()
        else:
            event.StopPropagation()

    # End OnExitApp
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

    # End OnClose
    #-------------------------------------------------------------------------


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

    # End OnViewToolBar
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

    # End OnUpdateViewToolBar
    # ------------------------------------------------------------------------


    def OnViewStatusBar(self, event):
        """
        Toggles whether the StatusBar is visible.

        """

        self.GetStatusBar().Show(not self.GetStatusBar().IsShown())
        self._LayoutFrame()

    # End OnViewStatusBar
    # ------------------------------------------------------------------------


    def OnUpdateViewStatusBar(self, event):
        """
        Updates the View StatusBar menu item.

        """

        event.Check(self.GetStatusBar().IsShown())

    # End OnUpdateViewStatusBar
    # ------------------------------------------------------------------------



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

    # End OnNewTab
    #-------------------------------------------------------------------------


    def OnCloseTab(self, event):
        """
        Close a page in the client.

        """

        evt = NotebookClosePageEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self._clientpanel, evt)

    # End OnCloseTab
    #-------------------------------------------------------------------------


    def OnFileAdded(self, event):
        """
        Add a file of the file manager.

        """

        self.AddFiles( [event.filename] )

    # End OnFileAdded
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

    # End OnFilesClosed
    #-------------------------------------------------------------------------


    #-------------------------------------------------------------------------
    # Help... Callbacks
    #-------------------------------------------------------------------------


    def OnAbout(self, event):
        """
        Open the About box.

        """

        wx.AboutBox( self._about )

    # End OnAbout
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

    # End OnSettings
    # ------------------------------------------------------------------------


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

    # End AddFiles
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

    # End OnFileWander
    #-------------------------------------------------------------------------


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

    # End DisplayTextInStatusbar
    #-------------------------------------------------------------------------


    def StartTimeInStatusBar(self):
        """
        Start the date of the StatusBar.

        """

        self.GetStatusBar().StartTime()

    # End StartTimeInStatusBar
    #-------------------------------------------------------------------------


    def StopTimeInStatusBar(self):
        """
        Stop the date of the StatusBar.

        """

        self.GetStatusBar().StopTime()

    # End StopTimeInStatusBar
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

    # End SetPrefs
    #-------------------------------------------------------------------------

#-----------------------------------------------------------------------------
