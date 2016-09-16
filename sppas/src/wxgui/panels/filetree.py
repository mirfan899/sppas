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
# File: filetree.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi, Cazambe Henry"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os.path

import audiodata.io

import wx
from wx.lib.buttons import GenBitmapButton, GenBitmapTextButton

from wxgui.cutils.imageutils   import spBitmap
from wxgui.dialogs.filedialogs import OpenSoundFiles
from wxgui.dialogs.filedialogs import SaveAsAnnotationFile
from wxgui.dialogs.msgdialogs  import ShowInformation
from wxgui.dialogs.msgdialogs  import ShowYesNoQuestion

import annotationdata.io

from wxgui.sp_icons import TREE_ROOT
from wxgui.sp_icons import TREE_FOLDER_CLOSE
from wxgui.sp_icons import TREE_FOLDER_OPEN
from wxgui.sp_icons import MIME_WAV
from wxgui.sp_icons import MIME_ASCII
from wxgui.sp_icons import MIME_PITCHTIER
from wxgui.sp_icons import MIME_TEXTGRID
from wxgui.sp_icons import MIME_TRS
from wxgui.sp_icons import MIME_EAF
from wxgui.sp_icons import MIME_XRA
from wxgui.sp_icons import MIME_MRK
from wxgui.sp_icons import MIME_SUBTITLES
from wxgui.sp_icons import MIME_ANVIL
from wxgui.sp_icons import MIME_ANTX
from wxgui.sp_icons import MIME_XTRANS
from wxgui.sp_icons import MIME_AUP

from wxgui.sp_icons import ADD_FILE_ICON
from wxgui.sp_icons import ADD_DIR_ICON
from wxgui.sp_icons import REMOVE_ICON
from wxgui.sp_icons import DELETE_ICON
from wxgui.sp_icons import EXPORT_AS_ICON
from wxgui.sp_icons import EXPORT_ICON

from wxgui.sp_consts import TREE_ICONSIZE

from wxgui.panels.mainbuttons import MainToolbarPanel


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

ID_TB_ADDDIR  = wx.NewId()
ID_TB_EXPORT  = wx.NewId()

# ----------------------------------------------------------------------------
# class filelistPanel
# ----------------------------------------------------------------------------

