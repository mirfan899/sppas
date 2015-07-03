#!/usr/bin/env python2
# -*- coding: utf8 -*-
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
#       Copyright (C) 2015  Brigitte Bigi
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

__author__ = "Tatsuya Watanabe"


import codecs
from datetime import datetime
import re

from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation




class Phonedit(Transcription):
    """
    PHONEDIT Signaix is a software for the analysis of sound, aerodynamic,
     articulatory and electro-physiological signals developped
     by the Parole et Langage Laboratory, Aix-en-Provence, France.
     It provides a complete environment for the recording,
     the playback, the display, the analysis, the labeling
     of multiparametric data. http://www.lpl-aix.fr/~lpldev/phonedit/

    """
    PATTERN_ANNOTATION = re.compile(r"""
                                     LBL_LEVEL_[A-Z]{2}_\d{6}=\s?
                                     (\".*\"|\S+|[ ]?)\s  # label
                                     (\S+)\s  # begin time
                                     (\S+)  # end time
                                     """, re.VERBOSE)

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """
        Creates a new Phonedit Transcription instance.
        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)

    # End __init__
    # ------------------------------------------------------------------


    def read(self, filename, encoding="iso8859-1"):
        """
        Read a Phonedit mark file.
        @param filename: intput filename.
        @param encoding: encoding.
        """
        with codecs.open(filename, mode="r", encoding=encoding) as fp:
            new_tier = None
            section_tier = "DSC_LEVEL_NAME="
            for line in fp:
                if line.startswith("[DSC_LEVEL_"):
                    new_tier = self.NewTier()
                elif section_tier in line:
                    line = line.replace(section_tier, "")
                    line = line.strip().strip('"')
                    if new_tier is not None:
                        new_tier.SetName( line )
                elif line.startswith("LBL_LEVEL"):
                    match = re.match(self.PATTERN_ANNOTATION, line)
                    if match:
                        label = Label(match.group(1).strip('"'))
                        begin = TimePoint(float(match.group(2)) / 1000)
                        end = TimePoint(float(match.group(3)) / 1000)
                        interval = TimeInterval(begin, end)
                        new_ann = Annotation(interval, label)
                        if new_tier is not None:
                            new_tier.Append(new_ann)

        # Update
        self.SetMinTime(0)
        self.SetMaxTime( self.GetEnd() )

    # End read
    # ------------------------------------------------------------------


    def write(self, filename, encoding="iso8859-1"):
        """
        Write a Phonedit mark file.
        @param filename: output filename.
        @param encoding: encoding.
        """
        code_a = ord("A")
        lastmodified = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        with codecs.open(filename, mode="w", encoding=encoding) as fp:
            for index_tier, tier in enumerate(self):
                level = "LEVEL_%s%s" % (
                        chr(code_a + index_tier / 26),
                        chr(code_a + index_tier % 26))
                fp.write("[DSC_%s]\n" % level)
                fp.write("DSC_LEVEL_NAME=\"%s\"\n" %  tier.GetName())
                fp.write("DSC_LEVEL_SOFTWARE=%s\n" %  "SPPAS")
                fp.write("DSC_LEVEL_LASTMODIF_DATE=%s\n" % lastmodified)
                fp.write("[LBL_%s]\n" % level)
                for index_ann, ann in enumerate(tier):
                    fp.write("LBL_%s_%06d= \"%s\" " % (
                        level, index_ann, ann.GetLabel().GetValue()))
                    if ann.GetLocation().IsPoint():
                        begin = ann.GetLocation().GetPointMidpoint() * 1000
                        end   = begin
                    else:
                        begin = ann.GetLocation().GetBeginMidpoint() * 1000
                        end   = ann.GetLocation().GetEndMidpoint() * 1000
                    fp.write("%f %f\n" %  (begin, end))

    # End write
    # ------------------------------------------------------------------
