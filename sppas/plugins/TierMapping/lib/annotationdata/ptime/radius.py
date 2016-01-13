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


class Radius(object):
    """
       Radius is required to compare 2 TimePoint instances.
    """
    def __init__(self, radius=0.00001):
        """ Creates a new Radius instance.
            Parameters:
              - radius (float)
        """
        if isinstance(radius, (float, int)) is False:
            raise TypeError("float argument required, not %r" % radius)
        if isinstance(radius, int):
            radius = float(radius)
        self.__radius = radius

    # End __init__
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------


    def Set(self, other):
        """ Set the radius to new Radius instance.
            Parameters:  other (Radius)
            Exception:   TypeError
            Return:      none
        """
        if isinstance(other, Radius) is False:
            raise TypeError("Radius argument required, not %r" % other)
        self.Value = other.Value

    # End Set
    # -----------------------------------------------------------------------


    def __GetValue(self):
        """ Get the radius value
            Parameters:  none
            Exception:   None
            Return:      float value
        """
        return self.__radius

    def __SetValue(self, radius):
        """ Set the radius to a new value.
            Parameters:
                - radius (float)
            Exception:   none
            Return:      TypeError
        """
        if isinstance(radius, (float, int)) is False:
            raise TypeError("float argument required, not %r" % radius)
        if isinstance(radius, int):
            radius = float(radius)
        self.__radius = radius

    Value = property(__GetValue, __SetValue)

    # End __GetValue and __SetValue
    # -----------------------------------------------------------------------
