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

import codecs

from utils import merge_overlapping_annotations
from utils import fill_gaps
from csvreader import CSVReader
from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation


class Ascii(Transcription):
    """ Represents an ascii Transcription input/output.

        For example, a TXT Transcription is represented
        as a 4 columns file:
            - 1st column is the tier name; 
            - 2nd column is the begin time;
            - 3rd column is the end time; 
            - 4th column is the label.
        Columns are separated by commas.
    """

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """ Creates a new Ascii Transcription instance.
        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)


    # ################################################################ #
    # Input
    # ################################################################ # 


    def read(self, filename, separator=';'):
        """ Read an ascii file.
            Interval are supposed to be time-continued.
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
                if len(row) != 4:
                    raise IOError('Ascii.read: Unexpected entry: %r' % row)

                name, loc_s, loc_e, label = row

                if tiername is None:
                    tier.Name = name
                    tiername = name
                elif tiername != name:
                    tier = self.NewTier(name)
                    tiername = name
                    prev = None

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
                elif prev and prev.BeginValue < annotation.EndValue\
                        and annotation.BeginValue < prev.EndValue:

                    prev.TextValue += ' ' + annotation.TextValue
                    prev.EndValue = annotation.EndValue

                else:
                    tier.Append(annotation)
                    prev = annotation

    # End read
    # ------------------------------------------------------------------   


    # ################################################################ #
    # Output
    # ################################################################ #


    def write(self, filename):
        if filename.lower().endswith(".txt"):
            self.writetxt(filename)
        elif filename.lower().endswith(".csv"):
            self.writecsv(filename)
        elif filename.lower().endswith(".info"):
            self.writeinfo(filename)
        elif filename.lower().endswith(".lab"):
            self.writelab(filename)
        elif filename.lower().endswith(".ipulab"):
            self.writeipulab(filename)
        elif filename.lower().endswith(".liatxt"):
            self.writeliatxt(filename)
        else:
            raise IOError("Unknown file format %s: " % filename)

    # End write
    # ------------------------------------------------------------------   


    def writetxt(self, filename):
        """ Write an ascii file, as txt file.
            Parameters:
                - filename is the output file name
            Exception:   IOError, Exception
            Return:      None
        """
        encoding='utf-8'
        with codecs.open(filename, 'w', encoding) as fp:
            for tier in self:
                if tier.IsEmpty():
                    continue

                if tier.IsInterval():
                    tier = fill_gaps(tier)
                    tier = merge_overlapping_annotations(tier)

                for annotation in tier:
                    fp.write( tier.Name )
                    fp.write(" ; ")
                    if annotation.IsInterval():
                        fp.write( str( annotation.BeginValue ) )
                        fp.write(" ; ")
                        fp.write( str( annotation.EndValue ) )
                    else:
                        fp.write( str( annotation.PointValue ) )
                        fp.write(" ; ")
                    fp.write(" ; ")
                    fp.write( annotation.TextValue )
                    fp.write("\n")

    # End writetxt
    # ------------------------------------------------------------------   


    def writecsv(self,filename):
        """ Write an ascii file, as csv file.
            Parameters:
                - filename is the output file name
            Exception:   IOError, Exception
            Return:      None
        """
        encoding='utf-8'
        with codecs.open(filename, 'w', encoding) as fp:
            for tier in self:
                if tier.IsEmpty():
                    continue

                if tier.IsInterval():
                    tier = fill_gaps(tier)
                    tier = merge_overlapping_annotations(tier)

                for annotation in tier:
                    fp.write(' "')
                    fp.write( tier.Name )
                    fp.write('";"')
                    if annotation.IsInterval():
                        fp.write( str( annotation.BeginValue ) )
                        fp.write('";"')
                        fp.write( str( annotation.EndValue ) )
                    else:
                        fp.write( str( annotation.PointValue ) )
                        fp.write('";"')
                    fp.write('";"')
                    fp.write( annotation.TextValue )
                    fp.write('"\n')

    # End writecsv
    # ------------------------------------------------------------------   


    def writelab(self, filename):
        """ Write an HTK lab file.

            Time is represented as 100ns.
            Lab files are used to create MLF files; they use the following
            specifications:
            [start1 [end1]] label1 [score] {auxlabel [auxscore]} [comment]
            where:
                - [.] are optionals (0 or 1)
                - {.} possible repetitions (1,2,3...)
            Parameters:  
                - filename is the output file name
            Exception:   IOError, Exception
            Return:      None
        """
        encoding='utf-8'
        with codecs.open(filename, 'w', encoding) as fp:
            for tier in self:
                if tier.IsEmpty():
                    continue
                if tier.IsInterval():
                    tier = fill_gaps(tier)
                    tier = merge_overlapping_annotations(tier)

                for annotation in tier:
                    if annotation.IsPoint():
                        __p = int(annotation.PointValue * 10000000)
                        fp.write(str(__p))
                        fp.write(" ")
                    else:
                        __s = int(annotation.BeginValue * 10000000)
                        __e = int(annotation.EndValue * 10000000)
                        if annotation.IsLabel():
                            labstr = annotation.TextValue.strip()
                            labstr = labstr.replace('.', ' ')
                            tablab = labstr.split()
                            if len(tablab) < 2:
                                fp.write(str( __s )+" ")
                                fp.write(str( __e )+" ")
                                fp.write(annotation.TextValue + "\n")
                            else:
                                fp.write(str( __s )+" ")
                                for label in tablab:
                                    fp.write(label + "\n")
                        else:
                            fp.write(str( __s )+" ")
                            fp.write(str( __e )+" sil\n")

    # End writelab
    # ------------------------------------------------------------------   


    def writeipulab(self, filename):
        """ Write an HTK lab file, segmented by IPUs.

            Time is represented as 100ns.
            Lab files are used to create MLF files; they use the following
            specifications:
            [start1 [end1]] label1 [score] {auxlabel [auxscore]} [comment]
            where:
                - [.] are optionals (0 or 1)
                - {.} possible repetitions (1,2,3...)
            Parameters:  
                - filename is the output file name
            Exception:   IOError, Exception
            Return:      None
        """
        inipu = False
        encoding='utf-8'
        with codecs.open(filename, 'w', encoding) as fp:
            for tier in self:
                if tier.IsEmpty():
                    continue
                if tier.IsInterval():
                    tier = fill_gaps(tier)
                    tier = merge_overlapping_annotations(tier)

                for annotation in tier:
                    if annotation.IsPoint():
                        __p = int(annotation.PointValue * 10000000)
                        fp.write(str(__p))
                        fp.write(" ")
                    else:
                        __s = int(annotation.BeginValue * 10000000)
                        __e = int(annotation.EndValue * 10000000)
                        if annotation.IsLabel():
                            labstr = annotation.TextValue.strip()
                            labstr = labstr.replace('.', ' ')
                            tablab = labstr.split()
                            if inipu == True:
                                for label in tablab:
                                    fp.write(label + "\n")
                            else:
                                if len(tablab) < 2:
                                    fp.write(str( __s )+" ")
                                    #fp.write(str( __e )+" ")
                                    fp.write(annotation.TextValue + "\n")
                                else:
                                    fp.write(str( __s )+" ")
                                    for label in tablab:
                                        fp.write(label + "\n")
                            inipu = True
                        else:
                            fp.write(str( __s )+" ")
                            fp.write(str( __e )+" sil\n")
                            inipu = False

    # End writeipulab
    # ------------------------------------------------------------------   


    def writeinfo(self, filename, t=0):
        """ Write an ascii file, with one tier of the Transcription.

            An info file is a 5 columns file:
            begin_time end_time middle_time number duration
            Parameters:
                - filename is the output file name
                - t is the tier number
            Exception:   IOError, Exception
            Return:      None
        """
        encoding='utf-8'
        with codecs.open(filename, 'w', encoding) as fp:

            tier = self[t]
            if tier.IsEmpty():
                fp.close()
                return

            if tier.IsInterval():
                tier = fill_gaps(tier)
                tier = merge_overlapping_annotations(tier)


            for annotation in tier:
                if annotation.IsInterval():
                    fp.write( str( annotation.BeginValue ) )
                    fp.write(" ")
                    fp.write( str( annotation.EndValue ) )
                    fp.write(" ")
                    duration = annotation.EndValue - annotation.BeginValue
                    middle = annotation.BeginValue + ( duration / 2.0 )
                    fp.write(str(middle))
                    fp.write(" ")

                    l = annotation.TextValue
                    l = l.strip()
                    tabl = l.split()
                    fp.write( str ( len(tabl)) )
                    fp.write(" ")

                    fp.write(str(duration))
                    fp.write("\n")

    # End writeinfo
    # ------------------------------------------------------------------   


    def writeliatxt(self, filename, t=0):
        """ Write an ascii file, with one tier of the Transcription.

            This output is the same as the output of LIA_nett script.
            1 column file with tokens. Interval separated by "<s>" and "</s>"
            Parameters:
                - filename is the output file name
                - t is the index of the tier to write
            Exception:   IOError
            Return:      None
        """
        encoding='iso8859-1'
        with codecs.open(filename, 'w', encoding) as fp:

            tier = self[t]
            if tier.IsEmpty():
                fp.close()
                return

            if tier.IsInterval():
                tier = fill_gaps(tier)
                tier = merge_overlapping_annotations(tier)

            for annotation in tier:
                fp.write("<s>\n")
                if annotation.IsInterval():
                    l = annotation.TextValue
                    l = l.strip()
                    tabl = l.split()
                    for w in tabl:
                        fp.write( w + "\n" )
                    fp.write(" ")
                fp.write("</s>\n")

    # End writeliatxt
    # ------------------------------------------------------------------   


