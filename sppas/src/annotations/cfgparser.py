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

    src.annotations.cfgparser.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    Here is an example with a comment, a section definition and two options:

        | # This is a comment in a configuration file
        | [Section]
        | option1 = value1
        | option2 = value2

"""
import codecs
try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

from structs.lang import sppasLangResource
from structs.baseoption import sppasOption
from sp_glob import encoding

# ----------------------------------------------------------------------------


class AnnotationConfigParser(object):
    """
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      brigitte.bigi@gmail.com
    :summary:      Class to read an annotation configuration file.

    The required section "Configuration" includes an id, a name and a
    description, as for example:
    
        | [Configuration]
        | id:    annotationid
        | name:  The Annotation Name
        | descr: Performs an annotation on a file.

    Then, a set of sections with name starting by "Resource" can be defined,
    with the relative path to resource directory, the type (file or dir) and
    the extension, as for example:
        
        | [Resource]
        | path:  vocab
        | type:  file
        | ext:   .stp

    Finally, a set of sections with name starting by "Option" can be appended,
    as follow:
        
        | [Option1]
        | id:    optid
        | type:  int
        | value: 0
        | text:  Explain what this option do here.

    """
    def __init__(self):
        """ Creates a new instance. """

        self._config = {}
        self._resources = []
        self._options = []
        self.parser = SafeConfigParser()

    # ------------------------------------------------------------------------

    def reset(self):
        """ Set all members to their default value. """

        self._config = {}
        self._resources = []
        self._options = []

    # ------------------------------------------------------------------------

    def get_config(self):
        """ Return the configuration dictionary. """
        
        return self._config

    def get_resources(self):
        """ Return the list of language resources. """
        
        return self._resources

    def get_options(self):
        """ Return the list of options. """
        
        return self._options

    # ------------------------------------------------------------------------

    def parse(self, filename):
        """ Parse a configuration file.

        :param filename: (str) Configuration file name.

        """
        self.reset()

        # Open the file with the correct encoding
        with codecs.open(filename, 'r', encoding) as f:
            self.parser.readfp(f)

        # Analyze content and set to appropriate data structures
        if self.parser.has_section("Configuration"):
            self._parse()
        else:
            raise Exception("Annotation configuration error: [Configuration] section required.")

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _parse(self):

        for section_name in self.parser.sections():

            if section_name == "Configuration":
                self._parse_config(self.parser.items(section_name))

            if section_name.startswith("Resource"):
                self._resources.append(self._parse_resource(self.parser.items(section_name)))

            if section_name.startswith("Option"):
                self._options.append(self._parse_option(self.parser.items(section_name)))

    # ------------------------------------------------------------------------

    def _parse_config(self, items):

        for name,value in items:
            self._config[name] = value.encode(encoding)

    # ------------------------------------------------------------------------

    def _parse_resource(self, items):

        rtype = ""
        rpath = ""
        rname = ""
        rext  = ""
        lr = sppasLangResource()
        for name, value in items:
            if name == "type":
                rtype = value.encode(encoding)
            elif name == "path":
                rpath = value.encode(encoding)
            elif name == "name":
                rname = value.encode(encoding)
            elif name == "ext":
                rext  = value.encode(encoding)
        lr.set(rtype, rpath, rname, rext)

        return lr

    # ------------------------------------------------------------------------

    def _parse_option(self, items):

        oid = ""
        otype = ""
        ovalue = ""
        otext = ""

        for name, value in items:
            if name == "type":
                otype = value.encode(encoding)
            elif name == "id":
                oid = value.encode(encoding)
            elif name == "value":
                ovalue = value.encode(encoding)
            elif name == "text":
                otext = value.encode(encoding)

        opt = sppasOption(oid)
        opt.set_type(otype)
        opt.set_value(ovalue)
        opt.set_text(otext)

        return opt

# ----------------------------------------------------------------------------
