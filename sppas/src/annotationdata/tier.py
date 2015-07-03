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
#       Copyright (C) 2011-2015  Brigitte Bigi
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
# File: tier.py
# ----------------------------------------------------------------------------

from annotation import Annotation
from ptime.point import TimePoint
from meta import MetaObject

__docformat__ = """epytext"""
__authors__   = """Tatsuya Watanabe, Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ---------------------------------------------------------------------------


class Tier(MetaObject):
    """
    @authors: Tatsuya Watanabe, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents a tier.

    A Tier is made of:
        - a name
        - an array of annotations
        - a set of metadata (not used)
        - a controlled vocabulary (not used)

    """
    DATA_TYPES = ("str", "int", "float")

    def __init__(self, name="NoName", data_type="str"):
        """
        Create a new Tier instance.

        @param name: (String) is the tier name.

        """
        super(Tier, self).__init__()
        self.__ann = []
        self.__parent = None
        self.__data_type = "str"
        self.__ctrlvocab = None

        self.SetDataType(data_type)
        self.SetName( name )

    # End __init__
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------

    def GetCtrlVocab(self):
        return self.__ctrlvocab

    # End GetCtrlVocab
    # -----------------------------------------------------------------------

    def SetCtrlVocab(self, vocab):
        for annotation in self:
            for word in annotation.GetLabel().GetLabels():
                if word not in vocab:
                    raise Exception("trying to set an invalid dictionnary")
        self.__ctrlvocab = vocab

    # End SetCtrlVocab
    # -----------------------------------------------------------------------

    ctrlvocab = property(GetCtrlVocab, SetCtrlVocab)

    def GetDataType(self):
        """
        Return the data type of the tier (String).

        """
        return self.__data_type

    # End GetDataType
    # -----------------------------------------------------------------------


    def SetDataType(self, data_type):
        """
        Set a data type to this tier.

        @param data_type: (string) data type of the tier.

        """
        if data_type not in Tier.DATA_TYPES:
            raise TypeError("Unknown data type error: %r" % data_type)
        self.__data_type = data_type

    # End SetDataType
    # -----------------------------------------------------------------------

    def GetTranscription(self):
        """
        Return the parent of the tier (Transcription).

        """
        return self.__parent

    # End GetTranscription
    # -----------------------------------------------------------------------


    def SetTranscription(self, parent):
        """
        Set the parent of the tier.

        @param parent: (Transcription)

        """
        if self.__parent is not None and self.GetReferenceTier():
            # Remove me of the current parent hierarchy!!!!!!
            self.__parent.hierarchy.removeTier(self)

        self.__parent = parent

    # End SetTranscription
    # -----------------------------------------------------------------------


    def GetName(self):
        """
        Return the name of the tier (String).

        """
        return self.__name

    # End GetName
    # -----------------------------------------------------------------------


    def SetName(self, name):
        """
        Set a new name to this tier.

        @param name: (string) the tier name

        """
        name = ' '.join(name.split())

        if isinstance(name, unicode):
            self.__name = name
        else:
            try:
                self.__name = name.decode("utf-8")
            except UnicodeDecodeError as e:
                raise e

    # End SetName
    # -----------------------------------------------------------------------


    def SetRadius(self, radius):
        """
        Assign a fixed radius to all TimePoint instances of the tier.

        @param radius: (float) is in seconds

        """

        if self.IsEmpty() is True:
            return

        for annotation in self:
            if annotation.GetLocation().IsPoint():
                annotation.GetLocation().SetPointRadius( radius )
            elif annotation.GetLocation().IsInterval():
                annotation.GetLocation().SetBeginRadius( radius )
                annotation.GetLocation().SetEndRadius( radius )

    # End SetRadius
    # -----------------------------------------------------------------------


    def GetSize(self):
        """
        Return the number of annotations (int).

        """
        return len(self.__ann)

    # end GetSize
    # -----------------------------------------------------------------------


    def GetAllPoints(self):
        """
        Return a list of timepoints in the tier.

        """
        if self.IsEmpty():
            return []

        points = []

        if self.IsPoint():
            for a in self.__ann:
                for localization in a.GetLocation():
                    place = localization.GetPlace()
                    points.append(place.GetPoint())

        elif self.IsInterval():
            for a in self.__ann:
                for localization in a.GetLocation():
                    place = localization.GetPlace()
                    points.append(place.GetBegin())
                    points.append(place.GetEnd())

        elif self.IsDisjoint():
            for a in self.__ann:
                for localization in a.GetLocation():
                    for interval in localization.GetPlace():
                        points.append(interval.GetBegin())
                        points.append(interval.GetEnd())

        else:
            raise Exception('Unknown tier type: Not Point, or Interval nor Disjoint!')

        return points

    # end GetAllPoints
    # -----------------------------------------------------------------------


    def GetBeginValue(self):
        """
        Return the begin value of the set of annotations (float,int).

        """
        return self.GetBegin().GetMidpoint()

    # end GetBeginValue
    # -----------------------------------------------------------------------


    def GetEndValue(self):
        """
        Return the end value of the tier (float,int).

        """
        return self.GetEnd().GetMidpoint()

    # end GetEndValue
    # -----------------------------------------------------------------------


    def GetBegin(self):
        """
        Return the begin instance of the set of annotations (TimePoint/FramePoint).

        """
        if self.IsEmpty():
            return TimePoint(0)

        if self.IsPoint() is True:
            return self.__ann[0].GetLocation().GetPoint()

        # Interval of Disjoint
        return self.__ann[0].GetLocation().GetBegin()


    # end GetBegin
    # -----------------------------------------------------------------------


    def GetEnd(self):
        """
        Return the end value of the tier (TimePoint/FramePoint).

        """
        if self.IsEmpty():
            return TimePoint(0)

        if self.IsPoint() is True:
            return self.__ann[-1].GetLocation().GetPoint()

        # Interval or Disjoint
        return self.__ann[-1].GetLocation().GetEnd()

    # end GetEnd
    # -----------------------------------------------------------------------


    def HasPoint(self, point):
        """
        Return True if the tier contains the given point.

        """
        return point in self.GetAllPoints()

    # end HasPoint
    # -----------------------------------------------------------------------


    def IsSuperset(self, tier):
        """
        Return True if this tier contains all timepoints of the given tier.

        """
        #Actually, the following does not work!
        #reftimes = self.GetAllPoints()
        #subtimes = tier.GetAllPoints()
        #return set(reftimes).issuperset(set(subtimes))

        for t in tier:
            if t.GetLocation().IsPoint():
                i = self.Index( t.GetLocation().GetPoint() )
                if i == -1:
                    return False
            else:
                i = self.Lindex( t.GetLocation().GetBegin() )
                if i == -1:
                    return False
                i = self.Rindex(t.GetLocation().GetEnd())
                if i == -1:
                    return False

        return True

    # end IsSuperset
    # -----------------------------------------------------------------------


    def IsEmpty(self):
        """
        Return True if the tier is empty (ie does not contain Annotations).

        """
        return len(self.__ann) == 0

    # End IsEmpty
    # -----------------------------------------------------------------------


    def IsDisjoint(self):
        """
        Return True if all annotations of the tier are linked to time disjoint.

        """
        if self.IsEmpty():
            return False

        return all(a.GetLocation().IsDisjoint() for a in self.__ann)

    # End IsDisjoint
    # -----------------------------------------------------------------------


    def IsInterval(self):
        """
        Return True if all annotations of the tier are linked to time interval.

        """
        if self.IsEmpty():
            return False

        return all(a.GetLocation().IsInterval() for a in self.__ann)

    # End IsInterval
    # -----------------------------------------------------------------------


    def IsPoint(self):
        """
        Return True if all annotations of the tier are linked to time point.

        """
        if self.IsEmpty():
            return False

        return all(a.GetLocation().IsPoint() for a in self.__ann)

    # End IsPoint
    # -----------------------------------------------------------------------


    def Find(self, begin, end, overlaps=True):
        """
        Return a list of annotations between begin and end.

        @param begin: (TimePoint) or None to start from the beginning of the tier
        @param end: (TimePoint) or None to end at the end off the tier
        @param overlaps: (bool)

        """
        if self.IsEmpty():
            return []

        if begin is None:
            begin = self.GetBegin() #self.GetBeginValue()

        if end is None:
            end = self.GetEnd() #self.GetEndValue()

        if overlaps is True:
            index = self.__find(begin)
            anns = list()
            for a in self.__ann[index:]:
                if a.GetLocation().IsPoint() and a.GetLocation().GetPoint() > end:
                    return anns
                if a.GetLocation().IsInterval() and a.GetLocation().GetBegin() >= end:
                    return anns
                anns.append(a)
            return anns

        if self.IsPoint():
            lo = self.Index(begin)
            hi = self.Index(end)
            if -1 in (lo, hi):
                return []
            for i in range(hi, self.GetSize()):
                a = self.__ann[i]
                if a.GetLocation().GetPoint() == end:
                    tmp = i
                else:break
            hi = tmp
        else:
            lo = self.Lindex(begin)
            hi = self.Rindex(end)
            if -1 in (lo, hi):
                return []
            for i in range(hi, self.GetSize()):
                a = self.__ann[i]
                if a.GetLocation().GetEnd() == end:
                    tmp = i
                else:break
            hi = tmp

        return [] if -1 in (lo, hi) else self.__ann[lo:hi+1]

    # -----------------------------------------------------------------------


    def GetAnnotationsStartAt(self, time):
        """
        Return a list of annotations, starting at the specified time.

        """
        annotations = []
        if self.IsPoint():
            index = self.Index(time)
            if index == -1:
                return annotations
            for i in range(index, self.GetSize()):
                a = self._ann[i]
                if a.GetLocation().GetPoint() == time:
                    annotations.append(a)
                else: break
        else:
            index = self.Lindex(time)
            if index == -1:
                return annotations
            for i in range(index, self.GetSize()):
                a = self.__ann[i]
                if a.GetLocation().GetBegin() == time:
                    annotations.append(a)
                else: break
        return annotations

    # End GetAnnotationsStartAt
    # -----------------------------------------------------------------------


    def GetAnnotationsEndAt(self, time):
        """
        Return a list of annotations, ending at the specified time.

        """
        annotations = []
        if self.IsPoint():
            return self.GetAnnotationsStartAt(time)

        index = self.Rindex(time)
        if index == -1: return []

        for i in range(index, len(self.__ann)):
            a = self.__ann[i]
            if time in [p.GetEnd() for p in a.GetLocation().GetPlaces()]:
                annotations.append(a)
            else:
                return annotations

        return annotations

    # end GetAnnotationsEndAt
    # -----------------------------------------------------------------------


    def __find(self, x):
        """
        Return the index of the annotation whose time value containing x.

        @param x: (TimePoint)

        """
        lo = 0
        hi = self.GetSize() - 1
        while lo < hi:
            mid = (lo + hi) / 2
            a = self.__ann[mid]
            if a.GetLocation().IsPoint():
                if a.GetLocation().GetPoint() == x:
                    return mid
                if x < a.GetLocation().GetPoint():
                    hi = mid
                else:
                    lo = mid + 1
            else: # Interval or Disjoint
                if a.GetLocation().GetBegin() == x or a.GetLocation().GetBegin() < x < a.GetLocation().GetEnd(): # only compare to the location with the highest score
                    return mid
                if x < a.GetLocation().GetEnd():
                    hi = mid
                else:
                    lo = mid + 1
        return hi

    # end Find
    # -----------------------------------------------------------------------


    def Index(self, time):
        """
        Return the index of the time point (int), or -1.
        Only is tier.IsPoint() is True.

        @param time: (TimePoint)

        """
        if self.IsPoint() is False:
            return -1
        lo = 0
        hi = self.GetSize()
        found = False
        while lo < hi:
            mid = (lo + hi) // 2
            a = self.__ann[mid]
            if time < a.GetLocation().GetPoint():
                hi = mid
            elif time > a.GetLocation().GetPoint():
                lo = mid + 1
            else:
                found = True
                break
        if not found:
            return -1
        # if the tier contains more than one annotation with the same point value,
        # the method returns the first one
        first = mid
        for i in range(mid, -1, -1):
            a = self.__ann[i]
            if a.GetLocation().GetPoint() == time:
                first = i
            else: break

        return first

    # End Index
    # ------------------------------------------------------------------------


    def Lindex(self, time):
        """
        Return the index of the interval starting at the given time point, or -1.

        @param time (TimePoint)

        """
        lo = 0
        hi = self.GetSize()
        found = False
        while lo < hi:
            mid = (lo + hi) // 2
            a = self.__ann[mid]
            if time < a.GetLocation().GetBegin():
                hi = mid
            elif time > a.GetLocation().GetBegin():
                lo = mid + 1
            else:
                found = True
                break

        if not found:
            return -1
        # if the tier contains more than one annotation with the same begin value,
        # the method returns the first one
        first = mid
        for i in range(mid, -1, -1):
            a = self.__ann[i]
            if a.GetLocation().GetBegin() == time:
                first = i
            else: break
        return first

    # End Lindex
    # ------------------------------------------------------------------------


    def Mindex(self, time, direction):
        """
        Return the index of the interval containing the given time point, or -1.

        @param time: (TimePoint)
        @param direction: (int)

        """
        for i, a in enumerate(self):
            if direction == -1:
                if a.GetLocation().GetBegin() <= time < a.GetLocation().GetEnd():
                    return i
            elif direction == 1:
                if a.GetLocation().GetBegin() < time <= a.GetLocation().GetEnd():
                    return i
            else:
                if a.GetLocation().GetBegin() < time < a.GetLocation().GetEnd():
                    return i
        return -1

    # End Mindex
    # ------------------------------------------------------------------------


    def Rindex(self, time):
        """
        Return the index of the interval ending at the given time point.

        @param time: (TimePoint)

        """
        lo = 0
        hi = len(self.__ann)
        found = False

        while lo < hi:
            mid = (lo + hi) // 2
            a = self.__ann[mid]
            if time < a.GetLocation().GetEnd():
                hi = mid
            elif time > a.GetLocation().GetEnd():
                lo = mid + 1
            else:
                found = True
                break

        if not found:
            return -1

        # if the tier contains more than one annotation with the same end value,
        # the method returns the first one
        first = mid
        for i in range(mid, -1, -1):
            a = self.__ann[i]
            if a.GetLocation().GetEnd() == time:
                first = i
            else: break

        return first

    # End Rindex
    # ------------------------------------------------------------------------


    def Near(self, time, direction=1):
        """
        Return the index of the annotation whose time value is
        closest to the given time.

        @param time: (TimePoint)
        @param direction: (int)
                - near 0
                - forward 1
                - backward -1

        """
        index = self.__find(time)
        a = self.__ann[index]
        if a.GetLocation().IsPoint() and a.GetLocation().GetPoint() == time:
            return index
        elif (a.GetLocation().IsInterval() or a.GetLocation().IsDisjoint()):
            if a.GetLocation().GetBegin() < time < a.GetLocation().GetEnd():
                return index
# BB:
#             if direction==0 and a.GetLocation().GetBegin() <= time <= a.GetLocation().GetEnd():
#                 return index
#             elif direction == 1 and a.GetLocation().GetBegin() <= time < a.GetLocation().GetEnd():
#                 return index
#             elif direction == -1 and a.GetLocation().GetBegin() <= time < a.GetLocation().GetEnd():
#                 return index
#       _next, _prev = (index + 1, index - 1)
        _next, _prev = (index, index - 1)
        # forward
        if direction == 1 or _prev < 0:
            return _next
        # backward
        elif direction == -1:
            return _prev
        # near
        next_a = self.__ann[_next]
        prev_a = self.__ann[_prev]
        time = time.GetMidpoint() if isinstance(time, TimePoint) else float(time)
        if next_a.GetLocation().IsPoint():
            if abs(time - prev_a.GetLocation().GetPointMidpoint()) < abs(next_a.GetLocation().GetPointMidpoint() - time):
                return _prev
            else:
                return _next
        else:
            if abs(time - prev_a.GetLocation().GetEndMidpoint()) < abs(next_a.GetLocation().GetBeginMidpoint() - time):
                return _prev
            else:
                return _next

    # end Near
    # -----------------------------------------------------------------------


    def Search(self, patterns, function='exact', pos=0, forward=True, reverse=False):
        """
        Return the index in the tier of the first annotation whose text value matches patterns.

        @param patterns: (list) is the list of strings to search
        @param pos: (int)
        @param forward: (bool)
        @param reverse: (bool)
        @param function: (str) is:
                -    exact (str): exact match
                -    iexact (str): Case-insensitive exact match
                -    startswith (str):
                -    istartswith (str): Case-insensitive startswith
                -    endswith (str):
                -    iendswith: Case-insensitive endswith
                -    contains (str):
                -    icontains: Case-insensitive contains
                -    regexp (str): regular expression

        """
        from filter import Sel

        hi = self.GetSize()
        lo = -1

        if pos < 0 or pos > hi - 1:
            raise IndexError("Tier index out of range")

        p = patterns.pop(0)
        match = Sel(**{function:p})
        for p in patterns:
            match = match | Sel(**{function:p})

        if reverse:
            match = ~match

        inc = 1 if forward else -1
        while pos not in (lo, hi):
            annotation = self.__ann[pos]
            if match(annotation):
                return pos
            pos += inc
        return -1

    # end Search
    # -----------------------------------------------------------------------


    def Remove(self, begin, end, overlaps=False):
        """
        Remove intervals between begin and end.
        It is an error if there is no such time points.

        @param begin: (TimePoint)
        @param end:   (TimePoint)
        @param overlaps: (bool)

        """
        if end < begin:
            raise ValueError("End TimePoint must be strictly greater than Begin TimePoint")
        if begin < self.GetBeginValue() or self.GetEndValue() < end:
            raise IndexError("index error.")
        annotations = self.Find(begin, end, overlaps)
        if not annotations:
            raise IndexError("error not found (%s, %s)." % (begin, end))
        for a in annotations:
            self.__ann.remove(a)

    # end Remove
    # -----------------------------------------------------------------------


    def Pop(self, i=-1):
        """
        Remove the annotation at the given position in the tier,
        and return it. If no index is specified, Pop() removes
        and returns the last annotation in the tier.

        @param i: (int)

        """
        try:
            return self.__ann.pop(i)
        except IndexError:
            raise IndexError("Pop from empty tier.")

    # end Pop
    # -----------------------------------------------------------------------


    def Append(self, annotation):
        """
        Add the given annotation to the end of the tier.

        @param annotation: (Annotation)

        """
        self.__validate_annotation(annotation)

        # Check if hierarchy
        reftier = self.GetReferenceTier()
        if reftier is not None:
            refpoints = reftier.GetAllPoints()

        # Append:
        if self.IsEmpty():
            if reftier is not None:
                if annotation.GetLocation().IsPoint():
                    if annotation.GetLocation().GetPoint() in refpoints:
                        self.__ann.append(annotation)
                    else:
                        raise ValueError("Attempt to append an annotation in a child tier, but reference has no corresponding time point.")
                else:
                    b = annotation.GetLocation().GetBegin()
                    e = annotation.GetLocation().GetEnd()
                    if b in refpoints and e in refpoints:
                        self.__ann.append(annotation)
                    else:
                        raise ValueError("Attempt to append an annotation in a child tier, but reference has no corresponding time interval (%s, %s)."%(b,e))
            else:
                self.__ann.append(annotation)

        else:
            last = self.__ann[-1]
            if last.GetLocation().IsPoint():
                end = last.GetLocation().GetPoint()
            else:
                end = last.GetLocation().GetEnd()

            if annotation.GetLocation().IsPoint():
                new = annotation.GetLocation().GetPoint()
            else:
                new = annotation.GetLocation().GetBegin()

            if end > new:
                error = (last.GetLocation().GetValue().GetPlace(), annotation.GetLocation().GetValue().GetPlace())
                raise ValueError("The tier already has an annotation at: %s, %s" % error)

            if reftier:
                if annotation.GetLocation().IsPoint():
                    if annotation.GetLocation().GetPoint() in refpoints:
                        self.__ann.append(annotation)
                    else:
                        raise ValueError("Attempt to append an annotation in a child tier, but reference has no corresponding time point.")
                else:
                    b = annotation.GetLocation().GetBegin()
                    e = annotation.GetLocation().GetEnd()
                    if b in refpoints and e in refpoints:
                        self.__ann.append(annotation)
                    else:
                        raise ValueError("Attempt to append an annotation in a child tier, but reference has no corresponding time interval (%s, %s)."%(b,e))
            else:
                self.__ann.append(annotation)

    # end Append
    # -----------------------------------------------------------------------

    def Add(self, annotation):
        """
        Add an annotation to the tier in sorted order.

        @param annotation: (Annotation)

        """
        self.__validate_annotation(annotation)

        if self.IsEmpty():
            lo = 0
            self.__ann.insert(lo, annotation)
        else:
            size = len(self.__ann)
            lo = 0
            hi = size
            while lo < hi:
                mid = (lo + hi) // 2
                if self.__ann[mid].GetLocation().GetValue().GetPlace() < annotation.GetLocation().GetValue().GetPlace():
                    lo = mid + 1
                elif self.__ann[mid].GetLocation().GetValue().GetPlace() <= annotation.GetLocation().GetValue().GetPlace():
                    lo = mid + 1
                else:
                    hi = mid

            if lo != size and not annotation.GetLocation().IsPoint():
                tmp = lo
                for ann in self.__ann[tmp:]:
                    if ann.GetLocation().GetBegin() != annotation.GetLocation().GetBegin():
                        break
                    if ann.GetLocation().GetEnd() < annotation.GetLocation().GetEnd():
                        lo += 1

            self.__ann.insert(lo, annotation)

        reftier = self.GetReferenceTier()
        if reftier is None or reftier.IsSuperset(self):
            return True
        else:
            self.__ann.pop(lo)
            return False

    # End Add
    # -----------------------------------------------------------------------

    def __validate_annotation(self, annotation):
        if isinstance(annotation, Annotation) is False:
            raise TypeError(
                "Annotation argument required, not %r" % annotation)

        # Check if controlled vocabulary
        if self.__ctrlvocab is not None:
            for word in annotation.GetLabel().GetLabels():
                if(word.GetValue() not in self.__ctrlvocab and
                   word.GetValue() != ''):  # praat needs empty values
                    raise ValueError(
                        "Attempt to append a free-annotation-label"
                        " in a controlled vocabulary tier.")

        if self.GetTranscription() is not None:
            hierarchy = self.GetTranscription().GetHierarchy()

            assocHierarchy = hierarchy.getHierarchy('TimeAssociation')
            for (former, latter) in assocHierarchy:
                if former is self or latter is self:
                    raise Exception(
                        'Tier modification invalidates hierarchy')

            alignHierarchy = hierarchy.getHierarchy('TimeAlignment')
            for (former, latter) in alignHierarchy:
                if latter is self:
                    if annotation.GetLocation().IsPoint():
                        i = self.Index(annotation.GetLocation().GetPoint())
                        if i == -1:
                            raise Exception(
                                'Tier modification invalidates hierarchy %s %s'
                                % (
                                    former.GetLocation().GetMidpoint(),
                                    latter.GetLocation().GetMidpoint()))
                    else:
                        l = self.Lindex(annotation.GetLocation().GetBegin())
                        if l == -1:
                            raise Exception(
                                'Tier modification invalidates hierarchy %s %s'
                                % (
                                    former.GetLocation().GetBeginMidpoint(),
                                    latter.GetLocation().GetBeginMidpoint()))

                        r = self.Rindex(annotation.GetLocation().GetEnd())
                        if r == -1:
                            raise Exception(
                                'Tier modification invalidates hierarchy %s %s'
                                % (
                                    former.GetLocation().GetEndMidpoint(),
                                    latter.GetLocation().GetEndMidpoint()))
    # End __validate_annotation
    # -----------------------------------------------------------------------

    def Copy(self):
        """
        Return a copy of the tier.

        """
        import copy
        newTier = copy.copy(self)
        newTier.__ann = copy.deepcopy(self.__ann)
        newTier.__data_type = copy.deepcopy(self.__data_type)
        newTier.__name = copy.deepcopy(self.__name)
        return newTier
    # End Copy
    # -----------------------------------------------------------------------


    def GetReferenceTier(self):
        """
        Return the reference tier of self, or None.

        """

        if self.__parent is None:
            return None

        try:
            return self.__parent.GetReferenceTier(self)
        except Exception:
            return None

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------


    def __iter__(self):
        for a in self.__ann:
            yield a


    def __getitem__(self, i):
        return self.__ann[i]


    def __len__(self):
        return len(self.__ann)



    def __call__(self, *args, **kwargs):
        """
        @deprecated
        """
        from filter import FilterFactory
        return FilterFactory(self, *args, **kwargs)


    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------
