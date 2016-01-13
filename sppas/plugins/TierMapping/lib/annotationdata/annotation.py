#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
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

import copy

from ptime.point import TimePoint
from ptime.interval import TimeInterval
from label.silence import Silence
from label.label import Label
from ptime.atime import Time


class Annotation(object):
    """ Represents an annotation.
        An annotation in SPPAS is:
            - a time object (a TimePoint or a TimeInterval instance);
            - a text (a Label instance or a Silence instance).
    """
    def __init__(self, time, text=Label("")):
        """ Creates a new Annotation instance.
            Parameters:
                - time (TimePoint, TimeInterval or TimeDisjoint) start time in seconds
                - text (Label or Silence)
            Exception TypeError
        """
        if isinstance(time, Time) is False:
            raise TypeError("TimePoint, TimeInterval or TimeDisjoint argument required, not %r" % time)
        if isinstance(text, (Label, Silence)) is False:
            raise TypeError("Label or Silence argument required, not %r" % text)
        self.__time = time
        self.__text = text

    # End __init__
    # -----------------------------------------------------------------------

    def __str__(self):
        return "%s%s" % (self.Time, self.Text)


    # End __str__
    # -----------------------------------------------------------------------


    def Set(self, annotation):
        """ Set the annotation to an instance of Annotation.
            Parameters:
                - entry is Label or Silence.
            Exception:   TypeError
            Return:      none
        """
        if isinstance(annotation, Annotation) is False:
            raise TypeError("Annotation argument required, not %r" % annotation)
        self.Text.Set(annotation.Text)
        self.Time.Set(annotation.Time)

    # End Set
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------


    def __GetText(self):
        """ Get the Text (Label or Silence).
            Parameters:  none
            Exception:   none
            Return:      (Label or Silence)
        """
        return self.__text

    def __SetText(self, text):
        """ Set the Text to Label or Silence.
            Parameters:  text
            Exception:   TypeError
            Return:      none
        """
        if isinstance(text, (Label, Silence)) is False:
            raise TypeError("Label or Silence argument required, not %r" % text)
        self.__text = text

    # Allow to use:
    # >>> annotation.Text
    Text = property(__GetText, __SetText)

    # End __GetText and __SetText
    # -----------------------------------------------------------------------


    def __GetTime(self):
        """ Get the Time (TimePoint or TimeInterval).
            Parameters:  none
            Exception:   none
            Return:      (TimePoint or TimeInterval)
        """
        return self.__time

    def __SetTime(self, time):
        """ Set the Time to TimePoint or TimeInterval.
            Parameters:  time (TimePoint, TimeInterval)
            Exception:   TypeError
            Return:      none
        """
        if isinstance(time, Time) is False:
            raise TypeError("TimePoint, TimeInterval or TimeDisjoint argument required, not %r" % time)
        self.__time = time

    Time = property(__GetTime, __SetTime)

    # End __GetTime and __SetTime
    # -----------------------------------------------------------------------


    def __GetBegin(self):
        """ Get the begin TimePoint.
            Parameters:  none
            Exception:   AttributeError
            Return:      TimePoint
        """
        try:
            return self.Time.Begin
        except AttributeError as e:
            raise e

    def __SetBegin(self, time):
        """ Set the begin time to TimePoint.
            Parameters:  time (TimePoint)
            Exception:   TypeError, AttributeError
            Return:      none
        """
        if isinstance(time, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % time)
        if self.IsInterval() is False:
            raise AttributeError("Annotation object has no attribute Begin.")
        if self.End <= time:
            raise ValueError("being time must be less than end time. (%s, %s)" % (time, self.End))
        self.Time.Begin = time

    Begin = property(__GetBegin, __SetBegin)

    # End __GetBegin and __SetBegin
    # -----------------------------------------------------------------------


    def __GetEnd(self):
        """ Get the end TimePoint.
            Parameters:  none
            Exception:   AttributeError
            Return:      TimePoint
        """
        try:
            return self.Time.End
        except AttributeError as e:
            raise e

    def __SetEnd(self, time):
        """ Set the end TimePoint to TimePoint.
            Parameters:  time (TimePoint)
            Exception:   TypeError, AttributeError
            Return:      none
        """
        if isinstance(time, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % time)
        if self.IsInterval() is False:
            raise AttributeError("Annotation object has no attribute End.")
        if self.Begin >= time:
            raise ValueError("end time must be greater than begin time. (%s, %s)" % (self.Begin, time))
        self.Time.End = time

    End = property(__GetEnd, __SetEnd)

    # End __GetEnd and __SetEnd
    # -----------------------------------------------------------------------


    def __GetPoint(self):
        """ Get the  TimePoint.
            Parameters:  none
            Exception:   AttributeError
            Return:      TimePoint
        """
        if self.IsPoint() is False:
            raise AttributeError("Annotation object has no attribute Point.")
        return self.Time

    def __SetPoint(self, time):
        """ Set the time point to TimePoint.
            Parameters:  time (TimePoint)
            Exception:   TypeError, AttributeError
            Return:      none
        """
        if isinstance(time, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % time)
        if self.IsPoint() is False:
            raise AttributeError("Annotation object has no attribute Point.")
        self.Time = time

    Point = property(__GetPoint, __SetPoint)

    # End __PointEnd and __Point
    # -----------------------------------------------------------------------


    def __GetTextValue(self):
        """ Get the string label.
            Parameters:  none
            Exception:   none
            Return:      string
        """
        return self.Text.Value

    def __SetTextValue(self, label):
        """ Set Text attribute value to the given label.
            Parameters:  label (string)
            Exception:   UnicodeDecodeError
            Return:      none
        """
        self.Text.Value = label

    TextValue = property(__GetTextValue, __SetTextValue)

    # End __GetTextValue and __SetTextValue
    # -----------------------------------------------------------------------


    def __GetBeginValue(self):
        """ Get begin time value.
            Parameters:  none
            Exception:   AttributeError
            Return:      float
        """
        if self.IsPoint():
            raise AttributeError("Annotation object has no attribute BeginValue.")
        return self.Begin.Value

    def __SetBeginValue(self, time):
        """ Set begin time value to the given time.
            Parameters:  time (float)
            Exception:   ValueError, AttributeError
            Return:      none
        """
        if self.IsPoint():
            raise AttributeError("Annotation object has no attribute BeginValue.")
        if time >= self.End:
            raise ValueError("begin time must be less than end time. (%s, %s)" % (time, self.End))
        self.Begin.Value = time

    BeginValue = property(__GetBeginValue, __SetBeginValue)

    # End __GetBeginValue and __SetBeginValue
    # -----------------------------------------------------------------------


    def __GetEndValue(self):
        """ Get end time value.
            Parameters:  none
            Exception:   AttributeError
            Return:      float
        """
        if self.IsPoint():
            raise AttributeError("Annotation object has no attribute EndValue.")
        return self.End.Value

    def __SetEndValue(self, time):
        """ Set end time value to the given time.
            Parameters:  time (float)
            Exception:   none
            Return:      none
        """
        if self.IsPoint():
            raise AttributeError("Annotation object has no attribute EndValue.")
        if time <= self.Begin:
            raise ValueError("end time must be greater than begin time. (%s, %s)" % (self.Begin, time))
        self.End.Value = time

    EndValue = property(__GetEndValue, __SetEndValue)

    # End __GetEndValue and __SetEndValue
    # -----------------------------------------------------------------------


    def __GetPointValue(self):
        """ Get point time value.
            Parameters:  none
            Exception:   AttributeError
            Return:      float
        """
        if self.IsInterval():
            raise AttributeError("Annotation object has no attribute PointValue.")
        return self.Point.Value

    def __SetPointValue(self, time):
        """ Set point time value to the given time.
            Parameters:  time (float)
            Exception:   none
            Return:      none
        """
        if self.IsInterval():
            raise AttributeError("Annotation object has no attribute PointValue.")
        self.Point.Value = time

    PointValue = property(__GetPointValue, __SetPointValue)

    # End __GetPointValue and __SetPointValue
    # -----------------------------------------------------------------------


    def Copy(self):
        """ Return a copy of the annotation.
            Parameters:  none
            Exception:   none
            Return:      Annotation
        """
        return copy.deepcopy(self)

    # End IsPoint
    # -----------------------------------------------------------------------


    def IsPoint(self):
        """ Check if the attribute Time is an instance of TimePoint.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return self.Time.IsPoint()

    # End IsPoint
    # -----------------------------------------------------------------------


    def IsInterval(self):
        """ Check if the attribute Time is an instance of TimeInterval.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return self.Time.IsInterval()

    # End IsInterval
    # -----------------------------------------------------------------------


    def IsDisjoint(self):
        """ Check if the attribute Time is an instance of TimeDisjoint.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return self.Time.IsDisjoint()

    # End IsDisjoint
    # -----------------------------------------------------------------------


    def IsSilence(self):
        """ Check if the attribute Text is an instance of Silence.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return self.Text.IsSilence()

    # End IsSilence
    # -----------------------------------------------------------------------

    def IsLabel(self):
        """ Check if the attribute Text is an instance of Label.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return self.Text.IsLabel()
