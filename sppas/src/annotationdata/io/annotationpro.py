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
import datetime

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
# Constants
# ---------------------------------------------------------------------------

now=datetime.datetime.now().strftime("%Y-%M-%d %H:%M")

ELT_REQUIRED_Configuration = {'version':'5', 'created':now, 'modified':now, 'samplerate':44100, 'fileversion':5, 'author':"SPPAS by Brigitte Bigi (C)"}

ELT_REQUIRED_Layer = {'id':None, 'name':'NoName', 'forecolor':"-16777216", 'backcolor':"-3281999", 'isselected':"false", 'height':"70"}
ELT_OPTIONAL_Layer = {'coordinatecontrolstyle':"0", 'islocked':"false", 'isclosed':"false", 'showonspectrogram':"false", 'showaschart':"false", 'chartminimum':"-50", 'chartmaximum':"50", 'showboundaries':"true", 'includeinfrequency':"true", 'parameter1name':"Parameter 1", 'parameter2name':"Parameter 2", 'parameter3name':"Parameter 3",'isvisible':"true", 'fontsize':"10" }

ELT_REQUIRED_Segment = {'id':None, 'idlayer':None, 'label':None, 'forecolor':'-16777216', 'backcolor':'-1', 'bordercolor':'-16777216', 'start':None, 'duration':None, 'isselected':'false'}
ELT_OPTIONAL_Segment = {'feature':None, 'language':None, 'group':None, 'name':None, 'parameter1':None, 'parameter2':None, 'parameter3':None, 'ismarker':"false", 'marker':None, 'rscript':None}

ELT_REQUIRED_Media = {'id':None, 'name':'NoName', 'filename':None, 'external':'false', 'current':'false'}

ANTX_RADIUS = 0.0005

# ---------------------------------------------------------------------------

def TimePoint(time):
    return annotationdata.ptime.point.TimePoint(time, ANTX_RADIUS)

# ---------------------------------------------------------------------------

class Antx(Transcription):
    """
    AnnotationPro stand-alone files.
    """

    def __init__(self, name="AnnotationSystemDataSet", coeff=1, mintime=None, maxtime=None):
        """
        Initialize a new instance.

        @type name: str
        @param name: the name of the transcription
        @type coeff: float
        @param coeff: the time coefficient (coeff=1 is seconds)
        """
        Transcription.__init__(self, name, coeff, mintime, maxtime)

    # -----------------------------------------------------------------

    @staticmethod
    def detect(filename):
        """
        Check whether a file seems to be an antx file or not.

        @type filename: str
        @param filename: filename
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

        #for child in tree.iter( tag=uri+"AudioFile" ):
        #    self.__read_audiofile(child, uri)

        for child in tree.iter( tag=uri+"Layer" ):
            self.__read_tier(child, uri)

        for child in tree.iter( tag=uri+"Segment" ):
            self.__read_annotation(child, uri)

    # End read
    # -----------------------------------------------------------------

    def __read_configuration(self, configurationRoot, uri):
        # Store all key/values in Transcription metadata
        newkey   = configurationRoot.find(uri+'Key').text.replace(uri,'')
        newvalue = configurationRoot.find(uri+'Value').text
        if newkey is not None:
            self.metadata[ newkey.lower() ] = newvalue

    # -----------------------------------------------------------------

    def __read_tier(self, tierRoot, uri):
        # Get the elements Tier instance need
        tier = self.NewTier( name=tierRoot.find(uri+'Name').text )

        # Put all information in metadata
        for node in tierRoot:
            if node.text:
                tier.metadata[ node.tag.replace(uri,'').lower() ] = node.text
                if 'id' in node.tag.lower():
                    self.__id_tier_map[node.text] = tier

    # -----------------------------------------------------------------

    def __read_annotation(self, annotationRoot, uri):
        # Get the elements Annotation instance need
        tier     = self.__id_tier_map.get( annotationRoot.find(uri+'IdLayer').text,None )
        start    = float( annotationRoot.find(uri+'Start').text )
        duration = float( annotationRoot.find(uri+'Duration').text )
        label    = Label( annotationRoot.find(uri+'Label').text )

        if tier is not None:

            # Create Annotation instance
            end = start + duration
            start = start / float( self.metadata.get('samplerate', 44100) )
            end   = end   / float( self.metadata.get('samplerate', 44100) )
            if end > start:
                location = Location(Localization(TimeInterval(TimePoint(start), TimePoint(end))))
            else:
                location = Location(Localization(TimePoint(start)))
            annotation = Annotation(location, label)

            # Put the other information in metadata
            for node in annotationRoot:
                if node.text:
                    if not node.tag.lower() in ['idlayer','start','duration', 'label']:
                        annotation.metadata[ node.tag.replace(uri,'').lower() ] = node.text

            # Add Annotation into Tier
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
                    self.__format_segment(root, tier, ann)

            # Write configurations
            for key,value in ELT_REQUIRED_Configuration.iteritems():
                Antx.__format_configuration(root, key, self.metadata.get(key,value))

            for key,value in self.metadata.iteritems():
                if not key in ELT_REQUIRED_Configuration.keys():
                    Antx.__format_configuration(root, key, self.metadata.get(key,value))

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
        if value:
            if key.lower() == 'modified':
                child_value.text = now
            else:
                child_value.text = unicode(value)

    # -----------------------------------------------------------------

    @staticmethod
    def __format_tier(root, tier):
        tier_root = ET.SubElement(root, 'Layer')

        # The elements SPPAS has interpretated
        child_id = ET.SubElement(tier_root, 'Id')
        tier_id = tier.metadata.get( 'id', gen_id() ) # get either the id we have or create one
        tier.metadata[ 'id' ] = tier_id               # it ensures the tier has really an id
        child_id.text = tier_id

        child_name = ET.SubElement(tier_root, 'Name')
        child_name.text = tier.GetName()

        # Either get metadata in tier or assign the default value
        for key,value in ELT_REQUIRED_Layer.iteritems():
            if not key in [ 'id','name' ]:
                child = ET.SubElement(tier_root, key)
                child.text = tier.metadata.get( key, value )

        # We also add all Antx optional elements
        for key,value in ELT_OPTIONAL_Layer.iteritems():
            child = ET.SubElement(tier_root, key)
            child.text = tier.metadata.get( key, value )

    # -----------------------------------------------------------------

    def __format_segment(self, root, tier, ann):
        segment_root = ET.SubElement(root, 'Segment')

        # The elements SPPAS has interpretated
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
        start    = start    * float( self.metadata.get('samplerate', 44100) )
        duration = duration * float( self.metadata.get('samplerate', 44100) )
        child_idstart.text = str(start)
        child_iddur.text = str(duration)

        # Antx required elements
        for key,value in ELT_REQUIRED_Segment.iteritems():
            if not key in [ 'id','idlayer', 'label', 'start', 'duration' ]:
                child = ET.SubElement(segment_root, key)
                child.text = ann.metadata.get( key, value )

        # We also add all Antx optional elements
        for key,value in ELT_OPTIONAL_Segment.iteritems():
            child = ET.SubElement(segment_root, key)
            child.text = ann.metadata.get( key, value )

    # ---------------------------------------------------------------------

