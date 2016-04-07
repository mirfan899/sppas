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
# File: phonunk.py
# ----------------------------------------------------------------------------

import re

from dagphon import DAGPhon
import resources.rutils as rutils

# ---------------------------------------------------------------------------
# Class PhonUnk
# ---------------------------------------------------------------------------

class PhonUnk:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Perform a G2P conversion for unknown entries.

    Phonetization, also called grapheme-phoneme conversion, is the process of
    representing sounds with phonetic signs. This class implements a
    language-independent algorithm to phonetize unknown words.
    Our system is based on the idea that given enough examples it should be
    possible to predict the pronunciation of unseen words purely by analogy.

    At this stage, it consists in exploring the unknown word from left to
    right and to find the longest strings in the dictionary.
    Since this algorithm uses the dictionary, the quality of
    such a phonetization will depend on this resource.

    For details, see the following reference:

        > Brigitte Bigi (2013).
        > A phonetization approach for the forced-alignment task,
        > 3rd Less-Resourced Languages workshop, 6th Language & Technology
        > Conference, Poznan (Poland).

    """
    def __init__(self, prondict):
        """
        Constructor.

        @param prondict (dict) with a set of couples:
            token=key, phonetization=value.

        >>> d = { 'a':'a|aa', 'b':'b', 'c':'c|cc', 'abb':'abb', 'bac':'bac' }
        >>> p = PhonUnk(d)
        """
        self.prondict = prondict
        self.dagphon = DAGPhon(variants=4)

    # ------------------------------------------------------------------
    # Getters and Setters
    # ------------------------------------------------------------------

    def set_variants(self, v):
        """
        Fix the maximum number of variants.

        @param v (int) If v is set to 0, all variants will be returned.

        """
        if v<0 or v>20:
            raise ValueError('Unexpected value for the number of variants.')
        self.dagphon.variants = v

    # -----------------------------------------------------------------------

    def get_phon(self,entry):
        """
        Return the phonetization of an unknown entry.

        @param entry is the string to phonetize
        @return a string with the proposed phonetization
        @raise Exception if the word can NOT be phonetized

        """
        __str = rutils.ToStrip( entry )
        __str = rutils.ToLower( __str )
        if len(__str) == 0:
            return ""

        #__str = re.sub("[\s]+", " ", entry)
        __str = re.sub("-$", "", __str)  # rustine
        __str = re.sub("'$", "", __str)  # rustine

        # Find all pronunciations of segments with a longest matching algo.
        # if entry contains separators:
        #  1. phonetize each part independently and
        #  2. separate segments with a space.
        __tabstr = re.split(u"[-'_\s]",__str)
        pronlr = ""
        for s in __tabstr:
            pronlr = pronlr + " " + self.__recurslr(s)
        pronrl = ""
        for s in __tabstr:
            pronrl = pronrl + " " + self.__recursrl(s)

        # Create the output
        pron = self.dagphon.decompose( pronlr.strip(), pronrl.strip() )

        if len(pron.strip())>0:
            return pron

        raise Exception('Unable to phonetize the unknown token: '+entry)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __longestlr(self,entry):
        """
        Select the longest phonetization of an entry, from the end.
        """
        i = len(entry)
        while (i>0):
            # Find in the dictionary a substring from 0 to i
            if self.prondict.has_key( entry[:i] ):
                # Return index for the longest string
                return i
            i = i-1

        # Did not find any pronunciation for this entry!
        return 0

    # -----------------------------------------------------------------------

    def __recurslr(self,str):
        """
        Recursive method to find a phonetization of a supposed unknown entry.
        Return a string with the proposed phonetization.
        Spaces separate segments.
        """
        if len(str) == 0:
            return ""

        # LEFT:
        # ###########
        # Find the index of the longest left string that can be phonetized
        leftindex = self.__longestlr(str)
        # Nothing can be phonetized at the left part!
        if leftindex == 0:
            _phonleft = ""
            leftindex = 1
            left = ""
        else:
            # left is from the first to the leftindex character in str
            left = str[:leftindex]
            # Phonetize
            if not self.prondict.has_key( left ):
                _phonleft = ""
            else:
                _phonleft = self.prondict.get( left )
            # The entire entry can be phonetized (nothing to do at right)
            ##if left == len(str):
            if leftindex == len(str):
                return _phonleft

        # RIGHT:
        # ###########
        right = str[leftindex:len(str)]
        if len(right) == 0:
            return _phonleft
        if self.prondict.has_key( right ):
            _phonright = self.prondict.get( right )
        else:
            # If right part of the entry is unknown...
            # Use recursivity to phonetize
            _phonright = self.__recurslr(right)

        if len(_phonleft)>0 and len(_phonright)>0:
            return _phonleft+" "+_phonright

        return _phonright

    # -----------------------------------------------------------------------

    def __longestrl(self,entry):
        """
        Select the longest phonetization of an entry, from the start.
        """
        i = 0
        while (i<len(entry)):
            # Find in the dictionary a substring from i to the entry-length
            if self.prondict.has_key( entry[i:] ):
                # Return index for the longest string
                return i
            i = i+1

        # Did not find any pronunciation for this entry!
        return len(entry)

    # -----------------------------------------------------------------------

    def __recursrl(self,str):
        """
        Recursive method to find a phonetization of a supposed unknown entry.
        Return a string with the proposed phonetization.
        Spaces separate segments.
        """
        if len(str) == 0:
            return ""

        # RIGHT:
        # ###########
        # Find the index of the longest right string that can be phonetized
        rightindex = self.__longestrl(str)
        # Nothing can be phonetized at the right part!
        if rightindex == len(str):
            _phonright = ""
            rightindex = len(str)-1
            right = ""
        else:
            # right is from the end to the rightindex character in str
            right = str[rightindex:]
            # Phonetize
            if not self.prondict.has_key( right ):
                _phonright = ""
            else:
                _phonright = self.prondict.get( right )
            # The entire entry can be phonetized (nothing to do at left)
            if rightindex == 0:
                return _phonright

        # LEFT:
        # ###########
        left = str[0:rightindex]
        if len(left) == 0:
            return _phonright
        if self.prondict.has_key( left ):
            _phonleft = self.prondict.get( left )
        else:
            # If left part of the entry is unknown...
            # Use recursivity to phonetize
            _phonleft = self.__recursrl( left )

        if len(_phonleft)>0 and len(_phonright)>0:
            return _phonleft+" "+_phonright

        return _phonleft

# ----------------------------------------------------------------------
