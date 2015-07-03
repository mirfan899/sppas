#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Tatsuya Watanabe
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import os
import subprocess
from ConfigParser import SafeConfigParser

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------

# example ...
# [Plugin Entry]
# Name=Mapping
# Icon=%(home)s%(sep)sicons%(sep)sfind-and-replace.png
# Command=python "%(home)s%(sep)sbin%(sep)smapping.py"
# Ignore=false


class PluginConfigParser(object):

    def __init__(self):
        self._parser = SafeConfigParser()
        self._section = "Plugin Entry"
        self._options = ('name', 'icon', 'command', 'iparam')
        self._file_section = "Files"
        self._os = ('unix', 'windows', 'mac')
        self._files = ('xra', 'textgrid', 'eaf', 'csv', 'wav', 'txt', 'pitchtier', 'trs', 'tag')

    # End __init__
    # ------------------------------------------------------------------------


    def read(self, filenames):
        """ Read a list of filenames.
            Return a list of plugins which were successfully parsed.
            Parameters:
                - filenames: list of filenames
            Return:
                - list of plugins
                   plugin = {
                            "icon": "path_to_icon",
                            "command": "command",
                            "name": "plugin_name",
                            "iparam":"-i",
                            "types": ['textgrid', 'eaf', 'tag', 'txt']
                            }
        """
        plugins = []
        if isinstance(filenames, basestring):
            filenames = [filenames]
        parser = self._parser
        for filename in filenames:
            ok = parser.read(filename)
            # file not found
            if not ok:
                continue
            if not parser.has_section(self._section):
                logger.debug("'%s' section required" % self._section)
                continue
            if parser.has_option(self._section, "ignore"):
                if parser.getboolean(self._section, "ignore"):
                    continue

            home = os.path.dirname(filename)
            sep = os.path.sep
            param = {'types':[]}
            succes = True

            for opt in self._options:
                if not parser.has_option(self._section, opt):
                    logger.debug("'%s' option required" % opt)
                    succes = False
                    break
                param[opt] = parser.get(self._section, opt, vars={'home':home, 'sep':sep})

            for _os in self._os:
                if parser.has_option(self._section, _os):
                    param[_os] = parser.get(self._section, _os, vars={'home':home, 'sep':sep})

            if parser.has_section(self._file_section):
                for infile in self._files:
                    if not parser.has_option(self._file_section, infile):
                        pass
                    else:
                        try:
                            type_supported = parser.getboolean(self._file_section, infile)
                        except Exception as e:
                            logger.debug(e)
                        else:
                            if type_supported:
                                param['types'].append(infile)
            if succes:
                plugins.append(param)
        return plugins

    # End read
    # ------------------------------------------------------------------------
