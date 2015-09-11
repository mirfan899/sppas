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
# File: syllabification.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import logging

from rules import Rules
from annotationdata.transcription import Transcription
from annotationdata.annotation import Annotation
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.label.label import Label
from annotationdata.tier import Tier

# ----------------------------------------------------------------------------

class Syllabification:
    """
    SPPAS automatic syllabification annotation.
    """

    def __init__(self, rulesfilename, logfile=None):
        """
        Create a new syllabification instance.

        Load rules from a text file, depending on the language and phonemes
        encoding. See documentation for details about this file.

        @param rulesfilename is a file with rules to syllabify.

        """
        # Load a set of initial rules from a file:
        self.load_rules(rulesfilename)

        # Create each instance:
        self.phonemes  = None
        self.syllables = None
        self.logfile   = logfile

        # Initializations
        self.vow1 = 0
        self.vow2 = 1

    # End __init__
    # ------------------------------------------------------------------


    def load_rules(self, rulesfilename):
        """
        Load the list of rules.

        @param rulesfilename is a file with rules to syllabify.

         """
        try:
            self.rules = Rules(rulesfilename)
        except Exception as e:
            raise IOError("Syll::sppasSyll. Failed in loading rules: %s\n"%str(e))


    # End load_rules
    # ------------------------------------------------------------------


    def get_syllables(self):
        """
        Return the syllables.

        @return A Transcription() with syllables

        """
        return self.syllables

    # End get_syllables
    # ------------------------------------------------------------------


    def add_syllable(self, limit):
        """
        Add a syllable to the object "syllables".

        Syllables is a list of phonemes between two limits, the one of the
        previous syllable and the one in parameter

        @param limit is the index of the last phoneme of the previous syllable

        """
        #the phoneme at the beginning of the syllable to add is the one which follow
        #the last phoneme of the previous syllable
        if self.syll.IsEmpty():
            starttime   = self.phonemes.GetBegin().GetMidpoint()
            startradius = self.phonemes.GetBegin().GetRadius()
        else:
            starttime = self.syll.GetEndValue()
            startradius = self.syll.GetEnd().GetRadius()

        #the end of the syllable is the end of the phoneme pointed by "limit"
        e = self.phonemes[limit].GetLocation().GetEnd().GetMidpoint()
        er = self.phonemes[limit].GetLocation().GetEnd().GetRadius()
        p = "" #phonemes
        c = "" #classes
        s = "" #structures

        for i in range(self.prevlimit, limit + 1):
            #print "infor%d"%i#c%
            strphone = self.phonemes[i].GetLabel().GetValue()
            #print "phon=%s\n"%strphone#c%
            strclass = self.rules.get_class( strphone )
            strtype = strclass
            if self.is_consonant(strtype):
                strtype = "C"
            p += strphone
            if strtype == "#":
                c += strphone
                s += strphone
            else:
                c += strclass
                s += strtype

        if len(p)>15:
            # MUST BE CHANGED : DO NOT RAISE AN EXCEPTION !!!!!!!!!!!!!!
            # JUST IGNORE THIS SEGMENT AND GO TO WORK FOR THE NEXT ONE !!!!!!
            raise Exception("Syll::sppasSyll. Failed when syllabifying (more than 15 phonemes in a syllable!)\n")

        time = TimeInterval(TimePoint(starttime,startradius), TimePoint(e,er))
        self.syll.Append(Annotation(time, Label(p)))

        time = TimeInterval(TimePoint(starttime,startradius), TimePoint(e,er))
        self.cls.Append(Annotation(time, Label(c)))

        time = TimeInterval(TimePoint(starttime,startradius), TimePoint(e,er))
        self.struct.Append(Annotation(time, Label(s)))

        self.prevlimit = limit + 1

    # End add_syllable
    # ------------------------------------------------------------------


    def find_next_break (self, start):
        """
        Find the index of the next vowel or silence.

        @param start is the position of the phoneme where the search will begin
        @return the position of the next vowel or break or the last phone

        """
        for i in range (start, self.phonemes.GetSize()):
            if 'error' in self.phonemes[i].GetLabel().GetValue().lower():
                self.phonemes[i].GetLabel().SetValue( '#' ) # Convert to silence
            strclass = self.rules.get_class(self.phonemes[i].GetLabel().GetValue())
            if not self.is_consonant(strclass):
                return i
        return self.phonemes.GetSize()-1

    # End find_next_break
    # ------------------------------------------------------------------


    def shift(self, limit):
        """
        Add a syllable that ends at the phoneme pointed by "limit".
        There can be a difference between the effective limit and the limit
        given in parameter if it is between two indivisible phonemes.

        @param limit is the index of the phoneme where the segmentation will take place
        @return effective limit

        """
        # if the limit is between two indivisible phonemes,
        # it will be moved except if the move reach the previous syllable
        if self.rules.get_class(self.phonemes[self.vow2].GetLabel().GetValue()) != "#" :
            _str = ""
            nb = self.vow2-self.vow1
            if nb > 1:
                if nb<5:# specific rules are sequences of 5 consonants max
                    _str = "ANY "*(5-nb) + "V "
                for i in range(1,nb):
                    _str = _str + self.phonemes[self.vow1+i].GetLabel().GetValue() + " "
            _str = _str.strip()

