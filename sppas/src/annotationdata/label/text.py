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
# File: tag.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------


class Text(object):

    def __init__(self, text, score=1., data_type="str"):
        """
        Initialize a new Text instance.

        @param text (str)
        @param score (float)
        @param data_type (str): The type of this value (str, int, float, bool)

        >>> t = Text( "2" )                      # "2"
        >>> t = Text(  2, data_type="int")       # 2
        >>> t = Text( "2", data_type="int")      # 2
        >>> t = Text( "2", data_type="float")    # 2.
        >>> t = Text( "true", data_type="bool")  # True
        >>> t = Text( 0, data_type="bool")       # False
        >>> t = Text( 1, data_type="bool")       # True

        """
        if data_type in ["float","int","bool"]:
            if data_type == "float":
                text = float(text)
            elif data_type == "int":
                text = int(text)
            else:
                text = bool(text)

        if isinstance(text, (float,int,bool)):
            text = str(text)

        if not isinstance(text, unicode):
            text = text.decode("utf-8")

        self.__value   = text.strip()
        self.__score = float(score)
        self.__data_type = data_type

    # ------------------------------------------------------------------------

    def SetValue(self, s, data_type="str"):
        """
        Change value of this Text.

        @param s: New value for this Text
        @param data_type: The type of this value (str, int, float, bool)

        """
        if not isinstance(s, unicode):
            s = s.decode("utf-8")

        self.__value = ' '.join(s.split())
        self._data_type = data_type

    # ------------------------------------------------------------------------

    def SetScore(self, s):
        """
        Change score of this Text.

        """
        self.__score = float(s)

    # ------------------------------------------------------------------------

    def GetValue(self):
        """
        Return the string corresponding to the value of this Text.

        """
        return self.__value

    # ------------------------------------------------------------------------

    def GetTypedValue(self):
        """
        Return the value of this Text, in its appropriate type.

        """
        if self.__data_type == "int":
            return int( self.__value )

        if self.__data_type == "float":
            return float( self.__value )

        if self.__data_type == "bool":
            if self.__value.lower() == "true":
                return True
            else:
                return False
        #    return boolean( self.__value )

        return self.__value

    # ------------------------------------------------------------------------

    def GetScore(self):
        """
        Return the score of this Text.

        """
        return self.__score

    # ------------------------------------------------------------------------

    def Equal(self, other):
        """
        Return True if the value of self is equal to the value of other.

        @param other (Text) text to compare with.

        """
        return self == other

    # ------------------------------------------------------------------------

    def StrictEqual(self, other):
        """
        Return True if self is strictly equal to other (Value and Score).

        @param other (Text) text to compare.

        """
        return self.GetTypedValue() == other.GetTypedValue() and self.GetScore() == other.GetScore()

    # ------------------------------------------------------------------------

    def IsEmpty(self):
        """
        Return True if the text value is an empty string.

        """
        return self.__value == ''

    # -----------------------------------------------------------------------

    def IsSpeech(self):
        """
        Return True if the text value is not a silence.

        """
        return not (self.IsSilence() or self.IsPause() or self.IsLaugh() or self.IsNoise() or self.IsDummy())

    # -----------------------------------------------------------------------

    def IsSilence(self):
        """
        Return True if the text value is a silence.

        """
        # SPPAS representation of silences
        if self.__value in ("#", "sil"):
            return True

        # The French CID corpus:
        if self.__value.startswith("gpf_"):
            return True

        return False

    # -----------------------------------------------------------------------

    def IsPause(self):
        """
        Return True if the text value is a short pause.

        """
        return self.__value == "+"

    # -----------------------------------------------------------------------

    def IsLaugh(self):
        """
        Return True if the text value is a laughing.

        """
        return self.__value == "@@"

    # -----------------------------------------------------------------------

    def IsNoise(self):
        """
        Return True if the text value is a noise.

        """
        return self.__value == "*"

    # -----------------------------------------------------------------------

    def IsDummy(self):
        """
        Return True if the text value is a dummy label.

        """
        return self.__value == "dummy"

    # ------------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------------

    Value = property(GetValue, SetValue)
    Score = property(GetScore, SetScore)

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __repr__(self):
        return "Text(value=%s, score=%s)" % (self.__value.encode("utf-8"), str(self.__score))

    def __str__(self):
        return self.__value.encode("utf-8")

    def __eq__(self, other):
        return self.GetTypedValue() == other.GetTypedValue()

# ----------------------------------------------------------------------------
