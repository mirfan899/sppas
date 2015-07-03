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


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from annotation   import Annotation
from ptime.radius import Radius

# ---------------------------------------------------------------------------

class Tier(object):
    """ Represents a tier.
        A Tier is made of:
            - a name
            - a set of metadata (not used)
            - an array of annotations.
    """

    def __init__(self, name="NoName"):
        """ Create a new Tier instance.
                - name (string): the tier name.
                - radius (Radius) time uncertainty in seconds.
        """
        self.__metadata = {}
        self.__ann      = []
        self.__SetName( name )

    # End __init__
    # -----------------------------------------------------------------------


    def __iter__(self):
        for a in self.__ann:
            yield a

    # End __iter__
    # -----------------------------------------------------------------------


    def __getitem__(self, i):
        return self.__ann[i]

    # End __getitem__
    # -----------------------------------------------------------------------


    def __len__(self):
        return len(self.__ann)

    # End __len__
    # -----------------------------------------------------------------------


    def __call__(self, *args, **kwargs):
        from filter import FilterFactory
        return FilterFactory(self, *args, **kwargs)

    # End __call__
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------


    def GetMetadata(self, key):
        """ Get a tier metadata using the key.
            Parameters:  key is the key of the element to find in the dictionary
            Exception:   none
            Return:      value of the element of key in parameters
        """
        return self.__metadata[key]


    def SetMetadata(self, (key, value)):
        """ Set a tier metadata.
            Parameters:
                - key is the key of the element to modify in the dictionary
                - value is the new value of this element
            Exception:   none
            Return:      none
        """
        self.__metadata[key] = value

    # End GetMetadata and SetMetadata
    # -----------------------------------------------------------------------


    def __GetName(self):
        """ Get the tier name string.
            Parameters:  none
            Exception:   none
            Return:      string label
        """
        return self.__name

    def __SetName(self, name):
        """ Set a new tier name.
            Parameters:
                - name (string): the tier name
            Exception:   none
            Return:      none
        """
        name = " ".join(name.split())
        if isinstance(name, unicode):
            self.__name = name
        else:
            try:
                self.__name = name.decode("utf-8")
            except UnicodeDecodeError as e:
                raise e

    Name = property(__GetName, __SetName)

    # End __GetName and __SetName
    # -----------------------------------------------------------------------


    def SetRadius(self, radius):
        """ Fix the radius of all TimePoint instances of the tier.
            Parameters:
                - p (float or Radius) radius in seconds
        """
        if isinstance(radius, float) is True:
            r = Radius(radius)
            radius = r
        if isinstance(radius, Radius) is False:
            raise TypeError("Radius argument required, not %r" % radius)
        if self.IsEmpty() is False:
            for annotation in self:
                if annotation.IsPoint():
                    annotation.Time.Radius = radius
                elif annotation.IsInterval():
                    annotation.Time.Begin.Radius = radius
                    annotation.Time.End.Radius = radius

    # End SetRadius
    # -----------------------------------------------------------------------


    def GetSize(self):
        """ Return the number of annotations
            Parameters:  none
            Exception:   none
            Return:      int
        """
        return len(self.__ann)

    # end GetSize
    # -----------------------------------------------------------------------


    def GetBegin(self):
        """ Return the begin time value of annotions.
            Parameters:  none
            Exception:   none
            Return:      float begin time value
        """
        if self.IsEmpty():
            return 0
        if self.IsInterval() is True:
            return self[0].Time.Begin.Value
        if self.IsPoint() is True:
            return self[0].Time.Value

    # end GetBegin
    # -----------------------------------------------------------------------


    def GetEnd(self):
        """ Return the end time value of the tier.
            Parameters:  none
            Exception:   none
            Return:      float end time value
        """
        if self.IsEmpty():
            return 0
        if self.IsInterval() is True:
            return self[-1].Time.End.Value
        if self.IsPoint() is True:
            return self[-1].Time.Value

    # end GetEnd
    # -----------------------------------------------------------------------


    def IsEmpty(self):
        """ Return True if the tier is empty.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        return len(self) == 0

    # End IsEmpty
    # -----------------------------------------------------------------------

    def IsDisjoint(self):
        """ Return True if all annotations of the tier are linked to time disjoint.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        if self.IsEmpty():
            return False
        return all(a.IsDisjoint() for a in self)


    # end IsInterval
    # -----------------------------------------------------------------------


    def IsInterval(self):
        """ Return True if all annotations of the tier are linked to time interval.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        if self.IsEmpty():
            return False
        return all(a.IsInterval() for a in self)


    # end IsInterval
    # -----------------------------------------------------------------------


    def IsPoint(self):
        """ Return True if all annotations of the tier are linked to time point.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        if self.IsEmpty():
            return False
        return all(a.IsPoint() for a in self)

    # end IsPoint
    # -----------------------------------------------------------------------


    def IsMixed(self):
        """ Return True if the tier contains annotations.
            Parameters:  none
            Exception:   none
            Return:      Boolean
        """
        if self.IsEmpty():
            return False
        return not self.IsDisjoint() and not self.IsInterval() and not self.IsPoint()

    # end IsMixed
    # -----------------------------------------------------------------------


    def Find(self, begin, end, overlaps=True):
        """ Return a list of annotaions between begin and end.
            Parameters:
                - begin (TimePoint)
                - end (TimePoint)
                - overlaps (bool)
            Return: list
        """
        if self.IsEmpty():
            return []
        if overlaps:
            index = self.__find(begin)
            anns = []
            for a in self[index:]:
                if a.IsPoint() and a.Time > end:
                    return anns
                if a.IsInterval() and a.Begin >= end:
                    return anns
                anns.append(a)
            return anns
        if self.IsPoint():
            lo = self.Index(begin)
            hi = self.Index(end)
        else:
            lo = self.Lindex(begin)
            hi = self.Rindex(end)
        return [] if -1 in (lo, hi) else self[lo:hi+1]


    def __find(self, x):
        """ Return the index of the annotation whose time value containing x.
            Parameters:
                - x (TimePoint)
            Return: (int)
        """
        lo = 0
        hi = self.GetSize()
        while lo < hi:
            mid = (lo + hi) / 2
            a = self[mid]
            if a.IsPoint():
                if a.Point == x:
                    return mid
                if x < a.Point:
                    hi = mid
                else:
                    lo = mid + 1
            else: # Interval or Disjoint
                if a.Begin == x or a.Begin < x < a.End:
                    return mid
                if x < a.End:
                    hi = mid
                else:
                    lo = mid + 1
        return hi

    # end Find
    # -----------------------------------------------------------------------


    def Index(self, time):
        """ Return the index of the time point.
            Parameters:
                - time (TimePoint)
            Return: (int)
        """
        lo = 0
        hi = self.GetSize()
        while lo < hi:
            mid = (lo + hi) // 2
            a = self[mid]
            if time < a.Point:
                hi = mid
            elif time > a.Point:
                lo = mid + 1
            else:
                return mid
        return -1

    # End Index
    # ------------------------------------------------------------------------


    def Lindex(self, time):
        """ Return the index of the interval starting at the given time point.
            Parameters:
                - time (TimePoint)
            Return: (int)
        """
        lo = 0
        hi = self.GetSize()
        while lo < hi:
            mid = (lo + hi) // 2
            a = self[mid]
            if time < a.Begin:
                hi = mid
            elif time > a.Begin:
                lo = mid + 1
            else:
                return mid
        return -1

    # End Lindex
    # ------------------------------------------------------------------------


    def Mindex(self, time, direction):
        """ Return the index of the interval containing the given time point.
            Parameters:
                - time (TimePoint)
                - direction (int)
            Return: (int)
        """
        for i, a in enumerate(self):
            if direction == -1:
                if a.Begin <= time < a.End:
                    return i
            elif direction == 1:
                if a.Begin < time <= a.End:
                    return i
            else:
                if a.Begin < time < a.End:
                    return i
        return -1

    # End Mindex
    # ------------------------------------------------------------------------


    def Near(self, time, direction=1):
        """
            Return the index of the annotation whose time value is
            closest to the given time.
            Parameters:
                - time (TimePoint)
                - direction (int):
                    - near 0
                    - forward 1
                    - backward -1
            Return: (int)
        """
        index = self.__find(time)
        a = self[index]
        if a.IsPoint() and a.Time == time:
            return index
        elif (a.IsInterval() or a.IsDisjoint()) and a.Begin <= time < a.End:
            return index

        _next, _prev = (index, index - 1)
        # forward
        if direction == 1 or _prev < 0:
            return _next
        # backward
        elif direction == -1:
            return _prev
        # near
        next_a = self[_next]
        prev_a = self[_prev]
        if next_a.IsPoint():
            if abs(float(time) - prev_a.PointValue) < abs(next_a.PointValue - float(time)):
                return _prev
            else:
                return _next
        else:
            if abs(float(time) - prev_a.EndValue) < abs(next_a.BeginValue - float(time)):
                return _prev
            else:
                return _next

    # end Near
    # -----------------------------------------------------------------------


    def Rindex(self, time):
        """ Return the index of the interval ending at the given time point.
            Parameters:
                - time (TimePoint)
            Return: (int)
        """
        lo = 0
        hi = self.GetSize()
        while lo < hi:
            mid = (lo + hi) // 2
            a = self[mid]
            if time < a.End:
                hi = mid
            elif time > a.End:
                lo = mid + 1
            else:
                return mid
        return -1

    # End Rindex
    # ------------------------------------------------------------------------


    def Remove(self, begin, end, overlaps=False):
        """ Remove intervals between begin and end.
            It is an error if there is no such time points.
            Parameters:
                - begin (TimePoint)
                - end   (TimePoint)
                - overlaps (bool)
            Exception:   IndexError
            Return:      none
        """
        if end < begin:
            raise ValueError("End TimePoint must be strictly greater than Begin TimePoint")
        if begin < self.GetBegin() or self.GetEnd() < end:
            raise IndexError("index error.")
        annotations = self.Find(begin, end, overlaps)
        if not annotations:
            raise IndexError("error not found (%s, %s)." % (begin, end))
        for a in annotations:
            self.__ann.remove(a)

    # end Remove
    # -----------------------------------------------------------------------


    def Search(self, patterns, function='exact', pos=0, forward=True, reverse=False):
        """ Return the index in the tier of the first annotation whose text value matches patterns.
            Parameters:
                - patterns (list): list of strings
                - pos (int)
                - forward (bool)
                - reverse (bool)
                - function (str):
                    exact (str): exact match
                    iexact (str): Case-insensitive exact match
                    startswith (str):
                    istartswith (str): Case-insensitive startswith
                    endswith (str):
                    iendswith: Case-insensitive endswith
                    contains (str):
                    icontains: Case-insensitive contains
                    regexp (str): regular expression
            Return: (int)
        """
        from filter import Bool
        hi = self.GetSize()
        lo = -1

        if pos < 0 or pos > hi - 1:
            raise IndexError("Tier index out of range")

        p = patterns.pop(0)
        match = Bool(**{function:p})
        for p in patterns:
            match = match | Bool(**{function:p})

        if reverse:
            match = ~match

        inc = 1 if forward else -1
        while pos not in (lo, hi):
            annotation = self[pos]
            if match(annotation):
                return pos
            pos += inc
        return -1

    # end Search
    # -----------------------------------------------------------------------


    def Pop(self, i=-1):
        """
            Remove the annotation at the given position in the tier,
            and return it. If no index is specified, Pop() removes
            and returns the last annotation in the tier.
            Parameters:
                - i (int)
            Exception:   IndexError
            Return:      Annotation
        """
        try:
            return self.__ann.pop(i)
        except IndexError:
            raise IndexError("Pop from empty tier.")

    # end Pop
    # -----------------------------------------------------------------------


    def Append(self, annotation):
        """ Add the given annotation to the end of the tier.
            Parameters:
                - annotation (Annotation)
            Exception:   TypeError, ValueError
            Return:      none
        """
        if isinstance(annotation, Annotation) is False:
            raise TypeError("Annotation argument required, not %r" % annotation)
        if self.IsEmpty():
            self.__ann.append(annotation)
        else:
            last = self[-1]
            if last.IsPoint():
                end = last.Time
            else:
                end = last.End
            if annotation.IsPoint():
                new = annotation.Time
            else:
                new = annotation.Begin
            if end > new:
                e = (last.Time, annotation.Time)
                raise ValueError("the tier already has an annotation at: %s, %s" % e)
            self.__ann.append(annotation)

    # end Append
    # -----------------------------------------------------------------------


    def Add(self, annotation):
        """ Add an annotation to the tier in sorted order.
            Parameters:
                - annotation (Annotation)
            Exception:   TypeError, ValueError
            Return:      none
        """
        if isinstance(annotation, Annotation) is False:
            raise TypeError("Annotation argument required, not %r" % annotation)
        if self.IsEmpty():
            self.__ann.insert(0, annotation)
        else:
            size = len(self)
            lo = 0
            hi = size
            while lo < hi:
                mid = (lo + hi) // 2
                if self[mid].Time < annotation.Time:
                    lo = mid + 1
                elif self[mid].Time <= annotation.Time:
                    lo = mid + 1
                else:
                    hi = mid

            if lo != size and self[lo-1].Time == annotation.Time:
                raise ValueError("the tier already has an annotation at : %s, %s"\
                        % (self[lo-1].Time, annotation.Time))
            self.__ann.insert(lo, annotation)

    # end Add
    # -----------------------------------------------------------------------


    def Copy(self):
        """ Return a copy of the tier.
            Parameters: none
            Exception:  none
            Return:     Tier
        """
        clone = Tier(self.Name)
        for a in self:
            clone.Append(a.Copy())
        return clone

    # end Copy
    # -----------------------------------------------------------------------
