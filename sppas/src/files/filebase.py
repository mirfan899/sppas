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

    src.files.filebase.py
    ~~~~~~~~~~~~~~~~~~~~~

    Base class for any type of files.

"""


class FileBase(object):
    """Represents any type of data linked to a filename.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, identifier):
        """Constructor of a FileBase.

        :param `identifier`: (str) Full name of a file/directory
        :raise: OSError if identifier does not match a file nor a directory

        The following members are stored:

            - id (str) Identifier - the absolute identifier [private]

        """
        self.__id = identifier
        self._state = States().UNUSED

    # -----------------------------------------------------------------------

    def get_id(self):
        """Return the identifier of the file, i.e. the full name."""
        return self.__id

    # -----------------------------------------------------------------------

    def get_state(self):
        """Return the state."""
        return self._state

    # -----------------------------------------------------------------------

    def match(self, functions, logic_bool="and"):
        """Return True if the file matches all or any of the functions.

        Functions are defined in a comparator. They return a boolean.
        The type of the value depends on the function.
        The logical not is used to reverse the result of the function.

        :param functions: list of (function, value, logical_not)
        :param logic_bool: (str) Apply a logical "and" or a logical "or" between the functions.
        :returns: (bool)

        """
        matches = list()
        for func, value, logical_not in functions:
            if logical_not is True:
                matches.append(not func(self, value))
            else:
                matches.append(func(self, value))

        if logic_bool == "and":
            is_matching = all(matches)
        else:
            is_matching = any(matches)

        return is_matching

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    id = property(get_id, None)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        """Allow to show the class at a given format.

        :param fmt: (str) the wanted format of string
        :return: (str)

        """
        return str(self).__format__(fmt)

    def __str__(self):
        """The string conversion of the object.

        :return: (str)

        """
        return '{!s:s}'.format(self.__id)

    def __repr__(self):
        """Function called by print.

        :return: (str) printed representation of the object.

        """
        return 'File: {!s:s}'.format(self.__id)

# ---------------------------------------------------------------------------


class States(object):
    """All states of any FileBase.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    :Example:

        >>>with States() as s:
        >>>    s.newKey = 'myNewValue'
        >>>    print(s.newKey)

    """

    def __init__(self):
        """Create the dictionary."""
        self.__dict__ = dict(
            UNUSED=0,
            CHECKED=1,
            LOCKED=2,
            ALL_CHECKED=3,
            ALL_LOCKED=4,
            AT_LEAST_ONE_CHECKED=5,
            AT_LEAST_ONE_LOCKED=6,
        )

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass
