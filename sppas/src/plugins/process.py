# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.plugins.process.py
    ~~~~~~~~~~~~~~~~~~~~~~

    Process a plugin.
    This is currently restricted to one file only.

"""

import os.path
import shlex
from subprocess import Popen, PIPE, STDOUT

# ----------------------------------------------------------------------------


class sppasPluginProcess(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Class to run a plugin.

    """
    def __init__(self, plugin_param):
        """ Creates a new sppasPluginProcess instance.

        :param plugin_param: (sppasPluginParam)

        """
        self._plugin = plugin_param
        self._process = None

    # ------------------------------------------------------------------------

    def run(self, filename):
        """ Execute the plugin in batch mode (ie don't wait it to be finished).

        :param filename: (str) The file name of the file on which to apply the plugin
        :returns: Process output message

        """
        # the command
        command = self._plugin.get_command()

        # append the options (sorted like in the configuration file)
        for opt in self._plugin.get_options().values():
            opt_id = opt.get_key()

            if opt_id == "input":
                command += " \"" + filename + "\" "

            elif opt_id == "options":
                value = opt.get_untypedvalue()
                if len(value) > 0:
                    command += " "+value

            elif opt_id == "output":
                value = opt.get_untypedvalue()
                if len(value) > 0:
                    fname = os.path.splitext(filename)[0]
                    command += " \"" + fname + value + "\" "

            elif opt.get_type() == "bool":
                value = opt.get_value()
                if value is True:
                    command += " " + opt.get_key()

            else:
                command += " "+opt.get_key()
                value = opt.get_untypedvalue()
                if len(value) > 0:

                    if value == "input":
                        command += " \"" + filename + "\" "
                    else:
                        command += " "+value

        args = shlex.split(command)
        for i, argument in enumerate(args):
            if "PLUGIN_PATH/" in argument:
                newarg = argument.replace("PLUGIN_PATH/", "")
                args[i] = os.path.join(self._plugin.get_directory(), newarg)
        self._process = Popen(args, shell=False, stdout=PIPE, stderr=STDOUT, universal_newlines=True)

    # ------------------------------------------------------------------------

    def communicate(self):
        """ Wait for the process and get output messages (if any) then return it. """

        line = self._process.communicate()
        return "".join(line[0])

    # ------------------------------------------------------------------------

    def stop(self):
        """ Terminate the process if it is running. """

        if self.is_running() is True:
            self._process.terminate()

    # ------------------------------------------------------------------------

    def is_running(self):
        """ Return True if the process is running. """

        if self._process is None:
            return False
        # A None value indicates that the process hasn't terminated yet.
        return self._process.poll() is None

    # ------------------------------------------------------------------------