# version (until SPPAS-1.7.2):
#        if (self.vow2-self.vow1) > 2 and self.rules.get_class(self.phonemes[self.vow2].GetLabel().GetValue()) != "#" and self.vow2 != self.phonemes.GetSize()-1:
#            _str = ""
#             if (limit - 2) > 0 and (limit + 2) < self.phonemes.GetSize():
#                 _str = self.phonemes[limit - 2].GetLabel().GetValue()\
#                         + " " + self.phonemes[limit - 1].GetLabel().GetValue()\
#                         + " " + self.phonemes[limit].GetLabel().GetValue()\
#                         + " " + self.phonemes[limit + 1].GetLabel().GetValue()\
#                         + " " + self.phonemes[limit + 2].GetLabel().GetValue()
#             elif (limit - 1) >= 0  and (limit + 2) < self.phonemes.GetSize():
#                 _str = "ANY " + self.phonemes[limit - 1].GetLabel().GetValue()\
#                         + " " + self.phonemes[limit].GetLabel().GetValue()\
#                         + " " + self.phonemes[limit + 1].GetLabel().GetValue()\
#                         + " " + self.phonemes[limit + 2].GetLabel().GetValue()

            if len(_str)>0:
                d = self.rules.get_gap( _str )
                if d != 0:
                    if limit+d >= self.vow1 and limit+d <= self.vow2:
                        limit += d

        # Adding the syllable
        self.add_syllable( limit )

        # Beginning of the new syllable
        self.vow1 = self.vow2
        self.vow2 = self.find_next_break( self.vow1+1 )
        return limit

    # End shift
    # ------------------------------------------------------------------


    def is_consonant(self, string):
        """
        Return true if string is not a vowel nor a silence.

        """
        return string not in ("V", "W", "#")


    def analyze_breaks(self):
        """
        Deal with the cases where syllabification is systematic (##, #V, V#).
        Edit the values of global variables vow1 and vow2

        """
        vbreak = True
        while vbreak == True:
            v1 = self.rules.get_class( self.phonemes[self.vow1].GetLabel().GetValue() )
            v2 = self.rules.get_class( self.phonemes[self.vow2].GetLabel().GetValue() )

            # the last phoneme is a consonant!
            if self.is_consonant(v2) and self.vow2 == self.phonemes.GetSize()-1:
                self.shift(self.vow2)
            # vow1=V and vow2 = #
            elif v1 in ("V", "W") and v2 == "#":
                self.shift(self.vow2-1)
            # vow1=# and vow2 = V
            elif v1 == "#" and v2 in ("V", "W"):
                self.shift(self.vow1)
            # vow1=# and vow2 = #
            elif v1 == "#" and v2 == "#":
                if self.vow2 == (self.vow1+1):
                    self.shift(self.vow1)
                else:
                    #Sometimes, there can be consonants, without vowel, between two breaks
                    self.add_syllable( self.vow1)
                    self.shift(self.vow2-1)
            else:
                vbreak = False

            if self.vow1 >= self.vow2:
                vbreak = False

    # End analyze_breaks
    # ------------------------------------------------------------------


    def syllabificationVV(self):
        """
        Break down into syllables: continue until positioning itself between
        two vowels (others cases are systematics), apply the suited rule.

        """
        # Call the rules only if we are between two vowels
        self.analyze_breaks()
        if self.vow1 >= self.vow2:
            return

        # Build two strings, one for the classes and one for the phonemes
        classes = "V"
        phones  = self.phonemes[self.vow1].GetLabel().GetValue()
        for i in range(self.vow1+1, self.vow2+1):
            classes += self.rules.get_class( self.phonemes[i].GetLabel().GetValue() )
            phones  += " "+self.phonemes[i].GetLabel().GetValue()

        # Apply the rule, add the syllable
        d = self.rules.get_boundary( phones )
        if d ==-1:
            if self.logfile:
                self.logfile.print_message("No rule found for" +classes,status=3)
            else:
                sys.stderr.write("INFO: no rule found for" +classes+"\n")
            d = 0

        self.shift( self.vow1 + d)

    # End syllabificationVV
    # ------------------------------------------------------------------


    def syllabify(self, phonemes):
        """
        Syllabify (after loading the rules).

        @param phonemes (Tier) is the tier to syllabify

        """
        # Init
        self.phonemes  = phonemes
        self.syllables = None
        self.prevlimit = 0

        # Verifications: is there any data to syllabify?
        if self.phonemes.IsEmpty() is True:
            raise IOError("Syll::sppasSyll. Empty phoneme tier.\n")

        # Create output Transcription
        self.syllables = Transcription("Syllabification")
        self.syll      = self.syllables.NewTier(name="Syllables")
        self.cls       = self.syllables.NewTier(name="Classes")
        self.struct    = self.syllables.NewTier(name="Structures")

        if self.phonemes.GetSize() == 1:
            self.add_syllable(0)
            return self.syllables

        # Initialization of vow1 and vow2
        if "dummy" in self.phonemes[0].GetLabel().GetValue():
            self.vow1 = self.find_next_break(1)
            self.add_syllable(0)
            if self.vow1 == 0:
                return self.syllables
        else:
            self.vow1 = self.find_next_break(0)
        self.vow2 = self.find_next_break( self.vow1+1 )

        # Syllabification is here:
        while self.vow1 < self.vow2:
            self.syllabificationVV()

        # Add the last set of phonemes as a new syllable
        # ----------------------------------------------
        lasti = self.phonemes.GetSize() -1
        classe  = self.rules.get_class( self.phonemes[lasti].GetLabel().GetValue() )

        if self.vow2 <= lasti and ( classe in ("V", "W", "#")):
            self.add_syllable( lasti )

        return self.syllables

    # End syllabify
    # ------------------------------------------------------------------


    def syllabify2(self, phonemesTier, intervalsTier):
        """
        Syllabify inside specific intervals.

        @param phonemesTier (Tier) is the tier to syllabify
        @param intervalsTier (Tier) is the reference tier

        @return:  syllables (Tier)

        """

        if intervalsTier.IsEmpty() is True:
            raise IOError("Syll::sppasSyll. Empty interval tier.\n")

        # Quick and dirty solution to allows the "Find" method to work properly
        # on manually annotated files. We should suppose the Radius value to be
        # already fixed properly... which is never the case, because we mostly
        # read data from textgrid files!
        phonemes = phonemesTier.Copy()    # do not damage the given tier
        phonemes.SetRadius(0.005)         # 10ms vagueness seems a reasonable value
        intervals = intervalsTier.Copy()
        intervals.SetRadius(0.005)
        # consequently, all our syllables tiers will have our default radius
        # instead of the original one fixed in the phonemes tier

        # Create output Transcription
        syllables = Transcription("Syllabification")
        syll      = syllables.NewTier(name="Syllables-seg")
        cls       = syllables.NewTier(name="Classes-seg")
        struct    = syllables.NewTier(name="Structures-seg")

        # Extract phonemes between start and end for each interval
        for interval in intervals:
            start = interval.GetLocation().GetBegin()
            end   = interval.GetLocation().GetEnd()
            phons = phonemes.Find(start, end, overlaps=False)

            if not phons or not len(phons):
                continue

            phon_tier = Tier()
            for phon in phons:
                phon_tier.Append(phon)

            # Debordement !
            if not syllables.IsEmpty() and syllables.GetEnd() > phon_tier.GetBeginValue():
                phon_tier.Pop(0)

            try:
                trs_syll = self.syllabify(phon_tier)
                syllable = trs_syll.Find("Syllables")
                classes  = trs_syll.Find("Classes")
                structs  = trs_syll.Find("Structures")

                for s, c, st in zip(syllable, classes, structs):
                    syll.Append(s)
                    cls.Append(c)
                    struct.Append(st)
            except Exception:
                pass # if overlaps

        return syllables

    # End syllabify2
    # ------------------------------------------------------------------
