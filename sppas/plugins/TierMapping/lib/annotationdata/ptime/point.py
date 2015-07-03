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

from atime import Time
from radius import Radius

class TimePoint(Time):
    """ Represents a time point identified by a time value.
        Generally, time is represented in seconds, as a float value.

        TimePoint relations are based on relations described in:
        Marc Vilain, Henry Kautz, Peter van Beek
        "Constraint Propagation Algorithms: A revised report"
        in: Readings in qualitative reasoning about physical systems
        Pages 373 - 381
        Morgan Kaufmann Publishers Inc. San Francisco, CA, USA ©1990
        ISBN:1-55860-095-7 

        Citation: 
        Time points can modelled by the real numbers, and their relations
        can be entirely expressed as inequalities. [...] these relations
        can be decomposed into disjunctions of simple relations, which in 
        this case number three: <, = and >.
        Seven consistent vectors can be formed: (<), (=), (>), (<=), (=>),
        (<=>) and (<>). 


        In the TimePoint instance, the 3 relations <, = and > take into
        account a radius value. For a point x, with a radius value
        of dx, and a point y with a radius value of dy, these relations
        are defined as:
            - x = y iff |x - y| <= dx + dy
            - x < y iff not(x = y) and x < y
            - x > y iff not(x = y) and x > y

        Examples:

            Strictly equals:

            x = 1.000, dx=0.
            y = 1.000, dy=0.
            x = y is true

            x = 1.00000000000, dx=0.
            y = 0.99999999675, dy=0.
            x = y is false

            Accept a "margin":

            x = 1.0000000000, dx=0.0005
            y = 1.0000987653, dx=0.0005
            x = y is true  (accept a margin of 1ms between x and y)

            x = 1.0000000, dx=0.0005
            y = 1.0011235, dx=0.0005
            x = y is false 

        The vectors of Vilain et al. are implemented by using python
        comparisons:
            - <     lower than
            - ==    equal
            - >     greater than
            - <=    lesser or equal than
            - >=    greater or equal than
            - !=    different (i.e. not equal)
            - ? (TODO)
        Pay attention that, in the TimePoint instance, these relations 
        take into account the radius. This means that to strictly 
        compare 2 TimePoint instances, the radius must be fixed to 0.
        The default is to use a radius value of 0.0005 (this means 1/2 ms).
    """

    def __init__(self, time, radius=None):
        """ Creates a new TimePoint instance.
            Parameters:
              - time (float) time value in seconds.
              - radius (Radius) is required to compare 2 instances.
        """
        try:
            time = float(time)
        except ValueError:
            raise TypeError("float argument required, not %r" % time)

        if time < 0.:
            raise ValueError("A time point can't be negative: %r" % time)

        if radius is None:
            radius = Radius()

        if isinstance(radius, Radius) is False:
            raise TypeError("Radius argument required, not %r" % radius)

        if time < radius.Value:
            radius.Value = time

        self.__time = time
        self.__radius = radius

    # End __init__
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------


    def Set(self, other):
        """ Set the time to a new TimePoint instance.
            Parameters:  other (TimePoint)
            Exception:   none
            Return:      none
        """
        if isinstance(other, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % other)
        self.Value = other.Value
        self.Radius = other.Radius

    # End Set
    # -----------------------------------------------------------------------


    def __GetValue(self):
        """ Get the TimePoint value, in seconds.
            Parameters:  none
            Exception:   None
            Return:      float value
        """
        return self.__time

    def __SetValue(self, time):
        """ Set the time to a new value.
            Parameters:
                - time is the new time to set the point.
            Exception:   none
            Return:      TypeError (if time is not float)
        """
        if isinstance(time, (int, float)) is False:
            raise TypeError("float argument required, not %r" % time)
        if isinstance(time, int):
            time = float(time)
        self.__time = time

    Value = property(__GetValue, __SetValue)

    # End __GetValue and __SetValue
    # -----------------------------------------------------------------------


    def __GetRadius(self):
        """ Get the radius used to compare TimePoint instances.
            Fixed in seconds.
            Parameters:  none
            Exception:   none
            Return:      Radius
        """
        return self.__radius

    def __SetRadius(self, radius):
        """ Fix the radius used to compare TimePoint instances.
            Float value, fixed in seconds.
            Parameters:
               - radius (Radius) is the radius (in seconds)
            Exception:   none
            Return:      none
        """
        if isinstance(radius, Radius) is False:
            raise TypeError("Radius argument required, not %r" % radius)
        self.__radius = radius

    Radius = property(__GetRadius, __SetRadius)

    # End __GetRadius and __SetRadius
    # -----------------------------------------------------------------------


    def __repr__(self):
        return "TimePoint(%f)" % self.Value

    # End __repr__
    # -----------------------------------------------------------------------


    def __str__(self):
        return "%f" % self.Value

    # End __str__
    # -----------------------------------------------------------------------


    def __eq__(self, other):
        """ Equal is required to use '==' between 2 TimePoint instances or 
            between a TimePoint and an other object representing time.
            This relationship takes into account the radius.
            Parameters:
                - other (TimePoint, float, int) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        if isinstance(other, (int, float, TimePoint)) is False:
            return False

        if isinstance(other, TimePoint) is True:
            delta = abs(self.Value - other.Value)
            radius = self.Radius.Value + other.Radius.Value
            #return delta < radius
            return delta <= radius

        if isinstance(other, (int, float)):
            delta = abs(self.Value - other)
            radius = self.Radius.Value
            #return delta < radius
            return delta <= radius

    # End __eq__
    # -----------------------------------------------------------------------


    def __ne__(self, other):
        """ NotEqual is required to use '!=' between 2 TimePoint instances
            or between a TimePoint and an other time object.
            This relationship takes into account the radius.
            Parameters:
                - other (TimePoint, float, int) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        return not self == other

    # End __ne__
    # -----------------------------------------------------------------------


    def __lt__(self, other):
        """ LowerThan is required to use '<' between 2 TimePoint instances
            or between a TimePoint and an other time object.
            Parameters:
                - other (TimePoint, float, int) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        if isinstance(other, TimePoint) is True:
            return self != other and self.Value < other.Value
        return self != other and self.Value < other

    # End __lt__
    # -----------------------------------------------------------------------


    def __le__(self, other):
        """ LowerEqual is required to use '<=' between 2 TimePoint instances 
            or between a TimePoint and an other time object.
            Parameters:
                - other (TimePoint, float, int) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        return self < other or self == other

    # End __le__
    # -----------------------------------------------------------------------


    def __gt__(self, other):
        """ GreaterThan is required to use '>' between 2 TimePoint instances 
            or between a TimePoint and an other time object.
            Parameters:
                - other (TimePoint, float, int) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        if isinstance(other, TimePoint) is True:
            return self != other and self.Value > other.Value
        return self != other and self.Value > other

    # End __gt__
    # -----------------------------------------------------------------------


    def __ge__(self, other):
        """ GreaterEqual is required to use '>=' between 2 TimePoint instances 
            or between a TimePoint and an other time object.
            Parameters:
                - other (TimePoint, float, int) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        return self > other or self == other

    # End __ge__
    # -----------------------------------------------------------------------


    def IsPoint(self):
        """ Check if the object is an instance of TimePoint.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return True

    # End IsPoint
    # -----------------------------------------------------------------------


    def Duration(self):
        """
            Return the duration of the time point, in seconds.
            Parameters:  none
            Exception:   none
            Return:      float
        """
        return 0.

    # End Duration
    # -----------------------------------------------------------------------
