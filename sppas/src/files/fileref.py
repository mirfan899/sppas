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

    src.files.fileref.py
    ~~~~~~~~~~~~~~~~~~~~~

"""

import re

from collections import OrderedDict

from sppas import sppasUnicode, sppasTypeError

from .filebase import FileBase
from enum import Enum

# ---------------------------------------------------------------------------


class AttValue(object):
    """Represents an attribute in the reference catalog.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    AttValue embeds a value its type and a description.

    """

    def __init__(self, att_value, att_type=None, att_description=None):
        """Constructor of AttValue.

        :param att_value: (str)
        :param att_type: (str)
        :param att_description: (str)

        """
        su = sppasUnicode(att_value)
        self.__value = su.to_strip()
        self.__valuetype = att_type
        if att_description is None:
            self.__description = att_description
        else:
            su = sppasUnicode(att_description)
            self.__description = su.to_strip()

    # -----------------------------------------------------------------------

    def get_value(self):
        """:return: current non-typed value (str)."""
        return self.__value

    # -----------------------------------------------------------------------

    def set_value(self, value):
        """
        set a new value.

        :param value: (string)

        """
        su = sppasUnicode(value)
        self.__value = su.to_strip()

    # -----------------------------------------------------------------------

    def get_value_type(self):
        """:return: current type of the value. (str, int, float, bool)."""
        return self.__valuetype if self.__valuetype is not None else 'str'

    # -----------------------------------------------------------------------

    def set_value_type(self, type):
        """Set a new type for the current value.

        :param type: (str) the new type name
        """
        if type in ('int', 'float', 'bool', 'str'):
            self.__valuetype = type
        else:
            raise sppasTypeError(type, 'int or float of bool or str')

    # -----------------------------------------------------------------------

    def get_typed_value(self):
        """:return: return the current typed value."""
        if self.__valuetype is not None or self.__valuetype != 'str':
            if self.__valuetype == 'int':
                return int(self.__value)
            elif self.__valuetype == 'float':
                return float(self.__value)
            elif self.__valuetype == 'bool':
                return self.__value.lower() == 'true'

        return self.__value

    # -----------------------------------------------------------------------

    def get_description(self):
        """:return: return current description (str)."""
        if self.__description is not None:
            su = sppasUnicode(self.__description)
            return su.to_strip()
        else:
            return self.__description

    # -----------------------------------------------------------------------

    def set_description(self, description):
        """set a new value for the description.

        :param description: (str).
        """
        su = sppasUnicode(description)
        self.__description = su.to_strip()

    description = property(get_description, set_description)

    # ---------------------------------------------------------
    # overloads
    # ----------------------------------------------------------

    def __str__(self):
        return '{!s:s}, {!s:s}'.format(self.__value,
                                       self.description) if self.description is not None else '{!s:s}'.format(
            self.__value)

    def __repr__(self):
        return 'AttValue: {!s:s}, {:s}'.format(self.__value,
                                               self.description) if self.description is not None else 'AttValue: {!s:s}'.format(
            self.__value)

    def __format__(self, fmt):
        return str(self).__format__(fmt)


# ---------------------------------------------------------------------------


class Reference(FileBase):
    """Represents a reference of a catalog about files.

    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Reference is a dictionary with a name. Its keys are only alphanumerics characters
    spaced with underscores and its values are all AttValue objects.

    """

    # ---------------------------------------------------------------------------
    class States(Enum):
        UNUSED = 0
        CHECKED = 1

    # ---------------------------------------------------------------------------

    class Types(Enum):
        NONE = 0
        SPEAKER = 1
        INTERACTION = 2

    # ---------------------------------------------------------------------------

    def __init__(self, identifier):
        """Constructor of the Category class.

        :param identifier: (str) identifier for the object, the name of the category

        """
        super(Reference, self).__init__(identifier)
        self.__attributs = OrderedDict()
        self.__type = self.Types.NONE
        self.__state = self.States.UNUSED

    # ---------------------------------------------------------------------------

    def add(self, key, value):
        """Add a new pair of key/value in the current dictionary.

        :param key: (str) should be only with alphanumeric characters and underscores
        :param value: (str, AttValue) will always be converted in AttValue object

        """

        # Used once hence declared inside add method
        def is_restricted_ascii(key_to_test):
            # if the string contains any other character than lower case a to z, upper case a to z and underscore it becomes a *
            ra = re.sub(r'[^a-zA-Z0-9_]', '*', key_to_test)
            return key_to_test == ra

        if is_restricted_ascii(key):
            if isinstance(value, AttValue):
                self.__attributs[key] = value
            else:
                self.__attributs[key] = AttValue(sppasUnicode(value).to_strip())
        else:
            raise ValueError('Non ASCII characters')

    # ---------------------------------------------------------------------------

    def pop(self, key):
        """Delete a pair of key/value.

        :param key: (str) is the key in the dictionary to delete

        """
        if key in self.__attributs.keys():
            self.__attributs.pop(key)
        else:
            raise ValueError('index not in Category')

    # ---------------------------------------------------------------------------

    def get_state(self):
        """Return its current state."""
        return self.__state

    # ---------------------------------------------------------------------------

    def set_state(self, state):
        """Set the current state to a new one.

        :param state: (Reference.States)
        :raises (sppasTypeError)

        """
        if isinstance(state, int):
            FileBase.state = state
        else:
            raise sppasTypeError(state, 'States')

    stateref = property(get_state, set_state)

    # ---------------------------------------------------------------------------

    def get_type(self):
        """Returns its current type"""
        return self.__type

    # ---------------------------------------------------------------------------

    def set_type(self, ref_type):
        """Set the type of the Reference to a new value within the authorized ones"""
        if isinstance(ref_type, self.Types):
            self.__type = ref_type
        else:
            raise sppasTypeError(ref_type, self.Types)

    type = property(get_type, set_type)

    # -----------------------------------------------------------------------
    # overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__attributs.keys())

    def __str__(self):
        return '{!s:s}'.format(self.__attributs)

    def __repr__(self):
        return 'Reference: {!s:s}'.format(self.__attributs)

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    def __getitem__(self, key):
        return self.__attributs[key]

    def __iter__(self):
        for key, value in self.__attributs.items():
            yield key, value

    def __contains__(self, key):
        return key in self.__attributs.keys()
