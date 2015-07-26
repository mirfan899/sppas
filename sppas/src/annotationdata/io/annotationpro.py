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
# ---------------------------------------------------------------------------

import xml.etree.cElementTree as ET

from annotationdata.transcription  import Transcription
from annotationdata.tier           import Tier
from annotationdata.label.label    import Label
from annotationdata.label.text     import Text
from annotationdata.ptime.location import Location
import annotationdata.ptime.point
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.disjoint import TimeDisjoint
from annotationdata.ptime.framepoint import FramePoint
from annotationdata.ptime.frameinterval import FrameInterval
from annotationdata.ptime.framedisjoint import FrameDisjoint
from annotationdata.ptime.localization import Localization
from annotationdata.annotation import Annotation
from annotationdata.hierarchy import Hierarchy
from utils import indent
from utils import gen_id

# ---------------------------------------------------------------------------

ANTX_RADIUS = 0.0005

def TimePoint(time):
    return annotationdata.ptime.point.TimePoint(time, ANTX_RADIUS)

# ---------------------------------------------------------------------------

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
        """
        Check whether a file seems to be an antx file or not.
        """
        tree = ET.parse(filename)
        root = tree.getroot()
        return "AnnotationSystemDataSetroot" in root.tag

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
        newkey   = configurationRoot.find(uri+'Key').text.replace(uri,'')
        newvalue = configurationRoot.find(uri+'Value').text
        if newkey is not None:
            self.metadata[ newkey ] = newvalue

    # -----------------------------------------------------------------

    def __read_tier(self, tierRoot, uri):
        tier = self.NewTier( name=tierRoot.find(uri+'Name').text )
        for node in tierRoot:
            if node.text:
                if 'name' in node.tag.lower():
                    pass
                elif 'id' in node.tag.lower():
                    self.__id_tier_map[node.text] = tier
                    tier.metadata[ node.tag.replace(uri,'').lower() ] = node.text
                else:
                    tier.metadata[ node.tag.replace(uri,'').lower() ] = node.text

    # -----------------------------------------------------------------

    def __read_annotation(self, annotationRoot, uri):
        tier     = self.__id_tier_map.get( annotationRoot.find(uri+'IdLayer').text,None )
        start    = float( annotationRoot.find(uri+'Start').text )
        duration = float( annotationRoot.find(uri+'Duration').text )
        label    = Label( annotationRoot.find(uri+'Label').text )

        if tier is not None:
            end = start + duration
            start = start / 1000.  #float(self.metadata['Samplerate'])
            end   = end / 1000.    # float(self.metadata['Samplerate'])
            if end > start:
                location = Location(Localization(TimeInterval(TimePoint(start), TimePoint(end))))
            else:
                location = Location(Localization(TimePoint(start/1000.)))
            annotation = Annotation(location, label)

            # Segment metadata
            for node in annotationRoot:
                if node.text:
                    if not node.tag.lower() in ['idlayer','start','duration', 'label']:
                        annotation.metadata[ node.tag.replace(uri,'').lower() ] = node.text
            tier.Add(annotation)

    # -----------------------------------------------------------------


    def write(self, filename, encoding='UTF-8'):
        """
        Write a Antx file.
        """
        try:
            root = ET.Element('AnnotationSystemDataSet')
            root.set('xmlns', 'http://tempuri.org/AnnotationSystemDataSet.xsd')

            # Write layers
            for tier in self:
                Antx.__format_tier(root, tier)

            # Write segments
            for tier in self:
                for ann in tier:
                    Antx.__format_segment(root, tier, ann)

            # Write configurations
            for key,value in self.metadata.iteritems():
                Antx.__format_configuration(root, key, value)

            indent(root)

            tree = ET.ElementTree(root)
            tree.write(filename, encoding=encoding, xml_declaration=True, method="xml")
            #TODO: add standalone="yes" in the declaration
            #(but not available with ElementTree)

        except Exception:
            #import traceback
            #print(traceback.format_exc())
            raise

    # End write
    # -----------------------------------------------------------------

    @staticmethod
    def __format_configuration(root, key, value):
        configuration_root = ET.SubElement(root, 'Configuration')
        child_key = ET.SubElement(configuration_root, 'Key')
        child_key.text = key
        child_value = ET.SubElement(configuration_root, 'Value')
        if value: child_value.text = unicode(value)

    # -----------------------------------------------------------------

    @staticmethod
    def __format_tier(root, tier):
        tier_root = ET.SubElement(root, 'Layer')
        child_id = ET.SubElement(tier_root, 'Id')
        tier_id = tier.metadata.get( 'id', gen_id() )
        tier.metadata[ 'id' ] = tier_id # ensure the tier has really an id
        child_id.text = tier_id
        child_name = ET.SubElement(tier_root, 'Name')
        child_name.text = tier.GetName()

        # List of default values for all metadata of a layer
        d = {}
        d['forecolor']  = "-16777216"
        d['backcolor']  = "-3281999"
        d['isselected'] = "false"
        d['height']     = "70"
        d['coordinatecontrolstyle'] = "0"
        d['islocked']          = "false"
        d['isclosed']          = "false"
        d['showonspectrogram'] = "false"
        d['showaschart']       = "false"
        d['chartminimum']      = "-50"
        d['chartmaximum']      = "50"
        d['showboundaries']    = "true"
        d['includeinfrequency']= "true"
        d['parameter1name']    = "Parameter 1"
        d['parameter2name']    = "Parameter 2"
        d['parameter3name']    = "Parameter 3"
        d['isvisible']         = "true"
        d['fontsize']          = "10"

        # Either get metadata in tier or assign default value
        for k,v in d.iteritems():
            child = ET.SubElement(tier_root, k)
            child.text = tier.metadata.get( k, v )

    # -----------------------------------------------------------------

    @staticmethod
    def __format_segment(root, tier, ann):
        segment_root = ET.SubElement(root, 'Segment')
        child_id = ET.SubElement(segment_root, 'Id')            # Id
        child_id.text = ann.metadata.get( 'id', gen_id() )
        child_idlayer = ET.SubElement(segment_root, 'IdLayer')  # IdLayer
        child_idlayer.text = tier.metadata[ 'id' ]
        child_idlabel = ET.SubElement(segment_root, 'Label')    # Label
        child_idlabel.text = ann.GetLabel().GetValue()
        child_idstart = ET.SubElement(segment_root, 'Start')    # Start
        child_iddur = ET.SubElement(segment_root, 'Duration')   # Duration
        if ann.GetLocation().IsPoint():
            start = ann.GetLocation().GetPoint().GetMidpoint()
        else:
            start = ann.GetLocation().GetBegin().GetMidpoint()
        duration = ann.GetLocation().GetDuration()
        start    = start * 1000.
        duration = duration * 1000.
        child_idstart.text = str(start)
        child_iddur.text = str(duration)

        # List of default values for all metadata of a segment
        d = {}
        d['isselected'] = "false"
        d['feature']    = None
        d['language']   = None
        d['group']      = None
        d['name']       = None
        d['parameter1'] = None
        d['parameter2'] = None
        d['parameter3'] = None
        d['ismarker']   = "false"
        d['marker']     = None
        d['rscript']    = None

        # Either get metadata in annotation or assign default value
        for k,v in d.iteritems():
            child = ET.SubElement(segment_root, k)
            child.text = ann.metadata.get( k, v )

    # ---------------------------------------------------------------------

