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
# File: wxoption.py
# ----------------------------------------------------------------------------

import wx
from structs.baseoption import BaseOption

# ----------------------------------------------------------------------------

class wxOption( BaseOption ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      One option of one preference value.

    """
    def __init__(self, optiontype, optionvalue, optiontext=""):
        """
        Creates a new Option() instance.

        optiontype is a string; one of:
            boolean, int, float, string, wx.colour, wx.size, wx.font

        """
        BaseOption.__init__(self, optiontype)
        self.set_type(optiontype)
        self.set_value(optionvalue)
        self.set_text( optiontext )

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_value(self):
        """
        Return the typed-value.
        Override the BaseOption.get_value().

        """
        v = BaseOption.get_value(self)
        if v is not None:
            return v

        if self._type == 'wx.size':
            #(w,h) = self._value
            #return wx.Size(w,h)
            return int(self._value)

        if self._type == 'wx.colour':
            if self._value is None:
                return None
            (r,g,b) = self._value
            return wx.Colour(r,g,b)

        if self._type == 'wx.font':
            (size, family, style, weight, u, face, enc) = self._value
            return wx.Font(size, family, style, weight, u, face, enc)

        if self._type == 'wx.align':
            if self._value.lower() == 'left':
                return wx.ALIGN_LEFT
            if self._value.lower() == 'right':
                return wx.ALIGN_RIGHT
            return wx.ALIGN_CENTRE

        raise TypeError('Unknown option type %s'%self._type)

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set_type(self, opttype):
        """ Set a new type. """

        opttype = opttype.lower()
        if opttype.startswith("wx"):
            self._type = opttype
        else:
            BaseOption.set_type(self,opttype)

    def set_value(self, value):
        """
        Set a new value.
        Override the BaseOption.set_value().

        """
        if self._type == 'wx.font':
            if isinstance(value,wx.Font):
                size   = value.GetPointSize()
                family = value.GetFamily()
                style  = value.GetStyle()
                weight = value.GetWeight()
                underline = value.GetUnderlined()
                face = value.GetFaceName()
                encoding = value.GetEncoding()
                self._value = (size, family, style, weight, underline, face, encoding)
            else:
                self._value = value

        elif self._type == 'wx.size':
            if isinstance(value,wx.Size):
                (w,h) = value
                self._value = (w,h)
            else:
                self._value = value

        elif self._type == 'wx.colour':
            if isinstance(value,wx.Colour):
                (r,g,b) = value
                self._value = (r,g,b)
            else:
                self._value = value

        elif self._type == 'wx.align':
            if value == wx.ALIGN_LEFT or value == 'left':
                self._value = 'left'
            elif value == wx.ALIGN_RIGHT or value == 'right':
                self._value = 'right'
            else:
                self._value = 'centre'

        else:
            self._value = value

    # ------------------------------------------------------------------------
