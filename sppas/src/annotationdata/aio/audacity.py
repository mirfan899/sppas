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
# File: audacity.py
# ---------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import xml.etree.cElementTree as ET

from ..transcription import Transcription
from ..label.label import Label
from ..ptime.point import TimePoint
from ..ptime.interval import TimeInterval
from ..annotation import Annotation

# -----------------------------------------------------------------

AUDACITY_RADIUS = 0.0005


def AudacityTimePoint(time, radius=AUDACITY_RADIUS):
    return TimePoint(time, radius)

# -----------------------------------------------------------------


def normalize(name):
    if name[0] == "{":
        uri, tag = name[1:].split("}")
        return tag
    else:
        return name

# -----------------------------------------------------------------


class Audacity(Transcription):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents the native format of Audacity files.

    Can work either on Audacity projects or Audacity Label tracks.

    """
    @staticmethod
    def detect(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        if root.find('project') is not None:
            return True

        return False

    # -----------------------------------------------------------------
    __format = '1.3.0'
    # -----------------------------------------------------------------

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Initialize a new AUP instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)

    # -----------------------------------------------------------------

    def read(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        for elem in tree.getiterator():
            name = normalize(elem.tag)
            if name == "labeltrack":
                self.__read_tier(elem, root)
            elif name == "wavetrack":
                pass

    # -----------------------------------------------------------------

    def __read_tier(self, tierRoot, root):
        tier = self.NewTier(tierRoot.attrib['name'])

        # Attributes are stored as metadata
        for key in ['height', 'minimized', 'isSelected']:
            if key in tierRoot.attrib:
                tier.metadata[key] = tierRoot.attrib[key]

        for annotationRoot in tierRoot.getiterator():
            name = normalize(annotationRoot.tag)
            if name == "label":
                label = annotationRoot.attrib['title']
                begin = float(annotationRoot.attrib['t'])
                end = float(annotationRoot.attrib['t1'])
                b = AudacityTimePoint(begin)

                if begin == end:
                    new_a = Annotation(b, Label(label))
                else:
                    e = AudacityTimePoint(end)
                    new_a = Annotation(TimeInterval(b,e), Label(label))

                tier.Add(new_a)

    # -----------------------------------------------------------------
