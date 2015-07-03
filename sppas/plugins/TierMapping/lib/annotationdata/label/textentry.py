#!/usr/bin/env python2
# -*- coding:utf-8 -*-
# Copyright (C) 2013  Brigitte Bigi
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.

from text import Text


class TextEntry(object):
    """Base class for Label and Silence."""

    def __init__(self, entry):
        self._texts = []
        if not isinstance(entry, Text):
            entry = Text(entry, score=1)
        self._texts.append(entry)

    # End __init__
    # -----------------------------------------------------------------------


    def __str__(self):
        return self.Value.encode("utf-8")

    # End __str__
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------


    def Set(self, entry):
        """ Set the label to Label or Silence.
            Parameters:
                - entry is Label or Silence.
            Exception:   TypeError
            Return:      none
        """
        if isinstance(entry, TextEntry) is False:
            raise TypeError("Label or Silence argument required, not %r" % entry)
        self.Value = entry.Value

    # End Set
    # -----------------------------------------------------------------------


    def __GetValue(self):
        """ Get the label string.
            Parameters:  none
            Exception:   none
            Return:      string label
        """
        if not self._texts:
            return ""
        text = max(self._texts, key=lambda x: x.Score)
        return text.Value

    def __SetValue(self, entry):
        """ Set the label to a new string.
            Parameters:
                - entry is the new string label
            Exception:   UnicodeDecodeError
            Return:      none
        """
        self.Unset()
        if not isinstance(entry, Text):
            entry = Text(entry, 1)
        self._texts.append(entry)

    Value = property(__GetValue, __SetValue)

    # End __GetValue and __SetValue
    # -----------------------------------------------------------------------


    def AddText(self, text):
        """ Add text to the list.
            Parameters:
                - text (Text)
            Exception: TypeError
            Return: none
        """
        if not isinstance(text, Text):
            raise TypeError("Text required not %r" % text)
        self._texts.append(text)

    # End Add Text
    # -----------------------------------------------------------------------


    def Unset(self):
        """ Set the label to empty string.
            Parameters:  none
            Exception:   none
            Return:      none
        """
        self._texts = []

    # End Unset
    # -----------------------------------------------------------------------


    def GetSize(self):
        return len(self._texts)

    def GetValues(self):
        """ Get the list of labels with their scores.
        """
        return self._texts


    # -----------------------------------------------------------------------

    def IsEmpty(self):
        """ Return True if the label is empty label.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return self.Value == ""

    # End IsEmpty
    # -----------------------------------------------------------------------


    def IsSilence(self):
        raise NotImplementedError

    # End IsSilence
    # -----------------------------------------------------------------------


    def IsLabel(self):
        raise NotImplementedError

    # End IsLabel
    # -----------------------------------------------------------------------
