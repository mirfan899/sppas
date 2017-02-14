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
# File: elan.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import datetime
import logging
import xml.etree.cElementTree as ET

from ..transcription import Transcription
from ..ctrlvocab import CtrlVocab
from ..media import Media
from ..label.label import Label
from ..ptime.point import TimePoint
from ..ptime.interval import TimeInterval
from ..annotation import Annotation

from .utils import indent
from .utils import gen_id
from .utils import merge_overlapping_annotations
from .utils import point2interval

# -----------------------------------------------------------------

CONSTRAINTS = {}
CONSTRAINTS["Time subdivision of parent annotation's time interval, no time gaps allowed within this interval"] = "Time_Subdivision"
CONSTRAINTS["Symbolic subdivision of a parent annotation. Annotations refering to the same parent are ordered"] = "Symbolic_Subdivision"
CONSTRAINTS["1-1 association with a parent annotation"] = "Symbolic_Association"
CONSTRAINTS["Time alignable annotations within the parent annotation's time interval, gaps are allowed"] = "Included_In"

# -----------------------------------------------------------------

ELAN_RADIUS = 0.02


def ElanTimePoint(time, radius=ELAN_RADIUS):
    return TimePoint(time, radius)


def linguistic_type_from_tier(tier):
    return (tier.metadata['LINGUISTIC_TYPE_REF']
            if 'LINGUISTIC_TYPE_REF' in tier.metadata else
            'SPPAS_%s' % tier.GetName())

# -----------------------------------------------------------------


