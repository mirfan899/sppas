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

from datetime import datetime
import xml.etree.cElementTree as ET

from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.label.text import Text
from annotationdata.ptime.location import Location
from annotationdata.ptime.point import TimePoint
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

class XRA(Transcription):
    """
    xra files are the native file format of the GPL tool SPPAS.
    """

    __format = '1.1'

    def __init__(self, name="NoName", mintime=None, maxtime=None):
        """
        Initialize a new XRA instance.
        @type name: str
        @param name: the name of the transcription
        @type coeff: float
        @param coeff: the time coefficient (coeff=1 is seconds)
        """
        Transcription.__init__(self, name, mintime, maxtime)

    # End __init__
    # -----------------------------------------------------------------

    @staticmethod
    def detect(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        return root.find('Tier') is not None

    # End detect
    # -----------------------------------------------------------------

    def read(self, filename):
        """
        Import a transcription from a .xra file.
        @type filename: str
        @param filename: filename
        """
        tree = ET.parse(filename)
        root = tree.getroot()

        self.__id_tier_map = {}

        metadataRoot = root.find('Metadata')
        if metadataRoot is not None:
            XRA.__read_metadata(self, metadataRoot)

        for tierRoot in root.findall('Tier'):
            self.__read_tier(tierRoot)

        hierarchyRoot = root.find('Hierarchy')
        if hierarchyRoot is not None:
            self.__read_hierarchy(hierarchyRoot)

        for vocabularyRoot in root.findall('Vocabulary'):
            self.__read_vocabulary(vocabularyRoot)

    # End read
    # -----------------------------------------------------------------

    def __read_hierarchy(self, hierarchyRoot):
        for linkNode in hierarchyRoot.findall('Link'):
            type = linkNode.attrib['Type']

            formerID = linkNode.attrib['From']
            former = self.__id_tier_map[formerID]

            latterID = linkNode.attrib['To']
            latter = self.__id_tier_map[latterID]

            self._hierarchy.addLink(type, former, latter)

    # -----------------------------------------------------------------

    def __read_vocabulary(self, vocabularyRoot):
        vocab = {}
        for entryNode in vocabularyRoot.findall('Entry'):
            vocab[entryNode.text] = None
            # TODO: add descriptions

        for tierNode in vocabularyRoot.findall('Tier'):
            tier = self.__id_tier_map[tierNode.attrib['ID']]
            tier.ctrlvocab = vocab

    # -----------------------------------------------------------------

    def __read_tier(self, tierRoot):
        name = tierRoot.attrib['tiername']
        tier = self.NewTier(name)

        id = tierRoot.attrib['ID']
        self.__id_tier_map[id] = tier

        metadataRoot = tierRoot.find('Metadata')
        if metadataRoot is not None:
            XRA.__read_metadata(tier, metadataRoot)

        # TODO: read medias somehow

        for annotationRoot in tierRoot.findall('Annotation'):
            XRA.__read_annotation(tier, annotationRoot)

    # -----------------------------------------------------------------

    @staticmethod
    def __read_annotation(tier, annotationRoot):

        locationRoot = annotationRoot.find('Location')
        location = XRA.__parse_location(locationRoot)

        labelRoot = annotationRoot.find('Label')
        label = XRA.__parse_label(labelRoot)

        annotation = Annotation(location, label)
        tier.Add(annotation)

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_location(locationRoot):
        localizationList = []
        for localizationRoot in locationRoot.findall('Localization'):
            localization = XRA.__parse_localization(localizationRoot)

            localizationList.append(localization)

        location = Location(localizationList[0])
        for localization in localizationList[1:]:
            location.AddValue(localization)

        return location

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_localization(localizationRoot):

        underlyingNode = localizationRoot.find('*')

        if underlyingNode.tag == 'TimePoint':
            point = XRA.__parse_time_point(underlyingNode)
            localization = Localization(point)

        elif underlyingNode.tag == 'FramePoint':
            point = XRA.__parse_frame_point(underlyingNode)
            localization = Localization(point)

        elif(underlyingNode.tag == 'TimeInterval' or
             underlyingNode.tag == 'FrameInterval'):
            interval = XRA.__parse_interval(underlyingNode)
            localization = Localization(interval)

        elif(underlyingNode.tag == 'TimeDisjoint' or
             underlyingNode.tag == 'FrameDisjoint'):
            disjoint = XRA.__parse_disjoint(underlyingNode)
            localization = Localization(disjoint)

        else:
            raise Exception(
                "Localization is not a valid type: %s" %
                repr(underlyingNode.tag))

        score = float(localizationRoot.attrib['score'])
        localization.SetScore(score)

        return localization

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_time_point(timePointNode):
        midpoint = float(timePointNode.attrib['midpoint'])
        radius = float(timePointNode.attrib['radius'])

        return TimePoint(midpoint, radius)

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_frame_point(framePointNode):
        midpoint = int(framePointNode.attrib['midpoint'])
        radius = int(framePointNode.attrib['radius'])

        return FramePoint(midpoint, radius)

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_interval(intervalRoot):
        isTimeInterval = intervalRoot.tag == 'TimeInterval'

        beginNode = intervalRoot.find('Begin')
        begin = (XRA.__parse_time_point(beginNode) if
                 isTimeInterval else
                 XRA.__parse_frame_point(beginNode))

        endNode = intervalRoot.find('End')
        end = (XRA.__parse_time_point(endNode) if
               isTimeInterval else
               XRA.__parse_frame_point(endNode))

        return (TimeInterval(begin, end) if
                isTimeInterval else
                FrameInterval(begin, end))

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_disjoint(disjointRoot):
        isTimeDisjoint = disjointRoot.tag == 'TimeDisjoint'
        intervalList = []

        for intervalRoot in (
            disjointRoot.findall('TimeInterval' if
                                 isTimeDisjoint else
                                 'FrameInterval')
        ):
            interval = XRA.__parse_interval(intervalRoot)
            intervalList.append(interval)

        return (TimeDisjoint(*intervalList) if
                isTimeDisjoint else
                FrameDisjoint(*intervalList))

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_label(labelRoot):
        label = Label()

        if 'scoremode' in labelRoot.attrib:
            # FIXME: it's min or max usually,
            # but there's no reason for it to only be builtins
            fun = globals()['__builtins__'][labelRoot.attrib['scoremode']]
            label.SetFunctionScore(fun)

        for textNode in labelRoot.findall('Text'):
            score = float(textNode.attrib['score'])
            content = (textNode.text if
                       textNode.text is not None else '')

            if 'type' in textNode.attrib:
                text = Text(content, score, textNode.attrib['type'])
            else:
                text = Text(content, score)

            label.AddValue(text)

        return label

    # -----------------------------------------------------------------

    @staticmethod
    def __read_metadata(metaObject, metadataRoot):
        for entryNode in metadataRoot.findall('Entry'):
            key = entryNode.attrib['Key'].lower()
            value = entryNode.text
            metaObject.metadata[key] = value

    # -----------------------------------------------------------------

    def write(self, filename, encoding='UTF-8'):
        """
        Write a XRA file.
        """
        try:
            root = ET.Element('Document')
            root.set('Author', 'SPPAS')
            root.set('Date', datetime.now().strftime("%Y-%m-%d"))
            root.set('Format', XRA.__format)

            self.__tier_id_map = {}
            self.__tier_counter = 0

            metadataRoot = ET.SubElement(root, 'Metadata')
            XRA.__format_metadata(metadataRoot, self)
            if len(metadataRoot.findall('Entry')) == 0:
                root.remove(metadataRoot)

            for tier in self:
                tierRoot = ET.SubElement(root, 'Tier')
                self.__format_tier(tierRoot, tier)

            hierarchyRoot = ET.SubElement(root, 'Hierarchy')
            self.__format_hierarchy(hierarchyRoot, self._hierarchy)

            for vocabulary, tierList in self.GetCtrlVocabs():
                vocabularyRoot = ET.SubElement(root, 'Vocabulary')
                XRA.__format_vocabulary(vocabularyRoot, vocabulary, tierList)

            indent(root)

            tree = ET.ElementTree(root)
            tree.write(filename, encoding=encoding, method="xml")

        except Exception:
            #import traceback
            #print(traceback.format_exc())
            raise

    # End write
    # -----------------------------------------------------------------

    def __format_hierarchy(self, hierarchyRoot, hierarchy):
        try:
            for type in Hierarchy.hierarchy_types:
                for (former, latter) in hierarchy.getHierarchy(type):
                    link = ET.SubElement(hierarchyRoot, 'Link')
                    link.set('Type', type)
                    # FIXME: this shouldn't be used because it breaks transaction unicity
                    link.set('From', self.__tier_id_map[former])
                    link.set('To', self.__tier_id_map[latter])
        except KeyError:
            #print('The current Hierarchy is invalid.')
            hierarchyRoot.clear()

    # End __format_hierarchy
    # -----------------------------------------------------------------

    @staticmethod
    def __format_vocabulary(vocabularyRoot, vocabulary, tierList):
        vocabularyRoot.set('ID', vocabulary.GetIdentifier())
        vocabularyRoot.set('description', vocabulary.GetDescription())
        for entry in vocabulary:
            entryNode = ET.SubElement(vocabularyRoot, 'Entry')
            entryNode.text = unicode(entry.Value)
        for tier in tierList:
            tierNode = ET.SubElement(vocabularyRoot, 'Tier')
            tierNode.set('ID', self.__tier_id_map[tier])

    # -----------------------------------------------------------------

    @staticmethod
    def __format_metadata(metadataRoot, metaObject):
        for key, value in metaObject.metadata.iteritems():
            entry = ET.SubElement(metadataRoot, 'Entry')
            entry.set('Key', key)
            entry.text = unicode(value)

    # -----------------------------------------------------------------

    def __format_tier(self, tierRoot, tier):
        id = gen_id() #'t%d' % self.__tier_counter
        tierRoot.set("ID", id)
        tier.metadata [ 'id' ] = id
        self.__tier_id_map[tier] = id
        self.__tier_counter += 1
        tierRoot.set("tiername", tier.GetName())

        metadataRoot = ET.SubElement(tierRoot, 'Metadata')
        XRA.__format_metadata(metadataRoot, tier)
        if len(metadataRoot.findall('Entry')) == 0:
            tierRoot.remove(metadataRoot)

        for annotation in tier:
            annotationRoot = ET.SubElement(tierRoot, 'Annotation')
            XRA.__format_annotation(annotationRoot, annotation)

        # TODO: add medias somehow

    # -----------------------------------------------------------------

    @staticmethod
    def __format_annotation(annotationRoot, annotation):
        locationRoot = ET.SubElement(annotationRoot, 'Location')
        XRA.__format_location(locationRoot,
                              annotation.GetLocation())

        labelRoot = ET.SubElement(annotationRoot, 'Label')
        XRA.__format_label(labelRoot, annotation.GetLabel())

    # -----------------------------------------------------------------

    @staticmethod
    def __format_label(labelRoot, label):
        labelRoot.set('scoremode', label.GetFunctionScore().__name__)
        for text in label.GetLabels():
            textNode = ET.SubElement(labelRoot, 'Text')
            XRA.__format_text(textNode, text)

    # -----------------------------------------------------------------

    @staticmethod
    def __format_text(textNode, text):
        textNode.set('score', unicode(text.GetScore()))

        typedValue = text.GetTypedValue()
        if isinstance(typedValue, int):
            textNode.set('type', 'int')
        elif isinstance(typedValue, float):
            textNode.set('type', 'float')
        elif isinstance(typedValue, bool):
            textNode.set('type', 'bool')
        elif isinstance(typedValue, str):
            textNode.set('type', 'str')

        textNode.text = text.GetValue()

    # -----------------------------------------------------------------

    @staticmethod
    def __format_location(locationRoot, location):
        for localization in location:
            localizationRoot = ET.SubElement(locationRoot,
                                             'Localization')
            XRA.__format_localization(localizationRoot, localization)

    # -----------------------------------------------------------------

    @staticmethod
    def __format_localization(localizationRoot, localization):
        localizationRoot.set('score', unicode(localization.GetScore()))
        if localization.IsTimePoint():
            point = ET.SubElement(localizationRoot, 'TimePoint')
            XRA.__format_point(point, localization.GetPoint())

        elif localization.IsTimeInterval():
            intervalRoot = ET.SubElement(localizationRoot, 'TimeInterval')
            XRA.__format_interval(intervalRoot, localization.GetPlace())

        elif localization.IsTimeDisjoint():
            disjointRoot = ET.SubElement(localizationRoot, 'TimeDisjoint')
            XRA.__format_disjoint(disjointRoot, localization.GetPlace())

        elif localization.IsFramePoint():
            framePoint = ET.SubElement(localizationRoot, 'FramePoint')
            XRA.__format_point(framePoint, localization.GetPoint())

        elif localization.IsFrameInterval():
            intervalRoot = ET.SubElement(localizationRoot, 'FrameInterval')
            XRA.__format_interval(intervalRoot, localization.GetPlace())

        elif localization.IsFrameDisjoint():
            disjointRoot = ET.SubElement(localizationRoot, 'FrameDisjoint')
            XRA.__format_disjoint(disjointRoot, localization.GetPlace())

        else:
            raise Exception("Localization is not a valid type")

    # -----------------------------------------------------------------

    @staticmethod
    def __format_point(pointNode, point):
        pointNode.set('midpoint', unicode(point.GetMidpoint()))
        pointNode.set('radius', unicode(point.GetRadius()))

    # -----------------------------------------------------------------

    @staticmethod
    def __format_interval(intervalRoot, interval):
        begin = ET.SubElement(intervalRoot, 'Begin')
        XRA.__format_point(begin, interval.GetBegin())

        end = ET.SubElement(intervalRoot, 'End')
        XRA.__format_point(end, interval.GetEnd())

    # -----------------------------------------------------------------

    @staticmethod
    def __format_disjoint(disjointRoot, disjoint):
        for interval in disjoint:
            intervalRoot = ET.SubElement(disjointRoot, 'Interval')
            XRA.__format_interval(intervalRoot, interval)

    # -----------------------------------------------------------------
