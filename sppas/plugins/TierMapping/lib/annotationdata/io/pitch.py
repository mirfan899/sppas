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


from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation
from annotationdata.tier import Tier


# ######################################################################### #

class Pitch( Transcription ):
    """ Represents a Transcription with pitch values.
    """

    def __init__(self, name="Pitch", coeff=1, delta=0.01, mintime=None, maxtime=None):
        """ Creates a new Pitch Tier instance.
        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)
        self.__delta  = delta
        self.__tier = Tier()

    # End __init__
    # ------------------------------------------------------------------    

    def Set(self, trs, name="empty"):
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

    # End Set
    # ------------------------------------------------------------------    

    def set_delta(self,delta):
        self.__delta = delta

    def get_delta(self):
        return self.__delta


    # ################################################################ #
    # Input
    # ################################################################ #

    def read(self, inputfilename):
        """ Read a PitchTier file (from file.hz or file.PitchTier).
        """
        if inputfilename.lower().endswith(".hz"):
            self.read_hz( inputfilename )
        elif inputfilename.lower().endswith(".pitchtier"):
            self.read_pitchtier( inputfilename )

    # End read
    # ------------------------------------------------------------------


    def read_pitchtier(self, filename):
        """ Read a PitchTier file (from Praat).
            Parameters:
                - filename is the input file name
            Exception:   IOError
            Return:      none
        """
        self.__delta = 0.
        with open(filename, "r") as fp:
            # Ignore Header
            for i in range(4):
                fp.readline()

            line = ""
            loc_s = -1.0
            loc_e = -1.0

            # Load each annotation of THE ONLY tier
            line = ""
            loc_s = -1.0
            tier = self.NewTier("Pitch")
            for line in fp:
                if line.find("number = ") > -1 or line.find("time = ") > -1:
                    # Time location of a new annotation
                    line = line.replace( "number = ", "" )
                    line = line.replace( "time = ", "" )
                    loc_s = float( line )
                elif line.find("value = ")>-1:
                    # Label (=value)
                    line = line.replace("value = ", "")
                    line = line.strip()
                    if( len(line)==0 ):
                        line = "0"
                    # Create the annotation and add to the tier
                    tier.Append(Annotation(TimePoint(loc_s), Label(line)))
                    # Initializations for the next annotation
                    loc_s = -1.0
            self.__tier = tier

    # End read_pitchtier
    # ------------------------------------------------------------------


    def read_hz(self, filename, delta=0.01):
        """ Read pitch values from an ascii file (one column) and set a value each 'delta' ms.
            Parameters:
                - filename is the input file name
            Exception:   IOError, Exception
            Return:      none
        """
        self.__delta = delta
        with open(filename,"r") as pitchfile:
            tier = self.NewTier("Pitch")
            self.__delta   = delta
            self.__tier = tier
            # The reference time point of each interval is the middle
            timeref = delta/2. # Start time
            for line in pitchfile:
                tier.Append(Annotation(TimePoint(timeref), Label(line)))
                timeref = timeref + delta

    # End read_hz
    # ------------------------------------------------------------------


    # ################################################################ #
    # Getters and Setters
    # ################################################################ #

    def set_pitch(self, values, delta):
        """ Create the pitch tier from a vector of pitch values.
            Parameters:
                - values is an array with pitch values
                - delta is the delta time between 2 values
            Exception:   Exception
            Return:      none
        """
        if len(values)==0:
            raise Exception("Trs::trsiopitch. Empty array values")

        tier = self.NewTier("Pitch")
        self.__delta   = delta
        # The reference time point of each interval is the middle
        timeref = delta/2.
        for v in values:
            tier.Append(Annotation(TimePoint(timeref), Label(str(v))))
            timeref = timeref + delta

        self.__tier = tier

    # End set_pitch
    # ------------------------------------------------------------------

    def __add_points_affine(self,array,delta,time1,pitch1,time2,pitch2):
        """ add_points_affine (NOT USED)
            Definition:
            On appelle fonction affine la relation qui,
            à tout nombre x, associe le nombre y tel que :
            y = mx + p
            Une fonction affine est definie par son coefficient
            m et le nombre p.
            Pour une fonction affine donnee, l’accroissement des images
            (c’est-à-dire la difference entre deux images) est
            proportionnel à l’accroissement des antecedents correspondants
            suivant le coefficient m.
            Par consequent, il suffit de connaître les images y1 et y2
            de deux nombres x1 et x2 par une fonction affine pour
            pouvoir determiner la valeur du coefficient m :
            m =  y2 − y1 / x2 − x1  
            On peut ensuite en deduire la valeur de p, et donc
            l’expression generale de la fonction affine.
        """
        # Timesep is rounded to milliseconds
        timesep = round(time2-time1,3)
        # A too long time between 2 values. Pitch is set to zero.
        if timesep > 0.02:
            m = 0
            p = 0
        else:
            # affine function parameters
            m = (pitch2-pitch1) / timesep
            p = pitch1 - (m * time1)
        # number of values to add in the time interval
        steps = int(timesep/delta)
        # then, add values:
        for step in range(1,steps):
            if steps>3:
                x = (step*delta) + time1
                y = (m * x) + p
            else:
                y = 0.
            array.append( y )


    def __add_points_linear(self,array,delta,time1,pitch,time2):
        """ Add_points linear.
        """
        # Timesep is rounded to milliseconds
        timesep = round(time2-time1,3)
        # A too long time between 2 values. Pitch is set to zero.
        if timesep > 0.02:
            p = 0
        else:
            p = pitch
        # number of values to add in the time interval
        steps = int(timesep/delta)
        # then, add values:
        for step in range(1,steps):
            array.append( p )


    def get_pitch_list(self, delta=0.01):
        """ Return a list of pitch values from the pitch tier.
            Parameters: 
                - delta
            Exception:   if empty tier!
            Return:      a list
        """
        pitch = []
        # Get the number of pitch values of the tier
        if self.__tier.IsEmpty():
            raise Exception("Empty pitch transcription.")
        nb = self.__tier.GetSize()

        # From time=0 to the first pitch value, pitch is 0.
        time1  = float(self.__tier[0].PointValue)
        pitch1 = float(self.__tier[0].TextValue)
        steps = int(time1/delta) - 1
        for step in range(steps):
            pitch.append(0)

        for annotation in self.__tier[1:]:
            time2  = annotation.PointValue
            pitch2 = float(annotation.TextValue)
            pitch.append(pitch1)
            self.__add_points_affine(pitch, delta, time1,pitch1, time2,pitch2)
            time1  = time2
            pitch1 = pitch2
        pitch.append(pitch2)

        return pitch

    # End get_pitchlist
    # ------------------------------------------------------------------


    # ################################################################ #
    # Output
    # ################################################################ #


    def write(self, filename):
        """ Write a PitchTier file or .hz file.
        """
        if filename.lower().endswith(".hz"):
            self.write_hz(filename)
        elif filename.lower().endswith(".pitchtier"):
            self.write_pitchtier(filename)

    # End read
    # ------------------------------------------------------------------

    def write_pitchtier(self, filename):
        """ Write a PitchTier file.
            Parameters:
                - filename is the output file name
            Exception:   none
            Return:      none
        """
        if self.IsEmpty() and self.__tier.IsEmpty():
            raise IOError('pitch.py. Writing error: empty pitch tier.\n')

        with open(filename, "w") as fp:
            # Header
            fp.write( "File type = \"ooTextFile\"\n" )
            fp.write( "Object class = \"PitchTier\"\n\n" )
            fp.write( "xmin = " + str(self.__tier.GetBegin()) + "\n" )
            fp.write( "xmax = " + str(self.__tier.GetEnd()) + "\n" )
            fp.write( "points: size = " + str(self.__tier.GetSize()) + "\n" )

            for i, annotation in enumerate(self.__tier, 1):
                fp.write( "points [%d]:\n" % i)
                fp.write( "    number = %s\n" % annotation.PointValue)
                fp.write( "    value = %s\n" % annotation.TextValue)

    # End write_pitchtier
    # ------------------------------------------------------------------


    def write_hz( self, filename ):
        """ Write a .hz file.
            Parameters:
                - filename is the output file name
                - values is the list of pitch values to write
            Exception:   none
            Return:      none
        """
        if self.IsEmpty() or self.__tier.IsEmpty():
            raise IOError('Writing error: empty pitch tier.\n')

        with open(filename, "w") as fp:
            __pitcharray = self.get_pitch_list()
            for i in range( len(__pitcharray)):
                fp.write("%.4f\n"%__pitcharray[i])
