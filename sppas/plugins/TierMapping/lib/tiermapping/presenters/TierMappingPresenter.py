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
from tiermapping.models.mappingloader import MappingCharLoader
from process import MappingThread, ProgressBar

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



class TierMappingPresenter(object):

    def __init__(self, view, files, mapping=None):
        self.view = view
        self.loader = MappingCharLoader()
        self.view.SetPresenter(self)
        self.fileList = []
        self.mapList = []
        self.selected_tables = []
        self.AppendFile(files)
        if mapping:
            self.LoadMapping(mapping)
        self.Init()

    def Init(self):
        self.view.Show()

    def InitView(self):
        self.view.ClearFileList()
        self.view.ClearMappingList()
        for f in self.fileList:
            self.view.AppendFile((f,))
        for m in self.mapList:
            self.view.AppendMapping((m.GetName(),))

    def AppendFile(self, files):
        if not files:
            return
        for f in files:
            if f not in self.fileList:
                self.fileList.append(f)
                self.view.AppendFile((f,))

    def LoadMapping(self, filenames):
        mappings = []
        for f in filenames:
            try:
                maps = self.loader.Load(f)
            except IOError as e:
                wx.MessageBox("{0}".format(e), "Error")
            else:
                mappings.extend(maps)
        self.AppendMapping(mappings)

    def AppendMapping(self, mapping):
        if not mapping:
            return
        for m in mapping:
            self.mapList.append(m)
            self.view.AppendMapping((m.GetName(),), True)

    def RemoveMapping(self):
        mapping = self.view.GetCheckedMappings()
        if not mapping:
            return
        for i in reversed(mapping):
            self.mapList.pop(i)
        self.InitView()

    def RemoveFile(self):
        checked_files = self.view.GetCheckedFiles()
        for i in reversed(checked_files):
            self.fileList.pop(i)
        self.InitView()

    def UnSelect(self, index):
        self.selected_tables.remove(index)

    def ShowMappingTable(self):
        selected_tables = self.view.GetSelectedMappings()
        if not selected_tables:
            return
        for i in selected_tables:
            if i not in self.selected_tables:
                mapping = self.mapList[i]
                self.selected_tables.append(i)
                self.view.CreateMappingTable(str(i), mapping)

    def Run(self):
        checked_mappings = self.view.GetCheckedMappings()
        checked_files = self.view.GetCheckedFiles()
        output_dir = self.view.GetOutputDir()
        output_format = self.view.GetOutputFormat()

        if not checked_mappings:
            return

        if not checked_files:
            return

        if not output_dir:
            return

        inputfiles = [self.fileList[i] for i in checked_files]
        mappings = [self.mapList[i] for i in checked_mappings]

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                if not os.path.exists(plugin_dir):
                    logging.debug("%s" % e)
                    return

        outputfiles = []
        for infile in inputfiles:
            base = os.path.splitext(os.path.basename(infile))[0]
            out = os.path.join(output_dir, base + "." + output_format)
            outputfiles.append(out)

        dialog = ProgressBar(self.view, message="Processing", title="Run")
        th = MappingThread(inputfiles,
                          outputfiles,
                          mappings,
                          dialog)
