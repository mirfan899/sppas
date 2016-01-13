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
from interval import TimeInterval


class TimeDisjoint(Time):
    """ Represents a sequence of time intervals.
        A time interval is identified by two points:
            - a begin time;
            - an end time.
    """

    def __init__(self, *intervals):
        """ Creates a new TimeDisjoint instance.
            Parameters:
                - *interval (TimeInterval) sequence of TimeInterval
            Exception TypeError
        """
        if not intervals:
            raise TypeError("constructor requires a sequence of TimeInterval")
        if not all(isinstance(i, TimeInterval) for i in intervals):
            raise TypeError("constructor requires a sequence of TimeInterval")
        self.__intervals = list(intervals)

    # End __init__
    # -----------------------------------------------------------------------


    def __repr__(self):
        return "TimeDisjoint(%s)" % ("".join([str(i) for i in self.__intervals]))

    # End __repr__
    # -----------------------------------------------------------------------


    def GetSize(self):
        """ Return the number of time intervals.
            Parameters:  none
            Exception:   none
            Return:      int
        """
        return len(self.__intervals)

    # End GetSize
    # -----------------------------------------------------------------------


    def __GetBegin(self):
        """ Get the begin TimePoint instance.
            Parameters:  none
            Exception:   none
            Return:      TimePoint
        """
        _min = min(interval for interval in self.__intervals)
        return _min.Begin

    def __SetBegin(self, time):
        """ Set the begin TimePoint instance to new TimePoint.
            Parameters:  time (TimePoint)
            Exception:   none
            Return:      none
        """
        _min = min(interval for interval in self.__intervals)
        _min.Begin = time

    Begin = property(__GetBegin, __SetBegin)

    # End __GetBegin and __SetBegin
    # -----------------------------------------------------------------------


    def __GetEnd(self):
        """ Get the end TimePoint instance.
            Parameters:  none
            Exception:   none
            Return:      TimePoint
        """
        _max = max(interval for interval in self.__intervals)
        return _max.End

    def __SetEnd(self, time):
        """ Set the end TimePoint instance to new TimePoint.
            Parameters:  time (TimePoint)
            Exception:   none
            Return:      none
        """
        _max = max(interval for interval in self.__intervals)
        _max.End = time

    End = property(__GetEnd, __SetEnd)

    # End __GetEnd and __SetEnd
    # -----------------------------------------------------------------------


    def __eq__(self, other):
        """ Equal is required to use '==' between 2 TimeDisjoint instances.
            Parameters:
                - other (TimeDisjoint) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        if not isinstance(other, TimeDisjoint):
            return False
        if self.GetSize() != other.GetSize():
            return False
        return all(self.GetInterval(i) == other.GetInterval(i) for i in range(self.GetSize()))


    # End __eq__
    # -----------------------------------------------------------------------


    def __ne__(self, other):
        """ NotEqual is required to use '!=' between 2 TimeDisjoint instances.
            Parameters:
                - other (TimeDisjoint) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        return not self == other

    # End __ne__
    # -----------------------------------------------------------------------


    def __lt__(self, other):
        """ LowerThan is required to use '<' between 2 TimeDisjoint instances.
            Parameters:
                - other (TimeDisjoint) is the other time
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
        """ LowerEqual is required to use '<=' between 2 TimeDisjoint instances.
            Parameters:
                - other (TimeDisjoint) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        return self == other or self < other

    # End __le__
    # -----------------------------------------------------------------------


    def __gt__(self, other):
        """ GreaterThan is required to use '>' between 2 TimeDisjoint instances.
            Parameters:
                - other (TimeDisjoint) is the other time
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
        """ GreaterEqual is required to use '>=' between 2 TimeDisjoint instances.
            Parameters:
                - other (TimeDisjoint) is the other time point to compare with.
            Exception:   none
            Return:      Boolean
        """
        return self == other or self > other

    # End __ge__
    # -----------------------------------------------------------------------


    def GetInterval(self, index):
        """ Return the TimeInterval specified position in this object.
            Parameters:
                - index (int)
            Exception: KeyError
            Return: TimeInterval
        """
        return self.__intervals[index]

    # End GetInterval
    # -----------------------------------------------------------------------


    def IsDisjoint(self):
        """ Check if the object is an instance of TimeDisjoint.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return True

    # End IsDisjoint
    # -----------------------------------------------------------------------


    def Duration(self):
        """
            Return the duration of the time point, in seconds.
            Parameters:  none
            Exception:   none
            Return:      float
        """
        return sum(interval.Duration() for interval in self.__intervals)

    # End Duration
    # -----------------------------------------------------------------------
