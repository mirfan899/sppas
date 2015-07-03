#!/usr/bin/env python2
# -*- coding: utf8 -*-
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

from tier import Tier

# ---------------------------------------------------------------------------

class Transcription(object):
    """ Represents a SPPAS transcription.
        Transcriptions in SPPAS are represented as:
            - a name
            - an array of tiers
            - a time coefficient (1=seconds).
    """

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """ Creates a new Transcription instance.
            Parameters:
                - name (string): the name of the transcription
                - coeff (float): the time coefficient (coeff=1 is seconds)
        """
        self.__SetName( name )
        self.__mintime = mintime
        self.__maxtime = maxtime
        self.__coeff = coeff
        self.__tiers = []

    # End __init__
    # ------------------------------------------------------------------


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


    def __GetMinTime(self):
        """ Return the minimum time value.
            Parameters: none
            Exception:  none
            Return:     float or None
        """
        return self.__mintime

    def __SetMinTime(self, mintime):
        """ Set the minimum time value.
            Parameters: none
            Exception:  none
            Return:     none
        """
        self.__mintime = mintime

    MinTime = property(__GetMinTime, __SetMinTime)

    # End __GetMinTime, __SetMinTime
    # ------------------------------------------------------------------


    def __GetMaxTime(self):
        """ Return the maximum time value.
            Parameters: none
            Exception:  none
            Return:     float or None
        """
        return self.__maxtime

    def __SetMaxTime(self, maxtime):
        """ Set the maximum time value.
            Parameters: none
            Exception:  none
            Return:     none
        """
        self.__maxtime = maxtime

    MaxTime = property(__GetMaxTime, __SetMaxTime)

    # End __GetMaxTime, __SetMaxTime
    # ------------------------------------------------------------------


    def Set(self, tiers, name='empty'):
        """ Set a transcription.
            Parameters:
                - tiers is a transcription or list of tiers.
            Exception:  None
            Return:     time value
        """
        if all(isinstance(tier, Tier) for tier in tiers) is False:
            raise TypeError("Tier argument required, not %r" % tiers)
        tiers = [tier for tier in tiers]
        self.Name = name
        self.__tiers = tiers

    # End Set
    # ------------------------------------------------------------------


    def __rename(self, tier):
        name = tier.Name
        i = 2
        while self.Find(name) is not None:
            name = u"%s-%d" % (tier.Name, i)
            i += 1
        tier.Name = name

    # End __rename
    # ------------------------------------------------------------------


    def GetSize(self):
        """ Return the number of tiers in the transcription.
            Parameters:  None
            Exception:   None
            Return:      An integer
        """
        return len(self.__tiers)

    # End GetSize
    # ------------------------------------------------------------------


    def NewTier(self, name="empty"):
        """ Add a new empty tier at the end of the transcription.
            Parameters:
                - name (string): the name of the tier to create
            Exception:   None
            Return:      new tier
        """
        tier = Tier(name)
        self.__rename(tier)
        self.__tiers.append(tier)
        return tier

    # End NewTier
    # ------------------------------------------------------------------


    def Add(self, tier, index=None):
        """ Add a new tier at a given index.
            Index must be lower than the transcription size.
            By default, the tier is added at the end of the list.
            Parameters:
                - tier (Tier): the tier to add to the transcription
                - index (int): the position in the list of tiers
            Exception:   IndexError
            Return:      Tier index
        """
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
    # ------------------------------------------------------------------


    def Append(self, tier):
        """ Append a tier in the transcription.
            Parameters:
                - tier (Tier): the tier to add to the transcription
            Exception:   None
            Return:      None
        """
        self.__rename(tier)
        self.__tiers.append(tier)

    # End Append
    # ------------------------------------------------------------------


    def Pop(self, index=-1):
        """ Pop a tier of the transcription.
            Parameters:
                - index (int): the index of the tier to pop. Default is the last one.
            Exception:   IndexError
            Return:      Tier
        """
        if self.IsEmpty():
            raise IndexError("Pop from empty transcription.")
        try:
            return self.__tiers.pop(index)
        except IndexError as e:
            raise e

    # End Pop
    # ------------------------------------------------------------------


    def Remove(self, index):
        """ Remove a tier of the transcription.
            Parameters:
                - index (int): the index of the tier to remove.
            Exception:   IndexError
            Return:      None
        """
        if index >= len(self.__tiers) or index < 0:
            raise IndexError
        del self.__tiers[index]

    # End Remove
    # ------------------------------------------------------------------


    def Find(self, name, case_sensitive=True):
        """ Find a tier from its name.
            Parameters:
                - name (string) EXACT name of the tier
                - case_sensitive (bool)
            Exception:  None
            Return:     Tier
        """
        for tier in self:
            if case_sensitive:
                if tier.Name == name.strip():
                    return tier
            else:
                if tier.Name.lower() == name.strip().lower():
                    return tier
        return None

    # End Find
    # ------------------------------------------------------------------


    def __len__(self):
        return len(self.__tiers)

    def __iter__(self):
        for x in self.__tiers:
            yield x

    def __getitem__(self, i):
        return self.__tiers[i]

    # End
    # ------------------------------------------------------------------------


    def GetBegin(self):
        """ Return the smaller begin time value of all tiers.
            Return 0 if the transcription contains no tiers.
            Parameters: none
            Exception:  none
            Return:     float
        """
        if self.IsEmpty():
            return 0
        return min(tier.GetBegin() for tier in self)

    # End GetBegin
    # ------------------------------------------------------------------


    def GetEnd(self):
        """ Return the higher end time value of all tiers.
            Return 0 if the transcription contains no tiers.
            Parameters: none
            Exception:  none
            Return:     float
        """
        if self.IsEmpty():
            return 0
        return max(tier.GetEnd() for tier in self)

    # End GetEnd
    # ------------------------------------------------------------------


    def IsEmpty(self):
        """ Ask the transcription to be empty or not.
            A transcription is empty if it does not contain tiers.
            Parameters:  none
            Exception:   none
            Return:      boolean
        """
        return len(self.__tiers) == 0

    # End IsEmpty
    # ------------------------------------------------------------------


    def Copy(self):
        """ Return a copy of the transcription.
            Parameters:  none
            Exception:   none
            Return:      Transcription
        """
        import copy
        return copy.deepcopy(self)


    # End Copy
    # ------------------------------------------------------------------


    def read(self):
        name = __class__.__name__
        raise NotImplementedError("%s does not support read()." % name)

    # End read
    # ------------------------------------------------------------------


    def write(self):
        name = __class__.__name__
        raise NotImplementedError("%s does not support write()." % name)

    # End write
    # ------------------------------------------------------------------


    # ################################################################ #
    # I/O (used to debug only!)
    # ################################################################ #

    def print_trs(self,timecoeff=1):
        if self.empty()==False:
            # for each tier
            for t in range(len(self.__tiers)):
                self.__tiers[t].print_tier()
        else:
            print "Empty transcription"
