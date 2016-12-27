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


import codecs
from xml.dom.minidom import parse
from xml.dom.expatbuilder import Node

from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.label.silence import Silence
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.annotation import Annotation


class Transcriber(Transcription):
    """ Represents a Transcription from Transcriber.
        trs files are the native file format of the GPL tool Transcriber:
        a tool for segmenting, labelling and transcribing speech.
        http://trans.sourceforge.net/en/presentation.php
    """

    def __init__(self, name="NoName", coeff=1, mintime=None, maxtime=None):
        """ Creates a new Transcriber Transcription instance.
        """
        self.__currentNode__ = None
        Transcription.__init__(self, name, coeff, mintime, maxtime)

    # End __init__
    # ------------------------------------------------------------------------


    def read(self, filename):
        """ Import a transcription from a .trs file.
            Parameters:
                - filename (String)
            Exception: IOError 
        """
        try:
            encoding='utf-8'
            fp = codecs.open(filename, 'r', encoding)
        except Exception, e:
            raise e

        #looking for the encoding
        firstline = fp.readline()
        if "encoding=\"" in firstline:
            self.encoding = firstline.split('encoding=\"')[1].split("\"")[0]
        else:
            self.encoding = 'utf_8'
        fp.close()

        try:
            self.doc = parse(filename)
        except Exception, e:
            raise e

        # One Tier by speaker is created depending on the "Speaker" nodes
        for speaker in self.get_root_element().getElementsByTagName('Speaker'):
            # create a new tier with the speaker ID
            tiername = speaker.getAttribute('id').strip()
            newtier = self.NewTier( tiername )
            # set the metadata to this tier
            for att in speaker.attributes.items():
                newtier.SetMetadata(att)

        # test if the transcription is empty (=no speaker)
        if self.IsEmpty():
            raise Exception('Empty Transcription.\n')

        # Examine only the "Turn" nodes
        for turn in self.get_root_element().getElementsByTagName('Turn'):

            # Get turn data
            self.start  = float( turn.getAttribute('startTime') )
            self.end    = float( turn.getAttribute('endTime') )
            speaker     = turn.getAttribute('speaker').strip()
            if not speaker:
                for tier in self:
                    if tier.IsEmpty() is False:
                        _end = tier.GetEnd()
                        if _end < self.start:
                            time = TimeInterval(TimePoint(_end), TimePoint(self.start))
                            silence = Silence("#")
                            tier.Append(Annotation(time, silence))
                    time = TimeInterval(TimePoint(self.start), TimePoint(self.end))
                    silence = Silence("#")
                    tier.Append(Annotation(time, silence))
                continue
            else:
                tier = self.Find(speaker)

            #for each node in the turn
            for child in turn.childNodes:

                if child.nodeType == Node.TEXT_NODE:
                    # add this text to the last created interval in the tier
                    self.add_label_at_end(tier, child.nodeValue)

                elif child.nodeType == Node.ELEMENT_NODE:
                    if child.tagName == 'Sync' or child.tagName == 'Background':
                        segment = float(child.getAttribute('time'))
                        #if it is not the beginning of the turn
                        # Change the end-time of the previous interval
                        if segment > self.start:
                            try:
                                tier[-1].EndValue = segment
                            except Exception, e:
                                continue
                        _end = segment
                        if tier.IsEmpty() is False:
                            _end = tier.GetEnd()
                        if _end < segment:
                            time = TimeInterval(TimePoint(_end), TimePoint(segment))
                            annotation = Annotation(time, Silence("#"))
                            tier.Append(annotation)
                        if child.tagName == 'Background':
                            time = TimeInterval(TimePoint(segment), TimePoint(self.end))
                            annotation = Annotation(time, Label("*"))
                            tier.Append(annotation)
                        else:
                            time = TimeInterval(TimePoint(segment), TimePoint(self.end))
                            annotation = Annotation(time)
                            tier.Append(annotation)

                    elif child.tagName == 'Event':
                        desc = child.getAttribute('desc')
                        # Add Laugh
                        if desc == "rire":
                            ext = child.getAttribute('extent')
                            if ext == 'begin' or ext == 'end':
                                self.add_label_at_end(tier, ' @@ ')
                            else:
                                self.add_label_at_end(tier, ' @ ')
                        # Inspiration
                        elif desc == "i":
                            self.add_label_at_end(tier, ' * ')
                        else:
                            self.add_label_at_end(tier, '(%s) '%child.getAttribute('desc'))

                    elif child.tagName == 'Who':
                        spk_idx = int(child.getAttribute('nb')) - 1
                        spk_list = speaker.split()
                        if spk_idx >= 0 and spk_idx < len(spk_list):
                            tier = self.Find( spk_list[spk_idx] )

                    elif child.tagName == 'Comment':
                        pass

            # Last interval of the turn
            tier[-1].EndValue =  self.end

        self.set_tier_names()

    # End read
    # ------------------------------------------------------------------   


    def set_tier_names(self):
        for tier in self:
            tier_name = tier.Name
            if 'trs' not in tier_name.lower() and 'trans' not in tier_name.lower() and 'ipu' not in tier_name.lower():
                tier_name= "trs-"+tier_name
            tier.Name = tier_name

    # ------------------------------------------------------------------   


    def add_label_at_end(self, tier, label):
        """ Append the node text to the last annotation of the tier.
            Parameters:  
               - tier is a Tier object
               - label is the text to add (string)
            Exception:   none#Unlabelled label instance
            Return:      none 
        """
        if len(label.strip()) == 0:
            return
        label = label.replace('\"', '\'')
        label = label.replace('\n', ' ')
        label = label.replace('\r', '')
        if (label.strip()=="+"):
            label = "#"
        try:
            if tier.IsEmpty():
                time = TimeInterval(TimePoint(self.start), TimePoint(self.end))
                text = Silence(label) if label == "#" else Label(label)
                annotation = Annotation(time, text)
                tier.Append(annotation)
            else:
                # Add the label to the last interval of the tier.
                # tier[-1].TextValue += label
                lastlabel = tier[-1].TextValue
                tier[-1].Text = Label(lastlabel + label)
        except UnicodeDecodeError as e:
            raise e

    # End add_label_at_end
    # ------------------------------------------------------------------   


    def get_root_element(self):
        if self.__currentNode__ == None:
            self.__currentNode__ = self.doc.documentElement
        return self.__currentNode__

    # End get_root_element
    # ------------------------------------------------------------------   
