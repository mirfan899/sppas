#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
#
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

# First implementation of INTSINT.
# UN-USED.


import os
import sys
import getopt
import math

from annotationdata.tier import Tier
from annotationdata.annotation import Annotation
from annotationdata.label.label import Label
from annotationdata.ptime.point import TimePoint
import momelutil


class Tone:
    """ A tone is represented by a label, 2 regressions coefficients and some statistics.
    """
    # ##################################################################### #
    # Constructor
    # ##################################################################### #
    def __init__(self,label):
        """ Create a Tone instance.
        """
        self.label = label
        self.a = 0
        self.b = 0
        # Statistics
        self.init_stats()

    def init_stats(self):
        """ Initialize all values.
        """
        self.sx  = 0.0
        self.sy  = 0.0
        self.sxy = 0.0
        self.sx2 = 0.0
        self.n   = 0


class Intsint:
    """ Provide optimal INTSINT coding for sequence of target points.
    """
    # ##################################################################### #
    # Constructor
    # ##################################################################### #
    def __init__(self, tier):
        """ Create an Intsint instance.
            Parameters:
                - tier contains a set of target points, with the corresponding f0 value.
            Return a tier with Insint coding.
            Exception if input tier is not a valid tier.
        """
        # Target points, with f0 values as labels.

        self.tierhz = tier
        _s = self.tierhz.GetSize()
        if _s < 2:
            raise BaseException('Intsint error. There is not enough targets.')

        # Set tones
        # ##############################################################
        # List of "absolute" tones
        self.toneabslist = [ 'T', 'M', 'B' ]
        # List of "relative" tones
        self.tonerellist = [ 'H', 'L', 'U', 'D', 'S' ]
        # All tones
        self.tonelist = self.toneabslist + self.tonerellist
        # Values associated to each tones: a, b and stats
        self.tones = {}
        for t in self.tonelist:
            self.tones[t] = Tone(t)
        # ##############################################################

        # Set i_min and i_max (indexes of min and max f0 values)
        self.set_f0()

        # Minimum duration between 2 values (miliseconds)
        self.min_pause = 500


    def run(self):
        """ Intsint is here.
        """
        return self.set_recode_intsint( self.set_initials_intsint() )


    # Useful getters and setters
    # ##################################################################

    def get_hz(self,i):
        return float( self.tierhz[i].GetLabel().GetValue() )
    def get_time(self,i):
        return float( self.tierhz[i].GetLocation().GetPointMidpoint() )

    def set_f0(self):
        """ set i_min and i_max.
        """
        _min  = 0.0
        _max  = 0.0
        self.i_max = 0
        self.i_min = 0
        try:
            _min  = self.get_hz(0)
            _max  = self.get_hz(0)
            for i in range( 1,self.tierhz.GetSize() ):
                _f0 = self.get_hz(i)
                if _f0 > _max:
                    _max = _f0
                    self.i_max = i
                if _f0 < _min:
                    _min = _f0
                    self.i_min = i
        except Exception:
            raise BaseException("intsint.set_f0(): Error in tier: "+self.tierhz.GetName())

    # ##################################################################

    def set_initials_intsint(self):
        # Create the tier without labels
        # Create points at the same time values than tierhz
        tierci = Tier( name="Intsint" )
        for i in range( self.tierhz.GetSize() ):
            tierci.Append( Annotation(TimePoint(self.get_time(i)) ) )

        # coefficient for tone 'S' initialised
        # to identity with preceding target
        self.tones['S'].a = 1

        # initial coding

        # targets between first and last coded:
        #   S if identical to preceding valley
        #   H for peak
        #   L for valley
        #   U in rising sequence
        #   D in falling sequence
        for i in range( 1,self.tierhz.GetSize()-1 ):
            # Prev. f0 value, in Hz
            targp = self.get_hz(i-1)
            # Current f0 value, in Hz
            targc = self.get_hz(i)
            # Next f0 value, in Hz
            targf = self.get_hz(i+1)
            # Targets are compared in an acceptable treshold.
            if ( momelutil.compare(targc , targp) == 0):
                tierci[i].GetLabel().SetValue( 'S' )
            else:
                if targc > targp:
                    if targc > targf:
                        # Current is higher than both prec and next
                        tierci[i].GetLabel().SetValue( 'H' )
                    else:
                        # Current is higher than prec but lower than next
                        tierci[i].GetLabel().SetValue( 'U' )
                else:
                    if targc > targf:
                        # Current is lower than prec and higher than next
                        tierci[i].GetLabel().SetValue( 'D' )
                    else:
                        # Current is lower than both prec and next
                        tierci[i].GetLabel().SetValue( 'L' )

        # initial target coded 'M'
        #   final target coded 'S', 'L' or 'H'
        tierci[0] = 'M'
        # the penultimate f0 target, in Hz
        targpp = self.get_hz( self.tierhz.GetSize()-2 )
        # the last f0 target, in Hz
        targp  = self.get_hz( self.tierhz.GetSize()-1 )
        c = momelutil.compare( targpp,targp )
        if c==0:
           tierci[-1].GetLabel().SetValue( 'S' )
        elif c==1:
           tierci[-1].GetLabel().SetValue( 'L' )
        else:
           tierci[-1].GetLabel().SetValue( 'H' )

        return tierci


    def set_recode_intsint(self, tierci):
        # Create the tier with targets
        self.tiercf = tierci

        # Highest target recoded 'T'
        self.tiercf[self.i_max].GetLabel().SetValue( 'T' )
        # Lowest target recoded 'B'
        self.tiercf[self.i_min].GetLabel().SetValue( 'B' )

        nchange = 2
        while (nchange > 0):

            nchange = 0

            # calculate means and regression coefficients
            # ###########################################

            # Set all stats to 0.
            for j in self.tonelist:
                self.tones[j].init_stats()

            # initial targets

            j = self.tiercf[0].GetLabel().GetValue()
            self.tones[j].sy = self.get_hz(0)
            self.tones[j].n += 1

            # intermediate targets

            for i in range (1,self.tiercf.GetSize()):
                j = self.tiercf[i].GetLabel().GetValue()
                self.tones[j].sx  += self.get_hz( i-1 )
                self.tones[j].sy  += self.get_hz( i )
                self.tones[j].sxy += self.get_hz( i ) * self.get_hz( i-1 )
                self.tones[j].sx2 += ( ( self.get_hz( i-1 ) ) * ( self.get_hz( i-1 ) ) )
                self.tones[j].n   += 1

            # calculate coefficients

            # - absolute tones
            #  mean value by tone
            for j in self.toneabslist:
                if self.tones[j].n != 0:
                    self.tones[j].a = 0.0
                    self.tones[j].b = self.tones[j].sy / self.tones[j].n

            # - relative tones
            #  linear regression by tone on preceding target - ratio
            #  to preceding target if only one case
            for j in self.tonerellist:
                if self.tones[j].n == 1:
                    self.tones[j].a = self.tones[j].sy / self.tones[j].sx
                elif self.tones[j].n > 1:
                    self.tones[j].a = (self.tones[j].sxy - self.tones[j].sx * self.tones[j].sy / self.tones[j].n) / (self.tones[j].sx2 - self.tones[j].sx * self.tones[j].sx / self.tones[j].n)
                    self.tones[j].b = self.tones[j].sy / self.tones[j].n - self.tones[j].a * self.tones[j].sx / self.tones[j].n

            # recoding */

            # H & L can be recoded as T and B, or U and D
            #  respectively if closer to respective mean than
            #  to predicted value by regression.
            for i in range(1,self.tierhz.GetSize()):
                if self.tiercf[i].GetLabel().GetValue() == 'H':
                    if( self.recode(i, 'T') ):
                        nchange += 1
                        self.tiercf[i].GetLabel().SetValue( 'T' )
                    elif self.recode(i, 'U'):
                        nchange += 1
                        self.tiercf[i].GetLabel().SetValue( 'U' )
                elif self.tiercf[i].GetLabel().GetValue() == 'L':
                    if self.recode(i, 'B'):
                        nchange += 1
                        self.tiercf[i].GetLabel().SetValue( 'B' )
                elif self.recode(i, 'D'):
                    nchange += 1
                    self.tiercf[i].GetLabel().SetValue( 'D' )

            # si ecart temporel > minimal pause duration,
            # recodage possible en 'M'
            if (self.get_time(i) - self.get_time(i-1)) > self.min_pause:
                if self.recode(i, 'M'):
                    nchange += 1
                    self.tiercf[i].GetLabel().SetValue( 'M' )

            return self.tiercf


    def recode(self, i_target_c, try_tone ):
        """ Recode.
            Parameters:
                - i_target_c : index of target to be eventually recoded
                - try_tone   : name of the new tone to try
            Return si erreur nouveau  codage < ancien retourne 1 ( recoding is necessary )
        """
        # Prec. target f0, in Hz
        targp = self.get_hz(i_target_c - 1)
        # Current target f0, in Hz
        targc = self.get_hz(i_target_c)

        tone1 = self.tiercf[i_target_c].GetLabel().GetValue()
        tone2 = try_tone
        targest1 = targp * self.tones[tone1].a + self.tones[tone1].b
        targest2 = targp * self.tones[tone2].a + self.tones[tone2].b
        return (  math.fabs(targest1-targc) > math.fabs(targest2-targc)  )

