#!/usr/bin/env python2
# -*- coding: iso-8859-15 -*-
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

import codecs

from annotationdata.transcription import Transcription
from annotationdata.tier import Tier
from annotationdata.label.label import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation

# ######################################################################### #

class Intensity(Transcription):
    """ Represents an Intensity Tier Transcription.
        Intensity (like TextGrid) is the native file format of the 
        GPL tool Praat: Doing phonetic with computers.
    """

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """ Creates a new Intensity Transcription instance.
        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)
        self.__tier = Tier()

    # End __init__
    # ------------------------------------------------------------------    


    def Set(self, trs):
        """ Set a transcription.
            Parameters:
                - trs (Transcription)
            Exception:  None
            Return:     time value
        """
        if isinstance(trs, Transcription) is False:
            raise TypeError("Transcription argument required, not %s" % trs)
        if trs.IsEmpty():
            self.__tiers = []
            self.__tier = Tier()
        else:
            tiers = [tier.Copy() for tier in trs]
            self.__tiers = tiers
            self.__tier = self.__tiers[0]


    # ################################################################ #
    # Input
    # ################################################################ #

    def read_intensity(self, filename):
        """ Read a short Intensity file.
            Parameters:
                - filename is the input file name
            Exception:   IOError
            Return:      none
        """
        try:
            fp = open(filename, "r")
        except Exception, e:
            raise e
        # TODO

    # End read_intensity
    # ------------------------------------------------------------------


    def read_intensitytier(self, filename):
        """ Read a IntensityTier file (TODO).
            Parameters:
                - filename is the input file name
            Exception:   IOError
            Return:      none
        """
        try:
            fp = open(filename, "r")
        except Exception, e:
            raise e
 
        # Ignore Header
        for i in range(8):
            fp.readline()
        # TODO

    # End read_intensitytier
    # ------------------------------------------------------------------


    def read(self, filename):
        """ Read a Intensity or IntensityTier file.
            Parameters:
                - filename is the input file name
            Exception:   IOError, Exception
            Return:      none
        """
        # Verify if the file exists
        try:
            fp = open(filename, "r")
        except IOError, e:
            raise e

        # Verify if the file is really a praat one!
        buffer = fp.readlines()
        fp.close()
        s = str(buffer)
        if (s.lower().find("intensity") == -1 ):
            raise IOError('Intensity.read: This is not an intensity file: '+filename)

        # A long textgrid contains points
        if (s.find("points [") > -1):
            self.read_intensitytier(filename)
        else:
            self.read_intensity(filename)

    # End read
    # ------------------------------------------------------------------


    # ################################################################ #
    # Output
    # ################################################################ #

    def write(self, filename):
        """ Write an IntensityTier file.
            Parameters:
                - filename is the output file name
            Exception:   none
            Return:      none
        """
        if self.IsEmpty():
            raise IOError("empty transcription.")

        with codecs.open(filename, "w") as fp:
            # Header
            fp.write( "File type = \"ooTextFile\"\n" )
            fp.write( "Object class = \"IntensityTier\"\n\n" )
            fp.write( "xmin = " + str(self.__tier.GetBegin()) + "\n" )
            fp.write( "xmax = " + str(self.__tier.GetEnd()) + "\n" )
            fp.write( "points: size = " + str(self.__tier.GetSize()) + "\n" )

            # For each annotation in this tier
            for i, annotation in enumerate(self.__tier, 1):
                fp.write( "points [%d]:\n" % i)
                fp.write( "    number = %s\n" % annotation.PointValue)
                fp.write( "    value = %s\n" % annotation.TextValue)

    # End write
    # ------------------------------------------------------------------   


    # ################################################################ #
    # Others...
    # ################################################################ # 

    def set_intensity(self, values, delta):
        """ Create an intensity tier from intensity values.
            Parameters:
                - values is an array with intensity values
                - delta is the delta time between 2 values
            Exception:   ValueError
            Return:      none
        """
        if len(values)==0:
            raise ValueError("Intensity.set_intensity: Empty array values")

        tier = self.NewTier()
        number = 0
        for v in range(values):
            tier.Append(Annotation(TimePoint(number), Label(str(v))))
            number = number + delta

        self.__tier = tier

    # End set_intensity
    # ------------------------------------------------------------------   
