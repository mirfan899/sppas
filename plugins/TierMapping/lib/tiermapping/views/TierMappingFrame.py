#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Tatsuya Watanabe
#
# This file is part of TierMapping.
#
# TierMapping is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TierMapping is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TierMapping.  If not, see <http://www.gnu.org/licenses/>.

import os
import wx

from tiermapping.images import(
        IMG_EXIT,
        IMG_ADD,
        IMG_EXCEL,
        IMG_REMOVE,
        IMG_EXCEL,
        IMG_FIND,
        IMG_CLEAR,
        IMG_ABOUT
        )

from FileList import FileList
from MapList import MapList
from OutputFormat import OutputFormat
from OutputDir import OutputDir
from MappingTable import MappingTable
from AboutBox import AboutBox

ID_RUN = wx.NewId()

PATH_RESOURCES = os.path.join(os.path.dirname(os.path.dirname(
                              os.path.dirname(
                              os.path.dirname(__file__)))),
                              "resources")


class TierMappingFrame(wx.Frame):

    def __init__(self, parent, presenter=None):
        wx.Frame.__init__(self, parent, size=(600, 400))
        self.InitUI()
        self.bind()
        self.presenter = presenter

    def InitUI(self):
        self._about = AboutBox()
        splitter = wx.SplitterWindow(self)
        # Left Panel
        leftPanel = wx.Panel(splitter)
        # Top
        self.fileList = FileList(leftPanel, style=wx.LC_EDIT_LABELS, size=(300, 150)) # wx.ListCtrl
        # Bottom
        staticbox = wx.StaticBox(leftPanel, label="")
        staticsizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)
        self.outputFormat = OutputFormat(leftPanel) # wx.ComboBox
        self.outputDir = OutputDir(leftPanel) # wx.combo.Comboctrl
        dirLabel = wx.StaticText(leftPanel, label='Output Directory: ')
        formatLabel = wx.StaticText(leftPanel, label='Output Format: ')
        staticsizer.Add(dirLabel, flag=wx.EXPAND|wx.ALL^wx.BOTTOM, border=5)
        staticsizer.Add(self.outputDir, flag=wx.EXPAND|wx.ALL, border=5)
        staticsizer.Add(formatLabel, flag=wx.EXPAND|wx.ALL^wx.BOTTOM, border=5)
        staticsizer.Add(self.outputFormat, flag=wx.EXPAND|wx.ALL, border=5)
        # Layout left panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.fileList, flag=wx.EXPAND|wx.ALL, border=5)
        sizer.Add(staticsizer, flag=wx.EXPAND|wx.ALL, border=5)
        leftPanel.SetSizer(sizer)
        # Left Panel
        rightPanel = wx.Panel(splitter)
        staticbox = wx.StaticBox(rightPanel, label="Mapping Table")
        sizer = wx.StaticBoxSizer(staticbox)
        self.mapList = MapList(rightPanel) # wx.ListCtrl
        # Layout left panel
        sizer.Add(self.mapList, proportion=1, flag=wx.EXPAND|wx.ALL^wx.LEFT, border=10)
        rightPanel.SetSizer(sizer)
        splitter.SplitVertically(leftPanel, rightPanel, 450)
        self.CreateToolBar()
        self.CreateStatusBar()
        # Set icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(IMG_FIND, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle('TierMapping')


    def CreateToolBar(self):
        toolbar = wx.ToolBar(self, style=wx.TB_TEXT)
        toolbar.AddLabelTool(id=wx.ID_EXIT,
                             label='Exit',
                             bitmap=wx.Bitmap(IMG_EXIT),
                             bmpDisabled=wx.NullBitmap,
                             kind=wx.ITEM_NORMAL,
                             shortHelp="Quit the application")
        toolbar.AddSeparator()
        toolbar.AddLabelTool(id=wx.ID_OPEN,
                             label='Add Files',
                             bitmap=wx.Bitmap(IMG_ADD),
                             bmpDisabled=wx.NullBitmap,
                             kind=wx.ITEM_NORMAL,
                             shortHelp="Add Annotation File")
        toolbar.AddLabelTool(id=wx.ID_DELETE,
                             label='Remove',
                             bitmap=wx.Bitmap(IMG_REMOVE),
                             bmpDisabled=wx.NullBitmap, kind=wx.ITEM_NORMAL,
                             shortHelp="Remove Annotation File")
        toolbar.AddSeparator()
        toolbar.AddLabelTool(id=wx.ID_NEW,
                             label='import',
                             bitmap=wx.Bitmap(IMG_EXCEL),
                             bmpDisabled=wx.NullBitmap,
                             kind=wx.ITEM_NORMAL,
                             shortHelp="Import csv file")
        toolbar.AddLabelTool(id=wx.ID_CLEAR,
                             label='Remove',
                             bitmap=wx.Bitmap(IMG_CLEAR),
                             bmpDisabled=wx.NullBitmap,
                             kind=wx.ITEM_NORMAL,
                             shortHelp="Remove csv file")
        toolbar.AddSeparator()
        toolbar.AddLabelTool(id=ID_RUN,
                             label='Run',
                             bitmap=wx.Bitmap(IMG_FIND),
                             bmpDisabled=wx.NullBitmap, kind=wx.ITEM_NORMAL,
                             shortHelp="Run")
        toolbar.AddSeparator()
        toolbar.AddLabelTool(id=wx.ID_ABOUT,
                             label='About',
                             bitmap=wx.Bitmap(IMG_ABOUT),
                             bmpDisabled=wx.NullBitmap, kind=wx.ITEM_NORMAL,
                             shortHelp="About")
        self.SetToolBar(toolbar)
        toolbar.Realize()

    def bind(self):
        toolbar = self.GetToolBar()
        toolbar.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        toolbar.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
        toolbar.Bind(wx.EVT_MENU, self.OnRemove, id=wx.ID_DELETE)
        toolbar.Bind(wx.EVT_MENU, self.OnLoadMapping, id=wx.ID_NEW)
        toolbar.Bind(wx.EVT_MENU, self.OnRemoveMapping, id=wx.ID_CLEAR)
        toolbar.Bind(wx.EVT_MENU, self.OnRun, id=ID_RUN)
        toolbar.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.mapList.Bind(wx.EVT_LEFT_DCLICK, self.OnShowMappingTable)

    def OnExit(self, event):
        self.Close()

    def OnOpen(self, event):
        wildcard = "Praat (*.TextGrid)|*.TextGrid|"\
                   "Praat (*.PitchTier)|*.PitchTier|"\
                   "Transcriber (*.trs)|*.trs|"\
                   "Elan (*.eaf)|*.eaf"
        dlg = wx.FileDialog(
            self,
            message="Choose a file",
            wildcard=wildcard,
            style=wx.OPEN|wx.MULTIPLE|wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.presenter.AppendFile(paths)
        dlg.Destroy()

    def OnRemove(self, event):
        self.presenter.RemoveFile()

    def OnLoadMapping(self, event):
        wildcard = "CSV (*.csv)|*.csv|"\
                   "All (*.*)|*.*"
        dlg = wx.FileDialog(
            self,
            message="Choose a file",
            wildcard=wildcard,
            style=wx.OPEN|wx.MULTIPLE|wx.CHANGE_DIR,
            defaultDir = PATH_RESOURCES
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.presenter.LoadMapping(paths)
        dlg.Destroy()

    def OnRemoveMapping(self, event):
        self.presenter.RemoveMapping()

    def OnShowMappingTable(self, event):
        self.presenter.ShowMappingTable()

    def OnCloseMappingTable(self, event):
        f = event.GetEventObject()
        self.presenter.UnSelect(int(f.GetName()))
        event.Skip()

    def OnRun(self, event):
        self.presenter.Run()

    def OnAbout(self, event):
        wx.AboutBox(self._about)

    def SetPresenter(self, presenter):
        self.presenter = presenter

    def AppendFile(self, row, check=True):
        self.fileList.AppendItem(row, check)

    def AppendMapping(self, row, check=False):
        self.mapList.AppendItem(row, check)

    def ClearFileList(self):
        self.fileList.DeleteAllItems()

    def ClearMappingList(self):
        self.mapList.DeleteAllItems()

    def GetCheckedFiles(self):
        return self.fileList.GetCheckedItems()

    def GetCheckedMappings(self):
        return self.mapList.GetCheckedItems()

    def GetSelectedMappings(self):
        return self.mapList.GetSelectedItems()

    def GetOutputDir(self):
        return self.outputDir.GetValue()

    def GetOutputFormat(self):
        return self.outputFormat.GetValue()

    def CreateMappingTable(self, index, mapping):
        f = MappingTable(self, mapping, name=index)
        f.Bind(wx.EVT_CLOSE, self.OnCloseMappingTable)
        f.Show()
