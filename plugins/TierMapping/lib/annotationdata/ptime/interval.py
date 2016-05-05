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
from point import TimePoint


class TimeInterval(Time):
    """ Represents a time interval.
        A time interval is identified by two points:
            - a begin time;
            - an end time.
        Time is represented by a TimePoint instance, in seconds, 
        as a float value.
    """

    def __init__(self, begin, end):
        """ Creates a new TimeInterval instance.
            Parameters:
                - begin (TimePoint) start time in seconds
                - end (TimePoint) end time in seconds
            Exception TypeError, ValueError
        """
        if isinstance(begin, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % begin)
        if isinstance(end, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % end)
        if  begin >= end:
            raise ValueError("End TimePoint must be strictly greater than"
                             " Begin TimePoint (see TimePoint definition)."
                             " (%s, %s)" % (begin, end))

        self.__begin = begin
        self.__end = end

    # End __init__
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------


    def Set(self, other):
        """ Set the TimeInterval instance to new TimeInterval.
            Parameters:  other (TimeInterval)
            Exception:   TypeError
            Return:      none
        """
        if isinstance(other, TimeInterval) is False:
            raise TypeError("TimeInterval argument required, not %r" % other)
        self.Begin.Set(other.Begin)
        self.End.Set(other.End)

    # End Set
    # -----------------------------------------------------------------------


    def __GetBegin(self):
        """ Get the begin TimePoint instance.
            Parameters:  none
            Exception:   none
            Return:      TimePoint
        """
        return self.__begin

    def __SetBegin(self, time):
        """ Set the begin TimePoint instance to new TimePoint.
            Parameters:  time (TimePoint)
            Exception:   none
            Return:      none
        """
        if isinstance(time, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % time)
        if time >= self.End:
            raise ValueError("End TimePoint must be strictly greater than"
                             " Begin TimePoint (see TimePoint definition)."
                             " (%s, %s)" % (time, self.End))
        self.__begin = time

    Begin = property(__GetBegin, __SetBegin)

    # End __GetBegin and __SetBegin
    # -----------------------------------------------------------------------


    def __GetEnd(self):
        """ Get the end TimePoint instance.
            Parameters:  none
            Exception:   none
            Return:      TimePoint
        """
        return self.__end

    def __SetEnd(self, time):
        """ Set the end TimePoint instance to new TimePoint.
            Parameters:  time (TimePoint)
            Exception:   none
            Return:      none
        """
        if isinstance(time, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % time)
        if self.Begin >= time:
            raise ValueError("End TimePoint must be strictly greater than"
                             " Begin TimePoint (see TimePoint definition)."
                             " (%s, %s)" % (self.Begin, time))
        self.__end = time

    End = property(__GetEnd, __SetEnd)

    # End __GetEnd and __SetEnd
    # -----------------------------------------------------------------------


    def __repr__(self):
        return "(%s,%s)" % (self.Begin, self.End)

    # End __repr__
    # -----------------------------------------------------------------------


    def __contains__(self, other):
        """ Return True if the given time point is contained in the interval.
            Parameters:
                - other  is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        if isinstance(other, (TimeInterval, TimePoint, float, int,)) is False:
            raise TypeError("%r cannot be compared with TimeInterval." % other)
        if isinstance(other, TimeInterval) is True:
            return self.Begin <= other.Begin and other.End <= self.End
        return self.Begin <= other <= self.End

    # End __contains__
    # -----------------------------------------------------------------------


    def __eq__(self, other):
        """ Equal is required to use '==' between 2 TimeInterval instances.
            Parameters:
                - other (TimeInterval) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        if isinstance(other, TimeInterval) is False:
            return False
        return self.Begin == other.Begin and self.End == other.End

    # End __eq__
    # -----------------------------------------------------------------------


    def __ne__(self, other):
        """ NotEqual is required to use '!=' between 2 TimeInterval instances.
            Parameters:
                - other (TimeInterval) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        return not self == other

    # End __ne__
    # -----------------------------------------------------------------------


    def __lt__(self, other):
        """ LowerThan is required to use '<' between 2 TimeInterval instances.
            Parameters:
                - other (TimeInterval, TimePoint, float, int) is the other time
                  point to compare with.
            Exception:   none
            Return:      Boolean
        """
        if isinstance(other, (TimePoint, float, int)):
            return self.End < other
        if isinstance(other, Time) is False:
            return False
        return self.Begin < other.Begin

    # End __lt__
    # -----------------------------------------------------------------------


    def __le__(self, other):
        """ LowerEqual is required to use '<=' between 2 TimeInterval instances.
            Parameters:
                - other (TimeInterval) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        return self < other or self == other

    # End __le__
    # -----------------------------------------------------------------------


    def __gt__(self, other):
        """ GreaterThan is required to use '>' between 2 TimeInterval instances.
            Parameters:
                - other (TimeInterval, TimePoint, float, int) is the other time
                  point to compare with.
            Exception:   none
            Return:      Boolean
        """
        if isinstance(other, (int, float, TimePoint)):
            return self.Begin > other
        if isinstance(other, Time) is False:
            return False
        return self.Begin > other.Begin

    # End __gt__
    # -----------------------------------------------------------------------


    def __ge__(self, other):
        """ GreaterEqual is required to use '>=' between 2 TimeInterval instances.
            Parameters:
                - other (TimeInterval) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        return self > other or self == other

    # End __ge__
    # -----------------------------------------------------------------------


    def IsInterval(self):
        """ Return True if this object is an instance of TimeInterval.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return True

    # End IsInterval
    # -----------------------------------------------------------------------


    def Duration(self):
        """
            Return the duration of the time point, in seconds.
            Parameters:  none
            Exception:   none
            Return:      float
        """
        return self.End.Value - self.Begin.Value

    # End Duration
    # -----------------------------------------------------------------------


    def Combine(self, other):
        """ Return a TimeInterval, the combine of two intervals.
            Parameters:
                - other (TimeInterval) is the other time interval to combine with.
            Exception:   TypeError
            Return:      TimeInterval
        """
        if isinstance(other, TimeInterval) is False:
            raise TypeError("TimeInterval argument required, not %r" % other)
        if self > other:
            other, self = self, other
        if self.End <= other.Begin:
            return TimeInterval(self.Begin, self.Begin)
        return TimeInterval(other.Begin, self.End)

    # End Combine
    # -----------------------------------------------------------------------


    def Union(self, other):
        """
            Return a TimeInterval representing the union of two intervals.
            Parameters:
                - other (TimeInterval)
            Exception:   TypeError
            Return:      TimeInterval
        """
        if isinstance(other, TimeInterval) is False:
            raise TypeError("TimeInterval argument required, not %r" % other)
        if self > other:
            other, self = self, other
        return TimeInterval(self.Begin, other.End)

    # End Union
    # -----------------------------------------------------------------------
