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

    src.plugins.manager.py
    ~~~~~~~~~~~~~~~~~~~~~~

    A manager for the set of plugins of a software: load, install, apply,
    delete, etc.

"""

import os
import shutil
import logging
import zipfile
from threading import Thread

from sp_glob import PLUGIN_PATH
from utils.fileutils import sppasDirUtils
from .param import sppasPluginParam
from .process import sppasPluginProcess

# ----------------------------------------------------------------------------


class sppasPluginsManager(Thread):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Class to manage the list of plugins into SPPAS.

    """
    def __init__(self):
        """ Instantiate the sppasPluginsManager and load the current plugins. """

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
        """ Get the list of plugin identifiers.

        :returns: List of plugin identifiers.

        """
        return self._plugins.keys()

    # ------------------------------------------------------------------------

    def get_plugin(self, plugin_id):
        """ Get the sppasPluginParam from a plugin identifier.

        :returns: sppasPluginParam matching the plugin_id or None

        """
        return self._plugins.get(plugin_id, None)

    # ------------------------------------------------------------------------

    def set_progress(self, progress):
        """ Fix the progress system to be used while executing a plugin.

        :param progress: (TextProgress or ProcessProgressDialog)

        """
        self._progress = progress

    # ------------------------------------------------------------------------

    def load(self):
        """ Load all installed plugins in the SPPAS directory.

        A plugin is not loaded if:

            - a configuration file is not defined or corrupted,
            - the platform system of the command does not match.

        """
        folders = self.__get_plugins()
        for plugin_folder in folders:
            try:
                self.append(plugin_folder)
            except Exception as e:
                logging.info("Plugin %s loading error: %s" % (plugin_folder, str(e)))

    # ------------------------------------------------------------------------

    def install(self, plugin_archive, plugin_folder):
        """ Install a plugin into the plugin directory.

        :param plugin_archive: (string) File name of the plugin to be installed (ZIP).
        :param plugin_folder: (string) Destination folder name of the plugin to be installed.

        """
        if zipfile.is_zipfile(plugin_archive) is False:
            raise TypeError('Unsupported plugin file type.')

        plugin_dir = os.path.join(PLUGIN_PATH, plugin_folder)
        if os.path.exists(plugin_dir):
            raise IOError("A plugin with the same name is already existing in that folder.")

        os.mkdir(plugin_dir)

        with zipfile.ZipFile(plugin_archive, 'r') as z:
            restest = z.testzip()
            if restest is not None:
                raise Exception('zip file corrupted.')
            z.extractall(plugin_dir)

        try:
            plugin_id = self.append(plugin_folder)
        except Exception:
            shutil.rmtree(plugin_dir)
            raise

        return plugin_id

    # ------------------------------------------------------------------------

    def delete(self, plugin_id):
        """ Delete a plugin of the plugins directory.

        :param plugin_id: (str) Identifier of the plugin to delete.

        """
        p = self._plugins.get(plugin_id, None)
        if p is not None:
            shutil.rmtree(p.get_directory())
            del self._plugins[plugin_id]
        else:
            raise ValueError("No such plugin: %s" % plugin_id)

    # ------------------------------------------------------------------------

    def append(self, plugin_folder):
        """ Append a plugin in the list of plugins.
        It is supposed that the given plugin folder name is a folder of the
        plugin directory.

        :param plugin_folder: (string) The folder name of the plugin.

        """
        # Fix the full path of the plugin
        plugin_path = os.path.join(PLUGIN_PATH, plugin_folder)
        if os.path.exists(plugin_path) is False:
            raise IOError("No such folder: %s" % plugin_path)

        # Find a file with the extension .ini
        f = self.__get_config_file(plugin_path)
        if f is None:
            raise IOError("No configuration file for the plugin.")

        # Create the plugin instance
        p = sppasPluginParam(plugin_path, f)
        plugin_id = p.get_key()

        # Append in our list
        if plugin_id in self._plugins.keys():
            raise KeyError("A plugin with the same key is already existing or plugin already loaded.")

        self._plugins[plugin_id] = p
        return plugin_id

    # ------------------------------------------------------------------------

    def run_plugin(self, plugin_id, file_names):
        """ Apply a given plugin on a list of files.

        :param plugin_id: (string) Identifier of the plugin to apply.
        :param file_names: (list) List of files on which the plugin has to be applied.

        """
        if self._progress is not None:
            self._progress.set_header(plugin_id)
            self._progress.update(0, "")

        if plugin_id not in self._plugins.keys():
            raise TypeError("No plugin with identifier %s is available." % plugin_id)

        output_lines = ""
        total = len(file_names)
        for i, pfile in enumerate(file_names):

            # Indicate the file to be processed
            if self._progress is not None:
                self._progress.set_text(os.path.basename(pfile)+" ("+str(i+1)+"/"+str(total)+")")
            output_lines += "Apply plugin on file: %s\n" % pfile

            # Apply the plugin
            process = sppasPluginProcess(self._plugins[plugin_id])
            process.run(pfile)
            result = process.communicate()
            if len(result) == 0:
                output_lines += "done."
            else:
                output_lines += result

            # Indicate progress
            if self._progress is not None:
                self._progress.set_fraction(float((i+1))/float(total))
            output_lines += "\n"

        # Indicate completed!
        if self._progress is not None:
            self._progress.update(1, "Completed.\n")
            self._progress.set_header("")

        return output_lines

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    @staticmethod
    def __init_plugin_dir():
        """ Create the plugin directory if any. """

        if os.path.exists(PLUGIN_PATH):
            return True
        try:
            os.makedirs(PLUGIN_PATH)
        except OSError:
            return False
        else:
            return True

    # ------------------------------------------------------------------------

    @staticmethod
    def __get_plugins():
        """ Return a list of plugin folders. """

        folders = []
        for entry in os.listdir(PLUGIN_PATH):
            entry_path = os.path.join(PLUGIN_PATH, entry)
            if os.path.isdir(entry_path):
                folders.append(entry)

        return folders

    # ------------------------------------------------------------------------

    @staticmethod
    def __get_config_file(plugin_dir):
        """ Return the config file of a given plugin. """

        sd = sppasDirUtils(plugin_dir)
        files = sd.get_files(extension=".ini", recurs=False)
        # Find a file with the extension .ini, and only one
        if len(files) == 1:
            return files[0]

        return None

    # ------------------------------------------------------------------------
