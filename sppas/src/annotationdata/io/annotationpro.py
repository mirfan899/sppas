#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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

from datetime import datetime
import xml.etree.cElementTree as ET

from annotationdata.transcription  import Transcription
from annotationdata.tier           import Tier
from annotationdata.label.label    import Label
from annotationdata.label.text     import Text
from annotationdata.ptime.location import Location
from annotationdata.ptime.point    import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.disjoint import TimeDisjoint
from annotationdata.ptime.framepoint import FramePoint
from annotationdata.ptime.frameinterval import FrameInterval
from annotationdata.ptime.framedisjoint import FrameDisjoint
from annotationdata.ptime.localization import Localization
from annotationdata.annotation import Annotation
from annotationdata.hierarchy import Hierarchy
from utils import indent


class Antx(Transcription):
    """
    AnnotationPro stand-alone files.
    """

    __format = '5.0'

    def __init__(self, name="AnnotationSystemDataSet", coeff=1, mintime=None, maxtime=None):
        """
        Initialize a new instance.
        @type name: str
        @param name: the name of the transcription
        @type coeff: float
        @param coeff: the time coefficient (coeff=1 is seconds)
        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)

    # End __init__
    # -----------------------------------------------------------------

    @staticmethod
    def detect(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        return root.find('AnnotationSystemDataSet') is not None

    # End detect
    # -----------------------------------------------------------------

    def read(self, filename):
        """
        Import a transcription from a .antx file.
        @type filename: str
        @param filename: filename
        """
        self.__id_tier_map = {}
        tree = ET.parse(filename)
        root = tree.getroot()
        uri = root.tag[:root.tag.index('}')+1]

        for child in tree.iter( tag=uri+'Configuration'):
            self.__read_configuration(child, uri)

        for child in tree.iter( tag=uri+"Layer" ):
            self.__read_tier(child, uri)

        for child in tree.iter( tag=uri+"Segment" ):
            self.__read_annotation(child, uri)

    # End read
    # -----------------------------------------------------------------

    def __read_configuration(self, configurationRoot, uri):
        newkey   = configurationRoot.find(uri+'Key').text
        newvalue = configurationRoot.find(uri+'Value').text
        if newkey is not None:
            self.metadata[newkey] = newvalue

    # End __read_configuration
    # -----------------------------------------------------------------

    def __read_tier(self, tierRoot, uri):
        tier = self.NewTier( name=tierRoot.find(uri+'Name').text )
        for node in tierRoot:
            if node.text:
                if 'name' in node.tag.lower():
                    pass
                elif 'id' in node.tag.lower():
                    self.__id_tier_map[node.text] = tier
                else:
                    tier.metadata[ node.tag ] = node.text

    # End __read_tier
    # -----------------------------------------------------------------

    def __read_annotation(self, annotationRoot, uri):
        tier     = self.__id_tier_map.get( annotationRoot.find(uri+'IdLayer').text,None )
        start    = float( annotationRoot.find(uri+'Start').text )
        duration = float( annotationRoot.find(uri+'Duration').text )
        label    = Label( annotationRoot.find(uri+'Label').text )

        if tier is not None:
            end = start + duration
            #start = start / float(self.metadata['Samplerate'])
            #end   = end / float(self.metadata['Samplerate'])
            if end > start:
                location = Location(Localization(TimeInterval(TimePoint(start/1000.), TimePoint(end/1000.))))
            else:
                location = Location(Localization(TimePoint(start/1000.)))
            annotation = Annotation(location, label)

            # Segment metadata
            for node in annotationRoot:
                if node.text:
                    if not node.tag.lower() in ['idlayer','start','duration', 'label']:
                        annotation.metadata[ node.tag.replace(uri,'') ] = node.text
            tier.Add(annotation)

    # End __read_annotation
    # -----------------------------------------------------------------

# ---------------------------------------------------------------------

