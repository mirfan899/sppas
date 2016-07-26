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
# File: baseoption.py
# ----------------------------------------------------------------------------

from sp_glob import encoding

# ----------------------------------------------------------------------------

class BaseOption( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Class to deal with one option.

    An option is a set of data with a main value and its type, then 3 other
    variables to store any kind of information.

    """
    def __init__(self, optiontype, optionvalue=""):
        """
        Creates a new option instance.

        """
        self._type  = optiontype.lower()
        self._value = optionvalue
        self._text  = ""
        self._name  = ""
        self._description = ""

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_type(self):
        """ Return the type (as a String) of the option. """
        return self._type

    def get_untypedvalue(self):
        """ Return the value as it was given. """
        return self._value

    def get_value(self):
        """ Return the typed-value or None. """

        if self._type.startswith('bool'):
            if isinstance(self._value, bool):
                return self._value
            if self._value.lower() == "true":
                return True
            else:
                return False

        if self._type.startswith('int') or self._type == 'long' or self._type == 'short':
            return int(self._value)

        if self._type == 'float' or self._type == 'double':
            return float(self._value)

        if self._type.startswith('str'):
            return self._value.decode(encoding)

        return None

    def get_name(self):
        """ Return the name of to this option. """
        return self._name

    def get_text(self):
        """ Return the brief text which describes the option. """
        return self._text

    def get_description(self):
        """ Return the long text which describes the option. """
        return self._description

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set(self, other):
        """ Set self to another instance. """
        self._type         = other.get_type()
        self._value        = other.get_value()
        self._text         = other.get_text()
        self._name         = other.get_name()
        self._description  = other.get_description()

    def set_type(self, opttype):
        """ Set a new type. """
        self._type = opttype

    def set_value(self, value):
        """ Set a new value. """
        self._value = value

    def set_name(self, name):
        """ Set the name of the options. """
        self._name = name

    def set_text(self, text):
        """ Set the brief text which describes the option. """
        self._text = text

    def set_description(self, descr):
        """ Set the long text which describes the option. """
        self._description = descr

    # ------------------------------------------------------------------------
