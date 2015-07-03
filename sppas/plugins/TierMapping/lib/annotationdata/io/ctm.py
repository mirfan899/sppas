#!/usr/bin/env python2
# -*- coding: UTF8 -*-
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

import re
import os.path
import codecs

from csvreader import CSVReader
from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation

# ######################################################################### #

class ScliteCTM( Transcription ):
    """ Represents a CTM Transcription.

        Included below is an example:

        ;;
        ;; Comments follow ';;'
        ;;
        ;; The Blank lines are ignored

        ;;
        7654 A 11.34 0.2 YES -6.763
        7654 A 12.00 0.34 YOU -12.384530
        7654 A 13.30 0.5 CAN 2.806418
        7654 A 17.50 0.2 AS 0.537922
        :
        7654 B 1.34 0.2 I -6.763
        7654 B 2.00 0.34 CAN -12.384530
        7654 B 3.40 0.5 ADD 2.806418
        7654 B 7.00 0.2 AS 0.537922 
    """

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """ Creates a new ScliteCTM Transcription instance.
        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)


    # ################################################################ #
    # Input
    # ################################################################ # 


    def read(self, filename, separator=' '):
        """ Read a ctm file.
            Parameters:
                - filename is the input file name
            Exception:   IOError
            Return:      None
        """
        with open(filename, "r") as f:
            reader = CSVReader(f, delimiter=separator)
            tiername = None
            prev = None
            tier = self.NewTier()

            for row in reader:
                if len(row) < 5:
                    raise IOError('Ascii.read: Unexpected entry: %r' % row)

                name, loc_s, loc_e, label = row

                if tiername is None:
                    tier.Name = name
                    tiername = name
                elif tiername != name:
                    tier = self.NewTier(name)
                    tiername = name

                time = TimeInterval(TimePoint(loc_s), TimePoint(loc_e))
                annotation = Annotation(time, Label(label))

                # Fill the temporal gap between previous annotation and
                # current annotation.
                if prev and prev.EndValue < annotation.BeginValue:
                    time = TimeInterval(TimePoint(prev.EndValue),
                                        TimePoint(annotation.BeginValue))
                    gap = Annotation(time)
                    tier.Append(gap)
                    tier.Append(annotation)
                    prev = annotation

                # if prev overlaps with annotation, merge them to one annotation.
                if prev and prev.BeginValue < annotation.EndValue\
                        and annotation.BeginValue < prev.EndValue:

                    prev.TextValue += ' ' + annotation.TextValue
                    prev.EndValue = annotation.EndValue

                else:
                    tier.Append(annotation)
                    prev = annotation

        # Create a new tier
        tier = self.NewTier()
        tiername = ""
        loc_s = 0.
        loc_e = 0.
        index = 0

        for line in fp:
            if line.strip().startswith(";;")==True:
                continue
            # Each line is a new annotation
            tab = line.split( separator )
            if len(tab) < 5:
                raise IOError('ScliteCTM.read: Unexpected entry: '+line)
            # Column 0: tier name
            name = self.__clean( tab[0] )
            if name != tiername:
                if len(tiername) > 0:
                    item = self.NewTier()
                    loc_s = 0.
                    loc_e = 0.
                    index = 0
                tier.Name = name
                tiername = name
            # Column 2: begin time ; column 3: duration; column 4: label;
            new_loc_s = float( tab[2] )
            if new_loc_s > loc_e:
                loc_s = new_loc_s
                # Add an empty interval...
                begin = TimePoint(loc_e)
                end = TimePoint(loc_s)
                interval = TimeInterval(begin, end)
                annotation = Annotation(interval)
                tier.Append(annotation)
                index = tier.GetSize() - 1

                # Add the requested interval...
                loc_e = loc_s + float( tab[3] )
                label = self.__clean( tab[4] )

                begin = TimePoint(loc_s)
                end = TimePoint(loc_e)
                interval = TimeInterval(begin, end)
                text = Label(label)
                annotation = Annotation(interval, text)
                tier.Append(annotation)
                index = tier.GetSize() - 1

            elif new_loc_s == loc_s:
                label = label + " / " + self.__clean( tab[3] )
                tier[index].TextValue = label
            else:
                # NOT IMPLEMENTED: 
                #loc_s = new_loc_s
                #loc_e = float( tab[2] )
                #new_label = self.__clean( tab[3] )
                #index = self.get_tier(item).find(loc_s,loc_e)
                #label = new_label + self.get_tier(item).get_label( index )
                #self.get_tier(item).set_ann_label( index,newlabel )
                print line.strip()+" [IGNORED]"

    # End read
    # ------------------------------------------------------------------   


    # ################################################################ #
    # Output
    # ################################################################ #

    def write(self, filename):
        """ Write a CTM file.
            Parameters:
                - filename is the output file name
            Exception:   IOError, Exception
            Return:      None
        """
        encoding='utf-8'
        with codecs.open(filename, 'w', encoding) as fp:
            # for each tier
            for tier in self:
                if tier.IsEmpty():
                    continue

                for annotation in tier:
                    fp.write( tier.Name )
                    fp.write(" A ")
                    fp.write( str(annotation.BeginValue) )
                    fp.write(" ")
                    fp.write( str(annotation.EndValue) )
                    fp.write(" ")
                    fp.write( annotation.TextValue )
                    fp.write("\n")

    # End write
    # ------------------------------------------------------------------   
