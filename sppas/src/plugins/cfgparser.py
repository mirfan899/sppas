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
# File: cfgparser.py
# ----------------------------------------------------------------------------
"""
    A config file consists of one or more named sections, each of which can
    contain individual options with names and values.

    Config file sections are identified by looking for lines starting with
    [ and ending with ]. The value between the square brackets is the section
    name, and can contain any characters except square brackets.

    Options are listed one per line within a section. The line starts with
    the name of the option, which is separated from the value by a colon (:)
    or equal sign (=).
    Whitespace around the separator is ignored when the file is parsed.

    A config file may include comments, prefixed by specific characters
    (# and ;).

    Example:
    ----------------

    # This is a comment in a configuration file
    [Section]
    option1 = value1
    option2 = value2

"""
# ----------------------------------------------------------------------------

from ConfigParser import SafeConfigParser
from shutil import copyfile
import collections

from structs.baseoption import Option

# ----------------------------------------------------------------------------

class sppasPluginConfigParser( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Class to read a plugin configuration file.

    The required section "Configuration" includes an id, a name and a
    description, as for example:
        [Configuration]
        id:    pluginid
        name:  The Plugin Name
        descr: Performs something on some files.
        icon:  path (optional)

    Then, a required section with the name "Command":
        [Command]
        windows: toto.exe
        macos:   toto.command
        linux:   toto.bash

    Finally, a set of sections with name starting by "Option" can be appended,
    as follow:
        [Option2]
        id:    -v
        type:  boolean
        value: False
        text:  Verbose mode

    Some specific 'id' or 'value' of Option sections can be defined and will be
    interpreted differently:
        - input
        - options

    """
    def __init__(self, filename=None):
        """
        Create a parser.

        """
        self._parser = SafeConfigParser()
        self._filename = None
        if filename is not None:
            self.parse( filename )

    # ------------------------------------------------------------------------

    def get_config(self):
        """
        Return the 'Configuration' section content.

        @return dictionary.

        """
        cfgdict = {}

        for section_name in self._parser.sections():
            if section_name == "Configuration":
                for name,value in self._parser.items(section_name):
                    cfgdict[name] = value.encode('utf-8')

        if not 'id' in cfgdict.keys():
            raise ValueError("[Configuration] section must contain an 'id' option.")

        return cfgdict

    # ------------------------------------------------------------------------

    def get_command(self):
        """
        Return the 'Command' section content.

        @return dictionary.

        """
        cfgdict = {}

        for section_name in self._parser.sections():
            if section_name == "Command":
                for name,value in self._parser.items(section_name):
                    cfgdict[name] = value.encode('utf-8')

        return cfgdict

    # ------------------------------------------------------------------------

    def get_options(self):
        """
        Return all the 'Option' section contents.
        The section name is used as key. Values are of type "Option".

        @return ordered dictionary.

        """
        cfgdict = collections.OrderedDict()

        for section_name in self._parser.sections():
            if section_name.startswith( "Option" ):
                opt = self.__parse_option(self._parser.items(section_name))
                cfgdict[section_name] = opt

        return cfgdict

    # ------------------------------------------------------------------------

    def set_options(self, options):
        """
        Re-set all the 'Option' section.

        @param options (ordered dictionary) with key=section name, and value
        if of type "Option" (with at least a "key").

        """
        # Remove all current options of the parser.
        currentoptions = []
        for section_name in self._parser.sections():
            if section_name.startswith( "Option" ):
                currentoptions.append[ section_name ]

        for section_name in currentoptions:
            self._parser.remove_section(section_name)

        # Append all new options to the parser.
        for section_name in options.keys():
            self.__set_option(section_name, options[section_name])

    # ------------------------------------------------------------------------

    def parse(self, filename):
        """
        Parse a configuration file.
        This will forget all previous configurations (if any).

        @param filename (str) Configuration file name.

        """
        # Open the file
        with open(filename, "r") as f:
            self._parser.readfp(f)
        self._filename = filename

        # Check content
        if self._parser.has_section( "Configuration" ):
            if not self._parser.has_section( "Command" ):
                raise ValueError("[Command] section is required.")
        else:
            raise ValueError("[Configuration] section is required.")

    # ------------------------------------------------------------------------

    def save(self, backup=True):
        """
        Save the configuration file.
        Copy the old one into a backup file.

        """
        if self._filename is None:
            raise Exception('This parser is not linked to a configuration file.')

        if backup is True:
            copyfile(self._filename, self._filename+".backup")

        with open(self._filename,'w') as cfg:
            self._parser.write(cfg)

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __parse_option(self, items):
        """ Parse an option, i.e. convert an "Option" section of the parser into an "Option" instance. """
        oid    = ""
        otype  = ""
        ovalue = ""
        otext  = ""

        for name,value in items:
            if name == "type":
                otype = value.encode('utf-8')
            elif name == "id":
                oid = value.encode('utf-8')
            elif name == "value":
                ovalue = value.encode('utf-8')
            elif name == "text":
                otext = value.encode('utf-8')

        opt = Option(oid)
        opt.set_type(otype)
        opt.set_value(ovalue)
        opt.set_text(otext)

        return opt

    # ------------------------------------------------------------------------

    def __set_option(self, section_name, option):
        """ Set an option, i.e. convert an "Option" instance into an "Option" section of the parser. """

        self._parser.add_section( section_name )
        self._parser.set(section_name, "id", option.get_key())

        if len(option.get_type()) > 0:
            self._parser.set(section_name, "type", option.get_type())

        if len(option.get_untypedvalue()) > 0:
            self._parser.set(section_name, "value",option.get_untypedvalue())

        if len(option.get_text()) > 0:
            self._parser.set(section_name, "text", option.get_text())


    # ------------------------------------------------------------------------
