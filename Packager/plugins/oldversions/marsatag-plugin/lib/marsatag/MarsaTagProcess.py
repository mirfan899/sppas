#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Tatsuya Watanabe
#
# This file is part of MarsaTagPlugin.
#
# MarsaTagPlugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MarsaTagPlugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MarsaTagPlugin.  If not, see <http://www.gnu.org/licenses/>.

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import os
import subprocess
import shlex


# ---------------------------------------------------------------------------



class MarsaTagProcess(object):

    def __init__(self, command):
        """
        Initialize PluginProcess.
        Parameters:
            - command (str): command line
            - iparam (str):
        """
        if not self.__check_command(command):
            raise IOError('MaraTag not found')
        self.command = command
        self.process = None

    # End __init__
    # ------------------------------------------------------------------------

    def __check_command(self, command):
        # Return True if command exists.
        NULL = open(os.devnull, 'w')
        if isinstance(command, unicode):
            command = command.encode('utf-8')
        command = shlex.split(command)
        try:
            p = subprocess.Popen(command, shell=False, stdout=NULL, stderr=NULL)
        except OSError as e:
            return False
        else:
            p.kill()
            return True

    # End __check_command
    # ------------------------------------------------------------------------


    def IsRunning(self):
        """
        Return True if the process is running.
        Returns: (bool)
        """
        if self.process is None:
            return False
        # A None value indicates that the process hasn't terminated yet.
        return self.process.poll() is None

    # End IsRunning
    # ------------------------------------------------------------------------


    def Run(self, inputfiles=None):
        """
        Execute the command.
        Parameters:
            inputfiles (list)
        """
        command = self.command
        if inputfiles:
            inputfiles = " ".join(["'{0}'".format(infile) for infile in  inputfiles])
            command = "%s %s" % (command, inputfiles)
        self.process = subprocess.Popen(command, shell=True)

    # End Run
    # ------------------------------------------------------------------------


    def Terminate(self):
        """
        Stop the process.
        """
        if self.IsRunning():
            self.process.terminate()

    # End Terminate
    # ------------------------------------------------------------------------
