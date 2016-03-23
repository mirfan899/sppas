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
# File: htk.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import codecs
from annotationdata.transcription    import Transcription
from annotationdata.label.label      import Label
import annotationdata.ptime.point
from annotationdata.ptime.framepoint import FramePoint
from annotationdata.ptime.interval   import TimeInterval
from annotationdata.annotation       import Annotation

#TODO: check whether lab and mlf files can support time overlaps
#from utils import merge_overlapping_annotations

# ----------------------------------------------------------------------------

HTK_RADIUS = 0.0005

# time values are in multiples of 100ns
TIME_UNIT = pow(10, -7)

# ----------------------------------------------------------------------------
# Useful functions
# ----------------------------------------------------------------------------

def TimePoint(time):
    return annotationdata.ptime.point.TimePoint(time, HTK_RADIUS)

# ----------------------------------------------------------------------------

def line_from_annotation(annotation):
    """
    Convert an annotation into a line for HTK lab of mlf files.

    """
    label = annotation.GetLabel().GetValue()

    if label == '':
        raise Exception("lab files do not support empty labels")

    if annotation.GetLocation().IsInterval():
        begin = str(int(1/TIME_UNIT * annotation.GetLocation().GetBeginMidpoint()))
        end   = str(int(1/TIME_UNIT * annotation.GetLocation().GetEndMidpoint()))
        if not ' ' in label:
            return "%s %s %s\n" % (begin, end, label)
        else:
            s = "%s " % (begin)
            s = s + label.replace(' ','\n')
            return s+"\n"
    else:
        point = str(int(1/TIME_UNIT * annotation.GetLocation().GetPointMidpoint()))
        return "%s %s\n" % (point, label)

# ---------------------------------------------------------------------------


class HTKLabel( Transcription ):
    """
    @authors: Jibril Saffi, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents HTK lab files.

    Corrected version (2016-03-16)!!
    The previous one was totally wrong...

    """

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        super(HTKLabel, self).__init__(name, mintime, maxtime)

    # ------------------------------------------------------------------------

    def read(self, filename):

        with codecs.open(filename, "r", 'utf-8') as fp:

            tier = self.NewTier()
            label = ""
            prevend = TimePoint(0.)

            for line in fp:
                line = line.strip().split()
                hasBegin = len(line) > 0 and line[0].isdigit()
                hasEnd   = len(line) > 1 and line[1].isdigit()

                if hasBegin and hasEnd:
                    if len(label)>0:
                        time = TimeInterval(prevend, TimePoint(float(line[0]) * TIME_UNIT))
                        tier.Add(Annotation(time, Label(label)))

                    time = TimeInterval(TimePoint(float(line[0]) * TIME_UNIT), TimePoint(float(line[1]) * TIME_UNIT))
                    label = " ".join(line[2:])
                    tier.Add(Annotation(time, Label(label)))
                    label = ""
                    prevend = TimePoint(float(line[1]) * TIME_UNIT)

                elif hasBegin:
                    label = label +" "+ " ".join(line[1:])

                else:
                    label = label +" "+ " ".join(line)

        self.SetMinTime(0.)
        self.SetMaxTime(self.GetEnd())

    # ------------------------------------------------------------------------

    def write(self, filename):

        with codecs.open(filename, 'w', 'utf-8', buffering=8096) as fp:

            if self.GetSize() != 1:
                raise Exception(
                    "Cannot write a multi tier annotation to a lab file.")

            tier = self[0]

            for annotation in tier:
                if annotation.GetLabel().GetValue() != '':
                    fp.write(line_from_annotation(annotation))

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class MasterLabel( Transcription ):
    """
    @authors: Jibril Saffi, Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents HTK mlf files.
    """

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        super(MasterLabel, self).__init__(name, mintime, maxtime)

    # -----------------------------------------------------------------

    def read(self, filename):
        with codecs.open(filename, "r", 'utf-8') as fp:
            line = ''
            while (not (line.strip().startswith('"') and line.strip().endswith('"'))):
                line = fp.next()

            try:
                while True:
                    tierName = line.strip()[1:-1]
                    tier = self.NewTier(tierName)
                    label = ""
                    prevend = 0.

                    line = fp.next()
                    while(line and
                          not (line.strip().startswith('"') and
                               line.strip().endswith('"'))):

                        line = line.strip().split()
                        hasBegin = len(line) > 0 and line[0].isdigit()
                        hasEnd   = len(line) > 1 and line[1].isdigit()

                        if hasBegin and hasEnd:
                            if len(label)>0:
                                time = TimeInterval(prevend,
                                                    TimePoint(float(line[0]) * TIME_UNIT))
                                tier.Add(Annotation(time, Label(label)))

                            time = TimeInterval(TimePoint(float(line[0]) * TIME_UNIT),
                                                TimePoint(float(line[1]) * TIME_UNIT))
                            label = " ".join(line[2:])
                            tier.Add(Annotation(time, Label(label)))
                            label = ""
                            prevend = TimePoint(float(line[1]) * TIME_UNIT)

                        elif hasBegin:
                            label = label +" "+ " ".join(line[1:])

                        else:
                            label = label +" "+ " ".join(line)

                        line = fp.next()

            except StopIteration:
                pass

    # End read
    # -----------------------------------------------------------------

    def write(self, filename):
        with codecs.open(filename, 'w', 'utf-8', buffering=8096) as fp:

            fp.write('#!MLF!#\n')

            for tier in self:
                fp.write('"%s"\n' % tier.GetName())

                for annotation in tier:
                    if(annotation.GetLabel().GetValue() != ''):
                        fp.write(line_from_annotation(annotation))

    # End write
    # -----------------------------------------------------------------
