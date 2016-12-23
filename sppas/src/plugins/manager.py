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
# File: manager.py
# ----------------------------------------------------------------------------

import os
import logging
import platform
from subprocess import Popen, PIPE, STDOUT

from sp_glob import PLUGIN_PATH
from utils.filesutils import get_files
from cfgparser import PluginConfigParser
from dns.rdatatype import OPT

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class pluginParam( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      One SPPAS plugin parameters (Private class).

    """
    def __init__(self, path, cfgfile):
        """
        Creates a new pluginParam instance.

        @param path (string) the directory where to find the plugin
        @param cfgfile (string) the file name of the plugin configuration (.ini)

        """
        # The path where to find the plugin
        self._path = path
        self.reset()

        # OK... fill members from the given file
        self.parse( os.path.join(path,cfgfile) )

    # ------------------------------------------------------------------------

    def reset(self):
        """
        Reset all members to their default value.

        """
        # An identifier to represent this plugin
        self._key  = None
        # The name of the plugin
        self._name = ""
        # The description of the plugin do
        self._desc = ""
        # The icon of the plugin application
        self._icon = ""
        # The command to be executed
        self._command = ""
        # The list of options to append to the command
        self._options = []

    # ------------------------------------------------------------------------

    def parse(self, filename):

        self.reset()
        p = PluginConfigParser()
        p.parse( filename )

        # get the command
        commands = p.get_command()
        system = platform.system()
        if system in commands.keys():
            self._command = commands[system]
        else:
            raise Exception("No command defined for the system: %s"%system)

        # get the configuration
        conf = p.get_config()
        self._key   = conf['id']
        self._name  = conf.get("name", "")
        self._descr = conf.get("descr", "No description available.")
        self._icon  = conf.get("icon", "")

        # get the options
        self._options = p.get_options()

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_key(self):
        return self._key

    def get_name(self):
        return self._name

    def get_descr(self):
        return self._descr

    def get_icon(self):
        return self._icon

    def get_options(self):
        return self._options

    def set_options(self, opt):
        self._options = opt

    # ------------------------------------------------------------------------

    def perform_command(self, filename):
        """
        Execute the plugin.

        @param filename (string) The file name of the file to apply the plugin
        @return Process output

        """
        # the command
        command = os.path.join(self._path,self._command)
        for opt in self._options:
            command += " "+opt.get_key()
            command += " "+opt.get_value()

        # Execute the command
        p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
        p.wait()
        line = p.communicate()

        return line

    # ------------------------------------------------------------------------


# ----------------------------------------------------------------------------


class PluginsManager( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Class to manage the list of plugins into SPPAS.

    """
    def __init__(self):
        self._plugins = {}

    # ------------------------------------------------------------------------

    def load(self):
        """
        Load the list of available plugins in the SPPAS directory.

        """
        cfgfiles = self.get_config_files()
        p = PluginConfigParser()
        for path,file in cfgfiles:
            try:
                p = pluginParam( path,file )
                pluginid = p.get_key()
                self._plugins[pluginid] = p
            except Exception as e:
                logging.debug('Error while loading plugin %s: %s'%(path,str(e)))

    # ------------------------------------------------------------------------

    def get_config_files(self):
        """ Return a dictionary with key=path and value=cfgfile. """

        inifiles = {}
        # Get The list of "ini" files (one for each plugin)
        for entry in os.listdir(PLUGIN_PATH):
            entrypath = os.path.join(PLUGIN_PATH, entry)
            if os.path.isdir(entrypath):
                # Find a file with the extension .ini
                files = get_files(entrypath, extension=".ini", recurs=False)
                if len(files) == 1:
                    inifiles[entrypath] = files[0]

        return inifiles

    # ------------------------------------------------------------------------

    def perform_plugin(self, pluginid, filenames):
        """
        Apply a given plugin on a list of files.

        @param pluginid (string) Identifier of the plugin to apply.
        @param filenames (list) List of files on which the plugin has to be applied.

        """
        if not pluginid in self._plugins.keys():
            raise TypeError("No plugin with identifier %s is available."%pluginid)

        outputlines = ""
        for file in filenames:
            outputlines = "Apply plugin on file: %s"%file
            lines = self._plugins[pluginid].perform_command( file )
            if len(lines) == 0:
                outputlines += "done."
            else:
                outputlines += lines

        return outputlines

    # ------------------------------------------------------------------------
