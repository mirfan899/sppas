#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# File: ctrlvocab.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

from annotationdata.label.text import Text

# ----------------------------------------------------------------------------
# An Entry of a controlled vocabulary:
# ---------------------------------------------------------------------------

class CtrlVocabEntry(object):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents an entry of a controlled vocabulary.

    An entry of a controlled vocabulary is a pair Text/description.

    """
    def __init__(self, str, desc=""):
        """
        Create a new CtrlVocabEntry instance.
        """
        self.__text = self.__entry2text(str)
        self.__desc = ' '.join(desc.split())

    # -----------------------------------------------------------------------

    @property
    def Text(self):
        """
        Return the Text instance.

        """
        return self.__text

    # ------------------------------------------------------------------------

    def GetDescription(self):
        """
        Return the description of the text entry.

        """
        return self.__desc

    # ------------------------------------------------------------------------

    def SetDescription(self, desc):
        """
        Set the description of the entry of a controlled vocabulary.
        """
        desc = ' '.join(desc.split())

        if isinstance(desc, unicode):
            self.__desc = desc
        else:
            self.__desc = desc.decode("utf-8")

    # -----------------------------------------------------------------------
    desc = property(GetDescription, SetDescription)
    # -----------------------------------------------------------------------

    def Equal(self, other):
        """
        Return True if the value of self is equal to the value of other.

        @param other (CtrlVocabEntry) text to compare.

        """
        return self == other

    # ------------------------------------------------------------------------

    def StrictEqual(self, other):
        """
        Return True if self is strictly equal to other (Text and Description).

        @param other (CtrlVocabEntry) text to compare.

        """
        return self.Text == other.Text and self.__desc == other.GetDescription()

    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __repr__(self):
        return "Entry(value=%s, description=%s)" % (self.__text, self.__desc)

    def __eq__(self, other):
        return self.Text == other.Text

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __entry2text(self, strentry):
        # Convert an entry (a String or a Text instance) to a Text instance.
        # Assign a score of 1 to the Text.
        if isinstance(strentry, Text):
            strentry.SetScore(1)
            return strentry
        return Text(strentry,1)

    # -----------------------------------------------------------------------

# End CtrlVocabEntry
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------

class CtrlVocab( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Generic representation of a media file.
    """

    def __init__(self, ctrlid):
        """

        @param ctrlid (str) Identifier of the controlled vocabulary

        """
        self.id        = ctrlid.strip()
        self.__desc    = ""
        self.__entries = list()

    # -----------------------------------------------------------------------

    def GetDescription(self):
        """
        Return the description of the text entry.

        """
        return self.__desc

    # ------------------------------------------------------------------------

    def SetDescription(self, desc):
        """
        Set the description of the entry of a controlled vocabulary.
        """
        desc = ' '.join(desc.split())

        if isinstance(desc, unicode):
            self.__desc = desc
        else:
            self.__desc = desc.decode("utf-8")

    # -----------------------------------------------------------------------
    desc = property(GetDescription, SetDescription)
    # -----------------------------------------------------------------------

    def Contains(self, entry):
        """
        Test if an entry is already in the controlled vocabulary.

        @param entry (String or Text) is the entry to check.
        @return a Boolean value

        """
        return CtrlVocabEntry(entry) in self.__entries

    # -----------------------------------------------------------------------

    def Append(self, entry, descr=""):
        """
        Append an entry in the controlled vocab, except if it is already in.

        @param entry (String or Text): the entry to append.
        @return Boolean

        """
        if not isinstance(entry,CtrlVocabEntry):
            text = CtrlVocabEntry(entry)
        else:
            text = entry
        text.desc = descr

        if text in self.__entries:
            return False

        self.__entries.append( text )
        return True

    # -----------------------------------------------------------------------

    def Add(self, i, entry, descr=""):
        """
        Add an entry to the controlled vocabulary at the specified index.

        @param i: (int) is the index
        @param entry: the entry to add.

        """
        if not isinstance(entry,CtrlVocabEntry):
            text = CtrlVocabEntry(entry)
        else:
            text = entry

        if text in self.__entries:
            return False
        if i < 0:
            return False

        if i >= len(self.__entries):
            self.__entries.append( text )
        else:
            self.__entries.insert( i, text )

        return True

    # -----------------------------------------------------------------------

    def Remove(self, entry):
        """
        Remove an entry of the controlled vocab, except if it is not in!

        @param entry (String): the entry to remove.
        @return Boolean

        """
        if not isinstance(entry,CtrlVocabEntry):
            text = CtrlVocabEntry(entry)
        else:
            text = entry

        if text not in self.__entries:
            return False

        self.__entries.remove( text )
        return True

    # -----------------------------------------------------------------------

    def Pop(self, i=-1):
        """
        Remove the entry at the given position in the controlled vocabulary.
        If no index is specified, Pop() removes and returns the last entry.

        @param i: (int)
        @return The removed entry.

        """
        try:
            return self.__entries.pop(i)
        except IndexError:
            return None

    # -----------------------------------------------------------------------

    def GetSize(self):
        """
        Return the number of entries in the controlled vocabulary.

        """
        return len(self.__entries)

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __iter__(self):
        for a in self.__entries:
            yield a

    def __getitem__(self, i):
        return self.__entries[i]

    def __len__(self):
        return len(self.__entries)

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------
