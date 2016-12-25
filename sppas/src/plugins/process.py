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
# File: process.py
# ----------------------------------------------------------------------------

import shlex
from subprocess import Popen, PIPE, STDOUT

# ----------------------------------------------------------------------------

class sppasPluginProcess( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Class to run a plugin.

    """
    def __init__(self, pluginparam):
        """
        Creates a new sppasPluginProcess instance.

        @param pluginparam (sppasPluginParam)

        """
        self.plugin = pluginparam
        self.process = None

    # ------------------------------------------------------------------------

    def run(self, filename):
        """
        Execute the plugin in batch mode (ie dont wait it to be finished).

        @param filename (string) The file name of the file to apply the plugin
        @return Process output message

        """
        # the command
        command = self.plugin.get_command()

        # append the options (sorted like in the configuration file)
        for opt in self.plugin.get_options().values():
            optid = opt.get_key()

            if optid == "input":
                command += " \"" + filename + "\" "

            elif optid == "options" or optid == "output":
                value = opt.get_untypedvalue()
                if len(value)>0:
                    command += " "+value

            else:
                command += " "+opt.get_key()
                value = opt.get_untypedvalue()
                if len(value)>0:

                    if value == "input":
                        command += " \"" + filename + "\" "
                    else:
                        command += " "+value

        # Execute the command
        if isinstance(command, unicode):
            command = command.encode('utf-8')

        args = shlex.split(command)
        self.process = Popen(args, shell=False, stdout=PIPE, stderr=STDOUT, universal_newlines=True)

    # ------------------------------------------------------------------------

    def communicate(self):
        """
        Wait for the process and get output messages (if any) then return it.

        """

        line = self.process.communicate()
        return "".join(line[0])

    # ------------------------------------------------------------------------

    def stop(self):
        """
        Terminate the process if it is running.

        """
        if self.is_running() is True:
            self.process.terminate()

    # ------------------------------------------------------------------------

    def is_running(self):
        """
        Return True if the process is running.

        """
        if self.process is None:
            return False
        # A None value indicates that the process hasn't terminated yet.
        return self.process.poll() is None

    # ------------------------------------------------------------------------
