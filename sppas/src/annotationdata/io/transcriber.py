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


import xml.etree.cElementTree as ET
from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation


def add_at_label_end(tier, annotation, labelString):
    oldlabel = annotation.GetLabel().GetValue()
    labelString = oldlabel + labelString
    newAnnotation = Annotation(annotation.GetLocation(),
                               Label(labelString))

    for i in range(0, len(tier)):
        if tier[i] is annotation:
            tier.Pop(i)
            break
    tier.Add(newAnnotation)

# End add_at_label_end
# -----------------------------------------------------------------


class Transcriber(Transcription):
    """
    Represents a Transcription from Transcriber.

    trs files are the native file format of the GPL tool Transcriber:
    a tool for segmenting, labelling and transcribing speech.

    See http://trans.sourceforge.net/en/presentation.php

    """

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new Transcriber Transcription instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)

    # End __init__
    # ------------------------------------------------------------------------

    @staticmethod
    def detect(filename):
        with codecs.open(filename, 'r', 'utf-8') as it:
            it.next()
            doctypeLine = it.next().strip()

        return doctypeLine == '<!DOCTYPE Trans SYSTEM "trans-14.dtd">'

    # End detect
    # -----------------------------------------------------------------

    def __read_turn(self, turnRoot):
        turnBegin = float(turnRoot.attrib['startTime'])
        turnEnd = float(turnRoot.attrib['endTime'])
        speakers = (turnRoot.attrib['speaker'].split()
                    if 'speaker' in turnRoot.attrib
                    else [])

        if len(speakers) == 0:
            tier = self[0]
        elif len(speakers) == 1:
            tier = self.Find('Trans'+speakers[0])
        else:
            tier = None

        begin = turnBegin

        # handle text direcltly inside the Turn
        if turnRoot.text.strip() != '':
            # create new annotation without end
            prevAnnotation = Annotation(TimeInterval(TimePoint(begin),
                                                     TimePoint(turnEnd)),
                                        Label(turnRoot.text))
            tier.Add(prevAnnotation)
        else:
            prevAnnotation = None

        for node in turnRoot.iter():
            if node.tag == 'Sync':
                begin = float(node.attrib['time'])
                if prevAnnotation is not None:
                    prevAnnotation.GetLocation().SetEnd(TimePoint(begin))

            elif node.tag == 'Who':
                index = int(node.attrib['nb']) - 1
                tier = self.Find('Trans'+speakers[index])

            elif node.tag == 'Event':
                if prevAnnotation is None:
                    prevAnnotation = Annotation(TimeInterval(TimePoint(begin),
                                                             TimePoint(turnEnd)
                                                             ),
                                                Label())
                    tier.Add(prevAnnotation)

                description = node.attrib['desc']
                extent = (node.attrib['extent']
                          if 'extent' in node.attrib
                          else '')
                if description == 'rire':
                    if extent == 'begin' or extent == 'end':
                        add_at_label_end(tier, prevAnnotation, ' @@ ')
                    else:
                        add_at_label_end(tier, prevAnnotation, ' @ ')
                elif description == 'i':
                    add_at_label_end(tier, prevAnnotation, ' * ')
                else:
                    add_at_label_end(tier,
                                     prevAnnotation, '(%s) ' % description)

            if node.tail.strip() != "":
                # create new annotation without end
                newAnnotation = Annotation(TimeInterval(TimePoint(begin),
                                                        TimePoint(turnEnd)
                                                        ),
                                           Label(node.tail))
                tier.Add(newAnnotation)
                # end the previous annotation
                prevAnnotation = newAnnotation

    # End __read_turn
    # -----------------------------------------------------------------

    def read(self, filename):
        """
        Import a transcription from a .trs file.

        @param filename: (str)

        """
        tree = ET.parse(filename)
        root = tree.getroot()

        # One Tier by speaker is created depending on the "Speaker" nodes
        for speaker in root.iter('Speaker'):
            # create a new tier with the speaker ID
            tiername = speaker.attrib['id'].strip()
            newtier = self.NewTier('Trans'+tiername)
            # set the metadata to this tier
            for key in speaker.attrib:
                newtier.metadata[key] = speaker.attrib[key]

        # test if the transcription is empty (=no speaker)
        if self.IsEmpty():
            self.NewTier('Trans')

        # Examine only the "Turn" nodes
        for turnRoot in root.iter('Turn'):
            self.__read_turn(turnRoot)

        # Update
        self.SetMinTime(0)
        self.SetMaxTime(self.GetEnd())

    # End read
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
