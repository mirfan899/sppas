#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
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
from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation
from annotationdata.tier import Tier

# ###########################################################################


class TextGrid(Transcription):
    """ Represents a TextGrid Transcription.
        TextGrid is the native file format of the GPL tool Praat:
        Doing phonetic with computers.
    """


    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """ Create a new TextGrid Transcription instance.
        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)


    # ################################################################ #
    # Input
    # ################################################################ #

    def read_short(self, filename):
        """ Read a short TextGrid file.
            Parameters:
                - filename is the textgrid file name
            Exception:   IOError
            Return:      none
        """
        encoding='utf-8'
        with codecs.open(filename, 'r', encoding) as fp:
            # Ignore Header
            for i in range(6):
                fp.readline()

            # Number of tiers in the TextGrid
            num_tier = int(fp.readline().strip())
            # for each tier
            for i in range(num_tier):
                # type of tier
                t_type = fp.readline().replace("\"","").strip()
                # create a new instance tier
                tier = self.NewTier()
                # item = self.NewTier()
                tiername = fp.readline().replace("\"","").strip()
                tier.NAME = tiername
                # self[item].NAME = tiername

                # Ignore (xmin xmax)
                for i in range(2):
                    fp.readline()

                # Number of annotation in the tier
                num_item = int(fp.readline().strip())
                if t_type == "IntervalTier":
                    # for each annotation
                    for i in range(num_item):
                        # Begin time interval
                        loc_s = float(fp.readline().strip())
                        # End time interval
                        loc_e = float(fp.readline().strip())
                        # Label
                        label = fp.readline().replace("\"", "").strip()
                        loc_s = TimePoint(loc_s)
                        loc_e = TimePoint(loc_e)
                        interval = TimeInterval(loc_s, loc_e)
                        tier.Append(Annotation(interval, Label(label)))
                        # self[item].Append(Annotation(interval, Label(label)))
                else: # TextTier
                    for i in range(num_item):
                        # Begin time interval
                        loc_s = float(fp.readline().strip())
                        # Label
                        label = fp.readline().replace("\"", "").strip()
                        tier.Append(Annotation(TimePoint(loc_s), Label(line)))

    # End read_short
    # ------------------------------------------------------------------   

    def read_long(self, filename):
        """ Read a TextGrid file.
            Parameters:
                - filename is the textgrid file name
            Exception:   IOError
            Return:      none
        """
        encoding='utf-8'
        with codecs.open(filename, 'r', encoding) as fp:
            # Ignore Header
            for i in range(7):
                fp.readline()
            # Load each annotation of each tier
            # Label, begin time, end time
            line = ""
            loc_s = -1.0
            loc_e = -1.0
            item = -1
            for line in fp:
                if( line.find("item []:")>-1 ):
                    continue
                if( line.find("item [")>-1 ):
                # New tier
                    tier = self.NewTier()
                    loc_s = -1.0
                    loc_e = -1.0
                elif line.find("name = ")>-1:
                # Tier name
                    line = line.replace( "name = ", "" )
                    line = line.replace( "\"", "" )
                    tier.Name = line.strip()
                elif line.find("xmin = ")>-1 or line.find("time = ")>-1 or line.find("number = ")>-1:
                # Begin time location of a new annotation
                    line = line.replace( "xmin = ", "" )
                    line = line.replace( "time = ", "" )
                    line = line.replace( "number = ", "" )
                    loc_s = float( line )
                    loc_e = -1.0
                elif line.find("xmax = ")>-1:
                # End time location of an annotation
                    line = line.replace("xmax = ", "")
                    loc_e = float( line )
                elif line.find("text = ")>-1 or line.find("mark = ")>-1:
                # Label
                    line = line.replace("text = ", "")
                    line = line.replace("mark = ", "")
                    line = line.replace( "\"", "" )
                    line = line.strip()
                    # Create the annotation and add to the tier
                    if( loc_e == -1.0 ):
                        tier.Append(Annotation(TimePoint(loc_s), Label(line)))
                    else:
                        loc_s = TimePoint(loc_s)
                        loc_e = TimePoint(loc_e)
                        interval = TimeInterval(loc_s, loc_e)
                        tier.Append(Annotation(interval, Label(line)))
                    # Initializations for the next annotation
                    loc_s = -1.0
                    loc_e = -1.0

    # End read_long
    # ------------------------------------------------------------------   


    def read(self, filename):
        """ Read a TextGrid file.
            Parameters:
                - filename is the textgrid file name
            Exception:   IOError, Exception
            Return:      none
        """
        # Verify if the file of existing
        encoding='utf-8'
        with codecs.open(filename, 'r', encoding) as fp:
            # Verify if the file is really a textgrid and if the encoding is utf8
            try:
                buffert = fp.read()
            except UnicodeDecodeError:
                raise UnicodeError("%r is not a us-ascii or UTF-8 encoding"
                                    % filename)

        if buffert.lower().find("textgrid") == -1:
            raise Exception('%r is not a valid textgrid.' % filename)

        # A long textgrid contains items (one item is one tier!)
        if (buffert.find("item [") > -1):
            self.read_long(filename)
        else:
            self.read_short(filename)

    # End read
    # ------------------------------------------------------------------

    # ################################################################ #
    # Output
    # ################################################################ #

    def write(self, filename):
        """ Write a TextGrid file.
            Parameters:
                - filename is the textgrid file name
            Exception:   IOError
            Return:      none
        """
        if self.IsEmpty():
            raise Exception("empty textgrid.")

        for tier in self:
            if tier.IsMixed():
                raise Exception("%r cannot be serialized as TextGrid file." % (tier.Name))

        encoding = 'utf-8'
        with codecs.open(filename, 'w', encoding) as fp:

            fp.write('File type = "ooTextFile"\n')
            fp.write('Object class = "TextGrid"\n')
            fp.write('\n')
            fp.write('xmin = %s\n' % (self.GetBegin()))
            fp.write('xmax = %s\n' % (self.GetEnd()))
            fp.write('tiers? <exists>\n')
            fp.write('size = %d\n' % (self.GetSize()))
            fp.write('item []:\n')

            for i, tier in enumerate(self, 1):
                if tier.IsEmpty():
                    continue
                else:
                    if tier.IsInterval():
                        tier = fill_gaps(tier)
                        tier = merge_overlapping_annotations(tier)
                        fp.write('    item [%d]:\n' % i)
                        fp.write('        class = "IntervalTier"\n')
                        fp.write('        name = "%s"\n' % tier.Name)
                        fp.write('        xmin = %s\n' % tier.GetBegin())
                        fp.write('        xmax = %s\n' % tier.GetEnd())
                        fp.write('        intervals: size = %s\n' % tier.GetSize())
                        for j, an in enumerate(tier, 1):
                            fp.write('        intervals [%d]:\n' % j)
                            fp.write('            xmin = %s\n' % an.BeginValue)
                            fp.write('            xmax = %s\n' % an.EndValue)
                            fp.write('            text = "%s"\n' % an.TextValue)
                    else:
                        fp.write('    item [%d]:\n' % (i))
                        fp.write('        class = "TextTier"\n')
                        fp.write('        name = "%s"\n' % tier.Name)
                        fp.write('        xmin = %s\n' % tier.GetBegin())
                        fp.write('        xmax = %s\n' % tier.GetEnd())
                        fp.write('        points: size = %s\n' % tier.GetSize())
                        for j, an in enumerate(tier, 1):
                            fp.write('        points [%d]:\n' % j)
                            fp.write('            time = %s\n' % an.PointValue)
                            fp.write('            mark = "%s"\n' % an.TextValue)

    # End write
    # ------------------------------------------------------------------