class FiletreePanel( wx.Panel ):
    """
    @author:  Brigitte Bigi, Cazembe Henry
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: A panel with a toolbar and a tree-style list of files.

    """
    def __init__(self, parent, preferences):

        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))

        # Members
        self._prefsIO = preferences

        font = self._prefsIO.GetValue('M_FONT')
        font.SetWeight( wx.BOLD )

        self._toolbar   = self._create_toolbar()
        self._filestree = self._create_filestree()

        _vbox = wx.BoxSizer(wx.VERTICAL)
        _vbox.Add(self._toolbar,   proportion=0, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=4)
        _vbox.Add(self._filestree, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=4)

        self.GetTopLevelParent().Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)

        self.Bind(wx.EVT_BUTTON, self.OnButtonClick)

        self.SetSizer(_vbox)
        self.SetMinSize((320,200))


    def _create_toolbar(self):
        """ Simulate the creation of a toolbar. """

        toolbar = MainToolbarPanel(self, self._prefsIO)
        toolbar.AddButton( wx.ID_ADD,    ADD_FILE_ICON, "Add files", tooltip="Add files into the list.")
        toolbar.AddButton( ID_TB_ADDDIR, ADD_DIR_ICON,  "Add dir", tooltip="Add a folder into the list.")
        toolbar.AddButton( wx.ID_REMOVE, REMOVE_ICON,   "Remove",  tooltip="Remove files of the list.")
        toolbar.AddButton( wx.ID_DELETE, DELETE_ICON,   "Delete",  tooltip="Delete definitively files of the computer.")
        toolbar.AddButton( wx.ID_SAVEAS, EXPORT_AS_ICON,"Copy",    tooltip="Copy files.")
        toolbar.AddButton( wx.ID_SAVE,   EXPORT_ICON,   "Export",  tooltip="Export files.")
        return toolbar

    # ------------------------------------------------------------------------

    def _create_filestree(self):
        """ Create the tree to store file names. """

        t = wx.TreeCtrl(self, 1, wx.DefaultPosition, (-1,-1), style=wx.TR_MULTIPLE|wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.NO_BORDER)
        t.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )
        t.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )
        t.SetFont( self._prefsIO.GetValue('M_FONT') )

        t.AddRoot('')

        il = wx.ImageList(TREE_ICONSIZE, TREE_ICONSIZE)
        self.rootidx      = il.Add(spBitmap(TREE_ROOT, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.fldridx      = il.Add(spBitmap(TREE_FOLDER_CLOSE, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.fldropenidx  = il.Add(spBitmap(TREE_FOLDER_OPEN,  TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.wavfileidx   = il.Add(spBitmap(MIME_WAV, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.txtfileidx   = il.Add(spBitmap(MIME_ASCII, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.csvfileidx   = il.Add(spBitmap(MIME_ASCII, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.ptierfileidx = il.Add(spBitmap(MIME_PITCHTIER, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.tgridfileidx = il.Add(spBitmap(MIME_TEXTGRID,  TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.trsfileidx   = il.Add(spBitmap(MIME_TRS, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.eaffileidx   = il.Add(spBitmap(MIME_EAF, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.xrafileidx   = il.Add(spBitmap(MIME_XRA, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.mrkfileidx   = il.Add(spBitmap(MIME_MRK, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.subfileidx   = il.Add(spBitmap(MIME_SUBTITLES, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.anvilfileidx = il.Add(spBitmap(MIME_ANVIL, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.antxfileidx  = il.Add(spBitmap(MIME_ANTX, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.xtransfileidx = il.Add(spBitmap(MIME_XTRANS, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))
        self.aupfileidx    = il.Add(spBitmap(MIME_AUP, TREE_ICONSIZE, theme=self._prefsIO.GetValue('M_ICON_THEME')))

        t.AssignImageList(il)

        return t

    # End create_gui
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnButtonClick(self, event):
        ide = event.GetId()
        if ide == wx.ID_ADD:
            self._add_file()
        elif ide == ID_TB_ADDDIR:
            self._add_dir()
        elif ide == wx.ID_REMOVE:
            self._remove()
        elif ide == wx.ID_DELETE:
            self._delete()
        elif ide == wx.ID_SAVEAS:
            self._copy()
        elif ide == wx.ID_SAVE:
            self._export()


    def OnKeyPress(self, event):
        """
        Respond to a keypress event.
        """
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_F5:
            self.RefreshTree(None)

        event.Skip()

    # ------------------------------------------------------------------------

    def _add_file(self):
        """ Add one or more file(s). """

        files = OpenSoundFiles()
        for f in files:
            self._append_file(f)

    # -----------------------------------------------------------------------

    def _add_dir(self):
        """ Add the content of a directory. """

        dlg = wx.DirDialog(self, message="Choose a directory:",defaultPath=os.getcwd())
        self.paths = []
        if dlg.ShowModal() == wx.ID_OK:
            self._append_dir(dlg.GetPath())
        dlg.Destroy()

    # -----------------------------------------------------------------------

    def _delete(self):
        """ Delete selected files from the file system and remove of the tree. """

        selection = self.GetSelected()
        str_list = ""

        # Ask user if sure?
        if len(selection) > 10:
            str_list = ("Are you sure you want to delete definitively %d files "
                        "of the file system?" % len(selection))
        else:
            for filename in selection:
                str_list += filename + '\n'
            str_list = ("Are you sure you want to delete definitively "
                        "the following file(s) of the file system?\n%s" % str_list)

        dlg = ShowYesNoQuestion( self, self._prefsIO, str_list)
        # Yes, the user wants to delete...
        if dlg == wx.ID_YES:

            errors = [] # list of not deleted files
            for filename in selection:
                try:
                    os.remove( filename )
                except Exception as e:
                    errors.append( filename )
                    for item in self._filestree.GetSelections():
                        f = self._filestree.GetItemText(item)
                        if filename.endswith( f ):
                            self._filestree.UnselectItem( item )

            # some files were not deleted
            if len(errors)>0:
                errormsg="\n".join(errors)
                ShowInformation( self, self._prefsIO, "Some files were not deleted.\n"
                        "Probably you don't have access right to do so...\n%s"%errormsg, style=wx.ICON_WARNING)

            # Remove deleted files of the tree
            self._remove()

    # -----------------------------------------------------------------------

    def _export(self):
        """ Export multiple files, i.e. propose to change the extension. Nothing else. """

        # Some selection?
        files = self.GetSelected()
        if not files:
            return

        # Ask for the expected file format
        errors = False
        extensions = annotationdata.io.extensions_out
        dlg = wx.SingleChoiceDialog( self,
                                   "Check the file format:",
                                   "File extension", extensions)
        dlg.SetSelection( 0 ) # default choice (=xra)

        if dlg.ShowModal() == wx.ID_OK:
            # get the index of the extension
            checked = dlg.GetSelection()
            # Convert all files
            for filename in files:
                try:
                    oldextension = os.path.splitext(filename)[1][1:]
                    newfilename = filename.replace("."+oldextension,extensions[checked])
                    trs = annotationdata.io.read( filename )
                    annotationdata.io.write(newfilename, trs)
                except Exception as e:
                    ShowInformation( self, self._prefsIO, "Export failed for file %s: %s" % (filename,e), style=wx.ICON_ERROR)
                    errors = True
                else:
                    self._append_file(newfilename)
        else:
            errors = None

        dlg.Destroy()

        if errors is False:
            ShowInformation( self, self._prefsIO, "Export with success.", style=wx.ICON_INFORMATION)

    # -----------------------------------------------------------------------

    def _copy(self):
        """ Export selected files. """

        # Some files to save???
        files = self.GetSelected()
        if not files: return

        for filename in files:
            default_dir  = os.path.dirname(filename)
            default_file = os.path.basename(filename)

            # Show the dialog and retrieve the user response.
            newfilename = SaveAsAnnotationFile( default_dir, default_file )
            # If it is the OK response, process the data.
            if newfilename:
                try:
                    trs = annotationdata.io.read(filename)
                    annotationdata.io.write(newfilename, trs)
                except Exception as e:
                    ShowInformation( self, self._prefsIO, "Copy/Export failed: %s" % e, style=wx.ICON_ERROR)
                else:
                    self._append_file(newfilename)

    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Functions
    # -----------------------------------------------------------------------


    def SetPrefs(self, prefs):
        """
        Fix new preferences.
        """
        self._prefsIO = prefs
        self.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )
        self.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )
        self.SetFont( self._prefsIO.GetValue('M_FONT') )

        font = self._prefsIO.GetValue('M_FONT')
        font.SetWeight( wx.BOLD )

        self._filestree.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )
        self._filestree.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )
        self._filestree.SetFont( self._prefsIO.GetValue('M_FONT') )

        self._toolbar.SetPrefs( self._prefsIO )

    # -----------------------------------------------------------------------

    def RefreshTree(self, filelist=None):
        """
        Refresh the tree, and optionally add new files.
        """
        if filelist is None:
            filelist = []
            for ext in audiodata.io.extensions:
                filelist.extend( self.GetSelected(ext) )

        for f in filelist:
            self._append_file(f)

    # -----------------------------------------------------------------------

    def GetSelected(self, extension=""):
        """
        Return a list containing the filepath of each selected regular
        file (not folders) from the tree. Selecting a folder item equals to select all its items.

        @param Extension of the selected file

        """
        sel = []
        # tree.GetSelections: this method accepts no parameters and
        # returns a Python list of wxTreeItemIds
        for item in self._filestree.GetSelections():
            filename = self._filestree.GetItemText(item)

            try:
                IsDir = os.path.isdir(filename)
            except UnicodeEncodeError:
                ShowInformation( None, self._prefsIO, "File names can only contain ASCII characters", style=wx.ICON_INFORMATION)
                continue

            if item == self._filestree.GetRootItem():
                dir_item, cookie = self._filestree.GetFirstChild(item)
                while(dir_item.IsOk()):
                    self._get_all_filepaths(dir_item, sel, extension=extension)
                    dir_item, cookie = self._filestree.GetNextChild(item, cookie)
                return sel
            elif IsDir is True:
                self._get_all_filepaths(item, sel, extension)
            else:
                dir_id = self._filestree.GetItemParent(item)
                dirname = self._filestree.GetItemText(dir_id)
                fpath = os.path.join(dirname, filename)
                #if the file has the right extension and is not already in the the list sel, append it to sel
                if filename.lower().endswith(extension.lower()) and not fpath in sel:
                    sel.append(fpath)

        return sel

    # -----------------------------------------------------------------------
#     def get_filestree(self):
#         return self._filestree


    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _remove(self):
        for item in self._filestree.GetSelections():
            self._filestree.DeleteChildren(item)
            if not item == self._filestree.GetRootItem():
                self._filestree.Delete(item)


    def _append_file(self, filename):
        """
        Add the file to the tree if it is not already in it.
        """
        # Get the directory name
        dirname   = os.path.dirname( filename )
        basename  = os.path.basename( filename )
        fname, fileExtension = os.path.splitext( filename )

        # Add the directory as item of the tree if it isn't already done
        item = self._get_item_by_label(dirname, self._filestree.GetRootItem())

        #item. IsOk will be False if dirname has not been added yet to the tree
        if not item.IsOk():
            item = self._add_item(self._filestree.GetRootItem(), dirname, isdir=True)

        if item.IsOk():
            #add the file only if it is not in the list
            child = self._get_item_by_label(basename, item)
            if not child.IsOk():
                child = self._add_item(item, basename)
            if fileExtension.lower() in audiodata.io.extensions:
                self._add_related_files(os.path.join(dirname, basename))
                self._filestree.SelectItem(child)

        self._filestree.SortChildren(item)
        self._filestree.ExpandAll()


    def _append_dir(self, txt):
        """
        Add the directory as item of the tree.
        """
        #files contains all the files in the appended dir
        files = os.listdir(txt)
        wavfile_list = []
        #store all the wav file names in wavfile_list
        for f in files:
            filename, extension = os.path.splitext(f)
            if extension.lower() in audiodata.io.extensions:
                wavfile_list.append(filename)

        #add all the children directories
        for f in files:
            try:
                if os.path.isdir(os.path.join(txt, f)):
                    self._append_dir(os.path.join(txt, f))
            except UnicodeDecodeError:
                pass

        #if the directory 'txt' does not directly contains wav file, leave the function
        if len(wavfile_list) == 0:
            self._filestree.ExpandAll()
            return

        #Test if the directory is already appended
        dir_already_appended = False
        for dir in self._get_all_dirs(self._filestree.GetRootItem()):
            if self._filestree.GetItemText(dir) == txt:
                dir_already_appended = True

        if dir_already_appended:
            item = self._get_item_by_label(txt, self._filestree.GetRootItem())
        else:
            # add a new dir node
            item = self._add_item(self._filestree.GetRootItem(), txt, isdir=True)

        for f in files:
            if self._is_file_in_dirnode(f, item):
                continue
            #if it is a wav file, add it as item of the tree
            try:
                if f.lower() in audiodata.io.extensions:
                    #self._add_item(item, f)
                    #add the file only if it is not in the list
                    child = self._get_item_by_label(os.path.basename( f ), item)
                    if not child.IsOk():
                        child = self._add_item(item, f)

            except UnicodeDecodeError:
                continue

            else:
                for wav_fname in wavfile_list:
                    #if the file is associated to a wave file, add it to the tree as a text file
                    try:
                        if f.startswith(wav_fname):
                            #self._add_item(item, f)
                            #add the file only if it is not in the list
                            child = self._get_item_by_label(os.path.basename( f ), item)
                            if not child.IsOk():
                                child = self._add_item(item, f)

                    except UnicodeDecodeError:
                        pass

        self._filestree.SelectItem(item)
        self._filestree.SortChildren(item)
        self._filestree.ExpandAll()


    def _add_item(self, parent, son, isdir=False):
        """
        Add an item 'son' of type 'type' to the node 'parent'

        -son is text of the item to be added
        -parent is the node to which the item will be added
        -isdir is true if the item to add is a dir
        -color is the background color of the item

        @return the child
        """
        fileName, fileExtension = os.path.splitext(son.lower())

        if isdir:
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.fldridx,     which=wx.TreeItemIcon_Normal)
            self._filestree.SetItemImage(child, self.fldropenidx, which=wx.TreeItemIcon_Expanded)

        elif fileExtension in audiodata.io.extensions:
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.wavfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension in [ ".txt",".ctm",".stm",".lab",".mlf" ]:
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.txtfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension == ".csv":
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.csvfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension == ".textgrid":
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.tgridfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension in [".pitchtier",".hz"]:
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.ptierfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension == ".trs": # Transcriber
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.trsfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension == ".mrk": # Phonedit
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.mrkfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension == ".eaf": # Elan
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.eaffileidx, wx.TreeItemIcon_Normal)

        elif fileExtension == ".xra":  # SPPAS
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.xrafileidx, wx.TreeItemIcon_Normal)

        elif fileExtension in [".srt",".sub"]:
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.subfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension == ".anvil":
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.anvilfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension == ".antx":
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.antxfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension == ".tdf":
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.xtransfileidx, wx.TreeItemIcon_Normal)

        elif fileExtension == ".aup":
            child = self._filestree.AppendItem(parent, son)
            self._filestree.SetPyData(child, None)
            self._filestree.SetItemImage(child, self.aupfileidx, wx.TreeItemIcon_Normal)

        else:
            return wx.TreeItemId()

        return child


    def _add_related_files(self, file_path):
        """
        Add all the files and directories with the same name and
        in the same directory as the file in parameters.
        """
        dirname  = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        dir_item  = self._get_item_by_label(dirname, self._filestree.GetRootItem())
        file_item = self._get_item_by_label(filename, dir_item)
        filename,extension = os.path.splitext(filename)

        #list of all the files in the same dirname
        #dir_files = os.listdir(dirname.encode('utf8'))
        dir_files = os.listdir(dirname)

        for f in dir_files:
            try:
                if f.startswith(filename):
                    item = self._get_item_by_label(f, self._filestree.GetRootItem())
                    if not item.IsOk():
                        #if the file is associated to the wave file, add it to the tree
                        if os.path.isfile(os.path.join(dirname,f)):
                            self._add_item(dir_item, f)
                        elif os.path.isdir(os.path.join(dirname,f)):
                            self._append_dir(os.path.join(dirname,f))
            except Exception:
                pass

        self._filestree.SortChildren(dir_item)
        self._filestree.ExpandAll()


    def _get_item_by_label(self, search_text, root_item):
        """
        Search the item that as 'search_text' as text and returns it.
        If not found, return a new wx.TreeItemId()
        """
        item, cookie = self._filestree.GetFirstChild(root_item)

        while item.IsOk():
            text = self._filestree.GetItemText(item)
            if text.lower() == search_text.lower():
                return item
            if self._filestree.ItemHasChildren(item):
                match = self._get_item_by_label(search_text, item)
                if match.IsOk():
                    return match
            item, cookie = self._filestree.GetNextChild(root_item, cookie)

        return wx.TreeItemId()


    def _get_all_dirs(self, root_item):
        """
        Return all the paths of the directories in the tree.
        """
        all_dirs = []
        item, cookie = self._filestree.GetFirstChild(root_item)
        while item.IsOk():
            all_dirs.append(item)
            item, cookie = self._filestree.GetNextChild(root_item, cookie)

        return all_dirs



    def _is_file_in_dirnode(self, filename, item):
        """
        Return true if a child of the node 'item' has as text 'filename'.
        """
        if not item.IsOk():
            return False
        file_item, cookie = self._filestree.GetFirstChild(item)
        while file_item.IsOk():
            text = self._filestree.GetItemText(file_item)
            #if the file already exists in the node 'item', return True
            if text.lower() == filename.lower():
                return True
            file_item, cookie = self._filestree.GetNextChild(item, cookie)

        return False


    def _get_all_filepaths(self, dir, pathlist=[], extension=""):
        """
        Return a list containing the filepath of each regular file
        (not folders) from the tree.
        """
        dirname = self._filestree.GetItemText(dir)
        file_item, cookie = self._filestree.GetFirstChild(dir)
        while(file_item.IsOk()):
            filename = self._filestree.GetItemText(file_item)
            fpath = os.path.join(dirname, filename)
            #if the file has the right extension and is not already in the the list pathlist
            if filename.lower().endswith(extension.lower()) and not fpath in pathlist:
                pathlist.append(fpath)
            file_item, cookie = self._filestree.GetNextChild(dir, cookie)

        return pathlist


# ----------------------------------------------------------------------------
