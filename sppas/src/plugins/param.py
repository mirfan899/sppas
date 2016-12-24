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
# File: param.py
# ----------------------------------------------------------------------------

import os
import platform
import shlex
from subprocess import Popen

from cfgparser import PluginConfigParser

# ----------------------------------------------------------------------------

class sppasPluginParam( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      One SPPAS plugin parameters.

    """
    def __init__(self, directory, cfgfile):
        """
        Creates a new pluginParam instance.

        @param directory (string) the directory where to find the plugin
        @param cfgfile (string) the file name of the plugin configuration (.ini)

        """
        # The path where to find the plugin
        self._directory = directory
        self.reset()

        # OK... fill members from the given file
        self.parse( os.path.join(directory,cfgfile) )

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

        # The command to be executed and its options
        self._command = ""
        self._options = []

    # ------------------------------------------------------------------------

    def parse(self, filename):

        self.reset()
        p = PluginConfigParser()
        p.parse( filename )

        # get the command
        command = self.__get_command(p.get_command())
        if not self.__check_command(command):
            raise IOError("Command not found: %s" % command)
        self._command = command

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

    def get_directory(self):
        return self._directory

    def get_command(self):
        return self._command

    def get_options(self):
        return self._options

    def set_options(self, opt):
        self._options = opt

    # ------------------------------------------------------------------------

    def __get_command(self, commands):
        """ Return the appropriate command from a list of available ones. """

        _system = platform.system().lower()

        if 'windows' in _system and 'windows' in commands.keys():
            return commands['windows']
        if 'darwin' in _system and 'macos' in commands.keys():
            return commands['macos']
        if 'linux' in _system and 'linux' in commands.keys():
            return commands['linux']

        raise Exception("No command defined for the system: %s. Supported systems are: %s"%(_system," ".join(commands.keys())))

    # ------------------------------------------------------------------------

    def __check_command(self, command):
        """ Return True if command exists. """

        NULL = open(os.devnull, 'w')
        if isinstance(command, unicode):
            command = command.encode('utf-8')
        command = shlex.split(command)
        try:
            p = Popen(command, shell=False, stdout=NULL, stderr=NULL)
        except OSError:
            return False
        else:
            p.kill()
            return True

    # ------------------------------------------------------------------------
