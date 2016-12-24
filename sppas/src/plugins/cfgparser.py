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
import codecs

from structs.baseoption import Option

# ----------------------------------------------------------------------------

class PluginConfigParser( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Class to read a plugin configuration file.

    The required section "Configuration" includes an id, a name and a
    description, as for example:
        [Configuration]
        id:    pluginid
        name:  The Plugin Name
        descr: Performs something on some files.
        icon:  path (optional)

    Then, a required section with the name "Command" containing the "file" to
    work on:
        [Command]
        windows: toto.exe file
        macos:   toto.command file
        linux:   toto.bash file

    Finally, a set of sections with name starting by "Option" can be appended,
    as follow:
        [Option2]
        id:    -v
        type:  boolean
        value: False
        text:  Verbose mode

    """
    def __init__(self):
        self.reset()
        self.parser = SafeConfigParser()

    # ------------------------------------------------------------------------

    def reset(self):
        """ Set all members to their default value. """

        self._config = {}
        self._command = {}
        self._options = []

    # ------------------------------------------------------------------------

    def get_config(self):
        """ Return the configuration dictionary. """
        return self._config

    def get_command(self):
        """ Return the commands dictionary. """
        return self._command

    def get_options(self):
        """ Return the list of options. """
        return self._options

    # ------------------------------------------------------------------------

    def parse(self, filename):
        """
        Parse a configuration file.

        @param filename (str) Configuration file name.

        """
        self.reset()

        # Open the file with the correct encoding
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            self.parser.readfp(f)

        # Analyze content and set to appropriate data structures
        if self.parser.has_section( "Configuration" ):
            if self.parser.has_section( "Command" ):
                self._parse()
            else:
                raise ValueError("[Command] section is required.")
        else:
            raise ValueError("[Configuration] section is required.")

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _parse(self):

        for section_name in self.parser.sections():

            if section_name == "Configuration":
                self._parse_config(self.parser.items(section_name))

            if section_name == "Command":
                self._parse_command(self.parser.items(section_name))

            if section_name.startswith("Option"):
                self._options.append( self._parse_option(self.parser.items(section_name)) )

    # ------------------------------------------------------------------------

    def _parse_config(self, items):

        for name,value in items:
            self._config[name] = value.encode('utf-8')
        if not 'id' in self._config.keys():
            raise ValueError("[Configuration] section must contain an 'id' option.")

    def _parse_command(self, items):

        for name,value in items:
            self._command[name] = value.encode('utf-8')


    def _parse_option(self, items):

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
