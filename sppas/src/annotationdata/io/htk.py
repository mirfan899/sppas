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
#       Copyright (C) 2015 Brigitte Bigi
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
import codecs
from annotationdata.transcription import Transcription
from annotationdata.label.label import Label as AnnotationLabel
import annotationdata.ptime.point
from annotationdata.ptime.framepoint import FramePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation


HTK_RADIUS = 0.0005
# time values are in multiples of 100ns
TIME_UNIT = pow(10, -7)


def TimePoint(time):
    return annotationdata.ptime.point.TimePoint(time, HTK_RADIUS)


def annotation_from_line(line, number):
    try:
        line = line.strip().split()

        hasBegin = len(line) > 0 and line[0].isdigit()
        hasEnd = len(line) > 1 and line[1].isdigit()

        if hasBegin and hasEnd:
            time = TimeInterval(TimePoint(float(line[0]) * TIME_UNIT),
                                TimePoint(float(line[1]) * TIME_UNIT))
            label = " ".join(line[2:])
        elif hasBegin:
            time = TimePoint(float(line[0])*TIME_UNIT)
            label = " ".join(line[1:])
        else:  # default to FramePoint
            time = FramePoint(number)
            label = " ".join(line)

        return Annotation(time, AnnotationLabel(label))
    except:
        raise Exception("Could not read line:%s" % repr(line))

# End annotation_from_line
# -----------------------------------------------------------------


def line_from_annotation(annotation):
    label = annotation.GetLabel().GetValue()

    if label == '':
        raise Exception("lab files do not support empty labels")

    if annotation.GetLocation().IsInterval():
        begin = str(int(
            1/TIME_UNIT * annotation.GetLocation().GetBeginMidpoint()))
        end = str(int(
            1/TIME_UNIT * annotation.GetLocation().GetEndMidpoint()))
        return "%s %s %s\n" % (begin, end, label)
    else:
        point = str(int(
            1/TIME_UNIT * annotation.GetLocation().GetPointMidpoint()))
        return "%s %s\n" % (point, label)

# End line_from_annotation
# -----------------------------------------------------------------


class Label(Transcription):
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        super(Label, self).__init__(name, mintime, maxtime)

    # End __init__
    # -----------------------------------------------------------------

    def read(self, filename):
        with codecs.open(filename, "r", 'utf-8') as fp:

            tier = self.NewTier()

            number = 1
            for line in fp:
                tier.Add(annotation_from_line(line, number))
                number += 1

        self.SetMinTime(0.)
        self.SetMaxTime(self.GetEnd())

    # End read
    # -----------------------------------------------------------------

    def write(self, filename):
        with codecs.open(filename, 'w', 'utf-8', buffering=8096) as fp:
            if self.GetSize() != 1:
                raise Exception(
                    "Cannot write a multi tier annotation to a lab file.")

            tier = self[0]

            for annotation in tier:
                if(annotation.GetLabel().GetValue() != ''):
                    fp.write(line_from_annotation(annotation))

    # End write
    # -----------------------------------------------------------------


class MasterLabel(Transcription):
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        super(MasterLabel, self).__init__(name, mintime, maxtime)

    # End __init__
    # -----------------------------------------------------------------

    def read(self, filename):
        with codecs.open(filename, "r", 'utf-8') as fp:
            line = ''
            number = 1
            while(not (line.strip().startswith('"') and
                       line.strip().endswith('"'))):
                line = fp.next()

            try:
                while True:
                    tierName = line.strip()[1:-1]

                    tier = self.NewTier(tierName)

                    line = fp.next()
                    while(line and
                          not (line.strip().startswith('"') and
                               line.strip().endswith('"'))):
                        tier.Add(annotation_from_line(line, number))
                        number += 1
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
