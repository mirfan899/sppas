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

    src.calculus.pluginsexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for plugins package.

"""
from sppas.src.config import plugins_translation

# -----------------------------------------------------------------------

_ = plugins_translation.gettext

# -----------------------------------------------------------------------

CFG_FILE_ERROR = ":ERROR 4010: "
SECT_CFG_FILE_ERROR = ":ERROR 4014: "
OPT_CFG_FILE_ERROR = ":ERROR 4016: "
ARCHIVE_FILE_ERROR = ":ERROR 4020: "
ARCHIVE_IO_ERROR = ":ERROR 4024: "
DUPLICATE_ERROR = ":ERROR 4030: "
PLUGIN_ID_ERROR = ":ERROR 4040: "
PLUGIN_FOLDER_ERROR = ":ERROR 4050: "
PLUGIN_KEY_ERROR = ":ERROR 4060: "
CMD_EXEC_ERROR = ":ERROR 4070: "
CMD_SYSTEM_ERROR = ":ERROR 4075: "
OPTION_KEY_ERROR = ":ERROR 4080: "

# -----------------------------------------------------------------------


class PluginConfigFileError(IOError):
    """:ERROR 4010: Missing plugin configuration file."""

    def __init__(self):
        self.parameter = CFG_FILE_ERROR + (_(CFG_FILE_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class PluginSectionConfigFileError(ValueError):
    """:ERROR 4014: Missing section {section_name} in the configuration file."""

    def __init__(self, section_name):
        self.parameter = SECT_CFG_FILE_ERROR + (_(SECT_CFG_FILE_ERROR)).format(section_name=section_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class PluginOptionConfigFileError(ValueError):
    """:ERROR 4016: Missing option {:s} in section {:s} of the configuration file."""

    def __init__(self, section_name, option_name):
        self.parameter = OPT_CFG_FILE_ERROR + \
                         (_(OPT_CFG_FILE_ERROR)).format(
                             section_name=section_name,
                             option_name=option_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class PluginArchiveFileError(Exception):
    """:ERROR 4020: Unsupported plugin file type."""

    def __init__(self):
        self.parameter = ARCHIVE_FILE_ERROR + (_(ARCHIVE_FILE_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class PluginArchiveIOError(IOError):
    """:ERROR 4024: Unsupported plugin file type."""

    def __init__(self):
        self.parameter = ARCHIVE_IO_ERROR + (_(ARCHIVE_IO_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class PluginDuplicateError(IOError):
    """:ERROR 4030:.

     A plugin with the same name is already existing in the plugins folder.

     """

    def __init__(self):
        self.parameter = DUPLICATE_ERROR + (_(DUPLICATE_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class PluginIdError(ValueError):
    """:ERROR 4040: No plugin with identifier {plugin_id} is available."""

    def __init__(self, plugin_id):
        self.parameter = PLUGIN_ID_ERROR + \
                         (_(PLUGIN_ID_ERROR)).format(plugin_id=plugin_id)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class PluginFolderError(IOError):
    """:ERROR 4050: No such plugin folder: {:s}."""

    def __init__(self, plugin_folder):
        self.parameter = PLUGIN_FOLDER_ERROR + \
                         (_(PLUGIN_FOLDER_ERROR)).format(plugin_folder=plugin_folder)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class PluginKeyError(KeyError):
    """:ERROR 4060:.
    A plugin with the same key is already existing or plugin already loaded.

    """

    def __init__(self):
        self.parameter = PLUGIN_KEY_ERROR + (_(PLUGIN_KEY_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class CommandExecError(OSError):
    """:ERROR 4070: {command_name} is not a valid command on your operating system."""

    def __init__(self, command_name):
        self.parameter = CMD_EXEC_ERROR + \
                         (_(CMD_EXEC_ERROR)).format(command_name=command_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class CommandSystemError(OSError):
    """:ERROR 4075: No command was defined for the system: {:s}. Supported systems of this plugin are: {:s}."""

    def __init__(self, current_system, supported_systems=[]):
        systems = ",".join(supported_systems)
        self.parameter = CMD_SYSTEM_ERROR + (_(CMD_SYSTEM_ERROR)).format(current_system=current_system, supported_systems=systems)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class OptionKeyError(KeyError):
    """:ERROR 4080: No option with key {:s}."""

    def __init__(self, key):
        self.parameter = OPTION_KEY_ERROR + (_(OPTION_KEY_ERROR)).format(key=key)

    def __str__(self):
        return repr(self.parameter)
