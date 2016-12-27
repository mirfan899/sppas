#!/usr/bin/env python2
# -*- coding: utf-8 -*-
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
from xml.dom.expatbuilder import Node

from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation


class Elan( Transcription ):
    """ Represents a Transcription from Elan.
        eaf files are the native file format of the GPL tool Elan:
        http://tla.mpi.nl/tools/tla-tools/elan/
        ELAN is a tool for the creation of annotations on video and 
        audio resources.
    """

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """ Creates a new Elan Transcription instance.
        """
        self.__currentNode__ = None
        Transcription.__init__(self, name, coeff, mintime, maxtime)

    # End __init__
    # ------------------------------------------------------------------------


    def read(self, filename):
        """ Import a transcription from a .eaf file.
            Parameters:
                - filename (String)
            Exception: IOError 
        """
        try:
            self.doc = parse( filename )
        except Exception, e:
            raise e

        # Get time type information
        for h in self.get_root_element().getElementsByTagName('HEADER'):
            if h.getAttribute('TIME_UNITS')=="milliseconds":
                self.unit = 1000.0
            if h.getAttribute('TIME_UNITS')=="seconds":
                self.unit = 1.0

        # Get time slots and time values
        mint = -1.0
        maxt = -1.0
        timeslots = {}
        for t in self.get_root_element().getElementsByTagName('TIME_ORDER'):
            for child in t.childNodes:
                if child.nodeType == Node.ELEMENT_NODE and child.tagName == 'TIME_SLOT':
                    tsid  = child.getAttribute('TIME_SLOT_ID') 
                    tsval = float( child.getAttribute('TIME_VALUE') ) / self.unit 
                    timeslots[tsid] = tsval
                    if mint == -1.0 or mint > tsval:
                        mint = tsval
                    if maxt == -1.0 or maxt < tsval:
                        maxt = tsval

        # A set of Tier is created depending on the "TIER" nodes
        for t in self.get_root_element().getElementsByTagName('TIER'):
            # create a new tier
            tiername = t.getAttribute('TIER_ID').strip()
            newtier = self.NewTier(tiername)
            # set the metadata to this tier
            for att in t.attributes.items():
                newtier.SetMetadata(att)

            # Tier structure:
            #<ANNOTATION>
            #    <ALIGNABLE_ANNOTATION ANNOTATION_ID="a1" TIME_SLOT_REF1="ts1" TIME_SLOT_REF2="ts7">
            #        <ANNOTATION_VALUE> bla bla bla </ANNOTATION_VALUE>
            #    </ALIGNABLE_ANNOTATION>
            #</ANNOTATION>

            #for each annotation in the tier
            for a in t.getElementsByTagName('ANNOTATION'):
                #for each alignable_annotation
                for ann in a.childNodes:
                    ts = 0.0
                    te = 0.0
                    if ann.attributes is None:
                        continue

                    # set the time values to this tier (from attributes)
                    ts = timeslots[ ann.getAttribute(u"TIME_SLOT_REF1") ]
                    te = timeslots[ ann.getAttribute(u"TIME_SLOT_REF2") ]

                    # set the label (from child element)
                    label = ""
                    for annval in ann.getElementsByTagName('ANNOTATION_VALUE'):
                        for l in annval.childNodes:
                            if l.nodeValue is not None:
                                label = label + l.nodeValue

                    # First interval?
                    if newtier.IsEmpty()==True and ts > mint:
                        time = TimeInterval(TimePoint(mint), TimePoint(ts))
                        newtier.Append(Annotation(time))
                    # Bug Elan. sometimes, 10 ms between 2 intervals.
                    if newtier.IsEmpty()==False and (newtier.GetEnd()-ts) < 0.011:
                        ts = newtier.GetEnd()
                    # Add the new annotation interval
                        time = TimeInterval(TimePoint(ts), TimePoint(te))
                        newtier.Append(Annotation(time, Label(label)))

        # last intervals (force all tiers to finish at the same time value)
        for tier in self:
            # be careful: the tier can be empty
            if tier.IsEmpty()==False and tier.GetEnd() < maxt:
                begin = TimePoint(tier.GetEnd())
                end = TimePoint(maxt)
                interval = TimeInterval(begin, end)
                annotation = Annotation(interval)
                tier.Append(annotation)

        if self.IsEmpty()==True:
            raise IOError('eaf.py. Empty Transcription.\n')

    # End read
    # ------------------------------------------------------------------   


    def get_root_element(self):
        if self.__currentNode__ == None:
            self.__currentNode__ = self.doc.documentElement
        return self.__currentNode__

    # End get_root_element
    # ------------------------------------------------------------------   
