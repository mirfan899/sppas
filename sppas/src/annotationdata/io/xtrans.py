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
# File: xtrans.py
# ---------------------------------------------------------------------------

import codecs
import mimetypes

from annotationdata.transcription import Transcription
from annotationdata.tier import Tier
from annotationdata.media               import Media

from annotationdata.annotation     import Annotation
from annotationdata.label.label    import Label
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint
import annotationdata.ptime.point
from utils import gen_id

# ----------------------------------------------------------------------------

TEXT_RADIUS = 0.0005

# ----------------------------------------------------------------------------

def TimePoint(time):
    return annotationdata.ptime.point.TimePoint(time, TEXT_RADIUS)

# ----------------------------------------------------------------------------

class Xtrans( Transcription ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Represents a text file from Xtrans software.

    XTrans is a multi-platform, multilingual, multi-channel transcription tool
    that supports manual transcription and annotation of audio recordings.
    Last version of Xtrans was distributed in 2009.
    Consequently... this class implements only a Xtrans reader, not a writer.

    Transcripts are output in a Tab Delimited Format (TDF).

    """
    @staticmethod
    def detect(filename):
        with codecs.open(filename, 'r', 'utf-8') as fp:
            lines = fp.readlines()
            for line in lines:
                if line.startswith(";;"):
                    continue
                tab = line.split('\t')
                if len(tab) < 12:
                    return False

        return True

    # --------------------------------------------------------------------

    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new Xtrans Transcription instance.

        """
        Transcription.__init__(self, name, mintime, maxtime)

    # -----------------------------------------------------------------------

    def read(self, filename):
        """
        Read an Xtrans file and fill the Transcription.
        It creates a tier for each speaker-channel observed in the file.

        """
        with codecs.open(filename, 'r', 'utf-8') as fp:
            lines = fp.readlines()

            rownames = lines[0].split('\t')
            lines.pop(0)
            medias = {}

            # Extract rows, create tiers and metadata.
            for line in lines:

                # a comment
                if line.startswith(';;'):
                    continue

                # a tab-delimited line
                line = line.split('\t')

                # fix the name of the tier
                channel = line[rownames.index('channel;int')]
                speaker = line[rownames.index('speaker;unicode')]
                tiername = speaker+'-'+channel

                # check for the tier (find it or create it)
                tier = self.Find(tiername)
                if tier is None:
                    tier = Tier(tiername)
                    mediaurl = line[rownames.index('file;unicode')]
                    if not mediaurl in medias:
                        mediaid = gen_id()
                        medias[mediaurl] = mediaid
                    mediaid = medias[mediaurl]
                    (mediamime,mediaencoding) = mimetypes.guess_type(mediaurl)
                    media = Media( mediaid, mediaurl, mediamime )
                    if mediaencoding is not None:
                        media.metadata[ "encoding" ] = mediaencoding

                    tier.SetMedia( media )
                    tier.metadata[ "speakerName" ]    = speaker
                    tier.metadata[ "speakerType" ]    = line[ rownames.index('speakerType;unicode') ]
                    tier.metadata[ "speakerDialect" ] = line[ rownames.index('speakerDialect;unicode') ]
                    tier.metadata[ "mediaChannel" ]   = channel
                    self.Append( tier )

                # Add the new annotation
                label = Label( line[rownames.index('transcript;unicode')] )
                begin = TimePoint( float( line[rownames.index('start;float')] ) )
                end   = TimePoint( float( line[rownames.index('end;float')] ) )
                new_ann = Annotation(TimeInterval(begin,end), label)
                tier.Add( new_ann )
