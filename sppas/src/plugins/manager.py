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
# File: manager.py
# ----------------------------------------------------------------------------

import os
import shutil
import logging
import zipfile
from threading import Thread

from sp_glob import PLUGIN_PATH
import utils.fileutils as fileutils
from param   import sppasPluginParam
from process import sppasPluginProcess

# ----------------------------------------------------------------------------

class sppasPluginsManager( Thread ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Class to manage the list of plugins into SPPAS.

    """
    def __init__(self):
        """
        Instantiate the sppasPluginsManager and load the current plugins.

        """
        Thread.__init__(self)

        # Load the installed plugins
        self._plugins = {}
        if self.__init_plugin_dir() is True:
            self.load()

        # To get progress information while executing a plugin
        self._progress = None

        # Start threading
        self.start()

    # ------------------------------------------------------------------------

    def get_plugin_ids(self):
        """
        Return the list of plugin identifiers.

        """
        return self._plugins.keys()

    # ------------------------------------------------------------------------

    def get_plugin(self, pluginid):
        """
        Return the sppasPluginParam from a plugin identifier.

        """
        return self._plugins[pluginid]

    # ------------------------------------------------------------------------

    def set_progress(self, progress):
        """
        Fix the progress system to be used while executing a plugin.

        @param progress (TextProgress or ProcessProgressDialog)

        """
        self._progress = progress

    # ------------------------------------------------------------------------

    def load(self):
        """
        Load all installed plugins in the SPPAS directory.

        A plugin is not loaded if:
            - a configuration file is not defined or corrupted,
            - the platform system of the command does not match.

        """
        folders = self.__get_plugins()
        for pluginfolder in folders:
            try:
                self.append(pluginfolder)
            except Exception as e:
                logging.info("Plugin %s loading error: %s"%(pluginfolder,str(e)))

    # ------------------------------------------------------------------------

    def install(self, pluginarchive, pluginfolder):
        """
        Install a plugin into the plugin directory.

        @param pluginarchive (string) File name of the plugin to be installed (ZIP).
        @param pluginfolder (string) Destination folder name of the plugin to be installed.

        """
        if zipfile.is_zipfile(pluginarchive) is False:
            raise TypeError('Unsupported plugin file type.')

        plugindir = os.path.join(PLUGIN_PATH,pluginfolder)
        if os.path.exists(plugindir):
            raise IOError("A plugin is already existing in that folder.")

        os.mkdir(plugindir)

        with zipfile.ZipFile(pluginarchive, 'r') as z:
            restest = z.testzip()
            if restest is not None:
                raise Exception('zip file corrupted.')
            z.extractall(plugindir)

        try:
            pluginid = self.append(pluginfolder)
        except Exception:
            shutil.rmtree(plugindir)
            raise

        return pluginid

    # ------------------------------------------------------------------------

    def delete(self, pluginid):
        """
        Delete a plugin of the plugin directory.

        @param pluginid (string) Identifier of the plugin to delete.

        """
        p = self._plugins.get( pluginid, None )
        if p is not None:
            shutil.rmtree( p.get_directory() )
            del self._plugins[pluginid]
        else:
            raise ValueError("No such plugin: %s"%pluginid)

    # ------------------------------------------------------------------------

    def append(self, pluginfolder):
        """
        Append a plugin in the list of plugins.
        It is supposed that the given plugin folder name is a folder of the
        plugin directory.

        @param pluginfolder (string) The folder name of the plugin.

        """
        # Fix the full path of the plugin
        pluginpath = os.path.join(PLUGIN_PATH,pluginfolder)
        if os.path.exists( pluginpath ) is False:
            raise IOError("No such folder: %s"%(pluginpath))

        # Find a file with the extension .ini
        f = self.__get_config_file(pluginpath)
        if f is None:
            raise IOError("No configuration file for the plugin.")

        # Create the plugin instance
        p = sppasPluginParam( pluginpath,f )
        pluginid = p.get_key()

        # Append in our list
        if pluginid in self._plugins.keys():
            raise KeyError("A plugin with the same key is already existing or plugin already loaded.")

        self._plugins[pluginid] = p
        return pluginid

    # ------------------------------------------------------------------------

    def run_plugin(self, pluginid, filenames):
        """
        Apply a given plugin on a list of files.

        @param pluginid (string) Identifier of the plugin to apply.
        @param filenames (list) List of files on which the plugin has to be applied.

        """
        if self._progress is not None:
            self._progress.set_header( pluginid )
            self._progress.update(0,"")

        if not pluginid in self._plugins.keys():
            raise TypeError("No plugin with identifier %s is available."%pluginid)

        outputlines = ""
        total = len(filenames)
        for i,pfile in enumerate(filenames):

            # Indicate the file to be processed
            if self._progress is not None:
                self._progress.set_text( os.path.basename(pfile)+" ("+str(i+1)+"/"+str(total)+")" )
            outputlines = "Apply plugin on file: %s\n"%pfile

            # Apply the plugin
            process = sppasPluginProcess( self._plugins[pluginid] )
            process.run( pfile )
            result = process.communicate()
            if len(result) == 0:
                outputlines += "done."
            else:
                outputlines += result

            # Indicate progress
            if self._progress is not None:
                self._progress.set_fraction(float((i+1))/float(total))
            outputlines += "\n"

        # Indicate completed!
        if self._progress is not None:
            self._progress.update(1,"Completed.\n")
            self._progress.set_header("")

        return outputlines

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __init_plugin_dir(self):
        """ Create the plugin directory if any. """

        if os.path.exists( PLUGIN_PATH ):
            return True
        try:
            os.makedirs( PLUGIN_PATH )
        except OSError:
            return False
        else:
            return True

    # ------------------------------------------------------------------------

    def __get_plugins(self):
        """ Return a list of plugin folders. """

        folders = []
        for entry in os.listdir(PLUGIN_PATH):
            entrypath = os.path.join(PLUGIN_PATH, entry)
            if os.path.isdir(entrypath):
                folders.append(entry)

        return folders

    # ------------------------------------------------------------------------

    def __get_config_file(self, plugindir):
        """ Return the config file of a given plugin. """

        # Find a file with the extension .ini, and only one
        files = fileutils.get_files(plugindir, extension=".ini", recurs=False)
        if len(files) == 1:
            return files[0]

        return None

    # ------------------------------------------------------------------------
