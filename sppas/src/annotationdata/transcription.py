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
#       Copyright (C) 2011-2014  Tatsuya Watanabe
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
# File: transcription.py
# ----------------------------------------------------------------------------

import copy
from utils.deprecated import deprecated
from meta import MetaObject
from tier import Tier
from hierarchy import Hierarchy

__docformat__ = """epytext"""
__authors__ = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


class Transcription(MetaObject):
    """
    @authors: Brigitte Bigi, Tatsuya Watanabe
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Generic representation of an annotated file.

    Transcriptions in SPPAS are represented with:
        - a name
        - tiers
        - meta-data
        - controlled vocabularies (yet not used)

    Inter-tier relations are managed by establishing alignment or constituency
    links between 2 tiers:
        - alignment: annotations of a tier A have only Time instances
          included in those of annotations of tier B;
        - constituency: annotations of a tier A have only Time instances
          included in those of annotations of tier B and labels of B are
          made of those of A.

    >>> transcription = Transcription()
    >>> tier1 = transcription.NewTier("tier1")
    >>> tier2 = transcription.NewTier("tier2")
    >>> transcription.AddSubdivision(tier1, tier2, type="alignment")

    Currently, meta-data are:
        - TIME_UNITS
        - MEDIA_FILE

    """

    def __init__(self, name="NoName", coeff=1, mintime=0., maxtime=0.):
        """
        Creates a new Transcription instance.

        @param name: (str) the name of the transcription
        @param coeff: (float) the time coefficient (coeff=1 is seconds)

        """
        super(Transcription, self).__init__()
        self.__name = u'NoName'
        self.__mintime = mintime
        self.__maxtime = maxtime
        self.__coeff = coeff
        self.__tiers = []
        self._hierarchy = Hierarchy()

        self.SetName(name)

    # End __init__
    # ------------------------------------------------------------------------------------

    def GetName(self):
        """
        Return the string of the name of the transcription.

        """
        return self.__name

    # End GetName
    # ------------------------------------------------------------------------------------

    def GetHierarchy(self):
        return self._hierarchy

    def SetName(self, name):
        """
        Set a new name.

        @param name: (str)

        @raise UnicodeDecodeError:

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
    # ------------------------------------------------------------------------------------

    def GetMinTime(self):
        """
        Return the minimum time value.

        """

        return self.__mintime

    # End GetMinTime
    # ------------------------------------------------------------------------------------

    def SetMinTime(self, mintime):
        """
        Set the minimum time value.

        """
        self.__mintime = mintime
        # TODO: Must check if min < max

    # End SetMinTime
    # ------------------------------------------------------------------------------------

    def GetCtrlVocabs(self):
        """
        Return a dictionnary-mapped tiers vocabularies
        for instance:
        {
            {elem1, elem2, elem3}:[tier1, tier2]
            {elem4}: [tier3]
        }
        """
        result = {}

        for tier in self:
            if tier.ctrlvocab is not None:
                if tier.ctrlvocab in result:
                    result[tier.ctrlvocab].append(tier)
                else:
                    result[tier.ctrlvocab] = [tier]

        return result

    # End GetCtrlVocabs
    # ------------------------------------------------------------------------------------


    def GetMaxTime(self):
        """
        Return the maximum time value.

        """
        # In theory, maxtime represents the duration of the annotated media.
        # Then, it can not be lesser than the end of the last annotation...
        # But... none of the annotation formats indicate such duration!
        # So, we do what we can with what we have.
        if self.GetEnd() > self.__maxtime:
            self.__maxtime = self.GetEnd()

        return self.__maxtime

    # End def GetMaxTime
    # ------------------------------------------------------------------------------------

    def SetMaxTime(self, maxtime):
        """
        Set the maximum time value.

        """
        self.__maxtime = maxtime

        if self.__maxtime < self.GetEnd():
            raise Exception(
                'Impossible to fix a max time value '
                'lesser than the end of annotations.')

    # End SetMaxTime
    # ------------------------------------------------------------------------------------

    def Set(self, tiers, name='empty'):
        """
        Set a transcription.

        @param tiers: tiers is a transcription or list of tiers.

        @raise TypeError:

        """
        if(isinstance(tiers, Transcription)):
            self.__name = tiers.__name
            self.metadata = tiers.metadata
            self.__mintime = tiers.__mintime
            self.__maxtime = tiers.__maxtime
            self.__coeff = tiers.__coeff
            self.__tiers = tiers.__tiers
            self._hierarchy = tiers._hierarchy
        if all(isinstance(tier, Tier) for tier in tiers) is False:
            raise TypeError("Tier argument required, not %r" % tiers)

        tiers = [tier for tier in tiers]
        self.__name = name
        self.__tiers = tiers

    # End Set
    # ------------------------------------------------------------------------------------

    @deprecated
    def GetMetadata(self, key):
        if(key not in self.metadata):
            return ''
        else:
            return self.metadata[key]

    # End GetMetadata
    # ------------------------------------------------------------------------------------

    @deprecated
    def SetMetadata(self, key, value):
        self.metadata[key] = value

    # End SetMetadata
    # ------------------------------------------------------------------------------------

    def GetSize(self):
        """
        Return the number of tiers in the transcription.

        """
        return len(self.__tiers)

    # End GetSize
    # ------------------------------------------------------------------------------------

    def NewTier(self, name="Empty"):
        """
        Add a new empty tier at the end of the transcription.

        @param name: (str) the name of the tier to create

        @return: newly created empty tier

        """
        tier = Tier(name)
        tier.SetTranscription(self)
        self.__rename(tier)
        self.__tiers.append(tier)

        return tier

    # End NewTier
    # ------------------------------------------------------------------------------------

    def Add(self, tier, index=None):
        """
        Add a new tier at a given index.

        Index must be lower than the transcription size.
        By default, the tier is appended at the end of the list.

        @param tier: (Tier) the tier to add to the transcription
        @param index: (int) the position in the list of tiers

        @raise IndexError:

        @return: Tier index

        """
        tier.SetTranscription(self)
        self.__rename(tier)

        if index is not None:
            if index >= len(self.__tiers) or index < 0:
                raise IndexError
            self.__tiers.insert(index, tier)
        else:
            self.__tiers.append(tier)
            index = len(self.__tiers)-1

        return index

    # End Add
    # ------------------------------------------------------------------------------------

    def Append(self, tier):
        """
        Append a tier in the transcription.

        @param tier (Tier) the tier to add to the transcription
        @return Tier index (int)

        """
        tier.SetTranscription(self)
        self.__rename(tier)
        self.__tiers.append(tier)

        if tier.GetEnd() > self.__maxtime:
            self.__maxtime = tier.GetEndValue()

        return len(self.__tiers)-1

    # End Append
    # ------------------------------------------------------------------------------------

    def Pop(self, index=-1):
        """
        Pop a tier of the transcription.

        @param index: the index of the tier to pop. Default is the last one.
        @raise IndexError:

        @return: Return the removed tier

        """
        if self.IsEmpty():
            raise IndexError("Pop from empty transcription.")

        try:
            self._hierarchy.removeTier(self.__tiers[index])
            return self.__tiers.pop(index)
        except IndexError as e:
            raise e

    # End Pop
    # ------------------------------------------------------------------------------------

    def Remove(self, index):
        """
        Remove a tier of the transcription.

        @param index: the index of the tier to remove.

        @raise IndexError:

        """
        if index >= len(self.__tiers) or index < 0:
            raise IndexError

        self._hierarchy.removeTier(self.__tiers[index])
        del self.__tiers[index]

    # End Remove
    # ------------------------------------------------------------------------------------

    def GetIndex(self, name, case_sensitive=True):
        """
        Get the index of a tier from its name.

        @param name: (str) EXACT name of the tier
        @param case_sensitive: (bool)

        @return: Return the tier index or -1

        """
        t = self.Find(name, case_sensitive)
        for i, tier in enumerate(self.__tiers):
            if t is tier:
                return i

        return -1

    # End GetIndex
    # ------------------------------------------------------------------------------------

    def Find(self, name, case_sensitive=True):
        """
        Find a tier from its name.

        @param name: (str) EXACT name of the tier
        @param case_sensitive: (bool)

        @return: Return the tier or None

        """
        for tier in self:
            if case_sensitive:
                if tier.GetName() == name.strip():
                    return tier
            else:
                if tier.GetName().lower() == name.strip().lower():
                    return tier

        return None

    # End Find
    # ------------------------------------------------------------------------------------

    def GetBegin(self):
        """
        Return the smaller begin time value of all tiers.
        ATTENTION: RETURN THE BEGIN MIDPOINT VALUE (NOT THE BEGIN)!!!!!!!!!
        MUST BE CHANGED!!!

        @return: Float value, or 0 if the transcription contains no tiers.

        """
        if self.IsEmpty():
            return 0.

        return min(tier.GetBeginValue() for tier in self)

    # End GetBegin
    # ------------------------------------------------------------------------------------

    def GetEnd(self):
        """
        Return the higher end time value of all tiers.
        Return 0 if the transcription contains no tiers.
        ATTENTION: RETURN THE END MIDPOINT VALUE (NOT THE END)!!!!!!!!!
        MUST BE CHANGED!!!

        @return: Float value, or 0 if the transcription contains no tiers.

        """
        if self.IsEmpty():
            return 0.

        return max(tier.GetEndValue() for tier in self)

    # End GetEnd
    # ------------------------------------------------------------------------------------

    def IsEmpty(self):
        """
        Ask the transcription to be empty or not.
        A transcription is empty if it does not contain tiers.

        @return: bool

        """
        return len(self.__tiers) == 0

    # End IsEmpty
    # ------------------------------------------------------------------------------------

    def Copy(self):
        """
        Return a copy of the transcription.

        """
        return copy.deepcopy(self)

    # End Copy
    # ------------------------------------------------------------------------------------

    def read(self):
        name = self.__class__.__name__
        raise NotImplementedError("%s does not support read()." % name)

    # End read
    # ------------------------------------------------------------------------------------

    def write(self):
        name = self.__class__.__name__
        raise NotImplementedError("%s does not support write()." % name)

    # End write
    # ------------------------------------------------------------------------------------

    def __rename(self, tier):
        name = tier.GetName()
        i = 2
        while self.Find(name) is not None:
            name = u"%s-%d" % (tier.GetName(), i)
            i += 1
        tier.SetName(name)

    # End __rename
    # ------------------------------------------------------------------------------------

    def __len__(self):
        return len(self.__tiers)

    # End __len__
    # ------------------------------------------------------------------------------------

    def __iter__(self):
        for x in self.__tiers:
            yield x

    # End __iter__
    # ------------------------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__tiers[i]

    # End __getitem__
    # ------------------------------------------------------------------------------------