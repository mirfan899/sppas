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

import datetime
import xml.etree.cElementTree as ET
from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
import annotationdata.ptime.point
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation
from utils import indent


ELAN_RADIUS = 0.02


def TimePoint(time, radius=ELAN_RADIUS):
    return annotationdata.ptime.point.TimePoint(time, radius)


def linguistic_type_from_tier(tier):
    return (tier.metadata['LINGUISTIC_TYPE_REF']
            if 'LINGUISTIC_TYPE_REF' in tier.metadata else
            'SPPAS_%s' % tier.GetName())

# End linguistic_type_from_tier
# -----------------------------------------------------------------


class Elan(Transcription):
    def read(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        headerRoot = root.find('HEADER')
        if 'MEDIA_FILE' in headerRoot.attrib:
            self.metadata['MEDIA_FILE'] = headerRoot.attrib['MEDIA_FILE']
        self.metadata['HEADER_CONTENTS'] = headerRoot
        self.__read_unit(headerRoot)

        timeOrderRoot = root.find('TIME_ORDER')
        self.__read_time_slots(timeOrderRoot)

        self.hierarchyLinks = {}

        # associate vocabs with linguistic types
        self.__read_ctrl_vocabs(root)

        for tierRoot in root.findall('TIER'):
            self.__read_tier(tierRoot, root)

        # manage hierarchyLinks
        for parentTierRef in self.hierarchyLinks:
            child = self.hierarchyLinks[parentTierRef]
            parent = self.Find(parentTierRef)
            # Elan's hierarchy
            try:
                self._hierarchy.addLink('TimeAlignment', child, parent)
            except:
                pass

        del self.hierarchyLinks
        del self.unit
        del self.timeSlots
        del self.ctrlVocabs

    # End read
    # -----------------------------------------------------------------

    def __read_tier(self, tierRoot, root):
        tier = self.NewTier(tierRoot.attrib['TIER_ID'])

        linguisticType = tierRoot.attrib['LINGUISTIC_TYPE_REF']
        if linguisticType in self.ctrlVocabs:
            tier.SetCtrlVocab(self.ctrlVocabs[linguisticType])
        tier.metadata['LINGUISTIC_TYPE_REF'] = linguisticType

        if 'PARENT_REF' in tierRoot.attrib:
            parentRef = tierRoot.attrib['PARENT_REF']
            self.__read_ref_tier(tier, tierRoot, parentRef, root)

        else:
            self.__read_alignable_tier(tier, tierRoot)

    # End __read_tier
    # -----------------------------------------------------------------

    def __read_ref_tier(self, tier, tierRoot, parentTierRef, root):
        # add a link to process later
        self.hierarchyLinks[parentTierRef] = tier

        # group annotations in batches
        batches = {}
        for annotationRoot in tierRoot.findall('ANNOTATION'):
            if annotationRoot[0].tag == 'ALIGNABLE_ANNOTATION':
                tier.Add(self.__parse_alignable_annotation(annotationRoot[0]))
            else:
                ref = annotationRoot[0].attrib['ANNOTATION_REF']
                if ref not in batches:
                    batches[ref] = []

                # FIXME: we don't take into account PREVIOUS_ANNOTATION
                # and suppose the tier is sorted
                batches[ref].append(annotationRoot)

        for ref in batches:
            realRefRoot = Elan.__find_real_ref(ref, root)

            beginKey = realRefRoot.attrib['TIME_SLOT_REF1']
            begin = self.timeSlots[beginKey].GetMidpoint()

            endKey = realRefRoot.attrib['TIME_SLOT_REF2']
            end = self.timeSlots[endKey].GetMidpoint()

            count = len(batches[ref])
            increment = (end - begin) / count

            x1 = begin
            x2 = begin + increment
            for annotationRoot in batches[ref]:
                label = annotationRoot[0].find('ANNOTATION_VALUE').text
                tier.Add(Annotation(TimeInterval(TimePoint(x1),
                                                 TimePoint(x2)),
                                    Label(label)))
                x1 += increment
                x2 += increment

    # End __read_ref_tier
    # -----------------------------------------------------------------

    @staticmethod
    def __find_real_ref(ref, root):
        while True:
            for annotationRoot in root.iter('ANNOTATION'):
                if annotationRoot[0].attrib['ANNOTATION_ID'] == ref:
                    if annotationRoot[0].tag == 'REF_ANNOTATION':
                        ref = annotationRoot[0].attrib['ANNOTATION_REF']
                        break
                    else:
                        return annotationRoot[0]

    # End __find_real_ref
    # -----------------------------------------------------------------

    def __read_alignable_tier(self, tier, tierRoot):
        for annotationRoot in tierRoot.findall('ANNOTATION'):
            tier.Add(self.__parse_alignable_annotation(
                annotationRoot.find('ALIGNABLE_ANNOTATION')))

    # End __read_alignable_tier
    # -----------------------------------------------------------------

    def __parse_alignable_annotation(self, alignableAnnotationRoot):
        label = alignableAnnotationRoot.find('ANNOTATION_VALUE').text

        beginKey = alignableAnnotationRoot.attrib['TIME_SLOT_REF1']
        begin = self.timeSlots[beginKey]

        endKey = alignableAnnotationRoot.attrib['TIME_SLOT_REF2']
        end = self.timeSlots[endKey]

        return Annotation(TimeInterval(begin,
                                       end),
                          Label(label))

    # End __parse_alignable_annotation
    # -----------------------------------------------------------------

    def __read_ctrl_vocabs(self, root):
        self.ctrlVocabs = {}

        for ctrlVocabRoot in root.findall('CONTROLLED_VOCABULARY'):
            vocab = {}
            for entryNode in ctrlVocabRoot.findall('CV_ENTRY'):

                vocab[entryNode.text] = None
                if 'DESCRIPTION' in entryNode.attrib:
                    vocab[entryNode.text] = entryNode.attrib['DESCRIPTION']

            linguisticNode = root.find(
                'LINGUISTIC_TYPE[@CONTROLLED_VOCABULARY_REF=\'%s\']' % (
                    ctrlVocabRoot.attrib['CV_ID'])
            )
            linguisticId = linguisticNode.attrib['LINGUISTIC_TYPE_ID']

            self.ctrlVocabs[linguisticId] = vocab

    # End __read_ctrl_vocabs
    # -----------------------------------------------------------------

    def __read_unit(self, headerRoot):
        unitString = headerRoot.attrib['TIME_UNITS']
        if unitString == 'milliseconds':
            self.unit = 0.001
        elif unitString == 'seconds':
            self.unit = 1.0

    # End __read_unit
    # -----------------------------------------------------------------

    def __read_time_slots(self, timeOrderRoot):
        timeSlotCouples = []
        for timeSlotNode in timeOrderRoot.findall('TIME_SLOT'):
            id = timeSlotNode.attrib['TIME_SLOT_ID']

            if 'TIME_VALUE' in timeSlotNode.attrib:
                value = TimePoint(
                    float(timeSlotNode.attrib['TIME_VALUE']) * self.unit)
            else:
                value = None

            timeSlotCouples.append((id, value))

            for i in range(1, len(timeSlotCouples)-1):
                (prevId, prevVal) = timeSlotCouples[i-1]
                (id, val) = timeSlotCouples[i]
                (nextId, nextVal) = timeSlotCouples[i+1]
                if val is None:
                    midPoint = (prevVal.GetMidpoint() +
                                nextVal.GetMidpoint()) / 2
                    newVal = TimePoint(midPoint, midPoint -
                                       prevVal.GetMidpoint())
                    timeSlotCouples[i] = (id, newVal)

            self.timeSlots = dict(timeSlotCouples)

    # End __read_time_slots
    # -----------------------------------------------------------------

    def write(self, filename):
        root = ET.Element('ANNOTATION_DOCUMENT')
        root.set('AUTHOR', 'SPPAS')
        root.set('DATE',
                 str(datetime.datetime.now()).replace(' ', 'T'))
        root.set('FORMAT', '2.7')
        root.set('VERSION', '2.7')
        root.set('xmlns:xsi',
                 'http://www.w3.org/2001/XMLSchema-instance')
        root.set(
            'xsi:noNamespaceSchemaLocation',
            'http://www.mpi.nl.tools/elan/EAFv2.7.xsd')

        headerRoot = ET.SubElement(root, 'HEADER')
        mediaFile = (self.metadata['MEDIA_FILE']
                     if 'MEDIA_FILE' in self.metadata
                     else '')
        headerRoot.set('MEDIA_FILE', mediaFile)
        headerRoot.set('TIME_UNITS', 'milliseconds')

        if 'HEADER_CONTENTS' in self.metadata:
            for node in self.metadata['HEADER_CONTENTS']:
                headerRoot.append(node)

        self.__build_timeslots()
        timeOrderRoot = ET.SubElement(root, 'TIME_ORDER')
        self.__format_timeslots(timeOrderRoot)

        self.__build_annotation_ids()

        for tier in self:
            tierRoot = ET.SubElement(root, 'TIER')
            self.__format_tier(tierRoot, tier)

        self.__write_linguistic_types(root)
        self.__write_ctrl_vocabs(root)

        del self.timeSlotIds
        del self.annotationIds

        indent(root)
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', method="xml")

    # End write
    # -----------------------------------------------------------------

    def __write_linguistic_types(self, root):
        types = set()
        for tier in self:
            types.add(linguistic_type_from_tier(tier))

        for type in types:
            typeRoot = ET.SubElement(root, 'LINGUISTIC_TYPE')
            typeRoot.set('LINGUISTIC_TYPE_ID', type)

    # End __write_linguistic_types
    # -----------------------------------------------------------------

    def __write_ctrl_vocabs(self, root):
        i = 0
        for tier in self:
            ctrlVocab = tier.GetCtrlVocab()
            if ctrlVocab is not None:
                # add reference to ctlrVocab in linguisticType
                linguisticType = linguistic_type_from_tier(tier)
                linguisticTypeRoot = root.find(
                    'LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID=\'%s\']' %
                    linguisticType)

                if('CONTROLLED_VOCABULARY_REF' not in
                   linguisticTypeRoot.attrib):

                    ctrlVocabRoot = ET.SubElement(root,
                                                  'CONTROLLED_VOCABULARY')
                    ctrlVocabId = 'cv%s' % i
                    ctrlVocabRoot.set('CV_ID', ctrlVocabId)
                    i += 1

                    linguisticTypeRoot.set(
                        'CONTROLLED_VOCABULARY_REF',
                        ctrlVocabId)

                    Elan.__format_ctrl_vocab(ctrlVocabRoot, ctrlVocab)

    # End __write_ctrl_vocabs
    # -----------------------------------------------------------------

    @staticmethod
    def __format_ctrl_vocab(ctrlVocabRoot, ctrlVocab):
        for value in ctrlVocab:
            valueNode = ET.SubElement(ctrlVocabRoot, 'CV_ENTRY')
            valueNode.text = value
            if ctrlVocab[value] is not None:
                valueNode.set('DESCRIPTION', ctrlVocab[value])

    # End __format_ctrl_vocab
    # -----------------------------------------------------------------

    def __format_timeslots(self, timeOrderRoot):
        for timeSlot in self.timeSlotIds:
            timeSlotId = self.timeSlotIds[timeSlot]
            timeSlotNode = ET.SubElement(timeOrderRoot, 'TIME_SLOT')
            timeSlotNode.set('TIME_SLOT_ID', timeSlotId)
            timeSlotNode.set('TIME_VALUE', str(int(timeSlot*1000)))

    # End __format_timeslots
    # -----------------------------------------------------------------

    def __format_tier(self, tierRoot, tier):
        linguisticType = linguistic_type_from_tier(tier)

        tierRoot.set('LINGUISTIC_TYPE_REF', linguisticType)

        tierRoot.set('TIER_ID', tier.GetName())

        parentTier = self._hierarchy.getParent(tier)
        if parentTier is not None:
            tierRoot.set('PARENT_REF', parentTier.GetName())
            self.previousRefId = None
            for annotation in tier:
                annotationRoot = ET.SubElement(tierRoot,
                                               'ANNOTATION')
                self.__format_ref_annotation(annotationRoot,
                                             annotation,
                                             parentTier)
            del self.previousRefId
        else:
            for annotation in tier:
                annotationRoot = ET.SubElement(tierRoot,
                                               'ANNOTATION')
                self.__format_alignable_annotation(annotationRoot, annotation)

    # End __format_tier
    # -----------------------------------------------------------------

    def __format_ref_annotation(self, annotationRoot, annotation, parentTier):
        begin = annotation.GetLocation().GetBeginMidpoint()
        end = annotation.GetLocation().GetEndMidpoint()

        parentAnnotation = None
        for parentTierAnnotation in parentTier:
            parentBegin = parentTierAnnotation.GetLocation().GetBeginMidpoint()
            parentEnd = parentTierAnnotation.GetLocation().GetEndMidpoint()
            if parentBegin <= begin and parentEnd >= end:
                parentAnnotation = parentTierAnnotation
                break

        # if no reference was found, we must defer to alignable annotations
        if parentAnnotation is None:
            self.__format_alignable_annotation(annotationRoot, annotation)
            return

        refRoot = ET.SubElement(annotationRoot, 'REF_ANNOTATION')

        id = self.annotationIds[annotation]
        refRoot.set('ANNOTATION_ID', id)

        parentAnnotationId = self.annotationIds[parentAnnotation]
        refRoot.set('ANNOTATION_REF',
                    parentAnnotationId)

        if self.previousRefId is not None:
            refRoot.set('PREVIOUS_ANNOTATION',
                        self.previousRefId)

        label = annotation.GetLabel().GetValue()
        valueRoot = ET.SubElement(refRoot, 'ANNOTATION_VALUE')
        valueRoot.text = label

        self.previousRefId = id

    # End __format_ref_annotation
    # -----------------------------------------------------------------

    def __format_alignable_annotation(self, annotationRoot, annotation):
        alignableRoot = ET.SubElement(annotationRoot, 'ALIGNABLE_ANNOTATION')

        alignableRoot.set('ANNOTATION_ID', self.annotationIds[annotation])

        begin = str(
            self.timeSlotIds[annotation.GetLocation().GetBeginMidpoint()])
        alignableRoot.set('TIME_SLOT_REF1', begin)

        end = str(
            self.timeSlotIds[annotation.GetLocation().GetEndMidpoint()])
        alignableRoot.set('TIME_SLOT_REF2', end)

        label = annotation.GetLabel().GetValue()
        valueRoot = ET.SubElement(alignableRoot, 'ANNOTATION_VALUE')
        valueRoot.text = label

    # End __format_alignable_annotation
    # -----------------------------------------------------------------

    def __build_annotation_ids(self):
        self.annotationIds = {}
        i = 0
        for tier in self:
            for annotation in tier:
                id = 'a%s' % i
                i += 1
                self.annotationIds[annotation] = id

    # End __build_annotation_ids
    # -----------------------------------------------------------------

    def __build_timeslots(self):
        self.timeSlotIds = {}
        i = 0
        for tier in self:
            for annotation in tier:
                location = annotation.GetLocation()

                begin = location.GetBeginMidpoint()
                if begin not in self.timeSlotIds:
                    self.timeSlotIds[begin] = 't%s' % i
                    i += 1

                end = location.GetEndMidpoint()
                if end not in self.timeSlotIds:
                    self.timeSlotIds[end] = 't%s' % i
                    i += 1

    # End __build_timeslots
    # -----------------------------------------------------------------
