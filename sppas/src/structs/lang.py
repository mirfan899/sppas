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
# File: lang.py
# ----------------------------------------------------------------------------

import os.path

from sp_glob import RESOURCES_PATH
import utils.fileutils

# ----------------------------------------------------------------------------

class LangResource( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Class to deal with a resource for a language.

    """
    def __init__(self):
        """
        Creates a new instance.

        """
        self.reset()

    # ------------------------------------------------------------------------

    def reset(self):
        """ Set all members to their default value. """

        # All available language resources (type, path, filename, extension)
        self._rtype = ""
        self._rpath = ""
        self._rname = ""
        self._rext  = ""

        # The list of languages the resource can provide
        self.langlist = []

        # The selected language
        self.lang = "und"

        # The language resource of the selected language
        self.langresource = ""

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_lang(self):
        return self.lang

    def get_langlist(self):
        return self.langlist

    def get_langresource(self):
        return self.langresource

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set(self, rtype, rpath, rname="", rext=""):
        """
        Set resources then fix the list of available languages.

        @param rtype (str) Resource type. One of: "file", "directory"
        @param rpath (str) Resource path
        @param rname (str) Resource file name
        @param rext (str)  Resource extension

        """
        self.reset()
        self._rtype = rtype
        self._rpath = rpath
        self._rname = rname
        self._rext = rext

        # Fix the language resource path/file
        directory = os.path.join(RESOURCES_PATH, rpath)
        if os.path.exists( directory ) is False:
            raise IOError('The resource directory %s does not exists.'%directory)
        if len(self._rname)>0:
            self.langresource = os.path.join(directory, self._rname)
        else:
            self.langresource = os.path.join(directory)

        # Fix the list of available languages
        if rtype == "file":

            langlistext = ""
            if len(rext) > 0:
                langlistext = utils.fileutils.get_files( directory, self._rext )
            self.langlist = [x[len(directory)+len(self._rname)+1:-len(self._rext)] for x in langlistext]

        elif rtype == "directory":
            self._rext = ""
            if len(rname)>0:
                self.langlist = [dirname.replace(rname, "") for dirname in os.listdir(directory) if dirname.startswith(rname) is True]

        else:
            self.reset()
            raise TypeError('Unknown resource type. Should be file or directory. Got %s'%rtype)

    # ------------------------------------------------------------------------

    def set_lang(self, lang):
        """
        Set the language.

        @param lang (str) The language must be "und" or one the language list.

        """
        if lang.lower() != "und" and not lang in self.langlist:
            raise ValueError('Unknown language %s.'%lang)

        self.lang = lang

        # Is there a resource available for this language?
        if lang in self.langlist:
            if len(self._rname)>0:
                self.langresource += lang + self._rext
            else:
                self.langresource = os.path.join(self.langresource, lang + self._rext)

    # ------------------------------------------------------------------------
