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
#
#       Copyright (C) 2013-2014  Tatsuya Watanabe
#       Copyright (C) 2014-2015  Brigitte Bigi
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
# File: text.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Tatsuya Watanabe, Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

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

    # End __init__
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

    # End SetValue
    # ------------------------------------------------------------------------


    def SetScore(self, s):
        """
        Change score of this Text.

        """
        self.__score = float(s)

    # End SetScore
    # ------------------------------------------------------------------------


    def GetValue(self):
        """
        Return the string corresponding to the value of this Text.

        """
        return self.__value

    # End GetValue
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

    # End GetTypedValue
    # ------------------------------------------------------------------------


    def GetScore(self):
        """
        Return the score of this Text.

        """
        return self.__score

    # End Score
    # ------------------------------------------------------------------------


    def Equal(self, other):
        """
        Return True if the value of self is equal to the value of other.

        @param other (Text) text to compare with.

        """
        return self == other

    # End Equal
    # ------------------------------------------------------------------------


    def StrictEqual(self, other):
        """
        Return True if self is strictly equal to other (Value and Score).

        @param other (Text) text to compare.

        """
        return self.GetTypedValue() == other.GetTypedValue() and self.GetScore() == other.GetScore()

    # End StrictEqual
    # ------------------------------------------------------------------------


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

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------
