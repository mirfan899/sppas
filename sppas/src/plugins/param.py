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
#                   Copyright (C) 2011-2017  Brigitte Bigi
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

from cfgparser import sppasPluginConfigParser

# ----------------------------------------------------------------------------


class sppasPluginParam(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      One SPPAS plugin set of parameters.

    """
    def __init__(self, directory, config_file):
        """
        Creates a new sppasPluginParam instance.

        :param directory: (string) the directory where to find the plugin
        :param config_file: (string) the file name of the plugin configuration

        """
        # The path where to find the plugin and its config
        self._directory = directory
        self._cfgfile   = config_file
        self._cfgparser = sppasPluginConfigParser()

        # Declare members and initialize
        self.reset()

        # OK... fill members from the given file
        self.parse()

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
        self._descr = ""
        # The icon of the plugin application
        self._icon = ""

        # The command to be executed and its options
        self._command = ""
        self._options = {}

    # ------------------------------------------------------------------------

    def parse(self):
        """
        Parse the configuration file of the plugin.

        """
        self.reset()
        filename = os.path.join(self._directory,self._cfgfile)
        self._cfgparser.parse(filename)

        # get the command
        command = self.__get_command(self._cfgparser.get_command())
        if not self.__check_command(command):
            raise IOError("Command not found: %s" % command)
        self._command = command

        # get the configuration
        conf = self._cfgparser.get_config()
        self._key   = conf['id']
        self._name  = conf.get("name", "")
        self._descr = conf.get("descr", "")
        self._icon  = conf.get("icon", "")

        # get the options
        self._options = self._cfgparser.get_options()

    # ------------------------------------------------------------------------

    def save(self):
        """
        Save the configuration file.
        Copy the old one into a backup file.

        """
        self._cfgparser.set_options(self._options)
        self._cfgparser.save(backup=True)

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

    def get_option_from_key(self, key):
        for option in self._options.values():
            if option.get_key() == key:
                return option
        raise KeyError("No option with key %s" % key)

    def get_options(self):
        return self._options

    def set_options(self, options_dict):
        self._options = options_dict

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    @staticmethod
    def __get_command(commands):
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

    @staticmethod
    def __check_command(command):
        """
        Return True if command exists.
        Test only the main command (i.e. the first string, without args).

        """
        command_args = shlex.split(command)
        test_command = command_args[0]

        NULL = open(os.devnull, 'w')
        if isinstance(test_command, unicode):
            test_command = test_command.encode('utf-8')
        try:
            p = Popen([test_command], shell=False, stdout=NULL, stderr=NULL)
        except OSError:
            return False
        else:
            p.kill()
            return True

    # ------------------------------------------------------------------------
