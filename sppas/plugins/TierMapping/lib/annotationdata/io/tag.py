#!/usr/bin/env python2
# -*- coding: iso-8859-15 -*-
#
# Copyright (C) 2013  Brigitte Bigi
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.



from xml.dom.minidom import parse

from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation


class Anchor:
    def __init__(self, offset, unit, signals):
        try:
            self.offset = float(offset)
        except ValueError:
            self.offset = None
        self.unit = unit
        self.signals = signals


class TranscriberAG (Transcription):
    """ Represents a Tag Transcription.
        Tag is the native file format of the GPL tool TranscriberAG:
        a tool for segmenting, labeling and transcribing speech.
    """

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """ Creates a new Tag Transcription instance.
        """
        self.__currentNode__ = None
        Transcription.__init__(self, name, coeff, mintime, maxtime)
        self.signal_index = {}
        self.anchors = {}

    # End __init__
    # -----------------------------------------------------------------------


    def read(self, filename):
        self.doc = parse(filename)
        #create one tier by speaker
        timeline = self.get_root_element().getElementsByTagName('Timeline')[0]

        for signal in timeline.getElementsByTagName('Signal'):
            id = signal.getAttribute('id')
            signal_metadata = signal.getElementsByTagName('Metadata')[0]

            for md_elem in signal_metadata.getElementsByTagName('MetadataElement'):
                if md_elem.getAttribute('name') == 'speaker_hint':
                    tier = self.NewTier( name = self.get_node_text(md_elem) )
                    self.signal_index[id] = tier

        if self.IsEmpty():
            raise Exception('Empty Transcription.\n')

        #adding metadata about the speakers
        for speaker in self.get_root_element().getElementsByTagName('Speaker'):
            for tier in self:
                if tier.Name == speaker.getAttribute('id'):
                    #for each attribute of speaker, add a new metadata to self.get_tier(i)
                    for att in speaker.attributes.items():
                        tier.SetMetadata(att)

        for anchor in self.get_root_element().getElementsByTagName('Anchor'):
            try:
                self.anchors[anchor.getAttribute('id')] = Anchor(anchor.getAttribute('offset'),
                                                                 anchor.getAttribute('unit'),
                                                                 anchor.getAttribute('signals'))
            except Exception, e:
                raise Exception('Anchor error at anchor element of id \'%s\':\n%s' % (anchor.getAttribute('id'),str(e)))

        for annot in self.get_root_element().getElementsByTagName('Annotation'):
            if annot.getAttribute('type') == 'unit':
                tier = self.signal_index[ self.anchors[annot.getAttribute('start')].signals ]
                self.add_annotation(tier, annot)

    # End read
    # -----------------------------------------------------------------------


    def add_annotation(self, tier, annot):
        """ Add a point or an interval annotation to the given tier
            Parameters:
                - tier (Tier)
                - annot is a DOM Element
            Return: None
        """
        start = self.get_annot_start(annot)
        end = self.get_annot_end(annot)
        if start == None:
            return
            tier.Append(TimePoint(self.get_annot_end(annot)),
                        Label(self.get_annot_label(annot)))
        elif end ==None:
            return
            tier.Append(TimePoint(self.get_annot_end(annot)),
                        Label(self.get_annot_label(annot)))
        else:
            tier.Append(TimeInterval(TimePoint(start), TimePoint(self.get_annot_end(annot))),
                        Label(self.get_annot_label(annot)))

    # End add_annotation
    # -----------------------------------------------------------------------


    def get_annot_label(self, annot):
        """ Return the label of an annotation using the Annotation node.
            Parameters: annot is a DOM Element
            Return: a string representing the label
        """
        for feature in annot.getElementsByTagName('Feature'):
            if feature.getAttribute('name') == 'value':
                return self.get_node_text(feature)
            elif feature.getAttribute('name') == 'desc':
                if self.get_node_text(feature) == 'laugh':
                    return "@"
                return "{%s}"% self.get_node_text(feature)
        return ""

    # End get_ann_label
    # -----------------------------------------------------------------------


    def get_annot_start(self, annot):
        """Return the start time of an annotation using the Annotation node.
            Parameters: annot is a DOM Element
            Return: a float corresponding to the start time or None if starttime does not exists
        """
        return self.anchors[annot.getAttribute('start')].offset

    # End get_ann_begin
    # -----------------------------------------------------------------------


    def get_annot_end(self, annot):
        """Return the end time of an annotation using the Annotation node.
            Parameters: annot is a DOM Element
            Return: a float corresponding to the end time
        """
        return self.anchors[annot.getAttribute('end')].offset

    # End get_ann_end
    # -----------------------------------------------------------------------


    def get_node_text(self, node):
        try:
            return node.childNodes[0].nodeValue
        except IndexError:
            return ""

    # End get_node_text
    # -----------------------------------------------------------------------


    def get_root_element(self):
        if self.__currentNode__ == None:
            self.__currentNode__ = self.doc.documentElement
        return self.__currentNode__

    # End get_root
    # -----------------------------------------------------------------------
