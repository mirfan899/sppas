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
    ~~~~~~~~~~~~~~~~~~~~

"""

import logging
import re

from collections import OrderedDict

from sppas import sppasTypeError, sppasIndexError
from sppas.src.utils.makeunicode import sppasUnicode

from .filebase import FileBase, States

# ---------------------------------------------------------------------------


class sppasAttribute(object):
    """Represents any attribute with a key, a value, and a description.

    :author:       Barthélémy Drabczuk, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This class embeds a key, a value, its type and a description.

    """

    VALUE_TYPES = ('str', 'int', 'float', 'bool')

    def __init__(self, key, value=None, att_type=None, descr=None):
        """Constructor of sppasAttribute.

        :param key: (str) The identifier key of the attribute
        :param value: (str) String representing the value of the attribute
        :param att_type: (str) One of the VALUE_TYPES
        :param descr: (str) A string to describe what the attribute is

        """
        self.__key = ""
        self.__set_key(key)

        self.__value = None
        self.set_value(value)
        
        self.__valuetype = 'str'
        self.set_value_type(att_type)

        self.__descr = None
        self.set_description(descr)

    # -----------------------------------------------------------------------

    @staticmethod
    def validate(key):
        """Return True the given key matches the requirements.

        A key should contain between 3 and 12 ASCII-characters only, i.e.
        letters a-z, letters A-Z and numbers 0-9.

        :param key: (str) Key to be validated
        :return: (bool)

        """
        def is_restricted_ascii(key_to_test):
            # change any other character than a to z and underscore in the key
            ra = re.sub(r'[^a-zA-Z0-9_]', '*', key_to_test)
            return key_to_test == ra

        if 2 < len(key) < 13:
            return is_restricted_ascii(key)
        return False

    # -----------------------------------------------------------------------

    def __set_key(self, key):
        su = sppasUnicode(key)
        key = su.unicode()

        if sppasAttribute.validate(key) is False:
            raise ValueError("Key {:s} is not valid. It should be between 3 and 12 ASCII-characters.".format(key))

        self.__key = key

    # -----------------------------------------------------------------------

    def get_key(self):
        """Return the key of the attribute."""
        return self.__key

    # -----------------------------------------------------------------------

    def get_value(self):
        """Return the current non-typed value.

        :returns: (str)

        """
        if self.__value is None:
            return ""
        return self.__value

    # -----------------------------------------------------------------------

    def set_value(self, value):
        """Set a new value.

        :param value: (str)

        """
        if value is None:
            self.__value = None
        else:
            su = sppasUnicode(value)
            self.__value = su.to_strip()

    # -----------------------------------------------------------------------

    def get_value_type(self):
        """Return the current type of the value.

        :returns: (str) Either: "str", "int", "float", "bool".

        """
        return self.__valuetype if self.__valuetype is not None else 'str'

    # -----------------------------------------------------------------------

    def set_value_type(self, type_name):
        """Set a new type for the current value.

        :param type_name: (str) the new type name

        """
        if type_name in sppasAttribute.VALUE_TYPES:
            self.__valuetype = type_name
        elif type_name is None:
            self.__valuetype = 'str'
        else:
            raise sppasTypeError(type_name, " ".join(sppasAttribute.VALUE_TYPES))

    # -----------------------------------------------------------------------

    def get_typed_value(self):
        """Return the current typed value.

        :return: (any type) the current typed value.

        """
        if self.__valuetype is not None or self.__valuetype != 'str':
            try:
                if self.__valuetype == 'int':
                    return int(self.__value)
                elif self.__valuetype == 'float':
                    return float(self.__value)
                elif self.__valuetype == 'bool':
                    return self.__value.lower() == 'true'
            except ValueError:
                raise
                # TODO: raise sppas Exception with appropriate msg

        return self.__value

    # -----------------------------------------------------------------------

    def get_description(self):
        """Return current description.

        :return: (str)

        """
        if self.__descr is None:
            return ""
        return self.__descr

    # -----------------------------------------------------------------------

    def set_description(self, description):
        """Set a new description of the attribute.

        :param description: (str)

        """
        if description is None:
            self.__descr = None
        else:
            su = sppasUnicode(description)
            self.__descr = su.to_strip()

    # -----------------------------------------------------------------------

    def serialize(self):
        """Return a dict representing this instance for json format."""
        d = dict()
        d['key'] = self.__key
        d['value'] = self.__value
        d['type'] = self.__valuetype
        d['descr'] = self.__descr
        return d

    # -----------------------------------------------------------------------

    @staticmethod
    def parse(d):
        """Return the sppasAttribute from the given dict.

        :param d: (dict) 'key' required. optional: 'value', 'type', 'descr'

        """
        k = d['key']
        v = None
        if 'value' in d:
            v = d['value']
        t = None
        if 'type' in d:
            t = d['type']
        descr = None
        if 'descr' in descr:
            t = descr['descr']

        return sppasAttribute(k, v, t, descr)

    # -----------------------------------------------------------------------

    def match(self, key, function, value):
        """Return True if the attribute value matches all of the functions.

        Functions are defined in a comparator. They return a boolean.
        The type of the value depends on the function.
        The logical not is used to reverse the result of the function.

        The given value is a tuple with both the key of the attribute and the
        expected value which has to match the given value.

        :returns: (bool)

        """
        if key != self.__key:
            return False
        return function(self, value)

    # ---------------------------------------------------------
    # overloads
    # ----------------------------------------------------------

    def __str__(self):
        return '{:s}, {:s}, {:s}'.format(
            self.__key,
            self.get_value(),
            self.get_description())

    def __repr__(self):
        return '{:s}, {:s}, {:s}'.format(
            self.__key,
            self.get_value(),
            self.get_description())

    def __format__(self, fmt):
        return str(self).__format__(fmt)

# ---------------------------------------------------------------------------


class FileReference(FileBase):
    """Represent a reference of a catalog about files.

    :author:       Barthélémy Drabczuk, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Reference is a dictionary with a name. Its keys are only alphanumerics characters
    spaced with underscores and its values are all sppasAttribute objects.

    """

    REF_TYPES = ('NONE', 'SPEAKER', 'INTERACTION')

    def __init__(self, identifier):
        """Constructor of the FileReference class.

        :param identifier: (str) identifier for the object, the name of the reference

        """
        super(FileReference, self).__init__(identifier)

        self.__attributs = list()
        self.__type = FileReference.REF_TYPES[0]

        # A free to use member to expand the class
        self.subjoined = None

    # ------------------------------------------------------------------------

    def att(self, key):
        """Return the attribute matching the given key or None.

        """
        su = sppasUnicode(key)
        key = su.unicode()
        for a in self.__attributs:
            if a.get_key() == key:
                return a

        return None

    # ------------------------------------------------------------------------

    def add(self, key, value=None, att_type=None, descr=None):
        """Append an attribute into the reference.

        """
        self.append(sppasAttribute(key, value, att_type, descr))

    # ------------------------------------------------------------------------

    def append(self, att):
        """Add an attribute.

        :param att: (sppasAttribute)

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")

        if att in self:
            raise KeyError('An attribute with key {:s} is already existing in'
                           'the reference {:s}.'.format(att.get_key(), self.id))

        self.__attributs.append(att)

    # ------------------------------------------------------------------------

    def pop(self, key):
        """Delete an attribute of this reference.

        :param key: (str, sppasAttribute) the key of the attribute to delete

        """
        if key in self:
            if isinstance(key, sppasAttribute) is False:
                key = self.att(key)
            self.__attributs.remove(key)
        else:
            raise ValueError('{:s} is not a valid key for {:s}'
                             ''.format(key, self.id))

    # ------------------------------------------------------------------------

    def set_state(self, state):
        """Set the current state to a new one.

        :param state: (Reference.States)
        :raises (sppasTypeError)

        """
        if isinstance(state, int):
            self._state = state
        else:
            raise sppasTypeError(state, 'States')

    # ------------------------------------------------------------------------

    def get_type(self):
        """Returns the type of the Reference."""
        return self.__type

    # ------------------------------------------------------------------------

    def set_type(self, ref_type):
        """Set the type of the Reference within the authorized ones."""
        if ref_type in FileReference.REF_TYPES:
            self.__type = ref_type
        else:
            try:
                ref_index = int(ref_type)
                if ref_index in range(0, len(FileReference.REF_TYPES)):
                    self.__type = FileReference.REF_TYPES[ref_index]
                else:
                    raise sppasIndexError(ref_index)
            except:
                raise sppasTypeError(ref_type, FileReference.REF_TYPES)

    # -----------------------------------------------------------------------

    def serialize(self):
        """Return a dict representing this instance for json format."""
        d = FileBase.serialize(self)
        d['attributes'] = list()
        for att in self.__attributs:
            a = self.__attributs[att].serialize()
            d['attributes'].append(a)
        d['subjoin'] = self.subjoined
        return d

    # -----------------------------------------------------------------------

    @staticmethod
    def parse(d):
        """Return the FileReference instance represented by the given dict.

        """
        ref = FileReference(d['id'])
        for att in d['attributes']:
            ref.add(sppasAttribute.parse(att))
        return ref

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __len__(self):
        return len(self.__attributs)

    def __str__(self):
        return '{:s}: {!s:s}'.format(self.id, self.__attributs)

    def __repr__(self):
        return '{:s}: {!s:s}'.format(self.id, self.__attributs)

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    def __iter__(self):
        for att in self.__attributs:
            yield att

    def __contains__(self, key):
        if isinstance(key, sppasAttribute) is False:
            su = sppasUnicode(key)
            key = su.unicode()
        for a in self.__attributs:
            if isinstance(key, sppasAttribute):
                if a is key:
                    return True
            else:
                if a.get_key() == key:
                    return True
        return False
