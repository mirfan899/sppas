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
# File: confparser.py
# ----------------------------------------------------------------------------

from ConfigParser import SafeConfigParser
import codecs

from structs.lang       import LangResource
from structs.baseoption import Option

# ----------------------------------------------------------------------------

class ConfigParser( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Class to read a configuration file.

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

    """
    def __init__(self):
        """ Creates a new instance. """

        self.reset()
        self.parser = SafeConfigParser()

    # ------------------------------------------------------------------------

    def reset(self):
        """ Set all members to their default value. """

        self.config = {}
        self.resources = []
        self.options   = []

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_config(self):
        """ Return the configuration dictionary. """
        return self.config

    def get_resources(self):
        """ Return the list of language resources. """
        return self.resources

    def get_options(self):
        """ Return the list of options. """
        return self.options

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
        self._parse( )

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _parse(self):

        for section_name in self.parser.sections():

            if section_name == "Configuration":
                self._parse_config(self.parser.items(section_name))

            if section_name.startswith("Resource"):
                self.resources.append( self._parse_resource(self.parser.items(section_name)) )

            if section_name.startswith("Option"):
                self.options.append( self._parse_option(self.parser.items(section_name)) )

    # ------------------------------------------------------------------------

    def _parse_config(self, items):

        for name,value in items:
            self.config[name] = value.encode('utf-8')

    # ------------------------------------------------------------------------

    def _parse_resource(self, items):

        rtype = ""
        rpath = ""
        rname = ""
        rext  = ""
        lr = LangResource()
        for name,value in items:
            if name == "type":
                rtype = value.encode('utf-8')
            elif name == "path":
                rpath = value.encode('utf-8')
            elif name == "name":
                rname = value.encode('utf-8')
            elif name == "ext":
                rext  = value.encode('utf-8')
        lr.set( rtype, rpath, rname, rext )

        return lr

    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------