class Elan( Transcription ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Represents the native format of Elan annotated files.
    """

    def read(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        # Read the main header
        headerRoot = root.find('HEADER')
        self.__read_unit(headerRoot)
        if 'MEDIA_FILE' in headerRoot.attrib:
            self.metadata['MEDIA_FILE'] = headerRoot.attrib['MEDIA_FILE']
        for mediaRoot in headerRoot.findall('MEDIA_DESCRIPTOR'):
            self.__read_media(mediaRoot)
        propertyRoot = headerRoot.find('PROPERTY')
        if propertyRoot is not None:
            self.metadata['PROPERTY_NAME']=propertyRoot.attrib['NAME']
            self.metadata['PROPERTY_VALUE']=propertyRoot.text

        timeOrderRoot = root.find('TIME_ORDER')
        self.__read_time_slots(timeOrderRoot)

        self.hierarchyLinks = {}

        # Read all controlled vocabularies, stored in self
        for vocabularyRoot in root.findall('CONTROLLED_VOCABULARY'):
            self.__read_ctrl_vocab(vocabularyRoot, root)

        # Read tiers
        for tierRoot in root.findall('TIER'):
            self.__read_tier(tierRoot, root)

        # Read tier properties (including controlled vocabularies)
        for linguisticRoot in root.findall('LINGUISTIC_TYPE'):
            self.__read_linguistic_type(linguisticRoot, root)

        # manage hierarchyLinks
        for parentTierRef in self.hierarchyLinks:
            child = self.hierarchyLinks[parentTierRef]
            parent = self.Find(parentTierRef)
            # Elan's hierarchy
            try:
                self._hierarchy.add_link('TimeAlignment', child, parent)
            except:
                # TODO: to send a warning
                pass

        del self.hierarchyLinks
        del self.unit
        del self.timeSlots

    # -----------------------------------------------------------------

    def __read_media(self, mediaRoot):
        # Create a Media instance
        mediaid   = gen_id()
        mediaurl  = mediaRoot.attrib['MEDIA_URL']
        mediamime = ''
        if 'MIME_TYPE' in mediaRoot.attrib:
            mediamime = mediaRoot.attrib['MIME_TYPE']
        media = Media( mediaid,mediaurl,mediamime )
        # Add metadata
        if 'RELATIVE_MEDIA_URL' in mediaRoot.attrib:
            media.metadata['RELATIVE_MEDIA_URL'] = mediaRoot.attrib['RELATIVE_MEDIA_URL']
        # Add media into Transcription();
        # but media not linked to tiers... Elan doesn't propose it
        self.AddMedia( media )

    # -----------------------------------------------------------------

    def __read_ctrl_vocab(self, vocabularyRoot, root):
        # Create a CtrlVocab instance
        idvocab = vocabularyRoot.attrib['CV_ID']
        ctrlvocab = CtrlVocab(idvocab)

        # Description
        if "DESCRIPTION" in vocabularyRoot.attrib:
            ctrlvocab.desc = vocabularyRoot.attrib['DESCRIPTION']

        # Add the list of entries
        for entryNode in vocabularyRoot.findall('CV_ENTRY'):
            entrytext = entryNode.text
            entrydesc = ""
            if "DESCRIPTION" in entryNode.attrib:
                entrydesc = entryNode.attrib['DESCRIPTION']
            ctrlvocab.Append( entrytext,entrydesc )

        # if Elan eaf format = 2.8
        for entryNode in vocabularyRoot.findall('CV_ENTRY_ML'):
            entryValueNode = entryNode.find('CVE_VALUE')
            entrytext = entryValueNode.text
            entrydesc = ""
            if "DESCRIPTION" in entryValueNode.attrib:
                entrydesc = entryValueNode.attrib['DESCRIPTION']
            ctrlvocab.Append( entrytext,entrydesc )

        self.AddCtrlVocab( ctrlvocab )

    # -----------------------------------------------------------------

    def __read_tier(self, tierRoot, root):
        tier = self.NewTier(tierRoot.attrib['TIER_ID'])

        linguisticType = tierRoot.attrib['LINGUISTIC_TYPE_REF']
        tier.metadata['LINGUISTIC_TYPE_REF'] = linguisticType

        for key in ['DEFAULT_LOCALE', 'PARTICIPANT']:
            if key in tierRoot.attrib:
                tier.metadata[key] = tierRoot.attrib[key]

        if 'PARENT_REF' in tierRoot.attrib:
            parentRef = tierRoot.attrib['PARENT_REF']
            self.__read_ref_tier(tier, tierRoot, parentRef, root)
        else:
            self.__read_alignable_tier(tier, tierRoot)

    # -----------------------------------------------------------------

    def __read_linguistic_type(self, linguisticRoot, root):
        linguisticType = linguisticRoot.attrib['LINGUISTIC_TYPE_ID']

        # which tier is using this linguistic type?
        found = False
        for tier in self:
            if linguisticType == tier.metadata['LINGUISTIC_TYPE_REF']:
                for key in ['CONSTRAINTS', 'GRAPHIC_REFERENCES', 'TIME_ALIGNABLE' ]:
                    if key in linguisticRoot.attrib:
                        tier.metadata[key] = linguisticRoot.attrib[key]
                # Associate tier with a controlled vocabulary
                if 'CONTROLLED_VOCABULARY_REF' in linguisticRoot.attrib:
                    ctrlvocabid = linguisticRoot.attrib['CONTROLLED_VOCABULARY_REF']
                    ctrlvocab = self.GetCtrlVocabFromId( ctrlvocabid )
                    if ctrlvocab is not None:
                        try:
                            tier.SetCtrlVocab( ctrlvocab )
                        except Exception:
                            # TODO: to send a warning
                            # Because it's a bug in Elan (accept non-controlled text in controlled tier)
                            pass

                found = True

        # what to do with unused linguistic types???????????
        if not found:
            pass

    # -----------------------------------------------------------------

    def __read_ref_tier(self, tier, tierRoot, parentTierRef, root):
        # add a link to process later
        self.hierarchyLinks[parentTierRef] = tier

        # group annotations in batches
        batches = {}
        for annotationRoot in tierRoot.findall('ANNOTATION'):
            if annotationRoot[0].tag == 'ALIGNABLE_ANNOTATION':
                tier.Add( self.__parse_alignable_annotation(annotationRoot[0]) )
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
                tier.Add(Annotation(TimeInterval(ElanTimePoint(x1), ElanTimePoint(x2)),
                                    Label(label)))
                x1 += increment
                x2 += increment

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

    # -----------------------------------------------------------------

    def __read_alignable_tier(self, tier, tierRoot):
        new_a = Annotation(TimePoint(0))
        for annotationRoot in tierRoot.findall('ANNOTATION'):
            annroot = annotationRoot.find('ALIGNABLE_ANNOTATION')
            if annroot is not None:
                new_a = self.__parse_alignable_annotation(annroot)
                tier.Add(new_a)
            else:
                annroot = annotationRoot.find('REF_ANNOTATION')
                if annroot is not None:
                    raise IOError('Corrupted ELAN file. '
                        'Expected an ALIGNABLE_ANNOTATION and got a REF_ANNOTATION: '
                        'PARENT_REF was not defined for tier {:s}. '.format(tier.GetName()))
                else:
                    logging.info('[ERROR] ELAN file error: tier {:s} contains a '
                        ' corrupted annotation after the annotation: '
                        '{:s}.'.format(tier.GetName(), new_a))

    # -----------------------------------------------------------------

    def __parse_alignable_annotation(self, alignableAnnotationRoot):
        label = alignableAnnotationRoot.find('ANNOTATION_VALUE').text

        beginKey = alignableAnnotationRoot.attrib['TIME_SLOT_REF1']
        begin = self.timeSlots[beginKey]

        endKey = alignableAnnotationRoot.attrib['TIME_SLOT_REF2']
        end = self.timeSlots[endKey]

        # TODO: store attrib "SVG_RE" in metadata

        return Annotation(TimeInterval(begin, end), Label(label))

    # -----------------------------------------------------------------

    def __read_unit(self, headerRoot):
        unitString = headerRoot.attrib['TIME_UNITS']
        if unitString == 'milliseconds':
            self.unit = 0.001
        elif unitString == 'seconds':
            self.unit = 1.0

    # -----------------------------------------------------------------

    def __read_time_slots(self, timeOrderRoot):
        timeSlotCouples = []
        for timeSlotNode in timeOrderRoot.findall('TIME_SLOT'):
            id = timeSlotNode.attrib['TIME_SLOT_ID']

            if 'TIME_VALUE' in timeSlotNode.attrib:
                value = ElanTimePoint(
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
                    newVal = ElanTimePoint(midPoint, midPoint -
                                       prevVal.GetMidpoint())
                    timeSlotCouples[i] = (id, newVal)

            self.timeSlots = dict(timeSlotCouples)

    # -----------------------------------------------------------------
    # Writer
    # -----------------------------------------------------------------

    def write(self, filename):
        root = ET.Element('ANNOTATION_DOCUMENT')
        root.set('AUTHOR', 'SPPAS by Brigitte Bigi')
        root.set('DATE',
                 str(datetime.datetime.now()).replace(' ', 'T'))
        root.set('FORMAT', '2.7')
        root.set('VERSION', '2.7')
        root.set('xmlns:xsi',
                 'http://www.w3.org/2001/XMLSchema-instance')
        root.set(
            'xsi:noNamespaceSchemaLocation',
            'http://www.mpi.nl.tools/elan/EAFv2.7.xsd')

        # The Header
        headerRoot = ET.SubElement(root, 'HEADER')
        mediaFile = (self.metadata['MEDIA_FILE']
                     if 'MEDIA_FILE' in self.metadata
                     else '')
        headerRoot.set('MEDIA_FILE', mediaFile)
        headerRoot.set('TIME_UNITS', 'milliseconds')
        # Media in Elan are sub-elements of the header
        self.__write_media(headerRoot)
        # Property
        if 'PROPERTY_NAME' in self.metadata.keys():
            propertyRoot = ET.SubElement(headerRoot, 'PROPERTY')
            propertyRoot.set( 'NAME', self.metadata['PROPERTY_NAME'])
            propertyRoot.text = self.metadata['PROPERTY_VALUE']

        # The list of Time slots
        self.__build_timeslots()
        timeOrderRoot = ET.SubElement(root, 'TIME_ORDER')
        self.__format_timeslots(timeOrderRoot)

        # Add an id in each annotation (in its metadata)
        self.__build_annotation_ids()

        # Tiers
        for tier in self:
            tierRoot = ET.SubElement(root, 'TIER')
            self.__format_tier(tierRoot, tier)

        # Ctrl Vocab and tier properties
        self.__write_linguistic_types(root)
        self.__write_constraints(root)
        self.__write_ctrl_vocabs(root)

        del self.timeSlotIds

        indent(root)
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', method="xml")

    # End write
    # -----------------------------------------------------------------

    def __write_media(self, root):
        for media in self.GetMedia():
            if media:
                mediaRoot = ET.SubElement(root, 'MEDIA_DESCRIPTOR')
                mediaRoot.set( 'MEDIA_URL', media.url )
                mediaRoot.set( 'MIME_TYPE', media.mime )
                # other...
                if 'RELATIVE_MEDIA_URL' in media.metadata.keys():
                    mediaRoot.set( 'RELATIVE_MEDIA_URL', media.metadata['RELATIVE_MEDIA_URL'] )

    # -----------------------------------------------------------------

    def __write_linguistic_types(self, root):
        # Create the list of nodes for linguistic types
        types = set()
        for tier in self:
            types.add(linguistic_type_from_tier(tier))

        for ltype in types:
            typeRoot = ET.SubElement(root, 'LINGUISTIC_TYPE')
            typeRoot.set('LINGUISTIC_TYPE_ID', ltype)

        # Add attributes
        for tier in self:
            linguisticType = linguistic_type_from_tier(tier)
            linguisticTypeRoot = root.find(
                'LINGUISTIC_TYPE[@LINGUISTIC_TYPE_ID=\'%s\']' %linguisticType)

            # required attribute
            if not 'TIME_ALIGNABLE' in linguisticTypeRoot.attrib:
                linguisticTypeRoot.set('TIME_ALIGNABLE', tier.metadata.get('TIME_ALIGNABLE', "true"))

            # Optional attributes
            for key in ['CONSTRAINTS', 'GRAPHIC_REFERENCES' ]:
                if not key in linguisticTypeRoot.attrib and key in tier.metadata.keys():
                    linguisticTypeRoot.set(key, tier.metadata[key])

            ctrlvocab = tier.GetCtrlVocab()
            if ctrlvocab is not None:
                # add reference to ctlrvocab in linguisticType
                if not 'CONTROLLED_VOCABULARY_REF' in linguisticTypeRoot.attrib:
                    linguisticTypeRoot.set('CONTROLLED_VOCABULARY_REF', ctrlvocab.id)

    # -----------------------------------------------------------------

    def __write_ctrl_vocabs(self, root):
        for vocabulary in self.GetCtrlVocab():
            if vocabulary is None:
                continue

            vocabularyRoot = ET.SubElement(root, 'CONTROLLED_VOCABULARY')

            # Set attribute
            vocabularyRoot.set('CV_ID', vocabulary.id)
            if len(vocabulary.desc)>0:
                vocabularyRoot.set('DESCRIPTION', vocabulary.desc)

            # Write the list of entries
            for entry in vocabulary:
                entryNode = ET.SubElement(vocabularyRoot, 'CV_ENTRY')
                entryNode.text = entry.Text.GetValue()
                if len(entry.desc)>0:
                    entryNode.set('DESCRIPTION',entry.desc)

    # -----------------------------------------------------------------

    def __write_constraints(self, root):
        for desc, stereotype in CONSTRAINTS.items():
            typeRoot = ET.SubElement(root, 'CONSTRAINT')
            typeRoot.set('DESCRIPTION', desc)
            typeRoot.set('STEREOTYPE', stereotype)

    # -----------------------------------------------------------------

    def __format_timeslots(self, timeOrderRoot):
        for timeSlot in self.timeSlotIds:
            timeSlotId = self.timeSlotIds[timeSlot]
            timeSlotNode = ET.SubElement(timeOrderRoot, 'TIME_SLOT')
            timeSlotNode.set('TIME_SLOT_ID', timeSlotId)
            timeSlotNode.set('TIME_VALUE', str(int(timeSlot*1000)))

    # -----------------------------------------------------------------

    def __format_tier(self, tierRoot, tier):
        linguisticType = linguistic_type_from_tier(tier)

        tierRoot.set('LINGUISTIC_TYPE_REF', linguisticType)
        tierRoot.set('TIER_ID', tier.GetName())
        for key in ['DEFAULT_LOCALE', 'PARTICIPANT']:
            if key in tier.metadata.keys():
                tierRoot.set(key, tier.metadata[key])

        if tier.IsPoint():
            tier = point2interval(tier, ELAN_RADIUS)
        tier = merge_overlapping_annotations(tier)

        parentTier = self._hierarchy.get_parent(tier)
        if parentTier is not None:
            tierRoot.set('PARENT_REF', parentTier.GetName())
            self.previousRefId = None

            for annotation in tier:
                annotationRoot = ET.SubElement(tierRoot, 'ANNOTATION')
                self.__format_ref_annotation(annotationRoot, annotation, parentTier)
            del self.previousRefId

        else:
            for annotation in tier:
                annotationRoot = ET.SubElement(tierRoot, 'ANNOTATION')
                created = self.__format_alignable_annotation(annotationRoot, annotation)
                if created is False:
                    tierRoot.remove(annotationRoot)

    # -----------------------------------------------------------------

    def __format_ref_annotation(self, annotationRoot, annotation, parentTier):
        begin = annotation.GetLocation().GetBeginMidpoint()
        end   = annotation.GetLocation().GetEndMidpoint()

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

        ida = annotation.metadata['id']
        refRoot.set('ANNOTATION_ID', ida)

        parentAnnotationId = parentAnnotation.metadata['id']
        refRoot.set('ANNOTATION_REF',
                    parentAnnotationId)

        if self.previousRefId is not None:
            refRoot.set('PREVIOUS_ANNOTATION',
                        self.previousRefId)

        label = annotation.GetLabel().GetValue()
        valueRoot = ET.SubElement(refRoot, 'ANNOTATION_VALUE')
        valueRoot.text = label

        self.previousRefId = id

    # -----------------------------------------------------------------

    def __format_alignable_annotation(self, annotationRoot, annotation):
        # the interval is too small???
        begin = str(self.timeSlotIds[round(annotation.GetLocation().GetBeginMidpoint(),4)])
        end   = str(self.timeSlotIds[round(annotation.GetLocation().GetEndMidpoint(),4)])
        if begin == end:
            return False
        alignableRoot = ET.SubElement(annotationRoot, 'ALIGNABLE_ANNOTATION')
        alignableRoot.set('ANNOTATION_ID', annotation.metadata['id'] )
        alignableRoot.set('TIME_SLOT_REF1', begin)
        alignableRoot.set('TIME_SLOT_REF2', end)

        label = annotation.GetLabel().GetValue()
        valueRoot = ET.SubElement(alignableRoot, 'ANNOTATION_VALUE')
        valueRoot.text = label
        return True

    # -----------------------------------------------------------------

    def __build_annotation_ids(self):
        i = 0
        for tier in self:
            for annotation in tier:
                ida = 'a%s' % i
                i += 1
                annotation.metadata['id'] = ida

    # -----------------------------------------------------------------

    def __build_timeslots(self):
        timevalues = []

        for tier in self:

            if tier.IsPoint():
                tier = point2interval(tier,ELAN_RADIUS)
            tier = merge_overlapping_annotations(tier)

            for annotation in tier:
                location = annotation.GetLocation()
                #What about PointTiers???????
                #TODO !!
                begin = round(location.GetBeginMidpoint(),4)
                end   = round(location.GetEndMidpoint(),4)
                if not begin in timevalues:
                    timevalues.append(begin)

                if not end in timevalues:
                    timevalues.append(end)

        self.timeSlotIds = {}
        for i,v in enumerate(timevalues):
            self.timeSlotIds[v] = 't%s' % i

    # -----------------------------------------------------------------
