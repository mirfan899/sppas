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
# File: audiosilencepresenter.py
# ----------------------------------------------------------------------------


__docformat__ = """epytext"""
__authors__   = """Nicolas Chazeau (n.chazeau94@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import audiodata
import annotationdata.io

from audiodata.audio import AudioPCM
from annotationdata.transcription import Transcription

import os
import codecs

# ----------------------------------------------------------------------------

class AudioSilencePresenter( object ):
    """
    @authors: Nicolas Chazeau, Brigitte Bigi
    @contact: n.chazeau94@gmail.com, brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: An audio presenter class to export silence.

    """
    def __init__(self, channelsil):
        """
        Create a AudioSilencePresenter.

        """
        self.channelsil = channelsil


    def __write_track(self, tracktxtname, trackcontent):
        encoding='utf-8'
        with codecs.open(tracktxtname,"w", encoding) as fp:
            fp.write(trackcontent)


    def write_tracks(self, trstracks, output, ext="txt", trsunits=[], trsnames=[]):
        """
        Write tracks in an output directory.

        Print only errors in a log file.

        @param trstracks   All tracks as an array of tuples (start,end)
        @param output      Directory name (String)
        @param ext         Tracks file names extension (String)
        @param trsunits    Tracks content (Array of string)
        @param trsnames    Expected tracks file's names (Array of string)
        @param logfile     Log file (sppasLog)

        """
        if not os.path.exists( output ):
            os.mkdir( output )

        # Write text tracks

        for i in range(len(trsunits)):
            trackbasename = ""
            if len(trsnames) > 0:
                # Specific names are given
                trackbasename = os.path.join(output, trsnames[i])
            else:
                trackbasename = os.path.join(output, "track_%.06d" % (i+1))
            if len(trackbasename)>0:
                # Write the transcription track content (if any)
                if len(trsunits)>0:
                    tracktxtname = trackbasename+"."+ext
                    if isinstance(trsunits[0], Transcription):
                        annotationdata.io.write(tracktxtname, trsunits[i])
                    else:
                        self.__write_track(tracktxtname, trsunits[i])

        # Write audio tracks

        if self.channelsil.get_channel() is None:
            return

        try:
            split_tracks = self.channelsil.track_data( trstracks )
        except Exception as e:
            raise Exception('Split into tracks failed: audio corrupted: %s'%e)

        for i, split_track in enumerate(split_tracks):
            trackbasename = ""
            if len(trsnames) > 0:
                # Specific names are given
                trackbasename = os.path.join(output, trsnames[i])
            else:
                trackbasename = os.path.join(output, "track_%.06d" % (i+1))
            if len(trackbasename)>0:
                # Write the audio track content
                trackwavname = trackbasename+".wav"
                audio_out = AudioPCM()
                audio_out.append_channel(self.channelsil.get_channel())
                try:
                    audiodata.io.save_fragment(trackwavname, audio_out, split_track)
                except Exception as e:
                    raise Exception("Split into tracks failed: can't write tracks: %s. %s"%(trackwavname,e))

# ----------------------------------------------------------------------------
