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

from annotationdata.transcription import Transcription
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation
from annotationdata.label.label import Label
import annotationdata.ptime.point
import xml.etree.cElementTree as ET


ANVIL_RADIUS = 0.02


def TimePoint(time):
    return annotationdata.ptime.point.TimePoint(time, ANVIL_RADIUS)


class Anvil(Transcription):
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Create a new Transcription instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)

    # End __init__
    # -----------------------------------------------------------------

    def read(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()

        # FIXME we ought to get the ctrl vocabs in the spec file
        # there also ought to be a representation of the hiererchy,
        # but since we have multiple, non aligned tiers,
        # it's not trivial to implement

        bodyRoot = root.find('body')

        self.__read_tracks(bodyRoot)

    # End read
    # -----------------------------------------------------------------

    def __read_tracks(self, bodyRoot):
        for trackRoot in bodyRoot.findall('track'):
            if(trackRoot.attrib['type'] == "primary" or
               trackRoot.attrib['type'] == "primarypoint"):
                self.__read_primary_track(trackRoot)

            elif trackRoot.attrib['type'] == "singleton":
                self.__read_singleton_track(trackRoot, bodyRoot)

            elif trackRoot.attrib['type'] == "span":
                self.__read_span_track(trackRoot, bodyRoot)

            elif trackRoot.attrib['type'] == "subdivision":
                self.__read_subdivision_track(trackRoot, bodyRoot)

            else:
                raise Exception('unknown track type')

    # End __read_tracks
    # -----------------------------------------------------------------

    def __read_primary_track(self, trackRoot):
        """
        Read a primary track (primary or primarypoint)
        """
        for attributeNode in trackRoot.iter('attribute'):
            tierName = (trackRoot.attrib['name'] +
                        '.' + attributeNode.attrib['name'])
            if self.Find(tierName) is None:
                self.NewTier(tierName)

        for elRoot in trackRoot.findall('el'):
            if trackRoot.attrib['type'] == 'primary':
                begin = float(elRoot.attrib['start'])
                end = float(elRoot.attrib['end'])
                if begin > end:
                    begin, end = end, begin
                elif begin == end:
                    continue

                location = TimeInterval(TimePoint(begin), TimePoint(end))
            elif trackRoot.attrib['type'] == 'primarypoint':
                time = float(elRoot.attrib['time'])
                location = TimePoint(time)
            else:
                raise Exception('unknown primary track type')

            for attributeNode in elRoot.findall('attribute'):
                label = attributeNode.text
                tier = self.Find(
                    trackRoot.attrib['name'] +
                    '.' + attributeNode.attrib['name'])
                tier.Append(Annotation(location, Label(label)))

    # End __read_primary_track
    # -----------------------------------------------------------------

    def __read_singleton_track(self, trackRoot, bodyRoot):
        # find ref
        refRoot = bodyRoot.find(
            "track[@name='%s']" %
            trackRoot.attrib['ref'])

        for attributeNode in trackRoot.iter('attribute'):
            tierName = (trackRoot.attrib['name'] +
                        '.' + attributeNode.attrib['name'])
            if self.Find(tierName) is None:
                self.NewTier(tierName)

        for elRoot in trackRoot.findall('el'):
            refEl = refRoot.find(
                "el[@index='%s']" %
                elRoot.attrib['ref'])
            begin = float(refEl.attrib['start'])
            end = float(refEl.attrib['end'])
            if begin > end:
                begin, end = end, begin
            elif begin == end:
                continue

            location = TimeInterval(TimePoint(begin), TimePoint(end))

            for attributeNode in elRoot.findall('attribute'):
                label = attributeNode.text
                tier = self.Find(
                    trackRoot.attrib['name'] +
                    '.' + attributeNode.attrib['name'])
                tier.Append(Annotation(location, Label(label)))

    # End __read_singleton_track
    # -----------------------------------------------------------------

    def __read_span_track(self, trackRoot, bodyRoot):
        # find ref
        refRoot = bodyRoot.find(
            "track[@name='%s']" %
            trackRoot.attrib['ref'])

        for attributeNode in trackRoot.iter('attribute'):
            tierName = (trackRoot.attrib['name'] +
                        '.' + attributeNode.attrib['name'])
            if self.Find(tierName) is None:
                self.NewTier(tierName)

        for elRoot in trackRoot.findall('el'):
            beginRef = elRoot.attrib['start']
            endRef = elRoot.attrib['end']
            beginEl = refRoot.find(
                "el[@index='%s']" %
                beginRef)
            endEl = refRoot.find(
                "el[@index='%s']" %
                endRef)
            begin = float(beginEl.attrib['start'])
            end = float(endEl.attrib['end'])
            if begin > end:
                begin, end = end, begin
            elif begin == end:
                continue

            location = TimeInterval(TimePoint(begin), TimePoint(end))

            for attributeNode in elRoot.findall('attribute'):
                label = attributeNode.text
                tier = self.Find(
                    trackRoot.attrib['name'] +
                    '.' + attributeNode.attrib['name'])
                tier.Append(Annotation(location, Label(label)))

    # End __read_span_track
    # -----------------------------------------------------------------

    def __read_subdivision_track(self, trackRoot, bodyRoot):
        # find ref
        refRoot = bodyRoot.find(
            "track[@name='%s']" %
            trackRoot.attrib['ref'])

        for attributeNode in trackRoot.iter('attribute'):
            tierName = (trackRoot.attrib['name'] +
                        '.' + attributeNode.attrib['name'])
            if self.Find(tierName) is None:
                self.NewTier(tierName)

        for elGroupRoot in trackRoot.findall('el-group'):
            refEl = refRoot.find(
                "el[@index='%s']" %
                elGroupRoot.attrib['ref'])

            timeSlots = []
            timeSlots.append(float(refEl.attrib['start']))
            for elRoot in elGroupRoot.findall('el'):
                if 'start' in elRoot.attrib:
                    timeSlots.append(float(elRoot.attrib['start']))
            timeSlots.append(float(refEl.attrib['end']))

            b = 0
            e = 1

            for elRoot in elGroupRoot.findall('el'):
                begin = timeSlots[b]
                b += 1
                end = timeSlots[e]
                e += 1
                location = TimeInterval(TimePoint(begin), TimePoint(end))

                for attributeNode in elRoot.findall('attribute'):
                    label = attributeNode.text
                    tier = self.Find(
                        trackRoot.attrib['name'] +
                        '.' + attributeNode.attrib['name'])
                    tier.Append(Annotation(location, Label(label)))

    # End __read_subdivision_track
    # -----------------------------------------------------------------
