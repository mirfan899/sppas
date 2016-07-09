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
# File: label.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------

from text import Text

# ----------------------------------------------------------------------------

class Label( object ):
    """
    @authors: Brigitte Bigi, Tatsuya Watanabe
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents a label.

    A label is a list of possible Text(), represented as a UNICODE string.
    A data type can be associated, as Text() can be 'int', 'float' or 'bool'.

    """
    def __init__(self, entry=None, data_type="str"):
        """
        Creates a new Label instance.

        A Label is represented as a unicode string.

        """
        # The list of possible Text for this Label
        self.__texts = []
        self.__fct   = max

        if entry is not None:
            if not isinstance(entry, Text):
                entry = Text(entry, score=1., data_type=data_type)
            self.__texts.append(entry)

    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------

    def Get(self):
        """
        Get the list of texts with their scores.

        """
        return self.__texts

    # -----------------------------------------------------------------------

    def Set(self, entry):
        """
        Set the label to a new label entry.

        @param entry (Label)

        """
        if isinstance(entry, Label) is False:
            raise TypeError("Label argument required, not %r" % entry)

        self.__texts = entry.Get()

    # -----------------------------------------------------------------------

    def AddValue(self, text):
        """
        Add a text into the list.

        @param text (Text)

        """
        if not isinstance(text, Text):
            raise TypeError("Text required not %r" % text)

        self.__texts.append(text)

    # -----------------------------------------------------------------------

    def RemoveValue(self, text):
        """
        Remove a text of the list.

        @param text (Text)

        @raise TypeError

        """
        if not isinstance(text, Text):
            raise TypeError("Text required not %r" % text)
        if text in self.__texts:
            self.__texts.remove(text)

    # -----------------------------------------------------------------------

    def SetValue(self, entry):
        """
        Remove all labels and append the new string.

        @param entry is the new string label

        """
        self.UnsetValue()

        if not isinstance(entry, Text):
            entry = Text(entry, 1.)

        self.__texts.append(entry)

    # -----------------------------------------------------------------------

    def UnsetValue(self):
        """
        Remove all labels.

        """
        self.__texts = []

    # -----------------------------------------------------------------------

    def GetSize(self):
        """
        Return the number of labels.

        """
        return len(self.__texts)

    # -----------------------------------------------------------------------

    def GetLabels(self):
        """
        Return a list of text instances of this label.

        """
        return [l for l in self.__texts]

    # -----------------------------------------------------------------------

    def GetFunctionScore(self):
        """
        Return the function used to compare scores.

        """
        return self.__fct

    # -----------------------------------------------------------------------

    def SetFunctionScore(self, fctname):
        """
        Set a new function to compare scores.

        @param fctname is one of min or max.

        """
        if fctname not in (min,max):
            raise TypeError('Expected min or max not %r' % fctname)

        self.__fct = fctname

    # -----------------------------------------------------------------------
    # Methods for the label with the best score
    # -----------------------------------------------------------------------

    def GetValue(self):
        """
        Return the string of the label with the best score.

        """
        if len(self.__texts) == 0:
            return ""  # hum... without Text() we suppose the dataype as string...

        text = self.__fct(self.__texts, key=lambda x: x.GetScore())
        return text.GetValue()

    # -----------------------------------------------------------------------

    def GetLabel(self):
        """
        Return the text instance of the label with the best score.

        """
        if len(self.__texts) == 0:
            return Text("") # hum... without Text() we suppose the dataype as string...

        text = self.__fct(self.__texts, key=lambda x: x.GetScore())
        return text

    # -----------------------------------------------------------------------

    def GetTypedValue(self):
        """
        Return the value of the label with the best score.

        """
        if len(self.__texts) == 0:
            return "" # hum... without Text() we suppose the datatype as string...

        text = self.__fct(self.__texts, key=lambda x: x.GetScore())
        return text.GetTypedValue()

    # -----------------------------------------------------------------------

    def IsEmpty(self):
        """
        Return True if the label with the best score is an empty string.

        """
        return self.GetLabel().IsEmpty()

    # -----------------------------------------------------------------------

    def IsSpeech(self):
        """
        Return True if the label with the best score is not a silence.

        """
        return self.GetLabel().IsSpeech()

    # -----------------------------------------------------------------------

    def IsSilence(self):
        """
        Return True if the label with the best score is an instance of Silence.

        """
        return self.GetLabel().IsSilence()

    # -----------------------------------------------------------------------

    def IsPause(self):
        """
        Return True if the label with the best score is a short pause.

        """
        return self.GetLabel().IsPause()

    # -----------------------------------------------------------------------

    def IsLaugh(self):
        """
        Return True if the label with the best score is a laughing.

        """
        return self.GetLabel().IsLaugh()

    # -----------------------------------------------------------------------

    def IsNoise(self):
        """
        Return True if the label with the best score is a noise.

        """
        return self.GetLabel().IsNoise()

    # -----------------------------------------------------------------------

    def IsDummy(self):
        """
        Return True if the label with the best score is a dummy label.

        """
        return self.GetLabel().IsDummy()

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        s = ""
        for t in self.__texts:
            s += "Text(value=%s,score=%s), " % (t.Value.encode("utf-8"), str(t.Score))
        return s

    def __str__(self):
        return self.GetValue().encode("utf-8")

    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------
